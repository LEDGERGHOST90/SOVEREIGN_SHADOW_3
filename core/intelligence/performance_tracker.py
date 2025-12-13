#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Performance Tracker
Tracks all strategy performance for self-annealing learning loop

Database Schema:
- trades: All executed trades with P&L
- strategy_performance: Aggregated metrics per strategy per regime
- regime_history: Historical regime classifications

Author: SovereignShadow Trading System
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Single trade record"""
    trade_id: str
    strategy_name: str
    regime: str
    asset: str
    timeframe: str
    side: str  # 'BUY' or 'SELL'
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: str
    exit_time: str
    pnl_usd: float
    pnl_percent: float
    exit_reason: str  # 'TAKE_PROFIT', 'STOP_LOSS', 'SIGNAL_EXIT', 'MANUAL'
    fees_usd: float = 0.0
    metadata: str = "{}"  # JSON string for additional data


@dataclass
class StrategyPerformance:
    """Aggregated strategy performance per regime"""
    strategy_name: str
    regime: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl_usd: float
    avg_pnl_percent: float
    sharpe_ratio: float
    max_drawdown: float
    expectancy: float
    profit_factor: float
    avg_win_usd: float
    avg_loss_usd: float
    last_updated: str
    score: float = 0.0  # Composite score for ranking


class PerformanceTracker:
    """
    Performance tracking database for strategy self-annealing
    
    Key features:
    - SQLite persistence
    - Trade-by-trade logging
    - Aggregated metrics per strategy/regime
    - Historical regime tracking
    - Strategy scoring for selection
    """
    
    def __init__(self, db_path: str = "sovereign_shadow.db"):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()
        
        logger.info(f"📊 Performance Tracker initialized: {db_path}")
    
    def _init_database(self):
        """Initialize database tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Trades table - individual trade records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                asset TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity REAL NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT NOT NULL,
                pnl_usd REAL NOT NULL,
                pnl_percent REAL NOT NULL,
                exit_reason TEXT NOT NULL,
                fees_usd REAL DEFAULT 0.0,
                metadata TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Strategy performance table - aggregated metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                total_pnl_usd REAL DEFAULT 0.0,
                avg_pnl_percent REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                expectancy REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                avg_win_usd REAL DEFAULT 0.0,
                avg_loss_usd REAL DEFAULT 0.0,
                score REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, regime)
            )
        """)
        
        # Regime history table - track regime changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regime_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regime TEXT NOT NULL,
                asset TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                confidence REAL NOT NULL,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_regime ON trades(regime)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_asset ON trades(asset)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategy_perf ON strategy_performance(strategy_name, regime)")
        
        self.conn.commit()
        logger.info("✅ Database tables initialized")
    
    def log_trade(self, trade: TradeRecord) -> bool:
        """
        Log a completed trade
        
        Args:
            trade: TradeRecord object
            
        Returns:
            bool: True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades (
                    trade_id, strategy_name, regime, asset, timeframe,
                    side, entry_price, exit_price, quantity,
                    entry_time, exit_time, pnl_usd, pnl_percent,
                    exit_reason, fees_usd, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id, trade.strategy_name, trade.regime, trade.asset,
                trade.timeframe, trade.side, trade.entry_price, trade.exit_price,
                trade.quantity, trade.entry_time, trade.exit_time,
                trade.pnl_usd, trade.pnl_percent, trade.exit_reason,
                trade.fees_usd, trade.metadata
            ))
            
            self.conn.commit()
            
            # Update aggregated performance
            self._update_strategy_performance(trade.strategy_name, trade.regime)
            
            logger.info(f"✅ Trade logged: {trade.trade_id} ({trade.strategy_name}) PnL: ${trade.pnl_usd:+.2f}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  Trade already exists: {trade.trade_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to log trade: {e}")
            return False
    
    def _update_strategy_performance(self, strategy_name: str, regime: str):
        """Update aggregated performance metrics for a strategy/regime"""
        cursor = self.conn.cursor()
        
        # Get all trades for this strategy/regime
        cursor.execute("""
            SELECT pnl_usd, pnl_percent FROM trades
            WHERE strategy_name = ? AND regime = ?
            ORDER BY exit_time ASC
        """, (strategy_name, regime))
        
        rows = cursor.fetchall()
        
        if not rows:
            return
        
        pnl_usd_list = [r['pnl_usd'] for r in rows]
        pnl_pct_list = [r['pnl_percent'] for r in rows]
        
        total_trades = len(rows)
        winning_trades = sum(1 for p in pnl_usd_list if p > 0)
        losing_trades = sum(1 for p in pnl_usd_list if p <= 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl_usd = sum(pnl_usd_list)
        avg_pnl_percent = sum(pnl_pct_list) / total_trades if total_trades > 0 else 0
        
        # Calculate win/loss averages
        wins = [p for p in pnl_usd_list if p > 0]
        losses = [p for p in pnl_usd_list if p <= 0]
        avg_win_usd = sum(wins) / len(wins) if wins else 0
        avg_loss_usd = sum(losses) / len(losses) if losses else 0
        
        # Profit factor
        total_wins = sum(wins)
        total_losses = abs(sum(losses))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win_usd) + ((1 - win_rate) * avg_loss_usd)
        
        # Sharpe ratio (simplified)
        import statistics
        if len(pnl_pct_list) >= 2:
            mean_return = statistics.mean(pnl_pct_list)
            std_return = statistics.stdev(pnl_pct_list)
            sharpe_ratio = (mean_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(pnl_usd_list)
        
        # Composite score (weighted combination of metrics)
        score = self._calculate_score(
            win_rate, expectancy, sharpe_ratio, profit_factor, total_trades
        )
        
        # Upsert performance record
        cursor.execute("""
            INSERT INTO strategy_performance (
                strategy_name, regime, total_trades, winning_trades, losing_trades,
                win_rate, total_pnl_usd, avg_pnl_percent, sharpe_ratio,
                max_drawdown, expectancy, profit_factor, avg_win_usd, avg_loss_usd,
                score, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(strategy_name, regime) DO UPDATE SET
                total_trades = excluded.total_trades,
                winning_trades = excluded.winning_trades,
                losing_trades = excluded.losing_trades,
                win_rate = excluded.win_rate,
                total_pnl_usd = excluded.total_pnl_usd,
                avg_pnl_percent = excluded.avg_pnl_percent,
                sharpe_ratio = excluded.sharpe_ratio,
                max_drawdown = excluded.max_drawdown,
                expectancy = excluded.expectancy,
                profit_factor = excluded.profit_factor,
                avg_win_usd = excluded.avg_win_usd,
                avg_loss_usd = excluded.avg_loss_usd,
                score = excluded.score,
                last_updated = excluded.last_updated
        """, (
            strategy_name, regime, total_trades, winning_trades, losing_trades,
            win_rate, total_pnl_usd, avg_pnl_percent, sharpe_ratio,
            max_drawdown, expectancy, profit_factor, avg_win_usd, avg_loss_usd,
            score, datetime.utcnow().isoformat()
        ))
        
        self.conn.commit()
    
    def _calculate_max_drawdown(self, pnl_list: List[float]) -> float:
        """Calculate maximum drawdown from P&L list"""
        if not pnl_list:
            return 0.0
        
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for pnl in pnl_list:
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def _calculate_score(
        self,
        win_rate: float,
        expectancy: float,
        sharpe_ratio: float,
        profit_factor: float,
        total_trades: int
    ) -> float:
        """
        Calculate composite score for strategy ranking
        
        Weights:
        - Expectancy: 30% (most important)
        - Sharpe Ratio: 25%
        - Win Rate: 20%
        - Profit Factor: 15%
        - Trade Count: 10% (more data = more confidence)
        """
        # Normalize metrics to 0-100 scale
        exp_score = min(max(expectancy * 100, 0), 100)
        sharpe_score = min(max(sharpe_ratio * 20, 0), 100)
        wr_score = win_rate * 100
        pf_score = min(max(profit_factor * 25, 0), 100)
        trade_score = min(total_trades * 2, 100)  # Cap at 50 trades
        
        # Weighted combination
        score = (
            exp_score * 0.30 +
            sharpe_score * 0.25 +
            wr_score * 0.20 +
            pf_score * 0.15 +
            trade_score * 0.10
        )
        
        return round(score, 2)
    
    def get_strategy_performance(
        self,
        strategy_name: str,
        regime: Optional[str] = None
    ) -> List[StrategyPerformance]:
        """
        Get performance metrics for a strategy
        
        Args:
            strategy_name: Strategy name
            regime: Optional regime filter
            
        Returns:
            List of StrategyPerformance objects
        """
        cursor = self.conn.cursor()
        
        if regime:
            cursor.execute("""
                SELECT * FROM strategy_performance
                WHERE strategy_name = ? AND regime = ?
            """, (strategy_name, regime))
        else:
            cursor.execute("""
                SELECT * FROM strategy_performance
                WHERE strategy_name = ?
            """, (strategy_name,))
        
        rows = cursor.fetchall()
        
        return [StrategyPerformance(
            strategy_name=r['strategy_name'],
            regime=r['regime'],
            total_trades=r['total_trades'],
            winning_trades=r['winning_trades'],
            losing_trades=r['losing_trades'],
            win_rate=r['win_rate'],
            total_pnl_usd=r['total_pnl_usd'],
            avg_pnl_percent=r['avg_pnl_percent'],
            sharpe_ratio=r['sharpe_ratio'],
            max_drawdown=r['max_drawdown'],
            expectancy=r['expectancy'],
            profit_factor=r['profit_factor'],
            avg_win_usd=r['avg_win_usd'],
            avg_loss_usd=r['avg_loss_usd'],
            score=r['score'],
            last_updated=r['last_updated']
        ) for r in rows]
    
    def get_top_strategies(
        self,
        regime: str,
        limit: int = 10,
        min_trades: int = 5
    ) -> List[StrategyPerformance]:
        """
        Get top performing strategies for a regime
        
        Args:
            regime: Market regime
            limit: Number of strategies to return
            min_trades: Minimum trades required
            
        Returns:
            List of StrategyPerformance sorted by score
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM strategy_performance
            WHERE regime = ? AND total_trades >= ?
            ORDER BY score DESC
            LIMIT ?
        """, (regime, min_trades, limit))
        
        rows = cursor.fetchall()
        
        return [StrategyPerformance(
            strategy_name=r['strategy_name'],
            regime=r['regime'],
            total_trades=r['total_trades'],
            winning_trades=r['winning_trades'],
            losing_trades=r['losing_trades'],
            win_rate=r['win_rate'],
            total_pnl_usd=r['total_pnl_usd'],
            avg_pnl_percent=r['avg_pnl_percent'],
            sharpe_ratio=r['sharpe_ratio'],
            max_drawdown=r['max_drawdown'],
            expectancy=r['expectancy'],
            profit_factor=r['profit_factor'],
            avg_win_usd=r['avg_win_usd'],
            avg_loss_usd=r['avg_loss_usd'],
            score=r['score'],
            last_updated=r['last_updated']
        ) for r in rows]
    
    def log_regime(
        self,
        regime: str,
        asset: str,
        timeframe: str,
        confidence: float,
        metadata: Optional[Dict] = None
    ):
        """Log a regime detection"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO regime_history (regime, asset, timeframe, confidence, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (regime, asset, timeframe, confidence, json.dumps(metadata or {})))
        
        self.conn.commit()
    
    def get_recent_trades(
        self,
        limit: int = 50,
        strategy_name: Optional[str] = None
    ) -> List[Dict]:
        """Get recent trades"""
        cursor = self.conn.cursor()
        
        if strategy_name:
            cursor.execute("""
                SELECT * FROM trades
                WHERE strategy_name = ?
                ORDER BY exit_time DESC
                LIMIT ?
            """, (strategy_name, limit))
        else:
            cursor.execute("""
                SELECT * FROM trades
                ORDER BY exit_time DESC
                LIMIT ?
            """, (limit,))
        
        return [dict(r) for r in cursor.fetchall()]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        cursor = self.conn.cursor()
        
        # Total trades
        cursor.execute("SELECT COUNT(*) as count FROM trades")
        total_trades = cursor.fetchone()['count']
        
        # Total P&L
        cursor.execute("SELECT SUM(pnl_usd) as total FROM trades")
        row = cursor.fetchone()
        total_pnl = row['total'] if row['total'] else 0
        
        # Win rate
        cursor.execute("SELECT COUNT(*) as count FROM trades WHERE pnl_usd > 0")
        wins = cursor.fetchone()['count']
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        # Unique strategies
        cursor.execute("SELECT COUNT(DISTINCT strategy_name) as count FROM trades")
        unique_strategies = cursor.fetchone()['count']
        
        # Best strategy per regime
        cursor.execute("""
            SELECT regime, strategy_name, score
            FROM strategy_performance
            WHERE (regime, score) IN (
                SELECT regime, MAX(score)
                FROM strategy_performance
                GROUP BY regime
            )
        """)
        best_per_regime = {r['regime']: r['strategy_name'] for r in cursor.fetchall()}
        
        return {
            'total_trades': total_trades,
            'total_pnl_usd': round(total_pnl, 2),
            'win_rate': round(win_rate * 100, 1),
            'unique_strategies': unique_strategies,
            'best_strategies_per_regime': best_per_regime,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("📊 Performance Tracker connection closed")


# Example usage
if __name__ == "__main__":
    import uuid
    
    tracker = PerformanceTracker("test_performance.db")
    
    # Log a test trade
    test_trade = TradeRecord(
        trade_id=str(uuid.uuid4()),
        strategy_name="ElderReversion",
        regime="choppy_volatile",
        asset="BTC/USDT",
        timeframe="15m",
        side="BUY",
        entry_price=100000,
        exit_price=102000,
        quantity=0.01,
        entry_time=datetime.utcnow().isoformat(),
        exit_time=datetime.utcnow().isoformat(),
        pnl_usd=20.0,
        pnl_percent=2.0,
        exit_reason="TAKE_PROFIT"
    )
    
    tracker.log_trade(test_trade)
    
    # Get summary
    summary = tracker.get_summary()
    print(f"\n📊 Performance Summary: {summary}")
    
    tracker.close()

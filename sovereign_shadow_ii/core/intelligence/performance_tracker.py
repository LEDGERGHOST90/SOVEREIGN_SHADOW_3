#!/usr/bin/env python3
"""
Performance Tracker - LEARNING LAYER

Tracks strategy performance over time to enable self-annealing learning loop.
Stores results in SQLite database for persistence.
"""

import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    strategy_name: str
    regime: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration_minutes: float
    last_updated: datetime


@dataclass
class TradeRecord:
    """Individual trade record"""
    trade_id: str
    strategy_name: str
    regime: str
    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    pnl_percent: float
    exit_reason: str
    market_context: Dict


class PerformanceTracker:
    """
    Tracks and analyzes strategy performance
    
    Features:
    - Persistent SQLite storage
    - Per-strategy, per-regime metrics
    - Real-time updates
    - Historical analysis
    """
    
    def __init__(self, db_path: str = "data/performance.db"):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_database()
        
        logger.info(f"✅ Performance tracker initialized: {db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                symbol TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                position_size REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_percent REAL NOT NULL,
                exit_reason TEXT,
                market_context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Strategy performance summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                total_pnl REAL DEFAULT 0.0,
                avg_win REAL DEFAULT 0.0,
                avg_loss REAL DEFAULT 0.0,
                largest_win REAL DEFAULT 0.0,
                largest_loss REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                avg_trade_duration_minutes REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, regime)
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategy_regime ON trades(strategy_name, regime)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_time ON trades(entry_time)")
        
        self.conn.commit()
        logger.info("✅ Database schema initialized")
    
    def log_trade(self, trade: TradeRecord):
        """
        Log a completed trade
        
        Args:
            trade: TradeRecord with trade details
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO trades (
                    trade_id, strategy_name, regime, symbol,
                    entry_time, exit_time, entry_price, exit_price,
                    position_size, pnl, pnl_percent, exit_reason, market_context
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id,
                trade.strategy_name,
                trade.regime,
                trade.symbol,
                trade.entry_time.isoformat(),
                trade.exit_time.isoformat(),
                trade.entry_price,
                trade.exit_price,
                trade.position_size,
                trade.pnl,
                trade.pnl_percent,
                trade.exit_reason,
                json.dumps(trade.market_context)
            ))
            
            self.conn.commit()
            
            # Update strategy performance
            self._update_strategy_performance(trade.strategy_name, trade.regime)
            
            logger.info(f"✅ Trade logged: {trade.trade_id} | {trade.strategy_name} | PnL: ${trade.pnl:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log trade: {e}")
            self.conn.rollback()
    
    def _update_strategy_performance(self, strategy_name: str, regime: str):
        """Update aggregated performance metrics for a strategy"""
        cursor = self.conn.cursor()
        
        # Get all trades for this strategy+regime
        cursor.execute("""
            SELECT pnl, pnl_percent, entry_time, exit_time
            FROM trades
            WHERE strategy_name = ? AND regime = ?
            ORDER BY entry_time
        """, (strategy_name, regime))
        
        trades = cursor.fetchall()
        
        if not trades:
            return
        
        # Calculate metrics
        total_trades = len(trades)
        pnls = [t[0] for t in trades]
        pnl_percents = [t[1] for t in trades]
        
        winning_trades = len([p for p in pnls if p > 0])
        losing_trades = len([p for p in pnls if p <= 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
        
        total_pnl = sum(pnls)
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        largest_win = max(wins) if wins else 0.0
        largest_loss = min(losses) if losses else 0.0
        
        # Profit factor
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        # Sharpe ratio (simplified)
        if len(pnl_percents) > 1:
            import statistics
            avg_return = statistics.mean(pnl_percents)
            std_return = statistics.stdev(pnl_percents)
            sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        for pnl in pnls:
            cumulative_pnl += pnl
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown
        
        # Average trade duration
        durations = []
        for trade in trades:
            entry = datetime.fromisoformat(trade[2])
            exit_time = datetime.fromisoformat(trade[3])
            duration = (exit_time - entry).total_seconds() / 60  # minutes
            durations.append(duration)
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Upsert performance record
        cursor.execute("""
            INSERT INTO strategy_performance (
                strategy_name, regime, total_trades, winning_trades, losing_trades,
                win_rate, total_pnl, avg_win, avg_loss, largest_win, largest_loss,
                profit_factor, sharpe_ratio, max_drawdown, avg_trade_duration_minutes,
                last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(strategy_name, regime) DO UPDATE SET
                total_trades = excluded.total_trades,
                winning_trades = excluded.winning_trades,
                losing_trades = excluded.losing_trades,
                win_rate = excluded.win_rate,
                total_pnl = excluded.total_pnl,
                avg_win = excluded.avg_win,
                avg_loss = excluded.avg_loss,
                largest_win = excluded.largest_win,
                largest_loss = excluded.largest_loss,
                profit_factor = excluded.profit_factor,
                sharpe_ratio = excluded.sharpe_ratio,
                max_drawdown = excluded.max_drawdown,
                avg_trade_duration_minutes = excluded.avg_trade_duration_minutes,
                last_updated = excluded.last_updated
        """, (
            strategy_name, regime, total_trades, winning_trades, losing_trades,
            win_rate, total_pnl, avg_win, avg_loss, largest_win, largest_loss,
            profit_factor, sharpe_ratio, max_dd, avg_duration,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        logger.info(f"✅ Updated performance: {strategy_name} in {regime}")
    
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
        
        results = []
        for row in rows:
            results.append(StrategyPerformance(
                strategy_name=row[1],
                regime=row[2],
                total_trades=row[3],
                winning_trades=row[4],
                losing_trades=row[5],
                win_rate=row[6],
                total_pnl=row[7],
                avg_win=row[8],
                avg_loss=row[9],
                largest_win=row[10],
                largest_loss=row[11],
                profit_factor=row[12],
                sharpe_ratio=row[13],
                max_drawdown=row[14],
                avg_trade_duration_minutes=row[15],
                last_updated=datetime.fromisoformat(row[16])
            ))
        
        return results
    
    def get_top_strategies(
        self,
        regime: str,
        min_trades: int = 10,
        top_n: int = 5
    ) -> List[StrategyPerformance]:
        """
        Get top performing strategies for a regime
        
        Args:
            regime: Market regime
            min_trades: Minimum trades required
            top_n: Number of strategies to return
        
        Returns:
            List of top StrategyPerformance objects
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM strategy_performance
            WHERE regime = ? AND total_trades >= ?
            ORDER BY sharpe_ratio DESC, win_rate DESC, total_pnl DESC
            LIMIT ?
        """, (regime, min_trades, top_n))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(StrategyPerformance(
                strategy_name=row[1],
                regime=row[2],
                total_trades=row[3],
                winning_trades=row[4],
                losing_trades=row[5],
                win_rate=row[6],
                total_pnl=row[7],
                avg_win=row[8],
                avg_loss=row[9],
                largest_win=row[10],
                largest_loss=row[11],
                profit_factor=row[12],
                sharpe_ratio=row[13],
                max_drawdown=row[14],
                avg_trade_duration_minutes=row[15],
                last_updated=datetime.fromisoformat(row[16])
            ))
        
        return results
    
    def get_all_trades(
        self,
        strategy_name: Optional[str] = None,
        regime: Optional[str] = None,
        limit: int = 100
    ) -> List[TradeRecord]:
        """Get recent trade records"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if strategy_name:
            query += " AND strategy_name = ?"
            params.append(strategy_name)
        
        if regime:
            query += " AND regime = ?"
            params.append(regime)
        
        query += " ORDER BY entry_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(TradeRecord(
                trade_id=row[0],
                strategy_name=row[1],
                regime=row[2],
                symbol=row[3],
                entry_time=datetime.fromisoformat(row[4]),
                exit_time=datetime.fromisoformat(row[5]),
                entry_price=row[6],
                exit_price=row[7],
                position_size=row[8],
                pnl=row[9],
                pnl_percent=row[10],
                exit_reason=row[11],
                market_context=json.loads(row[12]) if row[12] else {}
            ))
        
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("✅ Performance tracker closed")


def test_performance_tracker():
    """Test performance tracker"""
    print("\n" + "="*70)
    print("🧪 TESTING PERFORMANCE TRACKER")
    print("="*70)
    
    # Create tracker
    tracker = PerformanceTracker(db_path="data/test_performance.db")
    
    # Log sample trades
    for i in range(5):
        trade = TradeRecord(
            trade_id=f"TEST_{i}",
            strategy_name="ElderReversion",
            regime="choppy_volatile",
            symbol="BTC/USDT",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=99000 + i * 100,
            exit_price=99500 + i * 100,
            position_size=0.01,
            pnl=50 + i * 10,
            pnl_percent=0.5,
            exit_reason="take_profit",
            market_context={"rsi": 55}
        )
        tracker.log_trade(trade)
    
    # Get performance
    performance = tracker.get_strategy_performance("ElderReversion", "choppy_volatile")
    
    if performance:
        perf = performance[0]
        print(f"\n📊 ElderReversion Performance:")
        print(f"   Total Trades: {perf.total_trades}")
        print(f"   Win Rate: {perf.win_rate:.1f}%")
        print(f"   Total PnL: ${perf.total_pnl:.2f}")
        print(f"   Sharpe Ratio: {perf.sharpe_ratio:.2f}")
    
    # Get top strategies
    top = tracker.get_top_strategies("choppy_volatile", min_trades=1, top_n=3)
    print(f"\n🏆 Top Strategies for choppy_volatile:")
    for i, strat in enumerate(top, 1):
        print(f"   {i}. {strat.strategy_name}: {strat.win_rate:.1f}% WR, ${strat.total_pnl:.2f} PnL")
    
    tracker.close()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_performance_tracker()

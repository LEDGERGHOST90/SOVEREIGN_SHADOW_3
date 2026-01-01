#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - Performance Tracker (Learning Layer)
SQLite-based performance tracking for self-annealing loop

This is the Learning Layer of the D.O.E. Pattern:
- Tracks all strategy performance metrics
- Enables self-annealing loop (strategies improve based on results)
- Provides historical data for AI Strategy Selector
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    SQLite-based performance tracker for strategy learning loop.

    Tables:
    - trades: Individual trade records
    - strategy_performance: Aggregated strategy metrics
    - regime_performance: Strategy performance by market regime
    - daily_snapshots: Daily portfolio snapshots
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize performance tracker with SQLite database"""
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'data', 'performance.db'
            )

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_database()

        logger.info(f"PerformanceTracker initialized: {self.db_path}")

    def _init_database(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Trades table - individual trade records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                strategy_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                pnl_usd REAL,
                pnl_percent REAL,
                exit_reason TEXT,
                regime TEXT,
                timeframe TEXT,
                exchange TEXT,
                fees_usd REAL DEFAULT 0,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Strategy performance - aggregated metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_pnl_percent REAL DEFAULT 0,
                total_pnl_usd REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown_percent REAL DEFAULT 0,
                avg_trade_duration_hours REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, regime)
            )
        """)

        # Regime performance - strategy performance per regime
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regime_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                trades_count INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_pnl_percent REAL DEFAULT 0,
                total_pnl_usd REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0,
                UNIQUE(strategy_name, regime, timeframe, period_start)
            )
        """)

        # Daily portfolio snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                portfolio_value_usd REAL NOT NULL,
                daily_pnl_usd REAL DEFAULT 0,
                daily_pnl_percent REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                active_positions INTEGER DEFAULT 0,
                dominant_regime TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Strategy rankings - used by AI Strategy Selector
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regime TEXT NOT NULL,
                rank INTEGER NOT NULL,
                strategy_name TEXT NOT NULL,
                score REAL NOT NULL,
                win_rate REAL,
                avg_pnl_percent REAL,
                trades_count INTEGER,
                confidence REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(regime, rank)
            )
        """)

        self.conn.commit()
        logger.info("Database tables initialized")

    def record_trade(
        self,
        trade_id: str,
        strategy_name: str,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        entry_time: str,
        regime: str,
        timeframe: str = "15m",
        exchange: str = "coinbase",
        exit_price: Optional[float] = None,
        exit_time: Optional[str] = None,
        exit_reason: Optional[str] = None,
        fees_usd: float = 0,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Record a trade (entry or complete trade with exit)

        Returns:
            bool: True if successful
        """
        try:
            cursor = self.conn.cursor()

            # Calculate PnL if exit price provided
            pnl_usd = None
            pnl_percent = None
            if exit_price is not None:
                if side.lower() == 'buy':
                    pnl_usd = (exit_price - entry_price) * quantity - fees_usd
                    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
                else:
                    pnl_usd = (entry_price - exit_price) * quantity - fees_usd
                    pnl_percent = ((entry_price - exit_price) / entry_price) * 100

            cursor.execute("""
                INSERT OR REPLACE INTO trades (
                    trade_id, strategy_name, symbol, side, entry_price,
                    exit_price, quantity, entry_time, exit_time, pnl_usd,
                    pnl_percent, exit_reason, regime, timeframe, exchange,
                    fees_usd, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id, strategy_name, symbol, side, entry_price,
                exit_price, quantity, entry_time, exit_time, pnl_usd,
                pnl_percent, exit_reason, regime, timeframe, exchange,
                fees_usd, json.dumps(metadata) if metadata else None
            ))

            self.conn.commit()

            # Update aggregated metrics if trade is complete
            if exit_price is not None:
                self._update_strategy_metrics(strategy_name, regime)

            logger.info(f"Trade recorded: {trade_id} ({strategy_name})")
            return True

        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            return False

    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        exit_time: str,
        exit_reason: str,
        fees_usd: float = 0
    ) -> bool:
        """
        Close an open trade with exit details

        Returns:
            bool: True if successful
        """
        try:
            cursor = self.conn.cursor()

            # Get trade details
            cursor.execute(
                "SELECT * FROM trades WHERE trade_id = ?",
                (trade_id,)
            )
            trade = cursor.fetchone()

            if not trade:
                logger.error(f"Trade not found: {trade_id}")
                return False

            # Calculate PnL
            entry_price = trade['entry_price']
            quantity = trade['quantity']
            side = trade['side']

            if side.lower() == 'buy':
                pnl_usd = (exit_price - entry_price) * quantity - fees_usd
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            else:
                pnl_usd = (entry_price - exit_price) * quantity - fees_usd
                pnl_percent = ((entry_price - exit_price) / entry_price) * 100

            # Update trade
            cursor.execute("""
                UPDATE trades SET
                    exit_price = ?,
                    exit_time = ?,
                    pnl_usd = ?,
                    pnl_percent = ?,
                    exit_reason = ?,
                    fees_usd = fees_usd + ?
                WHERE trade_id = ?
            """, (exit_price, exit_time, pnl_usd, pnl_percent, exit_reason, fees_usd, trade_id))

            self.conn.commit()

            # Update aggregated metrics
            self._update_strategy_metrics(trade['strategy_name'], trade['regime'])

            logger.info(f"Trade closed: {trade_id} | PnL: ${pnl_usd:.2f} ({pnl_percent:.2f}%)")
            return True

        except Exception as e:
            logger.error(f"Failed to close trade: {e}")
            return False

    def _update_strategy_metrics(self, strategy_name: str, regime: str):
        """Update aggregated strategy performance metrics"""
        try:
            cursor = self.conn.cursor()

            # Get all completed trades for this strategy and regime
            cursor.execute("""
                SELECT * FROM trades
                WHERE strategy_name = ? AND regime = ? AND exit_price IS NOT NULL
            """, (strategy_name, regime))

            trades = cursor.fetchall()

            if not trades:
                return

            # Calculate metrics
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['pnl_usd'] > 0)
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

            pnl_list = [t['pnl_percent'] for t in trades]
            avg_pnl_percent = sum(pnl_list) / len(pnl_list)
            total_pnl_usd = sum(t['pnl_usd'] for t in trades)

            # Calculate Sharpe ratio (simplified)
            import statistics
            if len(pnl_list) > 1:
                std_dev = statistics.stdev(pnl_list)
                sharpe_ratio = (avg_pnl_percent / std_dev) if std_dev > 0 else 0
            else:
                sharpe_ratio = 0

            # Calculate max drawdown
            cumulative_pnl = 0
            peak = 0
            max_drawdown = 0
            for t in trades:
                cumulative_pnl += t['pnl_usd']
                if cumulative_pnl > peak:
                    peak = cumulative_pnl
                drawdown = peak - cumulative_pnl
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            max_drawdown_percent = (max_drawdown / peak * 100) if peak > 0 else 0

            # Calculate profit factor
            gross_profit = sum(t['pnl_usd'] for t in trades if t['pnl_usd'] > 0)
            gross_loss = abs(sum(t['pnl_usd'] for t in trades if t['pnl_usd'] < 0))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else gross_profit

            # Update or insert strategy performance
            cursor.execute("""
                INSERT OR REPLACE INTO strategy_performance (
                    strategy_name, regime, total_trades, winning_trades,
                    losing_trades, win_rate, avg_pnl_percent, total_pnl_usd,
                    sharpe_ratio, max_drawdown_percent, profit_factor, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_name, regime, total_trades, winning_trades,
                losing_trades, win_rate, avg_pnl_percent, total_pnl_usd,
                sharpe_ratio, max_drawdown_percent, profit_factor,
                datetime.utcnow().isoformat()
            ))

            self.conn.commit()

        except Exception as e:
            logger.error(f"Failed to update strategy metrics: {e}")

    def get_strategy_performance(
        self,
        strategy_name: str,
        regime: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a strategy

        Returns:
            Dict with performance metrics
        """
        try:
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

            if not rows:
                return {"strategy_name": strategy_name, "data": []}

            return {
                "strategy_name": strategy_name,
                "data": [dict(row) for row in rows]
            }

        except Exception as e:
            logger.error(f"Failed to get strategy performance: {e}")
            return {"error": str(e)}

    def get_top_strategies_for_regime(
        self,
        regime: str,
        limit: int = 10,
        min_trades: int = 5
    ) -> List[Dict]:
        """
        Get top performing strategies for a given market regime

        This is used by the AI Strategy Selector to choose strategies

        Args:
            regime: Market regime (e.g., 'trending_bullish', 'choppy_volatile')
            limit: Number of strategies to return
            min_trades: Minimum trades required for consideration

        Returns:
            List of top strategies with metrics
        """
        try:
            cursor = self.conn.cursor()

            # Score = (win_rate * 0.4) + (avg_pnl * 0.3) + (sharpe * 0.2) + (profit_factor_normalized * 0.1)
            cursor.execute("""
                SELECT
                    strategy_name,
                    regime,
                    total_trades,
                    win_rate,
                    avg_pnl_percent,
                    total_pnl_usd,
                    sharpe_ratio,
                    max_drawdown_percent,
                    profit_factor,
                    (win_rate * 0.4 +
                     CASE WHEN avg_pnl_percent > 0 THEN avg_pnl_percent * 10 ELSE 0 END * 0.3 +
                     sharpe_ratio * 10 * 0.2 +
                     CASE WHEN profit_factor > 0 THEN MIN(profit_factor, 5) * 10 ELSE 0 END * 0.1
                    ) as score,
                    last_updated
                FROM strategy_performance
                WHERE regime = ? AND total_trades >= ?
                ORDER BY score DESC
                LIMIT ?
            """, (regime, min_trades, limit))

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get top strategies: {e}")
            return []

    def update_strategy_rankings(self, regime: str):
        """Update strategy rankings for a given regime"""
        try:
            top_strategies = self.get_top_strategies_for_regime(regime, limit=20, min_trades=3)

            cursor = self.conn.cursor()

            # Delete old rankings for this regime
            cursor.execute("DELETE FROM strategy_rankings WHERE regime = ?", (regime,))

            # Insert new rankings
            for rank, strategy in enumerate(top_strategies, 1):
                cursor.execute("""
                    INSERT INTO strategy_rankings (
                        regime, rank, strategy_name, score, win_rate,
                        avg_pnl_percent, trades_count, confidence, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    regime, rank, strategy['strategy_name'], strategy['score'],
                    strategy['win_rate'], strategy['avg_pnl_percent'],
                    strategy['total_trades'],
                    min(strategy['total_trades'] / 20, 1.0),  # Confidence based on trade count
                    datetime.utcnow().isoformat()
                ))

            self.conn.commit()
            logger.info(f"Updated rankings for regime: {regime}")

        except Exception as e:
            logger.error(f"Failed to update rankings: {e}")

    def record_daily_snapshot(
        self,
        date: str,
        portfolio_value_usd: float,
        daily_pnl_usd: float,
        total_trades: int,
        winning_trades: int,
        active_positions: int,
        dominant_regime: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Record daily portfolio snapshot"""
        try:
            cursor = self.conn.cursor()

            daily_pnl_percent = (daily_pnl_usd / (portfolio_value_usd - daily_pnl_usd) * 100) \
                if portfolio_value_usd != daily_pnl_usd else 0

            cursor.execute("""
                INSERT OR REPLACE INTO daily_snapshots (
                    date, portfolio_value_usd, daily_pnl_usd, daily_pnl_percent,
                    total_trades, winning_trades, active_positions, dominant_regime, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date, portfolio_value_usd, daily_pnl_usd, daily_pnl_percent,
                total_trades, winning_trades, active_positions, dominant_regime,
                json.dumps(metadata) if metadata else None
            ))

            self.conn.commit()
            logger.info(f"Daily snapshot recorded: {date}")
            return True

        except Exception as e:
            logger.error(f"Failed to record daily snapshot: {e}")
            return False

    def get_portfolio_history(self, days: int = 30) -> List[Dict]:
        """Get portfolio history for the last N days"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT * FROM daily_snapshots
                ORDER BY date DESC
                LIMIT ?
            """, (days,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get portfolio history: {e}")
            return []

    def get_all_trades(
        self,
        strategy_name: Optional[str] = None,
        regime: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get trade history with optional filters"""
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM trades WHERE exit_price IS NOT NULL"
            params = []

            if strategy_name:
                query += " AND strategy_name = ?"
                params.append(strategy_name)

            if regime:
                query += " AND regime = ?"
                params.append(regime)

            if start_date:
                query += " AND entry_time >= ?"
                params.append(start_date)

            if end_date:
                query += " AND entry_time <= ?"
                params.append(end_date)

            query += " ORDER BY entry_time DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return []

    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("PerformanceTracker connection closed")


# Singleton instance for global access
_tracker_instance: Optional[PerformanceTracker] = None


def get_performance_tracker(db_path: Optional[str] = None) -> PerformanceTracker:
    """Get or create the global PerformanceTracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PerformanceTracker(db_path)
    return _tracker_instance


if __name__ == "__main__":
    # Test the performance tracker
    logging.basicConfig(level=logging.INFO)

    tracker = PerformanceTracker()

    # Record a test trade
    tracker.record_trade(
        trade_id="test_001",
        strategy_name="ElderReversion",
        symbol="BTC/USD",
        side="buy",
        entry_price=95000.0,
        quantity=0.01,
        entry_time=datetime.utcnow().isoformat(),
        regime="choppy_volatile",
        exchange="coinbase"
    )

    # Close the trade
    tracker.close_trade(
        trade_id="test_001",
        exit_price=96000.0,
        exit_time=datetime.utcnow().isoformat(),
        exit_reason="TAKE_PROFIT"
    )

    # Get performance
    perf = tracker.get_strategy_performance("ElderReversion")
    print(f"\nPerformance: {perf}")

    print("\nPerformanceTracker test complete!")

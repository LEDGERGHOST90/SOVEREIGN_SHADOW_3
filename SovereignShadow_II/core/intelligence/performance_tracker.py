"""
Performance Tracker
SQLite database for tracking strategy performance and enabling self-annealing loop
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Performance tracking database using SQLite
    Tracks trades, strategy performance, and enables learning loop
    """
    
    def __init__(self, db_path: str = "data/performance.db"):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                side TEXT NOT NULL,
                pnl_usd REAL,
                pnl_percent REAL,
                exit_reason TEXT,
                regime TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Strategy performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl_usd REAL DEFAULT 0.0,
                avg_pnl_percent REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, regime)
            )
        """)
        
        # Market regime history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regime_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                regime TEXT NOT NULL,
                confidence REAL,
                indicators TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Strategy selection log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                regime TEXT NOT NULL,
                selected_strategy TEXT NOT NULL,
                confidence REAL,
                alternatives TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Performance tracker database initialized")
    
    def log_trade(
        self,
        strategy_name: str,
        symbol: str,
        entry_time: datetime,
        entry_price: float,
        quantity: float,
        side: str,
        regime: str,
        exit_time: Optional[datetime] = None,
        exit_price: Optional[float] = None,
        pnl_usd: Optional[float] = None,
        pnl_percent: Optional[float] = None,
        exit_reason: Optional[str] = None
    ) -> int:
        """
        Log a trade to the database
        
        Returns:
            Trade ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trades (
                strategy_name, symbol, entry_time, exit_time,
                entry_price, exit_price, quantity, side,
                pnl_usd, pnl_percent, exit_reason, regime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy_name, symbol, entry_time, exit_time,
            entry_price, exit_price, quantity, side,
            pnl_usd, pnl_percent, exit_reason, regime
        ))
        trade_id = cursor.lastrowid
        self.conn.commit()
        
        # Update strategy performance
        self._update_strategy_performance(strategy_name, regime)
        
        logger.debug(f"📊 Trade logged: {strategy_name} - {symbol} - {side}")
        return trade_id
    
    def _update_strategy_performance(self, strategy_name: str, regime: str):
        """Update strategy performance metrics"""
        cursor = self.conn.cursor()
        
        # Get trade statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl_usd <= 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(pnl_usd) as total_pnl_usd,
                AVG(pnl_percent) as avg_pnl_percent
            FROM trades
            WHERE strategy_name = ? AND regime = ?
        """, (strategy_name, regime))
        
        stats = cursor.fetchone()
        
        if stats and stats['total_trades'] > 0:
            win_rate = (stats['winning_trades'] / stats['total_trades']) * 100 if stats['total_trades'] > 0 else 0
            
            # Calculate Sharpe ratio (simplified)
            cursor.execute("""
                SELECT pnl_percent FROM trades
                WHERE strategy_name = ? AND regime = ? AND pnl_percent IS NOT NULL
            """, (strategy_name, regime))
            
            returns = [row['pnl_percent'] for row in cursor.fetchall()]
            sharpe = 0.0
            if len(returns) > 1:
                import statistics
                mean_return = statistics.mean(returns)
                std_return = statistics.stdev(returns) if len(returns) > 1 else 0.0001
                sharpe = mean_return / std_return if std_return > 0 else 0
            
            # Calculate max drawdown
            cursor.execute("""
                SELECT pnl_usd FROM trades
                WHERE strategy_name = ? AND regime = ?
                ORDER BY entry_time
            """, (strategy_name, regime))
            
            cumulative = 0
            peak = 0
            max_dd = 0
            for row in cursor.fetchall():
                cumulative += row['pnl_usd'] or 0
                if cumulative > peak:
                    peak = cumulative
                drawdown = peak - cumulative
                if drawdown > max_dd:
                    max_dd = drawdown
            
            # Insert or update performance record
            cursor.execute("""
                INSERT INTO strategy_performance (
                    strategy_name, regime, total_trades, winning_trades,
                    losing_trades, total_pnl_usd, avg_pnl_percent,
                    win_rate, sharpe_ratio, max_drawdown
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(strategy_name, regime) DO UPDATE SET
                    total_trades = excluded.total_trades,
                    winning_trades = excluded.winning_trades,
                    losing_trades = excluded.losing_trades,
                    total_pnl_usd = excluded.total_pnl_usd,
                    avg_pnl_percent = excluded.avg_pnl_percent,
                    win_rate = excluded.win_rate,
                    sharpe_ratio = excluded.sharpe_ratio,
                    max_drawdown = excluded.max_drawdown,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                strategy_name, regime, stats['total_trades'],
                stats['winning_trades'], stats['losing_trades'],
                stats['total_pnl_usd'] or 0.0,
                stats['avg_pnl_percent'] or 0.0,
                win_rate, sharpe, max_dd
            ))
            
            self.conn.commit()
    
    def get_strategy_performance(
        self,
        strategy_name: Optional[str] = None,
        regime: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get strategy performance metrics
        
        Args:
            strategy_name: Filter by strategy name (optional)
            regime: Filter by regime (optional)
        
        Returns:
            List of performance dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM strategy_performance WHERE 1=1"
        params = []
        
        if strategy_name:
            query += " AND strategy_name = ?"
            params.append(strategy_name)
        
        if regime:
            query += " AND regime = ?"
            params.append(regime)
        
        query += " ORDER BY win_rate DESC, total_pnl_usd DESC"
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'strategy_name': row['strategy_name'],
                'regime': row['regime'],
                'total_trades': row['total_trades'],
                'winning_trades': row['winning_trades'],
                'losing_trades': row['losing_trades'],
                'total_pnl_usd': row['total_pnl_usd'],
                'avg_pnl_percent': row['avg_pnl_percent'],
                'win_rate': row['win_rate'],
                'sharpe_ratio': row['sharpe_ratio'],
                'max_drawdown': row['max_drawdown'],
                'last_updated': row['last_updated']
            })
        
        return results
    
    def log_regime(self, regime: str, confidence: float, indicators: Dict[str, Any]):
        """Log market regime detection"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO regime_history (timestamp, regime, confidence, indicators)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), regime, confidence, json.dumps(indicators)))
        self.conn.commit()
    
    def log_strategy_selection(
        self,
        regime: str,
        selected_strategy: str,
        confidence: float,
        alternatives: List[str]
    ):
        """Log strategy selection decision"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO strategy_selections (
                timestamp, regime, selected_strategy, confidence, alternatives
            ) VALUES (?, ?, ?, ?, ?)
        """, (datetime.now(), regime, selected_strategy, confidence, json.dumps(alternatives)))
        self.conn.commit()
    
    def get_top_strategies(self, regime: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing strategies for a regime
        
        Args:
            regime: Market regime
            limit: Maximum number of strategies to return
        
        Returns:
            List of top strategies sorted by performance
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM strategy_performance
            WHERE regime = ? AND total_trades >= 5
            ORDER BY win_rate DESC, sharpe_ratio DESC
            LIMIT ?
        """, (regime, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'strategy_name': row['strategy_name'],
                'regime': row['regime'],
                'total_trades': row['total_trades'],
                'win_rate': row['win_rate'],
                'avg_pnl_percent': row['avg_pnl_percent'],
                'sharpe_ratio': row['sharpe_ratio'],
                'total_pnl_usd': row['total_pnl_usd']
            })
        
        return results
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Performance tracker database closed")

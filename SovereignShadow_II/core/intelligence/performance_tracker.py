import sqlite3
import pandas as pd
from datetime import datetime
import os

class PerformanceTracker:
    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                strategy_name TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                quantity REAL,
                pnl_usd REAL,
                pnl_percent REAL,
                regime TEXT,
                reason TEXT
            )
        ''')
        
        # Create performance_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                timestamp TEXT,
                strategy_name TEXT,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                total_pnl REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def log_trade(self, trade_data):
        """
        Log a completed trade.
        trade_data: dict containing trade details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, strategy_name, symbol, side, price, 
                quantity, pnl_usd, pnl_percent, regime, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data.get('timestamp', datetime.now().isoformat()),
            trade_data['strategy_name'],
            trade_data['symbol'],
            trade_data['side'],
            trade_data['price'],
            trade_data['quantity'],
            trade_data.get('pnl_usd', 0.0),
            trade_data.get('pnl_percent', 0.0),
            trade_data.get('regime', 'unknown'),
            trade_data.get('reason', '')
        ))
        
        conn.commit()
        conn.close()

    def get_strategy_performance(self, strategy_name):
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM trades WHERE strategy_name = '{strategy_name}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
            
        # Calculate metrics
        total_trades = len(df)
        wins = df[df['pnl_usd'] > 0]
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = df['pnl_usd'].sum()
        
        return {
            'strategy_name': strategy_name,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl
        }

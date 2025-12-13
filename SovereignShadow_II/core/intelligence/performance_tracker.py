import sqlite3
import os
import pandas as pd
from datetime import datetime

class PerformanceTracker:
    def __init__(self, db_path="performance.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      strategy_name TEXT,
                      symbol TEXT,
                      side TEXT,
                      entry_price REAL,
                      exit_price REAL,
                      quantity REAL,
                      pnl_usd REAL,
                      pnl_percent REAL,
                      entry_time TIMESTAMP,
                      exit_time TIMESTAMP,
                      regime TEXT,
                      exit_reason TEXT)''')
        conn.commit()
        conn.close()

    def log_trade(self, trade_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trades 
                     (strategy_name, symbol, side, entry_price, exit_price, quantity, pnl_usd, pnl_percent, entry_time, exit_time, regime, exit_reason)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (trade_data.get('strategy_name'),
                   trade_data.get('symbol'),
                   trade_data.get('side'),
                   trade_data.get('entry_price'),
                   trade_data.get('exit_price'),
                   trade_data.get('quantity'),
                   trade_data.get('pnl_usd'),
                   trade_data.get('pnl_percent'),
                   trade_data.get('entry_time'),
                   trade_data.get('exit_time'),
                   trade_data.get('regime'),
                   trade_data.get('exit_reason')))
        conn.commit()
        conn.close()
    
    def get_performance_summary(self):
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM trades", conn)
            return df
        except Exception as e:
            print(f"Error reading performance data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

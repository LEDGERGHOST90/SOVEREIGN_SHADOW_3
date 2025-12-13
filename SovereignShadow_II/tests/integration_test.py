import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from core.backtesting.backtest_engine import BacktestEngine
from core.intelligence.performance_tracker import PerformanceTracker

def create_dummy_data(rows=200):
    dates = pd.date_range(start='2024-01-01', periods=rows, freq='1H')
    data = {
        'timestamp': dates,
        'open': np.random.uniform(100, 200, rows),
        'high': np.random.uniform(100, 200, rows),
        'low': np.random.uniform(100, 200, rows),
        'close': np.random.uniform(100, 200, rows),
        'volume': np.random.uniform(1000, 5000, rows)
    }
    # Ensure High is highest and Low is lowest
    df = pd.DataFrame(data)
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    return df

def test_integration():
    print("Starting Integration Test...")
    
    # 1. Setup Data
    df = create_dummy_data()
    data_path = 'dummy_data.csv'
    df.to_csv(data_path, index=False)
    
    # 2. Init Performance Tracker
    tracker = PerformanceTracker('test_perf.db')
    
    # 3. Init Backtest Engine
    engine = BacktestEngine(data_path, tracker)
    
    # 4. Test ElderReversion
    print("Testing ElderReversion...")
    result = engine.backtest_strategy('elder_reversion', 'choppy_volatile')
    print("Result:", result)
    
    # 5. Test DynamicCrossfire
    print("Testing DynamicCrossfire...")
    result2 = engine.backtest_strategy('dynamic_crossfire', 'trending_bullish')
    print("Result:", result2)
    
    # Cleanup
    if os.path.exists(data_path):
        os.remove(data_path)
    if os.path.exists('test_perf.db'):
        os.remove('test_perf.db')

if __name__ == "__main__":
    test_integration()

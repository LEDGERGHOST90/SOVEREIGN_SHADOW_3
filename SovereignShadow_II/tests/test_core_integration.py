import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.exchange_connectors.coinbase_connector import CoinbaseAdvancedConnector
from core.intelligence.regime_detector import MarketRegimeDetector
from core.intelligence.performance_tracker import PerformanceTracker
from strategies.modularized.elder_reversion.entry import ElderReversionEntry
from strategies.modularized.elder_reversion.exit import ElderReversionExit
from strategies.modularized.elder_reversion.risk import ElderReversionRisk
from core.backtesting.backtest_engine import BacktestEngine

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create dummy data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='15min')
        self.df = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.randn(200) + 100,
            'high': np.random.randn(200) + 102,
            'low': np.random.randn(200) + 98,
            'close': np.random.randn(200) + 100,
            'volume': np.random.rand(200) * 1000
        })
        # Force a dip for Elder Ray
        self.df.loc[199, 'close'] = 90
        self.df.loc[199, 'high'] = 91
        self.df.loc[199, 'low'] = 89
        
    def test_exchange_connector_init(self):
        # Should initialize even without keys (warning printed)
        connector = CoinbaseAdvancedConnector(use_sandbox=True)
        self.assertIsNotNone(connector)

    def test_regime_detector(self):
        detector = MarketRegimeDetector()
        regime = detector.analyze_market(self.df)
        print(f"Detected Regime: {regime}")
        self.assertIn(regime, ["choppy_volatile", "choppy_calm", "trending_volatile", "trending_calm", "unknown"])

    def test_elder_reversion(self):
        entry = ElderReversionEntry()
        # Need enough data for EMA 13
        signal = entry.generate_signal(self.df)
        print(f"Elder Signal: {signal}")
        self.assertIn('signal', signal)
        
    def test_backtest_engine(self):
        # Create a dummy CSV for backtester
        self.df.to_csv('dummy_data.csv', index=False)
        tracker = PerformanceTracker(db_path=":memory:") # Use in-memory DB for test
        engine = BacktestEngine('dummy_data.csv', tracker)
        
        result = engine.backtest_strategy('elder_reversion', 'choppy_volatile')
        print(f"Backtest Result: {result}")
        # It might return no trades, but should not crash
        if 'error' not in result:
             self.assertIn('total_trades', result)
        
        # Cleanup
        if os.path.exists('dummy_data.csv'):
            os.remove('dummy_data.csv')

if __name__ == '__main__':
    unittest.main()

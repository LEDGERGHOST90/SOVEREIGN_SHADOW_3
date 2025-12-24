Here's the complete implementation of the VolBand Divergence strategy for backtesting.py:

```python
# 🌙 Moon Dev Backtest AI Implementation
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Helper functions for Bollinger Bands components
def bbands_upper(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    upper, _, _ = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return upper

def bbands_middle(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    _, middle, _ = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return middle

def bbands_lower(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    _, _, lower = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return lower

class VolBandDivergence(Strategy):
    risk_percent = 0.01
    atr_multiplier = 1.5
    delta_window = 20
    delta_threshold = 2.0
    
    def init(self):
        # 🌙 Moon Dev Indicators Setup
        self.upper_band = self.I(bbands_upper, self.data.Close, 20, 2, 2, 0, name='Upper BB')
        self.middle_band = self.I(bbands_middle, self.data.Close, 20, 2, 2, 0, name='Middle BB')
        self.lower_band = self.I(bbands_lower, self.data.Close, 20, 2, 2, 0, name='Lower BB')
        
        # Band Width calculation
        self.band_width = self.I(lambda u, l, m: (u - l)/m, 
                                self.upper_band, self.lower_band, self.middle_band,
                                name='Band Width')
        
        # Band Width Percentile (100-period lookback)
        self.band_width_percentile = self.I(
            lambda x: np.array([np.percentile(x[max(0,i-100):i], 20) if i >= 100 else np.nan 
                              for i in range(len(x))]),
            self.band_width, name='BW Percentile')
        
        # Volume indicators
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume, name='OBV')
        self.price_low_min = self.I(talib.MIN, self.data.Low, 5, name='Price Low')
        self.obv_min = self.I(talib.MIN, self.obv, 5, name='OBV Low')
        self.price_high_max = self.I(talib.MAX, self.data.High, 5, name='Price High')
        self.obv_max = self.I(talib.MAX, self.obv, 5, name='OBV High')
        
        # Volatility measure
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR')
        
        # Track volume delta internally
        self.volume_deltas = []
        
    def next(self):
        # 🌙 Moon Dev Debug Prints
        if len(self.data) % 500 == 0:
            print(f"🌙✨ Moon Dev Progress: Bar {len(self.data)}/{len(self.data.df)}")
        
        # Calculate current Volume Delta
        current_obv = self.obv[-1] if len(self.obv) > 0 else 0
        prev_obv = self.obv[-2] if len(self.obv) > 1 else 0
        delta = current_obv - prev_obv
        self.volume_deltas.append(delta)
        
        # Check minimum data requirements
        if len(self.band_width) < 100 or len(self.atr) < 1:
            return
        
        # Bandwidth contraction condition
        bw_contraction = self.band_width[-1] < self.band_width_percentile[-1]
        
        # Divergence detection
        bullish_div = (self.price_low_min[-1] < self.price_low_min[-2] and 
                      self.obv_min[-1] > self.obv_min[-2])
        bearish_div =
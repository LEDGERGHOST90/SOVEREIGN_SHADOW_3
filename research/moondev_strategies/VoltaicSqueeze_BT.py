To address the problem, we need to create a backtesting implementation for the VoltaicSqueeze strategy using the specified requirements. Here's the step-by-step solution:

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VoltaicSqueeze(Strategy):
    # Strategy parameters
    bb_period = 20
    bb_stddev = 2
    keltner_period = 20
    keltner_multiplier = 1.5
    psar_accel = 0.02
    psar_max = 0.2
    atr_period = 14
    bbw_threshold_percentile = 20
    bbw_lookback = 20
    risk_pct = 0.01
    max_bars_held = 20
    
    def init(self):
        # Bollinger Bands components
        def bb_upper(close):
            upper, _, _ = talib.BBANDS(close, self.bb_period, self.bb_stddev, self.bb_stddev)
            return upper
        self.upper_bb = self.I(bb_upper, self.data.Close, name='UPPER_BB')
        
        def bb_lower(close):
            _, _, lower = talib.BBANDS(close, self.bb_period, self.bb_stddev, self.bb_stddev)
            return lower
        self.lower_bb = self.I(bb_lower, self.data.Close, name='LOWER_BB')
        
        # Keltner Channel components
        self.ema = self.I(talib.EMA, self.data.Close, self.keltner_period, name='EMA')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.keltner_period, name='ATR')
        self.upper_keltner = self.I(lambda ema, atr: ema + atr*self.keltner_multiplier, 
                                   self.ema, self.atr, name='UPPER_KELTNER')
        self.lower_keltner = self.I(lambda ema, atr: ema - atr*self.keltner_multiplier, 
                                   self.ema, self.atr, name='LOWER_KELTNER')
        
        # Bollinger Band Width
        self.bbw = self.I(lambda u, l: (u - l)/self.ema, 
                         self.upper_bb, self.lower_bb, name='BBW')
        
        # BBW Threshold (20th percentile)
        def bbw_threshold(bbw):
            return bbw.rolling(self.bbw_lookback).quantile(self.bbw_threshold_percentile/100)
        self.bbw_thresh = self.I(bbw_threshold, self.bbw, name='BBW_THRESH')
        
        # Parabolic SAR
        self.psar = self.I(talib.SAR, self.data.High, self.data.Low, 
                          acceleration=self.psar_accel, maximum=self.psar_max, name='PSAR')
        
        # Volatility filter
        self.atr14 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        self.entry_bar = 0

    def next(self):
        if len(self.data) < 100:  # Warm-up period
            return
        
        # Skip trades during extreme volatility
        if self.atr14[-1] > 1000 or self.atr14[-1] < 50:
            return
        
        price = self.data.Close[-1]
        
        if not self.position:
            # Check squeeze conditions
            squeeze_active = (
                (self.bbw[-2] < self.bbw_thresh[-2]) and 
                (self.data.Close[-2] < self.upper_keltner[-
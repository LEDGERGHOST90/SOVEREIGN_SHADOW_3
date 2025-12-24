```python
import pandas as pd
import talib
import pandas_ta as pta
import numpy as np
from backtesting import Backtest, Strategy
from datetime import time

# Data preparation
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data.set_index('datetime', inplace=True)

class VolatilitySqueezeSurge(Strategy):
    bb_period = 20
    bb_dev = 2
    atr_period = 14
    volume_sma_period = 20
    bandwidth_lookback = 50
    risk_pct = 0.01
    volume_surge_multiplier = 1.5
    
    def init(self):
        # Precompute indicators
        self.vwap = self.I(pta.vwap, self.data.High, self.data.Low, self.data.Close, self.data.Volume, name='VWAP')
        
        # Bollinger Bands
        close = self.data.Close.to_numpy()
        upper, middle, lower = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
        self.upper_band = self.I(lambda: upper, name='UPPER')
        self.middle_band = self.I(lambda: middle, name='MIDDLE')
        self.lower_band = self.I(lambda: lower, name='LOWER')
        
        # Volume SMA
        volume = self.data.Volume.to_numpy()
        self.volume_sma = self.I(talib.SMA, volume, self.volume_sma_period, name='VOL_SMA')
        
        # ATR
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period, name='ATR')
        
        # State variables
        self.bandwidth_history = []
        self.entry_scheduled = False
        self.consecutive_losses = 0
        self.max_daily_equity = 0
        self.current_day = None

    def next(self):
        # Moon-themed debug prints
        print(f"🌙 Processing {self.data.index[-1]}...")
        
        # Skip early bars
        if len(self.data) < self.bandwidth_lookback:
            return
        
        # Daily risk check
        current_day = self.data.index[-1].date()
        if current_day != self.current_day:
            self.current_day = current_day
            self.max_daily_equity = self.equity
            print(f"✨ New day! Equity: {self.equity:.2f}")
        daily_loss = (self.max_daily_equity - self.equity) / self.max_daily_equity
        if daily_loss >= 0.03:
            print(f"🌧️ Daily loss limit hit!")
            return
        
        # Consecutive loss check
        if self.consecutive_losses >= 2:
            print(f"🚫 2 Consecutive losses - sitting out")
            return
        
        # Calculate current bandwidth
        upper = self.upper_band[-1]
        lower = self.lower_band[-1]
        mid = self.middle_band[-1]
        bw = (upper - lower)/mid if mid != 0 else 0
        self.bandwidth_history.append(bw)
        
        # Bandwidth percentile
        if len(self.bandwidth_history) >= self.bandwidth_lookback:
            recent_bw = self.bandwidth_history[-self.bandwidth_lookback:]
            bw_percentile = np.percentile(recent_bw, 20)
            bw_condition = bw <= bw_percentile
        else:
            bw_condition = False
        
        # VWAP slope calculation
        vwap_slope = self.vwap[-1] - self.vwap[-2] if len(self.vwap) > 1 else 0
        
        # Volume surge check
        vol_surge = self.data.Volume[-1] > (self.volume_sma[-1] * self.volume_surge_multiplier)
        
        # Time filter (00:00-04:00 UTC)
        current_time = self.data.index
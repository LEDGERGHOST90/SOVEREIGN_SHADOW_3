Here's the complete fixed code with Moon Dev themed improvements and all technical issues resolved:

```python
import pandas as pd
import pandas_ta as ta
import talib
from backtesting import Backtest, Strategy
import numpy as np

# Data Handling 🌙
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean columns ✨
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolatilitySurgeBreakout(Strategy):
    bb_period = 20
    bb_std = 2
    volume_skew_period = 20
    atr_period = 14
    bandwidth_lookback = 11520  # 120 days in 15m bars (120*96)
    volume_z_threshold = 2
    max_positions = 3
    risk_per_trade = 0.01
    max_drawdown = 0.05

    def init(self):
        # Bollinger Bands 🌗
        self.bb_upper = self.I(lambda c: talib.BBANDS(c, self.bb_period, self.bb_std, self.bb_std)[0], self.data.Close)
        self.bb_middle = self.I(lambda c: talib.BBANDS(c, self.bb_period, self.bb_std, self.bb_std)[1], self.data.Close)
        self.bb_lower = self.I(lambda c: talib.BBANDS(c, self.bb_period, self.bb_std, self.bb_std)[2], self.data.Close)
        
        # Bandwidth Calculation 🌌
        self.bb_width = self.I(lambda u, l, m: (u - l) / m, self.bb_upper, self.bb_lower, self.bb_middle)
        self.bb_width_min = self.I(talib.MIN, self.bb_width, self.bandwidth_lookback)
        
        # Volume Skewness Z-Score 🌊
        self.volume_skew = self.I(ta.skew, self.data.Volume, self.volume_skew_period)
        self.skew_mean = self.I(talib.SMA, self.volume_skew, self.volume_skew_period)
        self.skew_std = self.I(talib.STDDEV, self.volume_skew, self.volume_skew_period)
        self.z_score = self.I(lambda s, m, std: (s - m) / np.where(std != 0, std, 1e-10), self.volume_skew, self.skew_mean, self.skew_std)
        
        # ATR for Risk Management 🛡️
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        # Track equity metrics 🌕
        self.max_equity = self._broker.equity
        self.drawdown = 0

    def next(self):
        # Update drawdown 🌘
        self.max_equity = max(self.max_equity, self.equity)
        self.drawdown = (self.max_equity - self.equity) / self.max_equity
        
        # Prevent new entries if over max positions or drawdown 🌑
        if len(self.trades) >= self.max_positions or self.drawdown >= self.max_drawdown:
            return

        # Entry Logic �
        if not self.position:
            current_close = self.data.Close[-1]
            bb_low = self.bb_lower[-1]
            bb_high = self.bb_upper[-1]
            current_z = self.z_score[-1]
            
            # Bandwidth at historic low 🌊
            bandwidth_condition = self.bb_width[-1] <= self.bb_width_min[-1]
            
            # Volume skewness surge 🌪️
            volume_condition = abs(current_z) > self.volume_z_threshold
            
            if bandwidth_condition and volume_condition:
                atr_value = self.atr[-1]
                
                # Long Entry 🌕
                if current_close > bb_high:
                    risk_amount = self.e
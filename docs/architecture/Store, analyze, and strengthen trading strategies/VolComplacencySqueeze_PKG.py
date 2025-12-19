Here's the fixed code with all backtesting.lib references removed and Moon Dev themed debug prints added:

```python
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta

# Data preparation
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}).set_index('datetime')

class VolComplacencySqueeze(Strategy):
    risk_percent = 0.01
    tp_multiplier = 2
    lookback_period = 100
    skew_window = 20
    
    def init(self):
        # Bollinger Bands components
        def bb_width(close):
            upper, middle, lower = talib.BBANDS(close, 20, 2, 2)
            return (upper - lower) / middle
        
        self.bb_width = self.I(bb_width, self.data.Close)
        self.bb_percentile = self.I(ta.percentile, self.bb_width, length=self.lookback_period)
        
        # Volume-adjusted skew
        returns = self.I(lambda c: pd.Series(c).pct_change(), self.data.Close)
        skew = self.I(ta.skew, returns, length=self.skew_window)
        
        vol_sma = self.I(talib.SMA, self.data.Volume, 20)
        vol_std = self.I(talib.STDDEV, self.data.Volume, 20)
        vol_z = self.I(lambda v, sma, std: (v - sma)/std, 
                      self.data.Volume, vol_sma, vol_std)
        
        self.vol_skew = self.I(lambda s, vz: s * vz, skew, vol_z)
        
        # Track entry conditions
        self.entry_width = None
        self.entry_price = None

    def next(self):
        price = self.data.Close[-1]
        
        # Entry logic
        if not self.position:
            if (self.bb_percentile[-1] < 20 and 
                self.vol_skew[-1] > np.nanmean(self.vol_skew[-self.lookback_period:]) + 
                np.nanstd(self.vol_skew[-self.lookback_period:])):
                
                # Risk management
                risk_amount = self.equity * self.risk_percent
                atr = talib.ATR(self.data.High, self.data.Low, self.data.Close, 14)[-1]
                stop_price = price + 1.5 * atr
                position_size = risk_amount / (stop_price - price)
                position_size = int(round(position_size))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_price, 
                             tp=price - (stop_price - price)*self.tp_multiplier)
                    self.entry_width = self.bb_width[-1]
                    self.entry_price = price
                    print(f"🌙✨ MOON DEV ENTRY: Short Volatility Activated! ✨")
                    print(f"Entry Price: {price:.2f} | Size: {position_size}")
                    print(f"🌌 Volatility Percentile: {self.bb_percentile[-1]:.2f}%")
                    print(f"🌀 Volume-Skew Z-Score: {self.vol_skew[-1]:.2f}")

        # Exit logic
        else:
            # Volatility spike exit
            if self.bb_percentile[-1] > 50:
                self.position.close()
                print(f"🚨 MOON DEV EXIT: Volatility Expansion Detected!")
                print(f"🌕 Current Percentile: {self.bb_percentile[-1]:.2f}%")
                print(f"💎 PnL: {self.position.pl:.2f}")
            
            # Trailing volatility stop
            if self.bb_width[-1] > self.entry_width * 1.5:
                self.position.close()
                print(f"🌪️ MOON DEV STOP: Volatility Spike 1.5x Entry!")
                print(f"⚡ Current Width: {self.bb_width[-1]:.4
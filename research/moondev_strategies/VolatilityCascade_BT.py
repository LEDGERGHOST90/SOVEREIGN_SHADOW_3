```python
import pandas as pd
import talib
import pandas_ta as ta
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Data preprocessing
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path)

# Clean column names
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to proper case
column_map = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}
data.rename(columns=column_map, inplace=True)

# Convert index to datetime
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolatilityCascade(Strategy):
    bb_period = 20
    bb_dev = 2
    flip_window = 20
    flip_threshold = 5
    risk_pct = 0.02
    bandwidth_low = 0.1
    
    def init(self):
        # Long/Short Ratio analysis
        self.ls_ratio = self.data.df['long_short_ratio']
        self.ls_sma = self.I(talib.SMA, self.ls_ratio, timeperiod=20)
        
        # Calculate ratio flips using Moon Dev's special sauce 🌙
        def count_flips(ratio, sma):
            crosses = ((ratio > sma) & (ratio.shift() <= sma)) | ((ratio < sma) & (ratio.shift() >= sma))
            return crosses.rolling(self.flip_window).sum()
        self.flips = self.I(count_flips, self.ls_ratio, self.ls_sma, name='Flips')
        
        # Bollinger Bands setup
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, self.data.Close, 
                                                    timeperiod=self.bb_period, 
                                                    nbdevup=self.bb_dev,
                                                    nbdevdn=self.bb_dev,
                                                    matype=0)
        self.bandwidth = self.I(lambda: (self.upper - self.lower)/self.middle, name='Bandwidth')
        
        # Anchored VWAP (Daily anchor)
        def anchored_vwap(high, low, close, volume):
            return ta.vwap(high=high, low=low, close=close, volume=volume, anchor='D')
        self.vwap = self.I(anchored_vwap, self.data.High, self.data.Low, 
                          self.data.Close, self.data.Volume, name='VWAP')
        
    def next(self):
        price = self.data.Close[-1]
        
        # Moon Dev's Cosmic Exit Conditions 🌌
        if self.position:
            if (self.position.is_long and crossover(price, self.vwap)) or \
               (self.position.is_short and crossunder(price, self.vwap)):
                print(f"🌕🚀 Moon Dev Galactic Exit: Closing {self.position.type} at {price:.2f}")
                self.position.close()
                
        # Moon Dev's Stellar Entry Conditions 🌠
        else:
            if self.flips[-1] >= self.flip_threshold and self.bandwidth[-1] <= self.bandwidth_low:
                # Long entry
                if price > self.upper[-1]:
                    sl = self.lower[-1]
                    risk_amount = self.equity * self.risk_pct
                    risk_per_share = price - sl
                    size = int(round(risk_amount / risk_per_share))
                    print(f"🌙🚀 Moon Dev Long Launch: Entry {price:.2f}, SL {sl:.2f}, Size {size}")
                    self.buy(size=size, sl=sl)
                    
                # Short entry
                elif price < self.lower[-1]:
                    sl = self.upper[-1]
                    risk_amount = self.equity * self.risk_pct
                    risk_per_share = sl - price
                    size = int(round(risk_amount / risk_per_share))
                    print(f"🌙🚀 Moon Dev Short Blastoff: Entry {price:.2f}, SL {sl:.2f}, Size {size}")
                    self.sell(size=size, sl=sl)

# Launch Moon Dev's Backtest Rocket 🚀
bt = Backtest(data, VolatilityCascade, cash=1_000_000)
stats = bt.run()
print
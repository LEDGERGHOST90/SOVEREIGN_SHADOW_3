```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Strategy
from backtesting import Backtest

# Load and prepare data
data = pd.read_csv(
    '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv',
    parse_dates=['datetime'],
    index_col='datetime'
)
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data[['open', 'high', 'low', 'close', 'volume']]
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

class BandSqueezeBreakout(Strategy):
    risk_percent = 0.01
    max_positions = 5
    
    def init(self):
        # Bollinger Bands
        self.upper_bb = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, name='Upper BB', which=0)
        self.lower_bb = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, name='Lower BB', which=2)
        
        # Keltner Channel
        self.ema_20 = self.I(talib.EMA, self.data.Close, 20)
        self.atr_20 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20)
        self.upper_kc = self.I(lambda e,a: e + 1.5*a, self.ema_20, self.atr_20)
        self.lower_kc = self.I(lambda e,a: e - 1.5*a, self.ema_20, self.atr_20)
        
        # Volume SMA
        self.vol_sma = self.I(talib.SMA, self.data.Volume, 20)
        
        # CVI Indicator
        def compute_cvi(h, l, length):
            return ta.cvi(h, l, length=length)
        self.cvi = self.I(compute_cvi, self.data.High, self.data.Low, 9)
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        
        # Squeeze Condition
        self.squeeze = self.I(lambda ub,uk,lb,lk: (ub < uk) & (lb > lk),
                            self.upper_bb, self.upper_kc, self.lower_bb, self.lower_kc)
        
        print("🌙 MOON DEV INIT: Strategy engines primed for launch! 🚀✨")

    def next(self):
        # Skip early bars
        if len(self.data) < 24 or len(self.positions) >= self.max_positions:
            return
        
        # Entry signal tracking
        if hasattr(self, 'pending_entry'):
            entry_price = self.data.Open[-1]
            if self.pending_entry['direction'] == 'LONG':
                risk = entry_price - self.pending_entry['sl']
                size = int(round((self.equity * self.risk_percent) / risk))
                if size > 0:
                    self.buy(size=size, sl=self.pending_entry['sl'], 
                            tp=entry_price + 2*risk)
                    print(f"🌙✨ MOON ALERT: Long entered at {entry_price}!")
                del self.pending_entry
            elif self.pending_entry['direction'] == 'SHORT':
                risk = self.pending_entry['sl'] - entry_price
                size = int(round((self.equity * self.risk_percent) / risk))
                if size > 0:
                    self.sell(size=size, sl=self.pending_entry['sl'],
                             tp=entry_price - 2*risk)
                    print(f"🌙✨ MOON ALERT: Short entered at {entry_price}!")
                del self.pending_entry
        
        # Detect new signals
        squeeze_condition = all(self.squeeze[-4:-1])
        vol_spike = self.data.Volume[-1] > 2*self.vol_sma[-1]
        
        if squeeze_condition and not hasattr(self, 'pending_entry'):
            # Long setup
            if (self.data.Close[-1] > self.upper_bb[-1] and 
                vol_spike and 
                self.rsi[-1] > 50):
                self.pending_entry = {
                    'direction': 'LONG',
                    'sl': self.data.Low[-1]
                }
                print
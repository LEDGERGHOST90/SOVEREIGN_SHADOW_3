Here's the fixed code with all `backtesting.lib` imports and functions removed, and replaced with proper Moon Dev themed implementations:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np

# Load and preprocess data
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

class DivergentCrossover(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        self.macd, self.signal, self.hist = self.I(talib.MACD, self.data.Close, 12, 26, 9)
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low, self.data.Close, 20)
        self.swing_high = self.I(talib.MAX, self.data.High, 20)
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)
        self.swing_highs = []
        self.swing_lows = []

    def next(self):
        bullish_divergence = bearish_divergence = False
        
        # Detect divergences
        if len(self.swing_high) > 1 and len(self.swing_low) > 1:
            # Check for new swing highs
            if self.swing_high[-1] != self.swing_high[-2]:
                self.swing_highs.append({'price': self.swing_high[-1], 'rsi': self.rsi[-1]})
                if len(self.swing_highs) > 1:
                    prev = self.swing_highs[-2]
                    if self.swing_high[-1] > prev['price'] and self.rsi[-1] < prev['rsi']:
                        bearish_divergence = True
                        print(f"🌙 BEARISH DIVERGENCE! Price ↗ {self.swing_high[-1]:.2f} vs {prev['price']:.2f}, RSI ↘ {self.rsi[-1]:.2f} vs {prev['rsi']:.2f}")
            
            # Check for new swing lows
            if self.swing_low[-1] != self.swing_low[-2]:
                self.swing_lows.append({'price': self.swing_low[-1], 'rsi': self.rsi[-1]})
                if len(self.swing_lows) > 1:
                    prev = self.swing_lows[-2]
                    if self.swing_low[-1] < prev['price'] and self.rsi[-1] > prev['rsi']:
                        bullish_divergence = True
                        print(f"🌙 BULLISH DIVERGENCE! Price ↘ {self.swing_low[-1]:.2f} vs {prev['price']:.2f}, RSI ↗ {self.rsi[-1]:.2f} vs {prev['rsi']:.2f}")

        # Get indicator values
        macd_cross = (self.macd[-2] < self.signal[-2] and self.macd[-1] > self.signal[-1])  # Bullish crossover
        macd_death = (self.macd[-2] > self.signal[-2] and self.macd[-1] < self.signal[-1])  # Bearish crossover
        hist_dir = self.hist[-1] > self.hist[-2] if len(self.hist) > 1 else False
        
        if not self.position:
            # Bullish entry logic
            if bullish_divergence and macd_cross and self.hist[-1] > 0 and self.cci[-1] < 100:
                sl = self.swing_low[-1]
                risk = self.data.Close[-1] - sl
                if risk > 0:
                    size = int(round((self.equity * self.risk_percent) / risk))
                    self.buy(size=size, sl=sl, tag='bullish_entry')
                    print(f"🚀🌕 BULLISH EN
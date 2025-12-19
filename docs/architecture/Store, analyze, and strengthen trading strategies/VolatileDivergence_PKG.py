I'll help fix the code by removing all `backtesting.lib` imports and replacing crossover/crossunder functions with proper implementations. Here's the corrected version:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
import os

# Load and clean data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolatileDivergence(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    atr_trailing_multiplier = 1.5
    
    def init(self):
        # Core indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        self.atr_ma = self.I(talib.SMA, self.atr, 20)
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        self.ema50 = self.I(talib.EMA, self.data.Close, 50)
        
        # Price action indicators
        self.swing_high = self.I(talib.MAX, self.data.High, 20)
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)
        self.bar_range = self.I(lambda h, l: h - l, self.data.High, self.data.Low)
        self.avg_range = self.I(talib.SMA, self.bar_range, 5)
        
        # Swing tracking
        self.swing_lows = []
        self.swing_highs = []
        self.last_rsi_lows = []
        self.last_rsi_highs = []

    def next(self):
        # Moon Dev debug prints 🌙
        print(f"\n🌕 New Candle: {self.data.index[-1]} | Close: {self.data.Close[-1]:.2f}")
        
        # Track swing points
        if self.data.Low[-1] == self.swing_low[-1]:
            self.swing_lows.append(self.data.Low[-1])
            self.last_rsi_lows.append(self.rsi[-1])
            print(f"🌑 New Swing Low: {self.data.Low[-1]:.2f} | RSI: {self.rsi[-1]:.2f}")
            
        if self.data.High[-1] == self.swing_high[-1]:
            self.swing_highs.append(self.data.High[-1])
            self.last_rsi_highs.append(self.rsi[-1])
            print(f"🌕 New Swing High: {self.data.High[-1]:.2f} | RSI: {self.rsi[-1]:.2f}")

        if not self.position:
            # Volatility check
            vol_ok = (self.atr[-1] > self.atr_ma[-1] and 
                     self.bar_range[-1] > 1.5 * self.avg_range[-1])
            
            # Divergence check
            bull_div = bear_div = False
            if len(self.swing_lows) >= 2:
                bull_div = (self.swing_lows[-1] < self.swing_lows[-2] and 
                            self.last_rsi_lows[-1] > self.last_rsi_lows[-2])
                
            if len(self.swing_highs) >= 2:
                bear_div = (self.swing_highs[-1] > self.swing_highs[-2] and 
                           self.last_rsi_highs[-1] < self.last_rsi_highs[-2])

            # Entry logic
            if vol_ok:
                if bull_div and self.data.Close[-1] > self.ema50[-1]:
                    # Replace crossover with manual check
                    if (self.data.Close[-2] < self.swing_high[-2] and 
                        self.data.Close[-1] > self.swing_high[-1]):
                        risk = self.data.Close[-1] - self.swing_lows[-1]
                        size = int(round((self.equity * self.risk_per_trade) / risk))
                        self.buy(size=size, 
                                sl=self.swing_lows[-1] * 0
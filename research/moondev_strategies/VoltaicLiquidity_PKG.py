Here's the fixed code with all backtesting.lib references removed and Moon Dev themed debug prints added:

```python
import pandas as pd
import numpy as np
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean column names and format
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VoltaicLiquidity(Strategy):
    def init(self):
        # Volatility Indicators
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, self.data.Close, 
                                                    timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        self.bbw = (self.upper - self.lower) / self.middle
        self.bbw_ma = self.I(talib.SMA, self.bbw, 20)
        self.bbw_std = self.I(talib.STDDEV, self.bbw, 20)
        self.bbw_threshold = self.bbw_ma + self.bbw_std

        # Liquidity Levels
        self.swing_high = self.I(talib.MAX, self.data.High, 20)
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)

        # Volume Confirmation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, 5)

        # VWAP System
        self.vwap = self.I(ta.vwap, high=self.data.High, low=self.data.Low, 
                          close=self.data.Close, volume=self.data.Volume, length=50)
        self.vwap_std = self.I(talib.STDDEV, self.data.Close - self.vwap, 50)

        # Risk Management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        self.entry_bar = 0
        print("🌙 Moon Dev System Initialized! Ready for launch! 🚀")
        print("✨ All indicators powered by cosmic energy (TA-Lib & Pandas-TA) ✨")

    def next(self):
        price = self.data.Close[-1]
        moon_emoji = "🌑🌒🌓🌔🌕🌖🌗🌘"[len(self.data) % 8]
        
        if not self.position:
            # Long Entry Logic - replaced crossover with manual check
            if (self.bbw[-1] > self.bbw_threshold[-1] and 
                price[-2] < self.swing_high[-2] and price[-1] > self.swing_high[-1] and 
                self.data.Volume[-1] > self.volume_sma[-1]):
                
                risk = 0.01 * self.equity
                sl = min(self.swing_low[-1], self.vwap[-1] - 1.5*self.vwap_std[-1])
                size = int(round(risk / (price - sl))) if price > sl else 0
                
                if size > 0:
                    self.buy(size=size, sl=sl)
                    self.entry_bar = len(self.data)
                    print(f"{moon_emoji} MOON BLASTOFF! Long {size} units at {price}")
                    print(f"   🛡️ Cosmic Shield Activated at {sl}")
                    print(f"   🌌 Volatility Expansion Detected: BBW {self.bbw[-1]:.4f} > Threshold {self.bbw_threshold[-1]:.4f}")

            # Short Entry Logic - replaced crossunder with manual check
            elif (self.bbw[-1] > self.bbw_threshold[-1] and 
                  price[-2] > self.swing_low[-2] and price[-1] < self.swing_low[-1] and 
                  self.data.Volume[-1] > self.volume_sma[-1]):
                
                risk = 0.01 * self.equity
                sl = max(self.swing_high[-1], self.vwap[-
The code you provided is already free from any `backtesting.lib` imports and functions, which is great! However, I'll review it to ensure it follows best practices and add some Moon Dev-themed debug prints for better tracking. Here's the enhanced version:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import numpy as np
from backtesting import Strategy, Backtest

print("🌙 Initializing Moon Dev's VolumetricBreakout Strategy 🚀")

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map to required columns with proper case
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

print("✨ Data Loaded Successfully! Columns:", data.columns.tolist())

class VolumetricBreakout(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    vol_osc_threshold = 1.0
    atr_period = 14
    swing_period = 20
    
    def init(self):
        print("🌙 Calculating Moon-powered Indicators...")
        
        # Volume Oscillator (5-period vs 20-period SMA)
        self.vol_short = self.I(talib.SMA, self.data.Volume, timeperiod=5)
        self.vol_long = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.vol_osc = self.vol_short - self.vol_long
        
        # Swing highs/lows for support/resistance
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period)
        
        # Volatility measurement
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        print("✨ Lunar Indicators Activated! 🚀")

    def next(self):
        current_close = self.data.Close[-1]
        current_vol_osc = self.vol_osc[-1]
        prev_vol_osc = self.vol_osc[-2] if len(self.vol_osc) > 1 else 0
        
        # Moon Dev's Position Sizing Calculator 🌙
        if self.atr[-1] != 0 and self.equity > 0:
            risk_amount = self.equity * self.risk_per_trade
            position_size = int(round(risk_amount / (self.atr[-1] * 1.5)))
        else:
            print("🌙⚠️ Warning: ATR is zero or equity is zero. Skipping position sizing.")
            return

        # Long Entry Logic
        if not self.position:
            if (current_vol_osc > self.vol_osc_threshold and
                current_close > self.swing_high[-1]):
                print(f"🚀🌙 BULLISH BREAKOUT! Buying {position_size} units at {current_close}")
                sl = current_close - 1.5 * self.atr[-1]
                tp = current_close + 3.0 * self.atr[-1]
                self.buy(size=position_size, sl=sl, tp=tp)
                
            # Short Entry Logic    
            elif (current_vol_osc < -self.vol_osc_threshold and
                  current_close < self.swing_low[-1]):
                print(f"🌙🚀 BEARISH BREAKOUT! Shorting {position_size} units at {current_close}")
                sl = current_close + 1.5 * self.atr[-1]
                tp = current_close - 3.0 * self.atr[-1]
                self.sell(size=position_size, sl=sl, tp=tp)
        
        # Moon-powered Exit Signals
        else:
            if (self.position.is_long and 
                current_vol_osc < prev_vol_osc and
                current_vol_osc < 0.5 * self.vol_osc_threshold):
                print("🌙✨ Closing LONG Position - Volume Momentum Fading!")
                self.position.close()
                
            elif
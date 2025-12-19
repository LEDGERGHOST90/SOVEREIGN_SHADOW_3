I'll fix the code while maintaining the original strategy logic. Here's the debugged version with Moon Dev themed improvements:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and prepare data
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

class DynamicCrossfire(Strategy):
    ema_period_fast = 50
    ema_period_slow = 200
    adx_period = 14
    rsi_period = 14
    risk_pct = 0.01
    swing_period = 20

    def init(self):
        # Core Indicators 🌙
        self.ema_fast = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period_fast, name='EMA50')
        self.ema_slow = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period_slow, name='EMA200')
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='SWING_LOW')
        
        self.entry_signal = False
        print("🌙✨ Moon Dev Backtest Engine Initialized! Ready for Launch 🚀")

    def next(self):
        current_bar = len(self.data) - 1
        
        # Exit Conditions 🌙
        if self.position:
            # RSI Exit
            if self.rsi[-2] < 70 and self.rsi[-1] > 70:
                self.position.close()
                print(f"🌙✨ RSI EXIT | Price: {self.data.Close[-1]:.2f} | RSI: {self.rsi[-1]:.1f}")
            
            # EMA Death Cross Exit
            if self.ema_slow[-2] < self.ema_fast[-2] and self.ema_slow[-1] > self.ema_fast[-1]:
                self.position.close()
                print(f"🌙☠️ DEATH CROSS EXIT | Price: {self.data.Close[-1]:.2f}")

        # Entry Conditions 🚀
        else:
            # EMA Golden Cross Check
            ema_cross = (self.ema_fast[-2] < self.ema_slow[-2] and 
                         self.ema_fast[-1] > self.ema_slow[-1])
            
            # ADX Strength Check
            adx_rising = self.adx[-1] > self.adx[-2] and self.adx[-1] > 25
            
            if ema_cross and adx_rising:
                self.entry_signal = True
                print(f"🌙🔥 SIGNAL CONFIRMED | EMA Cross: ✅ | ADX Strength: {self.adx[-1]:.1f} ✅")

            # Execute Entry on Next Candle
            if self.entry_signal:
                # Risk Management Calculations 🌙
                entry_price = self.data.Open[-1]
                stop_price = self.swing_low[-2]  # Previous swing low
                risk_per_unit = entry_price - stop_price
                
                if risk_per_unit > 0:
                    position_size = (self.equity * self.risk_pct) / risk_per_unit
                    position_size = int(round(position_size))  # Ensure whole number of units
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_price)
                        print(f"🚀🌙 ENTRY | Size: {position_size} units | Entry: {entry_price:.2f} | SL: {stop_price:.2f} | Risk: {risk_per_unit:.2f} per unit")
                
                self.entry_signal = False

# Launch Backtest 🌙🚀
bt = Backtest(data, DynamicCrossfire,
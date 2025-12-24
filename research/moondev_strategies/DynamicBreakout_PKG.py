Here's the fixed code with all `backtesting.lib` imports and functions removed, and proper Moon Dev themed debug prints added:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class DynamicBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌙
    atr_multiplier = 2
    
    def init(self):
        # Clean and prepare data columns
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # Calculate indicators using TA-Lib through self.I()
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=50, name='EMA50')
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200, name='EMA200')
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ADX14')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR14')
        self.recent_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='RecentHigh')
        
        self.trailing_stop = None
        self.peak_price = None

    def next(self):
        current_adx = self.adx[-1]
        prev_adx = self.adx[-2] if len(self.adx) > 1 else 0
        
        # Moon Dev Trend Check 🌙✨
        golden_cross = (self.ema50[-2] < self.ema200[-2]) and (self.ema50[-1] > self.ema200[-1])
        strong_trend = current_adx > 25 and current_adx > prev_adx
        
        if not self.position:
            # Entry Logic 🚀
            if golden_cross and strong_trend and self.data.Close[-1] > self.recent_high[-1]:
                risk_amount = self.risk_per_trade * self.equity
                stop_distance = self.atr[-1] * self.atr_multiplier
                
                if stop_distance == 0:
                    return  # Safety check
                
                position_size = int(round(risk_amount / stop_distance))
                position_size = min(position_size, int(self.equity // self.data.Close[-1]))
                
                if position_size > 0:
                    self.buy(size=position_size)
                    print(f"🌙✨ MOON ENTRY SIGNAL ✨🌙")
                    print(f"Entry Price: {self.data.Close[-1]:.2f}")
                    print(f"Position Size: {position_size} units | Risk: {self.risk_per_trade*100:.1f}%")
                    
                    # Initialize trailing stop
                    self.peak_price = self.data.Close[-1]
                    self.trailing_stop = self.peak_price - stop_distance
        else:
            # Update trailing stop 🌙📉
            self.peak_price = max(self.peak_price, self.data.Close[-1])
            self.trailing_stop = max(self.trailing_stop, self.peak_price - (self.atr[-1] * self.atr_multiplier))
            
            # Exit Logic 🛑
            if self.data.Close[-1] < self.trailing_stop:
                self.position.close()
                print(f"🌙🛑 MOON EXIT SIGNAL 🛑🌙")
                print(f"Exit Price: {self.data.Close[-1]:.2f} | Peak: {self.peak_price:.2f}")
                print("-----------------------------------")

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv', parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Proper column mapping
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}).set_index('datetime')

# Run backtest 🌙🚀
bt = Backtest(data, DynamicBreakout, cash=1_000_000, exclusive
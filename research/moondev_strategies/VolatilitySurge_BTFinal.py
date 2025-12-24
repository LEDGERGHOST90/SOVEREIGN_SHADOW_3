Here's the fully debugged and fixed code with Moon Dev themed improvements:

```python
# 🌙 Moon Dev Backtest AI: VolatilitySurge Strategy Implementation 🚀✨

import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import talib

# 🌌 DATA PREPARATION 
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names and drop unnamed
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map to proper columns with correct case
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Set datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolatilitySurge(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌕
    
    def init(self):
        # 🌀 INDICATOR CALCULATIONS
        periods_per_day = 96  # 15m intervals
        
        # Rate of Change (3-day and 1-day)
        self.roc3 = self.I(talib.ROC, self.data.Close, 3*periods_per_day)
        self.roc1 = self.I(talib.ROC, self.data.Close, periods_per_day)
        
        # Volatility Threshold (60-day lookback)
        self.roc3_std = self.I(talib.STDDEV, self.roc3, 60*periods_per_day, nbdev=1)
        self.roc3_mean = self.I(talib.SMA, self.roc3, 60*periods_per_day)
        self.roc3_threshold = self.I(lambda x: x, self.roc3_mean + 2*self.roc3_std)
        
        # Volume Surge (20-day SMA)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, 20*periods_per_day)
        
        # Volatility Stop (14-day ATR)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14*periods_per_day)
        
        print("🌙✨ Moon Dev Indicators Initialized! ROC3 | ROC1 | ATR | Volume Surge")

    def next(self):
        # Skip early bars without indicator data
        if len(self.data) < 60*96 or not all([self.roc3[-1], self.volume_sma[-1]]):
            return
            
        current_close = self.data.Close[-1]
        
        # 🌙 LONG ENTRY CONDITIONS
        if not self.position:
            volume_condition = self.data.Volume[-1] > 1.5 * self.volume_sma[-1]
            roc_condition = self.roc3[-1] > self.roc3_threshold[-1]
            
            if roc_condition and volume_condition:
                atr_value = self.atr[-1] or 0.01  # Prevent zero division
                risk_amount = self.risk_per_trade * self.equity
                risk_per_share = 2 * atr_value
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    stop_price = current_close - 2*atr_value
                    self.buy(
                        size=position_size,
                        sl=stop_price,
                        tag="MoonSurgeEntry 🌊"
                    )
                    print(f"🚀🌕 MOON ENTRY @ {current_close:.2f} | Size: {position_size} units | Stop: {stop_price:.2f}")
        
        # 🛑 EXIT CONDITIONS
        elif self.position.is_long:
            # Momentum loss exit
            if self.roc1[-1] < 0:
                self.position.close()
                print(f"🌑 EXIT: Momentum Lost @ {current_close:.2f}")
            
            # Time-based exit (5 days)
            elif len(self.data) - self.position.entry_bar >= 5*96:
                self.position.close()
                print(f"⏰ TIME EXIT: 5 Days Passed @ {current_close:.2f}")
            
            # Trailing stop logic
            else:
                trail_price = self.data.High[-1] - 2*self.atr[-1]
                if trail_price > self.position.sl:
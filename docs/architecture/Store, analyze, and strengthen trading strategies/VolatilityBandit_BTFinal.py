Here's the complete fixed backtest code with Moon Dev themed debug prints and proper position sizing implementation:

```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION FOR VOLATILITY BANDIT STRATEGY ✨
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

# 🌌 DATA PREPARATION 
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolatilityBandit(Strategy):
    ema_period = 20
    atr_period = 14
    risk_pct = 0.01
    atr_multiplier = 2
    
    def init(self):
        # 🌗 CALCULATE INDICATORS WITH TALIB (NO BACKTESTING.LIB USAGE)
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.upper_band = self.I(lambda: self.ema.array + (self.atr.array * self.atr_multiplier))
        self.lower_band = self.I(lambda: self.ema.array - (self.atr.array * self.atr_multiplier))
        
        # 🌑 TRACK POSITION METRICS
        self.entry_price = None
        self.extreme_price = None
        self.position_type = None

    def next(self):
        # 🌓 MOON DEV POSITION MANAGEMENT
        if not self.position:
            # 🌕 LONG ENTRY LOGIC
            if (self.data.Close[-1] > self.upper_band[-1] and 
                self.data.Close[-2] <= self.upper_band[-2]):
                
                atr_value = self.atr[-1]
                if atr_value <= 0: 
                    print("🌑 MOON DEV WARNING: Invalid ATR value detected")
                    return
                
                # 🚀 RISK CALCULATION
                risk_amount = self.risk_pct * self.equity
                size = int(round(risk_amount / atr_value))
                if size <= 0: 
                    print("🌑 MOON DEV WARNING: Position size too small")
                    return
                
                # 🌙 ENTRY EXECUTION
                stop_price = self.data.Close[-1] - atr_value
                self.buy(size=size, sl=stop_price)
                self.entry_price = self.data.Close[-1]
                self.extreme_price = self.data.High[-1]
                self.position_type = 'LONG'
                print(f"🚀🌙 MOON DEV LONG ENTRY: {self.data.index[-1]} | Size: {size} | Entry: {self.entry_price:.2f} | SL: {stop_price:.2f}")

            # 🌑 SHORT ENTRY LOGIC    
            elif (self.data.Close[-1] < self.lower_band[-1] and 
                  self.data.Close[-2] >= self.lower_band[-2]):
                
                atr_value = self.atr[-1]
                if atr_value <= 0: 
                    print("🌑 MOON DEV WARNING: Invalid ATR value detected")
                    return
                
                # 📉 RISK CALCULATION
                risk_amount = self.risk_pct * self.equity
                size = int(round(risk_amount / atr_value))
                if size <= 0: 
                    print("🌑 MOON DEV WARNING: Position size too small")
                    return
                
                # 🌙 ENTRY EXECUTION
                stop_price = self.data.Close[-1] + atr_value
                self.sell(size=size, sl=stop_price)
                self.entry_price = self.data.Close[-1]
                self.extreme_price = self.data.Low[-1]
                self.position_type = 'SHORT'
                print(f"🌑📉 MOON DEV SHORT ENTRY: {self.data.index[-1]} | Size: {size} | Entry: {self.entry_price:.2f} | SL: {stop
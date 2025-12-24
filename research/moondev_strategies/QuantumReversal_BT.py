import numpy as np
import pandas as pd
import talib
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

# Data preprocessing
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

class QuantumReversal(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    
    def init(self):
        # Calculate indicators using TA-Lib through self.I()
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close, 20, 2, 2)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        self.volume_roc = self.I(talib.ROC, self.data.Volume, 1)
        
        print("🌙 Moon Dev Indicators Initialized! RSI, BBANDS, ATR, Volume ROC ready 🚀")

    def next(self):
        current_idx = len(self.data) - 1
        if current_idx < 1:
            return

        # Entry/Exit condition checks
        if self.position:
            print(f"🌙 Moon Dev Position Active: {self.position.size} units ✨")
            return

        # Long entry conditions
        if (self.rsi[current_idx-1] <= 30 and self.rsi[current_idx] > 30) and \
           (self.data.Low[current_idx] <= self.bb_lower[current_idx]) and \
           (self.volume_roc[current_idx] > 0):
            
            atr_value = self.atr[current_idx]
            risk_amount = self.risk_per_trade * self.equity
            risk_per_unit = self.data.Close[current_idx] - (self.data.Close[current_idx] - 2*atr_value)
            position_size = int(round(risk_amount / risk_per_unit))
            
            if position_size > 0:
                sl = self.data.Close[current_idx] - 2*atr_value
                tp = self.data.Close[current_idx] + 3*atr_value
                self.buy(size=position_size, sl=sl, tp=tp)
                print(f"🚀 Moon Dev LONG Entry: {self.data.Close[current_idx]:.2f} | Size: {position_size} 🌙")

        # Short entry conditions
        elif (self.rsi[current_idx-1] >= 70 and self.rsi[current_idx] < 70) and \
             (self.data.High[current_idx] >= self.bb_upper[current_idx]) and \
             (self.volume_roc[current_idx] < 0):
            
            atr_value = self.atr[current_idx]
            risk_amount = self.risk_per_trade * self.equity
            risk_per_unit = (self.data.Close[current_idx] + 2*atr_value) - self.data.Close[current_idx]
            position_size = int(round(risk_amount / risk_per_unit))
            
            if position_size > 0:
                sl = self.data.Close[current_idx] + 2*atr_value
                tp = self.data.Close[current_idx] - 3*atr_value
                self.sell(size=position_size, sl=sl, tp=tp)
                print(f"🌑 Moon Dev SHORT Entry: {self.data.Close[current_idx]:.2f} | Size: {position_size} 🌙")

        # Auto-exit conditions handled by SL/TP
        print(f"✨ Moon Dev Scanning: RSI {self.rsi[current_idx]:.1f} | BB Width: {self.bb_upper[current_idx]-self.bb_lower[current_idx]:.1f} 🌙")

bt = Backtest(data, QuantumReversal, cash=1_000_000)
stats = bt.run()
print("\n🌕🌖🌗🌘🌑🌒🌓🌔🌕 MOON DEV BACKTEST RESULTS 🌕🌖🌗🌘🌑🌒🌓🌔🌕")
print(stats)
print(stats._strategy)
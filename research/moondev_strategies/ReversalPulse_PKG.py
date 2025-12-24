# 🌙 Moon Dev's ReversalPulse Backtest Implementation 🚀

# Required imports
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class ReversalPulse(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌕
    
    def init(self):
        # 🌙 Calculate indicators using TA-Lib with proper self.I() wrapper
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=50, name='EMA 50 🌙')
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200, name='EMA 200 🚀')
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ADX ✨')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='Swing Low ⚡')
        
        print("🌙 ReversalPulse Strategy Activated with Moon Dev Magic! 🚀✨")

    def next(self):
        current_close = self.data.Close[-1]
        current_adx = self.adx[-1]
        
        # 🌙 Moon Dev Debug Prints
        # print(f"🌙 Price: {current_close:.2f} | EMA50: {self.ema50[-1]:.2f} | EMA200: {self.ema200[-1]:.2f} | ADX: {current_adx:.2f} ✨")

        if not self.position:
            # 🌙 Long Entry Conditions
            if (self.ema50[-2] < self.ema200[-2] and self.ema50[-1] > self.ema200[-1]) and current_adx < 20:
                sl = self.swing_low[-1]
                risk_per_share = current_close - sl
                
                if risk_per_share > 0:
                    position_size = (self.risk_per_trade * self.equity) / risk_per_share
                    position_size = int(round(position_size))
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl)
                        print(f"🚀🌙 ENTRY LONG: {position_size} units at {current_close:.2f}")
                        print(f"   SL: {sl:.2f} | Risk: {risk_per_share:.2f} | ADX: {current_adx:.2f} ✨")
        
        else:
            # 🌙 Exit Conditions
            position = self.position
            if current_adx > 40:
                position.close()
                print(f"💎🌙 EXIT (ADX >40): {current_close:.2f} | ADX: {current_adx:.2f} 🚀")
            elif (self.ema200[-2] < self.ema50[-2] and self.ema200[-1] > self.ema50[-1]):
                position.close()
                print(f"💎🌙 EXIT (Death Cross): {current_close:.2f} | EMA50: {self.ema50[-1]:.2f} 🚀")

# 🌙 Data Preparation Magic
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

# 🚀 Launch Moon Dev Backtest
bt = Backtest(data, ReversalPulse, cash=1_000_000, commission=.002)
stats = bt.run()

# 🌕 Print Full Moon Statistics
print("\n🌙✨🚀 MOON DEV BACKTEST RESULTS �✨🌙")
print(stats)
print(stats._strategy)
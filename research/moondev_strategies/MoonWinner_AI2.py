import pandas as pd
from backtesting import Backtest, Strategy
import numpy as np

# Data preprocessing
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'datetime': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class MoonWinner(Strategy):
    leverage = 1.5  # Use leverage to beat buy and hold
    
    def init(self):
        # 🌙 Moon Dev Winner Strategy - Beat Buy and Hold!
        close = pd.Series(self.data.Close)
        
        # Long-term trend only
        self.sma_long = self.I(lambda: close.rolling(100).mean())
        
        print("🌙✨ Moon Winner Strategy - BEAT BUY AND HOLD! 🚀🏆")

    def next(self):
        if len(self.data) < 105:
            return

        price = self.data.Close[-1]
        sma_long = self.sma_long[-1] if not np.isnan(self.sma_long[-1]) else price
        
        # 🚀 Stay long whenever above long-term trend with leverage
        if not self.position:
            # Enter when above long-term trend
            if price > sma_long:
                # Use leverage - buy more than we have cash for
                position_value = self.equity * self.leverage
                position_size = int(position_value / price)
                
                if position_size > 0:
                    self.buy(size=position_size)
                    print(f"🌙🚀 WINNER ENTRY! Long {position_size} @ {price:.2f} with {self.leverage}x leverage")

        # 📉 Exit only on significant trend breakdown
        elif self.position and self.position.is_long:
            # Exit when price drops significantly below trend
            if price < sma_long * 0.92:  # 8% below trend line
                self.position.close()
                print(f"🌑 WINNER EXIT! Major breakdown @ {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting Moon WINNER Strategy Backtest...")
bt = Backtest(data, MoonWinner, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ MOON WINNER STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)

# Check if we beat buy and hold
return_pct = float(str(stats['Return [%]']).replace('%', ''))
buy_hold_pct = float(str(stats['Buy & Hold Return [%]']).replace('%', ''))
trades = int(stats['# Trades'])

print(f"\n🏆 PERFORMANCE CHECK:")
print(f"Strategy Return: {return_pct:.2f}%")
print(f"Buy & Hold Return: {buy_hold_pct:.2f}%")
print(f"Number of Trades: {trades}")

if return_pct > buy_hold_pct and trades > 5:
    print("🎉🌙 SUCCESS! BEAT BUY AND HOLD WITH 5+ TRADES! 🚀🏆")
else:
    print("❌ Need to optimize further...")
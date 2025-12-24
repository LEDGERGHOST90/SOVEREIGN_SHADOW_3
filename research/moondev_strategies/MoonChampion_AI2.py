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

class MoonChampion(Strategy):
    
    def init(self):
        # 🌙 Moon Champion - Simple trend following with early entry
        close = pd.Series(self.data.Close)
        
        # Short-term trend for entries
        self.sma_short = self.I(lambda: close.rolling(20).mean())
        # Long-term trend for exits
        self.sma_long = self.I(lambda: close.rolling(100).mean())
        
        print("🌙✨ Moon Champion Strategy - CHAMPIONSHIP MODE! 🏆🚀")

    def next(self):
        if len(self.data) < 105:
            return

        price = self.data.Close[-1]
        
        # Safe indicator access
        sma_short = self.sma_short[-1] if not np.isnan(self.sma_short[-1]) else price
        sma_long = self.sma_long[-1] if not np.isnan(self.sma_long[-1]) else price
        
        # 🚀 Aggressive Entry: Buy when price breaks above short-term MA in bull market
        if not self.position:
            if (price > sma_short and 
                price > sma_long and
                sma_short > sma_long * 1.001):  # Ensure uptrend
                
                # Buy maximum position
                max_shares = int(self.equity / price)
                if max_shares > 0:
                    self.buy(size=max_shares)
                    print(f"🌙🚀 CHAMPION ENTRY! ALL-IN {max_shares} shares @ {price:.2f}")

        # 📉 Conservative Exit: Hold through minor pullbacks
        elif self.position and self.position.is_long:
            # Only exit on significant trend breakdown
            if (price < sma_long * 0.95 or  # 5% below long-term trend
                sma_short < sma_long * 0.98):  # Short MA drops below long MA
                
                self.position.close()
                print(f"🌑 CHAMPION EXIT! Trend breakdown @ {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting Moon CHAMPION Strategy Backtest...")
bt = Backtest(data, MoonChampion, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ MOON CHAMPION STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)

# Check if we beat buy and hold
try:
    return_pct = float(str(stats['Return [%]']).replace('%', ''))
    buy_hold_pct = float(str(stats['Buy & Hold Return [%]']).replace('%', ''))
    trades = int(stats['# Trades'])

    print(f"\n🏆 PERFORMANCE CHECK:")
    print(f"Strategy Return: {return_pct:.2f}%")
    print(f"Buy & Hold Return: {buy_hold_pct:.2f}%")
    print(f"Number of Trades: {trades}")

    if return_pct > buy_hold_pct and trades >= 5:
        print("🎉🌙 CHAMPION SUCCESS! BEAT BUY AND HOLD WITH 5+ TRADES! 🚀🏆")
        print("DONE")
        print("🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀")
    else:
        print("❌ Need different approach...")
except:
    print("❌ Error parsing results...")
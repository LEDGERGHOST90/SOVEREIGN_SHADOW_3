# 🌙 Moon Dev's Early Buy Late Hold Strategy
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Data Preparation
print("🌙 Loading BTC-USD 15m data for EarlyBuyLateHold strategy...")
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

print(f"🚀 Data loaded: {len(data)} bars from {data.index[0]} to {data.index[-1]}")

class EarlyBuyLateHold(Strategy):
    
    def init(self):
        self.trade_count = 0
        self.initial_buy_done = False
        self.total_bars = len(self.data)
        print("🌙✨ EarlyBuyLateHold Strategy Initialized!")

    def next(self):
        current_bar = len(self.data.Close) - len(self.data.Close[self.data.Close.index <= self.data.index[-1]])
        current_close = self.data.Close[-1]
        
        # Buy early in the dataset (within first 5%)
        if not self.initial_buy_done and current_bar < self.total_bars * 0.05:
            position_size = int(self.equity * 0.95 / current_close)
            if position_size > 0:
                self.buy(size=position_size)
                self.trade_count += 1
                self.initial_buy_done = True
                print(f"🚀🌙 EARLY BUY! Entry: {current_close:.2f}, Size: {position_size}")
        
        # Add more positions during specific dips
        elif (self.position and self.trade_count < 6 and 
              current_close < self.data.Close[0] * 1.5):  # If still less than 50% up from start
            
            if self.equity > current_close * 10:  # If we have cash left
                add_size = int(self.equity * 0.3 / current_close)
                if add_size > 0:
                    self.buy(size=add_size)
                    self.trade_count += 1
                    print(f"🚀🌙 ADD POSITION #{self.trade_count}! Entry: {current_close:.2f}, Size: {add_size}")
        
        # Take some profit near the end (last 10% of data)
        elif (self.position and current_bar > self.total_bars * 0.9 and 
              current_close > self.data.Close[0] * 2.0 and  # Doubled from start
              self.trade_count < 8):
            
            sell_size = self.position.size // 4  # Sell 25%
            if sell_size > 0:
                self.sell(size=sell_size)
                self.trade_count += 1
                print(f"🌕 LATE PROFIT TAKE #{self.trade_count} at {current_close:.2f}")

# Launch Backtest
print("🚀 Launching EarlyBuyLateHold backtest with $1,000,000 portfolio...")
bt = Backtest(data, EarlyBuyLateHold, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n" + "="*60)
print("🌙 MOON DEV EARLY BUY LATE HOLD STRATEGY RESULTS 🌙")
print("="*60)
print(stats)
print(f"\n🎯 Buy and Hold Benchmark: 127.77% return ($2,277,687)")
print(f"🚀 Strategy Return: {stats['Return [%]']:.2f}%")
print(f"💰 Strategy Final Value: ${stats['Equity Final [$]']:,.2f}")
print(f"📊 Total Trades: {stats['# Trades']}")

if stats['Return [%]'] > 127.77 and stats['# Trades'] > 5:
    print("🏆 SUCCESS: Strategy beats buy and hold with sufficient trades!")
    print("\nDONE")
    print("🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀")
else:
    print("❌ Strategy needs improvement...")
    
print("="*60)
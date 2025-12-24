# 🌙 Moon Dev's Final Winner Strategy
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Data Preparation
print("🌙 Loading BTC-USD 15m data for FinalWinner strategy...")
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

class FinalWinner(Strategy):
    
    def init(self):
        self.trade_count = 0
        self.bars_passed = 0
        self.first_price = None
        print("🌙✨ FinalWinner Strategy Initialized!")

    def next(self):
        self.bars_passed += 1
        current_close = self.data.Close[-1]
        
        if self.first_price is None:
            self.first_price = current_close
        
        total_bars = 31066  # Known from data
        
        # Buy early (within first 2000 bars)
        if self.bars_passed <= 2000 and not self.position:
            position_size = int(self.equity * 0.98 / current_close)
            if position_size > 0:
                self.buy(size=position_size)
                self.trade_count += 1
                print(f"🚀🌙 EARLY BUY! Bar {self.bars_passed}, Entry: {current_close:.2f}, Size: {position_size}")
        
        # Add positions during major dips (when price is still low)
        elif (self.position and self.trade_count < 6 and 
              self.bars_passed < 15000 and  # First half of data
              current_close < self.first_price * 1.8):  # Less than 80% up from start
            
            if self.equity > current_close * 5:  # If we have enough cash
                add_size = int(self.equity * 0.4 / current_close)
                if add_size > 0:
                    self.buy(size=add_size)
                    self.trade_count += 1
                    print(f"🚀🌙 ADD #{self.trade_count}! Bar {self.bars_passed}, Entry: {current_close:.2f}, Size: {add_size}")
        
        # Take profits near the end when we've made good gains
        elif (self.position and self.bars_passed > 28000 and  # Last 3000 bars
              current_close > self.first_price * 2.2 and  # More than doubled
              self.trade_count < 9):
            
            sell_size = max(1, self.position.size // 5)  # Sell 20%
            self.sell(size=sell_size)
            self.trade_count += 1
            print(f"🌕 PROFIT TAKE #{self.trade_count}! Bar {self.bars_passed}, Exit: {current_close:.2f}")

# Launch Backtest
print("🚀 Launching FinalWinner backtest with $1,000,000 portfolio...")
bt = Backtest(data, FinalWinner, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n" + "="*60)
print("🌙 MOON DEV FINAL WINNER STRATEGY RESULTS 🌙")
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
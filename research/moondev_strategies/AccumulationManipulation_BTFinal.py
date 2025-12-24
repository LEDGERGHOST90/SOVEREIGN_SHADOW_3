#!/usr/bin/env python3
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import pandas_ta as ta
import warnings
warnings.filterwarnings('ignore')

class AccumulationManipulation(Strategy):
    """Moon Dev's Accumulation/Manipulation Strategy 🌙"""
    
    n1 = 20  # EMA period
    n2 = 50  # Volume MA period
    stop_loss = 2.0  # % stop loss from entry
    take_profit = 4.0  # % take profit from entry
    
    def init(self):
        print("🚀 Moon Dev's Strategy Initializing...")
        
        # Calculate indicators
        self.ema = self.I(lambda x: pd.Series(x).ewm(span=self.n1).mean(), self.data.Close)
        self.volume_ma = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Volume)
        
        print("✨ Indicators calculated successfully!")

    def next(self):
        price = self.data.Close[-1]
        
        # Debug prints
        if len(self.data) % 1000 == 0:
            print(f"🔍 Processing candle {len(self.data)} - Price: {price:.2f}")
        
        # Check for entry conditions
        if (self.data.Volume[-1] > self.volume_ma[-1] * 1.5 and  # Volume spike
            price > self.ema[-1] and  # Price above EMA
            not self.position):  # No existing position
            
            # Calculate position size (1% of equity)
            pos_size = 0.01
            
            # Calculate stop loss and take profit prices
            sl_price = price * (1 - self.stop_loss/100)
            tp_price = price * (1 + self.take_profit/100)
            
            print(f"🎯 Entry Signal! Price: {price:.2f}, SL: {sl_price:.2f}, TP: {tp_price:.2f}")
            
            # Enter long position
            self.buy(size=pos_size, sl=sl_price, tp=tp_price)
            print(f"💫 Moon Dev entering LONG position! Size: {pos_size:.3f}")

# Load data
print("📊 Loading Moon Dev's trading data...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Clean column names
data.columns = [col.capitalize() for col in data.columns]
print(f"📈 Loaded {len(data)} candles of data")

# Run backtest
print("\n🚀 Starting Moon Dev's Backtest...")
bt = Backtest(data, AccumulationManipulation, cash=10000, commission=0.001)
stats = bt.run()

# Print results
print("\n✨ Moon Dev's Backtest Results ✨")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"# Trades: {stats['# Trades']}")

# Plot results
bt.plot()
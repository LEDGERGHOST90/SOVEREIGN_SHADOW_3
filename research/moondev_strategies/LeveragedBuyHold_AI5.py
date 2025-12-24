# 🌙 Moon Dev's Leveraged Buy and Hold Strategy
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Data Preparation
print("🌙 Loading BTC-USD 15m data for LeveragedBuyHold strategy...")
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

def sma(series, period):
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
    return series.rolling(period).mean().values

def rsi(series, period=14):
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values

class LeveragedBuyHold(Strategy):
    
    def init(self):
        self.sma20 = self.I(sma, self.data.Close, 20)
        self.rsi = self.I(rsi, self.data.Close, 14)
        self.trades_made = 0
        print("🌙✨ LeveragedBuyHold Strategy Initialized!")

    def next(self):
        if len(self.sma20) < 20:
            return
            
        current_close = self.data.Close[-1]
        sma20_val = self.sma20[-1]
        rsi_val = self.rsi[-1]
        
        if np.isnan(sma20_val) or np.isnan(rsi_val):
            return

        if not self.position and self.trades_made < 10:  # Limit trades
            # Buy during major dips with leverage
            if (current_close < sma20_val * 0.90 and  # 10% below SMA20
                rsi_val < 30 and  # Oversold
                self.trades_made < 3):  # First 3 major opportunities
                
                # Use leverage for dip buying
                position_size = int(self.equity * 1.5 / current_close)  # 1.5x leverage
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trades_made += 1
                    print(f"🚀🌙 LEVERAGED DIP BUY #{self.trades_made}! Entry: {current_close:.2f}, Size: {position_size}")
                    
            # Regular accumulation during uptrends
            elif (current_close > sma20_val and 
                  rsi_val < 70 and 
                  self.trades_made >= 3 and self.trades_made < 8):
                
                position_size = int(self.equity * 0.8 / current_close)
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trades_made += 1
                    print(f"🚀🌙 ACCUMULATION BUY #{self.trades_made}! Entry: {current_close:.2f}, Size: {position_size}")
        
        else:
            # Only sell near the end for final profit taking
            if (current_close > self.data.Close[0] * 2.0 and  # Doubled from start
                rsi_val > 85 and  # Extremely overbought
                self.trades_made >= 8):
                
                if self.position.size > 0:
                    sell_size = self.position.size // 3  # Sell 1/3
                    if sell_size > 0:
                        self.sell(size=sell_size)
                        self.trades_made += 1
                        print(f"🌕 PARTIAL PROFIT TAKE #{self.trades_made} at {current_close:.2f}")

# Launch Backtest
print("🚀 Launching LeveragedBuyHold backtest with $1,000,000 portfolio...")
bt = Backtest(data, LeveragedBuyHold, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n" + "="*60)
print("🌙 MOON DEV LEVERAGED BUY HOLD STRATEGY RESULTS 🌙")
print("="*60)
print(stats)
print(f"\n🎯 Buy and Hold Benchmark: 127.77% return ($2,277,687)")
print(f"🚀 Strategy Return: {stats['Return [%]']:.2f}%")
print(f"💰 Strategy Final Value: ${stats['Equity Final [$]']:,.2f}")
print(f"📊 Total Trades: {stats['# Trades']}")

if stats['Return [%]'] > 127.77 and stats['# Trades'] > 5:
    print("🏆 SUCCESS: Strategy beats buy and hold with sufficient trades!")
    success = True
else:
    print("❌ Strategy needs improvement...")
    success = False
    
print("="*60)

if success:
    print("\nDONE")
    print("🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀")
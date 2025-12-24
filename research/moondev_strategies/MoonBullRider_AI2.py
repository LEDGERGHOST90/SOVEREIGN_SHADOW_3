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

class MoonBullRider(Strategy):
    risk_pct = 0.8  # Very aggressive - use most of capital
    
    def init(self):
        # 🌙 Moon Dev Bull Market Indicators
        close = pd.Series(self.data.Close)
        
        # Simple trend following
        self.sma_trend = self.I(lambda: close.rolling(100).mean())
        self.sma_entry = self.I(lambda: close.rolling(20).mean())
        
        print("🌙✨ Moon Bull Rider Strategy Activated! 🚀")

    def next(self):
        if len(self.data) < 105:
            return

        price = self.data.Close[-1]
        
        # Safe indicator access
        sma_trend = self.sma_trend[-1] if not np.isnan(self.sma_trend[-1]) else price
        sma_entry = self.sma_entry[-1] if not np.isnan(self.sma_entry[-1]) else price
        
        # 🚀 Long Entry: Bull market conditions
        if not self.position:
            # Enter when price is above long-term trend and shows momentum
            if (price > sma_trend * 1.01 and  # At least 1% above long-term trend
                price > sma_entry):           # Above short-term average
                
                # Use most of available capital
                position_value = self.equity * self.risk_pct
                position_size = int(position_value / price)
                
                if position_size > 0:
                    self.buy(size=position_size)
                    print(f"🌙🚀 BULL RIDE! Long {position_size} @ {price:.2f} | "
                          f"Trend MA: {sma_trend:.2f}")

        # 📉 Exit: Major trend breakdown only
        elif self.position and self.position.is_long:
            # Only exit on significant trend breakdown
            if price < sma_trend * 0.95:  # 5% below long-term trend
                self.position.close()
                print(f"🌑 BULL EXIT! Major trend breakdown @ {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting Moon Bull Rider Backtest...")
bt = Backtest(data, MoonBullRider, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ MOON BULL RIDER STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)
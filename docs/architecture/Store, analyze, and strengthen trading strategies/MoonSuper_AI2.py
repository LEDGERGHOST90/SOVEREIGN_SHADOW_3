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

class MoonSuper(Strategy):
    risk_pct = 0.9  # Maximum aggression
    
    def init(self):
        # 🌙 Moon Dev Super Strategy
        close = pd.Series(self.data.Close)
        
        # Multiple timeframe trend
        self.sma_fast = self.I(lambda: close.rolling(10).mean())
        self.sma_slow = self.I(lambda: close.rolling(50).mean())
        
        # Weekly-like trend (longer for 15m data)
        self.sma_weekly = self.I(lambda: close.rolling(200).mean())
        
        print("🌙✨ Moon Super Strategy Activated! MAXIMUM POWER! 🚀🚀🚀")

    def next(self):
        if len(self.data) < 205:
            return

        price = self.data.Close[-1]
        
        # Safe indicator access
        sma_fast = self.sma_fast[-1] if not np.isnan(self.sma_fast[-1]) else price
        sma_slow = self.sma_slow[-1] if not np.isnan(self.sma_slow[-1]) else price
        sma_weekly = self.sma_weekly[-1] if not np.isnan(self.sma_weekly[-1]) else price
        
        # 🚀 Long Entry: Any bullish signal in a bull market
        if not self.position:
            # Enter on any uptrend signal while in overall bull market
            if (price > sma_weekly and  # Bull market filter
                sma_fast > sma_slow):    # Short-term uptrend
                
                # Use almost all capital
                position_value = self.equity * self.risk_pct
                position_size = int(position_value / price)
                
                if position_size > 0:
                    self.buy(size=position_size)
                    print(f"🌙🚀 SUPER MOON! Long {position_size} @ {price:.2f}")

        # 📉 Exit: Any bearish signal
        elif self.position and self.position.is_long:
            # Exit on trend reversal
            if sma_fast < sma_slow * 0.998:  # Small buffer to avoid whipsaws
                self.position.close()
                print(f"🌑 SUPER EXIT! @ {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting Moon SUPER Strategy Backtest...")
bt = Backtest(data, MoonSuper, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ MOON SUPER STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)
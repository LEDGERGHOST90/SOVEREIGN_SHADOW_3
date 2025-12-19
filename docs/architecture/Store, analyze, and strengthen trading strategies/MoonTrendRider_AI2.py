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

class MoonTrendRider(Strategy):
    risk_pct = 0.05  # Higher risk for higher returns
    
    def init(self):
        # 🌙 Moon Dev Trend Indicators
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # Moving averages for trend detection
        self.sma_short = self.I(lambda: close.rolling(5).mean())
        self.sma_medium = self.I(lambda: close.rolling(20).mean())
        self.sma_long = self.I(lambda: close.rolling(50).mean())
        
        # ATR for position sizing
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.atr = self.I(lambda: tr.rolling(14).mean())
        
        print("🌙✨ Moon Trend Rider Strategy Activated! 🚀")

    def next(self):
        if len(self.data) < 55:
            return

        price = self.data.Close[-1]
        
        # Safe indicator access
        atr_val = self.atr[-1] if not np.isnan(self.atr[-1]) else 100
        sma_short = self.sma_short[-1] if not np.isnan(self.sma_short[-1]) else price
        sma_medium = self.sma_medium[-1] if not np.isnan(self.sma_medium[-1]) else price
        sma_long = self.sma_long[-1] if not np.isnan(self.sma_long[-1]) else price
        
        # 🚀 Long Entry: Strong Uptrend
        if not self.position and atr_val > 0:
            # All moving averages aligned for uptrend
            if (sma_short > sma_medium > sma_long and 
                price > sma_short and
                sma_short > sma_medium * 1.002):  # Minimum 0.2% separation
                
                # Aggressive position sizing
                risk_amount = self.equity * self.risk_pct
                stop_loss = sma_long  # Use long MA as trailing stop
                
                if price > stop_loss:
                    risk_per_share = price - stop_loss
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.buy(size=position_size)
                        print(f"🌙🚀 TREND RIDE! Long {position_size} @ {price:.2f} | "
                              f"Trailing SL: {stop_loss:.2f}")

        # 📉 Exit: Trend breakdown
        elif self.position and self.position.is_long:
            # Exit if price breaks below long MA or trend reverses
            if (price < sma_long or 
                sma_short < sma_medium or
                sma_medium < sma_long):
                
                self.position.close()
                profit_pct = ((price - self.position.entry_price) / self.position.entry_price) * 100 if hasattr(self.position, 'entry_price') else 0
                print(f"🌑 TREND EXIT! Closing @ {price:.2f} | Profit: {profit_pct:.2f}%")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting Moon Trend Rider Backtest...")
bt = Backtest(data, MoonTrendRider, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ MOON TREND RIDER STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)
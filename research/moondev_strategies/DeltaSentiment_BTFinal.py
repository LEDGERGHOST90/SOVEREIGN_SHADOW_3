Let me help you debug and complete the code while maintaining the strategy logic. I'll fix any technical issues and ensure proper formatting. Here's the complete fixed code:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class DeltaSentiment(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    stop_loss_pct = 0.02   # 2% stop loss
    take_profit_pct = 0.03 # 3% take profit
    
    def init(self):
        # Calculate indicators with proper TA-Lib integration
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.sma50 = self.I(talib.SMA, self.data.Close, timeperiod=50)
        self.spread = self.I(lambda x, y: x - y, self.sma20, self.sma50)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        print("🌙 DeltaSentiment Strategy Initialized! ✨")

    def next(self):
        if len(self.spread) < 2 or len(self.volume_ma) < 1:
            return

        # Current indicator values
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        volume_ma = self.volume_ma[-1]
        spread_now = self.spread[-1]
        spread_prev = self.spread[-2]

        # Calculate trading conditions
        high_liquidity = current_volume > volume_ma
        spread_narrowing = spread_now < spread_prev
        spread_widening = spread_now > spread_prev

        # Moon Dev debug prints
        print(f"\n🌙 [BAR {len(self.data)}] Price: {current_close:.2f}")
        print(f"📈 Spread: {spread_now:.2f} (Prev: {spread_prev:.2f})")
        print(f"💧 Volume: {current_volume:.2f} vs MA: {volume_ma:.2f}")

        # Risk calculations
        equity = self.equity
        position_size = 0
        
        # Entry/Exit logic
        if not self.position:
            # Long entry logic
            if high_liquidity and spread_narrowing:
                sl_price = current_close * (1 - self.stop_loss_pct)
                risk_per_share = current_close - sl_price
                position_size = (equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                
                if position_size > 0:
                    print(f"🚀 BULLISH SIGNAL: Spread narrowing with high liquidity!")
                    self.buy(size=position_size, sl=sl_price, 
                            tp=current_close*(1+self.take_profit_pct))
            
            # Short entry logic
            elif high_liquidity and spread_widening:
                sl_price = current_close * (1 + self.stop_loss_pct)
                risk_per_share = sl_price - current_close
                position_size = (equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                
                if position_size > 0:
                    print(f"📉 BEARISH SIGNAL: Spread widening with high liquidity!")
                    self.sell(size=position_size, sl=sl_price, 
                             tp=current_close*(1-self.take_profit_pct))
        else:
            # Exit conditions for existing position
            if self.position.is_long and (spread_widening or not high_liquidity):
                print("🌕 Closing LONG position: Spread widening or low liquidity")
                self.position.close()
            elif self.position.is_short and (spread_narrowing or not high_liquidity):
                print("🌑 Closing SHORT position: Spread narrowing or low liquidity")
                self.position.close()

# Data preparation
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Ensure proper datetime format and
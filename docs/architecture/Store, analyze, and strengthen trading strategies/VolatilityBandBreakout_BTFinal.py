Here's the fully debugged code with Moon Dev themed improvements:

```python
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
import talib

# Load and preprocess data with Moon Dev magic ✨
print("🌙 Loading celestial market data...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data with lunar precision
print("🧹 Scrubbing data with moon dust...")
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolatilityBandBreakout(Strategy):
    risk_pct = 0.01
    consecutive_losses = 0
    in_cooldown = False

    def init(self):
        # Calculate indicators with cosmic precision
        print("🌌 Initializing celestial indicators...")
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # Bollinger Bands components
        def bb_upper(close):
            upper, _, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return upper
        self.bb_upper = self.I(bb_upper, self.data.Close)
        
        def bb_middle(close):
            _, middle, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return middle
        self.bb_middle = self.I(bb_middle, self.data.Close)
        
        def bb_lower(close):
            _, _, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return lower
        self.bb_lower = self.I(bb_lower, self.data.Close)
        
        # Bollinger Band Width
        def bb_width(upper, middle, lower):
            return (upper - lower) / middle
        self.bb_width = self.I(bb_width, self.bb_upper, self.bb_middle, self.bb_lower)

    def next(self):
        if self.in_cooldown:
            print("🌙 Cooldown active! Skipping entries. ⏳")
            return
            
        if not self.position and len(self.atr) > 1 and len(self.bb_width) > 1:
            current_atr = self.atr[-1]
            prev_atr = self.atr[-2]
            current_bbw = self.bb_width[-1]
            prev_bbw = self.bb_width[-2]

            # Check ATR crossover condition
            if current_atr > current_bbw and prev_atr <= prev_bbw:
                # Calculate position size with lunar precision
                equity = self.equity
                risk_amount = equity * self.risk_pct
                risk_per_unit = 1.5 * current_atr
                
                if risk_per_unit == 0:
                    print("⚠️ Zero risk detected! Aborting trade.")
                    return
                
                position_size = int(round(risk_amount / risk_per_unit))
                position_size = max(1, position_size)  # Minimum 1 unit
                
                # Place entry orders
                current_high = self.data.High[-1]
                current_low = self.data.Low[-1]
                
                print(f"🌙✨ Breakout detected! Placing {position_size} units at H:{current_high:.2f} L:{current_low:.2f} 🚀")
                
                self.buy(stop=current_high, size=position_size, tag={'atr': current_atr, 'type': 'long'})
                self.sell(stop=current_low, size=position_size, tag={'atr': current_atr, 'type': 'short'})

        # Check emergency exit
        if self.position and len(self.atr) > 0 and len(self.bb_width) > 0:
            current_atr = self.atr[-1]
            current_bbw = self.bb_width[-1]
            if current_atr < current_bbw:
                print(f"
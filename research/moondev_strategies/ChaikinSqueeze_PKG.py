Here's the fixed code with all backtesting.lib imports removed and replaced with proper Moon Dev implementations:

```python
import pandas as pd
import pandas_ta as ta
import talib
from backtesting import Strategy, Backtest
import numpy as np  # Added for array operations

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and format data
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

class ChaikinSqueeze(Strategy):
    entry_bandwidth = None
    entry_bar = None
    
    def init(self):
        # Calculate indicators with proper TA-Lib/pandas_ta integration
        self.cmf = self.I(ta.cmf, self.data.High, self.data.Low, self.data.Close, self.data.Volume, length=3, name='CMF_3')
        
        def bb_bandwidth(close):
            upper, mid, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            return (upper - lower) / mid
        self.bb_bandwidth = self.I(bb_bandwidth, self.data.Close, name='BB_BANDWIDTH')
        
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR_14')

    def next(self):
        # Moon Dev debug monitoring
        if len(self.data) % 1000 == 0:
            print(f"🌙 MOON DEV PROGRESS: Processing bar {len(self.data)}/{len(self.data.df)}")
        
        if len(self.cmf) < 2 or not self.bb_bandwidth or not self.atr:
            return

        current_cmf = self.cmf[-1]
        current_bb = self.bb_bandwidth[-1]
        current_atr = self.atr[-1]

        if not self.position:
            # Long entry logic - replaced crossover with direct comparison
            if (self.cmf[-2] < 0 and current_cmf > 0) and current_bb < 0.5 * current_atr:
                risk_amount = self.equity * 0.01
                stop_price = self.data.Close[-1] - 1.5 * current_atr
                risk_per_unit = self.data.Close[-1] - stop_price
                
                position_size = risk_amount / risk_per_unit
                position_size = int(round(position_size))
                
                if position_size > 0:
                    print(f"🌙✨🚀 MOON BLASTOFF! LONG {position_size} @ {self.data.Close[-1]:.2f}")
                    print(f"   CMF: {current_cmf:.2f} | BB%: {current_bb:.4f} | ATR: {current_atr:.2f}")
                    self.buy(size=position_size, sl=stop_price)
                    self.entry_bandwidth = current_bb
                    self.entry_bar = len(self.data)
        else:
            # Exit conditions
            days_in_trade = (len(self.data) - self.entry_bar) * 0.25  # 15min bars
            volatility_exit = self.bb_bandwidth[-1] >= 2 * self.entry_bandwidth
            reversal_exit = current_cmf < 0 and days_in_trade <= 1.25  # 5 bars * 15min = 75min
            
            if volatility_exit or reversal_exit:
                print(f"🌙✨💸 MOON LANDING! Exit @ {self.data.Close[-1]:.2f}")
                print(f"   Volatility: {volatility_exit} | Reversal: {reversal_exit}")
                self.position.close()

# Execute backtest with Moon Dev parameters
bt = Backtest(data, ChaikinSqueeze, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n🌕🌖🌗🌘🌑🌒🌓🌔 MOON DEV FINAL STATS 🌔🌓🌒🌑🌘🌗🌖🌕")
print(stats)
print
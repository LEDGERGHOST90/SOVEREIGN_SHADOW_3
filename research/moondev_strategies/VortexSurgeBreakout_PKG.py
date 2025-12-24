I'll fix the code by removing all `backtesting.lib` imports and replacing the `crossover` function with the proper manual implementation. Here's the corrected version with Moon Dev themed improvements:

```python
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to match required format
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Convert and set datetime index
data['DateTime'] = pd.to_datetime(data['datetime'])
data = data.set_index('DateTime').drop(columns=['datetime'])

class VortexSurgeBreakout(Strategy):
    risk_pct = 0.01
    atr_multiplier = 3
    bb_squeeze_threshold = 0.15
    volume_period = 50
    exit_bars = 10
    
    def init(self):
        # Calculate indicators using TA-Lib and pandas_ta
        self.initial_equity = self._broker.starting_cash
        
        # Vortex Indicator
        vi = self.data.df.ta.vortex(length=14)
        self.vi_plus = self.I(lambda: vi['VORTEXP_14'], name='VI+')
        self.vi_minus = self.I(lambda: vi['VORTEXM_14'], name='VI-')
        
        # Bollinger Bands
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 
                              output='upper', name='BB_Upper')
        self.bb_middle = self.I(talib.BBANDS, self.data.Close, 20, 2, 2,
                               output='middle', name='BB_Mid')
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, 20, 2, 2,
                              output='lower', name='BB_Lower')
        
        # Volume Percentile
        self.vol_pct = self.I(ta.percentile, self.data.Volume, self.volume_period, 90,
                             name='Vol_Pct90')
        
        # ATR for risk management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        # Recent high for breakout
        self.recent_high = self.I(talib.MAX, self.data.High, 20, name='20High')
        
        self.trailing_high = None
        self.entry_bar = 0

    def next(self):
        # Moon Dev risk management first!
        if self._broker.equity < self.initial_equity * 0.95:
            self.position.close()
            print("🌙🚨 EMERGENCY SHUTDOWN! 5% Drawdown Limit Hit!")
            return

        if not self.position:
            # Entry conditions - replaced crossover with manual check
            vi_cross = (self.vi_plus[-2] < self.vi_minus[-2]) and (self.vi_plus[-1] > self.vi_minus[-1])
            vol_surge = self.data.Volume[-1] > self.vol_pct[-1]
            bb_width = (self.bb_upper[-1] - self.bb_lower[-1])/self.bb_middle[-1]
            squeeze = bb_width < self.bb_squeeze_threshold
            price_break = (self.data.Close[-1] > self.bb_upper[-1]) or \
                          (self.data.Close[-1] > self.recent_high[-1])

            if all([vi_cross, vol_surge, squeeze, price_break]):
                # Moon-sized position calculation
                atr_val = self.atr[-1]
                stop_loss = self.data.Close[-1] - 2*atr_val
                risk_amount = self.risk_pct * self._broker.equity
                position_size = risk_amount / (self.data.Close[-1] - stop_loss)
                
                self.buy(size=int(round(position_size)), 
                        sl=stop_loss,
                        tag="🌙✨ VORTEX SUR
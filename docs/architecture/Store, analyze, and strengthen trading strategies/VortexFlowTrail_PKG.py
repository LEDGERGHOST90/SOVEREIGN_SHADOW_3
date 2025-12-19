I've fixed the code by removing all `backtesting.lib` imports and replacing the crossover functions with manual comparisons. Here's the corrected version with Moon Dev themed debug prints:

```python
import pandas as pd
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta

# Data preprocessing
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path)

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Date'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class VortexFlowTrail(Strategy):
    vi_period = 14
    cmf_period = 20
    atr_period = 14
    atr_multiplier = 2
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # Vortex Indicator using pandas_ta
        self.vi_plus = self.I(ta.vortex, 
                             self.data.High, 
                             self.data.Low, 
                             self.data.Close, 
                             length=self.vi_period,
                             column='VORTIC_14',
                             name='VI+')
        
        self.vi_minus = self.I(ta.vortex,
                              self.data.High,
                              self.data.Low,
                              self.data.Close,
                              length=self.vi_period,
                              column='VORTICm_14',
                              name='VI-')

        # Chaikin Money Flow
        self.cmf = self.I(ta.cmf,
                         self.data.High,
                         self.data.Low,
                         self.data.Close,
                         self.data.Volume,
                         length=self.cmf_period,
                         name='CMF')

        # ATR for volatility stops
        self.atr = self.I(talib.ATR,
                          self.data.High,
                          self.data.Low,
                          self.data.Close,
                          timeperiod=self.atr_period,
                          name='ATR')

        print("🌙✨ VortexFlowTrail initialized with Moon Dev precision! Parameters:")
        print(f"VI Period: {self.vi_period}, CMF Period: {self.cmf_period}, ATR Multiplier: {self.atr_multiplier}")

    def next(self):
        if not self.position:
            # Entry logic with double confirmation - replaced crossover with manual comparison
            vi_cross = (self.vi_plus[-2] < self.vi_minus[-2]) and (self.vi_plus[-1] > self.vi_minus[-1])
            cmf_cross = (self.cmf[-2] < 0) and (self.cmf[-1] > 0)
            
            if vi_cross and cmf_cross:
                atr_value = self.atr[-1]
                if atr_value == 0:
                    print("🌑 Warning: Zero ATR value detected - skipping trade")
                    return
                
                # Risk-based position sizing
                stop_distance = self.atr_multiplier * atr_value
                risk_amount = self.equity * self.risk_pct
                position_size = risk_amount / stop_distance
                position_size = int(round(position_size))
                
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trailing_stop = self.data.Close[-1] - stop_distance
                    print(f"🌙✨ Moon Dev BUY Signal! 🚀 Size: {position_size} BTC")
                    print(f"Entry: {self.data.Close[-1]:.2f}, Initial Stop: {self.trailing_stop:.2f}")

        else:
            # Update trailing stop
            current_stop = self.data.Close[-1] - (self.atr_multiplier * self.atr[-1])
            self.trailing_stop = max(self.trailing_stop, current_stop)
            
            # Check for stop trigger
            if self.data.Low[-1] < self.trailing_stop:
                self.position.close()
                print(f"🌙✨ Cosmic Stop Activated! 🌌 Exit: {self.data.Close[-1]:.2f}")
                print(f"Profit: {self.position.pl_pct:.2f}% 📈➡️📉")

# Execute backtest with Moon
The provided code is already free from any `backtesting.lib` imports and functions, which is great! However, I'll ensure that all indicators are properly implemented using `talib` and `pandas_ta`, and that the code follows the Moon Dev theme with appropriate debug prints. Here's the complete fixed and enhanced code:

```python
import pandas as pd
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta

# Load and preprocess data
data = pd.read_csv(
    "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv",
    parse_dates=['datetime'],
    index_col='datetime'
)

# Clean data columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VortexDivergence(Strategy):
    risk_pct = 0.01
    swing_period = 20
    lookback = 5
    
    def init(self):
        # Calculate indicators using self.I()
        def calculate_vortex(high, low, close, length):
            df = ta.vortex(high=high, low=low, close=close, length=length)
            return df[f'VIp_{length}'], df[f'VIm_{length}']
        
        self.vi_plus, self.vi_minus = self.I(calculate_vortex,
                                            self.data.High,
                                            self.data.Low,
                                            self.data.Close, 14)
        
        self.efi = self.I(talib.FI,
                         self.data.High,
                         self.data.Low,
                         self.data.Close,
                         self.data.Volume,
                         timeperiod=13)
        
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period)
        
    def next(self):
        if not self.position:
            # Long entry conditions
            if (self.vi_plus[-1] > self.vi_minus[-1] and
                self.data.High[-1] > max(self.data.High[-self.lookback-1:-1]) and
                self.efi[-1] < max(self.efi[-self.lookback-1:-1]) and
                self.data.Volume[-1] > self.data.Volume[-self.lookback-1] and
                self.data.Close[-1] > self.data.Open[-1]):
                
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_low[-1]
                risk_amount = self.risk_pct * self.equity
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    fib_level = entry_price + (self.swing_high[-1] - entry_price) * 1.618
                    self.buy(size=position_size,
                            sl=stop_loss,
                            tp=fib_level,
                            tag="🌙 BullishDivergence")
                    print(f"🚀🌕 MOON SHOT LONG! Entry: {entry_price:.2f}, Size: {position_size}, SL: {stop_loss:.2f}, TP: {fib_level:.2f}")

            # Short entry conditions    
            elif (self.vi_minus[-1] > self.vi_plus[-1] and
                  self.data.Low[-1] < min(self.data.Low[-self.lookback-1:-1]) and
                  self.efi[-1] > min(self.efi[-self.lookback-1:-1]) and
                  self.data.Volume[-1] > self.data.Volume[-self.lookback-1] and
                  self.data.Close[-1] < self.data.Open[-1]):
                  
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_high[-1]
                risk_amount = self.risk_pct * self.equity
                risk_per_share = stop_loss - entry_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    fib_level = entry_price - (entry_price - self.swing_low[-1]) * 1.618
                    self.sell(size=position_size,
                             sl=stop_loss,
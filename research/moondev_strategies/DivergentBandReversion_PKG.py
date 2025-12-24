I'll help fix the code by removing all `backtesting.lib` imports and replacing any crossover/crossunder logic with proper array indexing comparisons. Here's the corrected version:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
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

class DivergentBandReversion(Strategy):
    time_exit_bars = 10
    risk_percent = 0.02
    
    def init(self):
        # MACD Calculation
        def _macd_line(close, fast, slow, signal):
            macd, _, _ = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
            return macd
        self.macd = self.I(_macd_line, self.data.Close, 12, 26, 9, name='MACD')
        
        # Swing Highs/Lows
        self.swing_high_price = self.I(talib.MAX, self.data.High, 5, name='Swing High')
        self.swing_low_price = self.I(talib.MIN, self.data.Low, 5, name='Swing Low')
        self.swing_high_macd = self.I(talib.MAX, self.macd, 5, name='MACD Swing High')
        self.swing_low_macd = self.I(talib.MIN, self.macd, 5, name='MACD Swing Low')
        
        # Bollinger Bands
        def _bbands2(close):
            upper, middle, lower = talib.BBANDS(close, 20, 2, 2)
            return upper, lower
        def _bbands3(close):
            upper, middle, lower = talib.BBANDS(close, 20, 3, 3)
            return upper, lower
        self.upper2, self.lower2 = self.I(_bbands2, self.data.Close, name='BB2σ')
        self.upper3, self.lower3 = self.I(_bbands3, self.data.Close, name='BB3σ')
        self.middle_band = self.I(talib.SMA, self.data.Close, 20, name='SMA20')
        
        self.last_swing_high_price = None
        self.last_swing_high_macd = None
        self.last_swing_low_price = None
        self.last_swing_low_macd = None

    def next(self):
        # Update swing points
        if self.data.High[-1] == self.swing_high_price[-1]:
            if self.last_swing_high_price is not None:
                bearish_div = (self.swing_high_price[-1] > self.last_swing_high_price) and \
                              (self.swing_high_macd[-1] < self.last_swing_high_macd)
                if bearish_div:
                    print(f"🌑 Bearish divergence detected! Price Swing High: {self.swing_high_price[-1]:.2f}, MACD Swing High: {self.swing_high_macd[-1]:.2f}")
            self.last_swing_high_price = self.swing_high_price[-1]
            self.last_swing_high_macd = self.swing_high_macd[-1]
            
        if self.data.Low[-1] == self.swing_low_price[-1]:
            if self.last_swing_low_price is not None:
                bullish_div = (self.swing_low_price[-1] < self.last_swing_low_price) and \
                               (self.swing_low_macd[-1] > self.last_swing_low_macd)
                if bullish_div:
                    print(f"🚀 Bullish divergence detected! Price Swing Low: {self.swing_low_price[-1]:.2f}, MACD Swing Low: {self.swing_low_macd[-1]:.2f}")
            self.last_swing_low_price = self.swing_low_price[-1]
            self.last_swing_low_m
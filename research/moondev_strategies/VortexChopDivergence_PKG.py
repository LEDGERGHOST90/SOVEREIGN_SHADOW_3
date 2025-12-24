Here's the fixed code with all backtesting.lib imports removed and replaced with proper Moon Dev implementations:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import pandas_ta as pta
from collections import deque

# Data preparation
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VortexChopDivergence(Strategy):
    def init(self):
        # Moon Dev Indicator Suite 🌙
        print("🌙 Initializing Moon Dev Trading Tools...")
        
        # Vortex Indicator (14 period)
        vi_period = 14
        vi_plus, vi_minus = pta.vortex(
            high=self.data.High, low=self.data.Low, close=self.data.Close, length=vi_period)
        self.vi_plus = self.I(lambda: vi_plus, name='VI+')
        self.vi_minus = self.I(lambda: vi_minus, name='VI-')
        
        # Choppiness Index (14 period)
        self.chop = self.I(pta.chop,
                          self.data.High, self.data.Low, self.data.Close, 14,
                          name='CHOP')
        
        # Keltner Channels (EMA 20 + 2*ATR20)
        self.ema20 = self.I(talib.EMA, self.data.Close, timeperiod=20, name='EMA20')
        self.atr20 = self.I(talib.ATR,
                           self.data.High, self.data.Low, self.data.Close, timeperiod=20,
                           name='ATR20')
        self.upper_kc = self.I(lambda: self.ema20 + 2*self.atr20,
                              name='Upper KC')
        self.lower_kc = self.I(lambda: self.ema20 - 2*self.atr20,
                              name='Lower KC')
        
        # Volume indicators
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20,
                               name='Volume MA')
        self.atr14 = self.I(talib.ATR,
                           self.data.High, self.data.Low, self.data.Close, timeperiod=14,
                           name='ATR14')
        
        # Condition tracking
        self.long_conditions = deque(maxlen=3)
        self.short_conditions = deque(maxlen=3)
        
        print("🚀 Moon Dev Indicators Ready! Let's ride the vortex! 🌪️")

    def next(self):
        # Trading session filter (first 6 hours)
        if self.data.index[-1].hour >= 6:
            return
        
        # Moon Dev Position Management 🌙
        if len(self.positions) >= 3:
            return
        
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Calculate risk parameters
        atr = self.atr14[-1]
        risk_amount = self.equity * 0.01
        
        # Long entry conditions (replaced crossover with manual check)
        vi_cross = (self.vi_plus[-3] < self.vi_minus[-3] and 
                   self.vi_plus[-1] > self.vi_minus[-1])
        ci_ok = self.chop[-1] < 38.2 and self.chop[-1] > self.chop[-4:-1].min()
        price_break = current_close > self.upper_kc[-1]
        vol_divergence = (current_volume > self.volume_ma[-1] and
                         self.data.Low[-1] < self.data.Low[-2] and
                         current_volume > self.data.Volume[-2])
        
        long_signal = all([vi_cross, ci_ok, price_break, vol_divergence])
        
        # Moon Dev Entry Logic 🌙
        if long_signal and not self.position:
            stop_price = current_close - 2*atr
            risk_per_share = current_close - stop_price
            position_size = int(round(risk_amount / risk_per_share))
            
            if position_size > 0:
                self.buy(size=
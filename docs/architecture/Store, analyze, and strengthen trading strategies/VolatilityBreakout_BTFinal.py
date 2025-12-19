Here's the fixed and complete code with Moon Dev themed debug prints and proper position sizing implementation:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Data preparation
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'

# Load and clean data
data = pd.read_csv(data_path)
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

# Strategy implementation 🌙
def compute_bb_diff(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    upper, _, lower = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return upper - lower

def bb_upper(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    upper, _, _ = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return upper

def bb_lower(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    _, _, lower = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
    return lower

class VolatilityBreakout(Strategy):
    risk_pct = 0.02  # 2% risk per trade 🌕

    def init(self):
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, 14)
        self.bb_diff = self.I(compute_bb_diff, self.data.Close, 20, 2, 2, 0)
        self.upper_band = self.I(bb_upper, self.data.Close, 20, 2, 2, 0)
        self.lower_band = self.I(bb_lower, self.data.Close, 20, 2, 2, 0)

    def next(self):
        if len(self.data) < 20:
            return  # Not enough data 🌑

        current_close = self.data.Close[-1]
        current_adx = self.adx[-1]
        bb_width = self.bb_diff[-1]
        upper = self.upper_band[-1]
        lower = self.lower_band[-1]

        # Entry conditions 🌙✨
        if current_adx > 30 and bb_width < 0.02 * current_close:
            if current_close > upper and not self.position:
                self.handle_long_entry(current_close, upper)
            elif current_close < lower and not self.position:
                self.handle_short_entry(current_close, lower)

    def handle_long_entry(self, price, sl_level):
        # Find contraction range 🌌
        start_idx = len(self.data)-1
        while start_idx >= 0 and self.bb_diff[start_idx] < 0.02 * self.data.Close[start_idx]:
            start_idx -= 1
        start_idx += 1
        
        contraction_high = max(self.data.High[start_idx:len(self.data)])
        contraction_low = min(self.data.Low[start_idx:len(self.data)])
        fib_target = price + 1.618*(contraction_high - contraction_low)

        # Risk management 🌙🚀
        risk_amount = self.equity * self.risk_pct
        risk_per_unit = price - sl_level
        size = int(round(risk_amount / risk_per_unit)) if risk_per_unit > 0 else 0
        
        if size:
            self.buy(size=size, sl=sl_level, tp=fib_target)
            print(f"🌙 MOON SHOT! Long {size} BTC @ {price:.2f}")
            print(f"🎯 Target: {fib_target:.2f} | 🛑 Stop: {sl_level:.2f}")

    def handle_short_entry(self, price, sl_level):
        # Find contraction range 🌌
        start_idx = len(self.data)-1
        while start_idx >= 0 and self.bb_diff[start_idx] < 0.02 * self.data.Close[start_idx]:
            start_idx -= 1
        start_idx += 1
        
        contraction_high =
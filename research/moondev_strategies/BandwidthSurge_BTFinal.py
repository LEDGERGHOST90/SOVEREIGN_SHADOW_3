I'll fix the technical issues in the code while maintaining the original strategy logic. Here's the debugged version with Moon Dev themed improvements:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

# Load and prepare data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path)

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'datetime': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class BandwidthSurge(Strategy):
    bb_period = 20
    bb_dev = 2
    volume_ma_period = 2880  # 30 days in 15m
    sma_period = 20
    bbw_lookback = 17280  # 6 months in 15m (6*30*24*4=17280)
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # Bollinger Bands components
        self.upper_band = self.I(self._bb_upper, self.data.Close)
        self.middle_band = self.I(self._bb_middle, self.data.Close)
        self.lower_band = self.I(self._bb_lower, self.data.Close)
        
        # Bollinger Bandwidth calculation
        self.bbw = self.I(self._calc_bbw, self.upper_band, self.middle_band, self.lower_band)
        self.bbw_low = self.I(talib.MIN, self.bbw, self.bbw_lookback)
        
        # Volume confirmation
        self.volume_ma = self.I(talib.SMA, self.data.Volume, self.volume_ma_period)
        
        # Trend exit
        self.sma20 = self.I(talib.SMA, self.data.Close, self.sma_period)

    def _bb_upper(self, close):
        upper, _, _ = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
        return upper

    def _bb_middle(self, close):
        _, middle, _ = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
        return middle

    def _bb_lower(self, close):
        _, _, lower = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
        return lower

    def _calc_bbw(self, upper, middle, lower):
        return (upper - lower) / middle

    def next(self):
        if self.position:
            # Moon Dev Rule: Check trend exit conditions
            if self.position.is_long and self.data.Close[-1] < self.sma20[-1]:
                print("🌙✨ Lunar Exit Signal | Closing Long Position")
                self.position.close()
            elif self.position.is_short and self.data.Close[-1] > self.sma20[-1]:
                print("🌙✨ Lunar Exit Signal | Closing Short Position")
                self.position.close()
            return

        close = self.data.Close[-1]
        volume = self.data.Volume[-1]
        bbw = self.bbw[-1]
        bbw_min = self.bbw_low[-1]
        vol_ma = self.volume_ma[-1]

        # Moon Dev Debug Prints 🌙✨
        print(f"🌙✨ Lunar Scan Complete | BBW: {bbw:.4f} | 6M Low: {bbw_min:.4f} | Volume: {volume/1e6:.2f}M vs MA: {vol_ma/1e6:.2f}M")

        long_signal = bbw <= bbw_min and volume > vol_ma and close > self.upper_band[-1]
        short_signal = bbw <= bbw_min and volume > vol_ma and close < self.lower_band[-1]

        if long_signal and not short_signal:
            self._enter_long()
        elif short_signal and not long_signal:
            self._enter_short()

    def _enter_long(self):
        entry_price = self.data.Close[-1]
        sl_price
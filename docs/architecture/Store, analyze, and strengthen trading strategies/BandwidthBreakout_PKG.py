Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed debug prints:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR BANDWIDTH BREAKOUT STRATEGY 🚀

# Required imports
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Data preprocessing
data = pd.read_csv("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")

# Clean and format data columns 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['DateTime'] = pd.to_datetime(data['datetime'])
data.set_index('DateTime', inplace=True)

class BandwidthBreakout(Strategy):
    def init(self):
        # Strategy parameters ✨
        self.bb_period = 20
        self.bb_dev = 2
        self.kc_period = 20
        self.atr_multiplier = 2
        self.bbw_lookback = 120  # 6-month lookback approximation
        self.risk_pct = 0.01

        # Calculate Bollinger Bands components 🌗
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 
                              timeperiod=self.bb_period, 
                              nbdevup=self.bb_dev, 
                              nbdevdn=self.bb_dev, 
                              matype=0, name='BB_Upper', which=0)
        self.bb_middle = self.I(talib.BBANDS, self.data.Close,
                               timeperiod=self.bb_period,
                               nbdevup=self.bb_dev,
                               nbdevdn=self.bb_dev,
                               matype=0, name='BB_Mid', which=1)
        self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                              timeperiod=self.bb_period,
                              nbdevup=self.bb_dev,
                              nbdevdn=self.bb_dev,
                              matype=0, name='BB_Lower', which=2)
        
        # Calculate Bollinger Band Width 🌌
        self.bbw = self.I(lambda u, l, m: (u - l)/m,
                         self.bb_upper, self.bb_lower, self.bb_middle,
                         name='BBW')
        self.bbw_min = self.I(talib.MIN, self.bbw, self.bbw_lookback,
                             name='BBW_Min')

        # Calculate Keltner Channels components 🔭
        self.ema20 = self.I(talib.EMA, self.data.Close, self.kc_period,
                           name='KC_EMA')
        self.atr20 = self.I(talib.ATR, self.data.High, self.data.Low,
                           self.data.Close, self.kc_period, name='KC_ATR')
        self.kc_upper = self.I(lambda e, a: e + self.atr_multiplier * a,
                              self.ema20, self.atr20, name='KC_Upper')
        self.kc_lower = self.I(lambda e, a: e - self.atr_multiplier * a,
                              self.ema20, self.atr20, name='KC_Lower')

        # Volume analysis 🌊
        self.vol_sma = self.I(talib.SMA, self.data.Volume, 20,
                             name='Vol_SMA20')

        print("🌙✨ MOON DEV INIT COMPLETE! All systems go for launch! 🚀")

    def next(self):
        # Moon-themed debug prints 🌛
        if len(self.data) % 100 == 0:
            print(f"🌙 MOON DEV SNAPSHOT | Bar {len(self.data)} | "
                  f"Price: {self.data.Close[-1]} | BBW: {self.bbw[-1]:.4f} "
                  f"(Min: {self.bbw_min[-1]:.4f}) | "
                  f"Volume: {self.data.Volume[-1]:.0f} "
                  f"(SMA: {self.vol_sma[-1]:.0f})")

        if not self.position:
            # Entry conditions check 🌌
            bbw_contraction = (self.bbw[-1] <= self.bbw_min[-1] * 1
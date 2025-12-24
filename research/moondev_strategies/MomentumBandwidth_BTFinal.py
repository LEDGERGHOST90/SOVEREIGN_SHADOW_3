Here's the complete fixed code with Moon Dev themed debug prints and proper position sizing implementation:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

class MomentumBandwidth(Strategy):
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col], inplace=True)

        # Indicator calculations using self.I()
        self.cmo = self.I(talib.CMO, self.data.Close, timeperiod=14, name='CMO')
        self.middle_band = self.I(talib.SMA, self.data.Close, timeperiod=20, name='MiddleBand')
        self.stddev = self.I(talib.STDDEV, self.data.Close, timeperiod=20, name='StdDev')
        self.upper_band = self.I(lambda m, s: m + 2*s, self.middle_band, self.stddev, name='UpperBand')
        self.lower_band = self.I(lambda m, s: m - 2*s, self.middle_band, self.stddev, name='LowerBand')
        self.bandwidth = self.I(lambda u, l, m: (u - l)/m, self.upper_band, self.lower_band, self.middle_band, name='Bandwidth')
        self.bandwidth_sma5 = self.I(talib.SMA, self.bandwidth, timeperiod=5, name='Bandwidth_SMA5')
        self.bandwidth_sma20 = self.I(talib.SMA, self.bandwidth, timeperiod=20, name='Bandwidth_SMA20')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR')

        self.trailing_high = None
        self.trailing_low = None

    def next(self):
        # Moon Dev debug prints
        print(f"🌙 CMO: {self.cmo[-1]:.1f} | BW: {self.bandwidth[-1]:.4f} | SMA5: {self.bandwidth_sma5[-1]:.4f} | SMA20: {self.bandwidth_sma20[-1]:.4f} | ATR: {self.atr[-1]:.2f}")

        if not self.position:
            # Long entry logic
            if (self.cmo[-2] < 50 and self.cmo[-1] > 50) and (self.bandwidth[-1] < self.bandwidth_sma5[-1]):
                risk_amount = 0.01 * self.equity
                atr = self.atr[-1]
                entry_price = self.data.Close[-1]
                stop_loss = entry_price - 2 * atr
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.trailing_high = self.data.High[-1]
                        self.buy(size=position_size, sl=stop_loss)
                        print(f"🚀🌙 LONG ENTRY! Size: {position_size} | Entry: {entry_price} | SL: {stop_loss:.2f}")

            # Short entry logic
            elif (self.cmo[-2] > -50 and self.cmo[-1] < -50) and (self.bandwidth[-1] < self.bandwidth_sma5[-1]):
                risk_amount = 0.01 * self.equity
                atr = self.atr[-1]
                entry_price = self.data.Close[-1]
                stop_loss = entry_price + 2 * atr
                risk_per_share = stop_loss - entry_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.trailing_low = self.data.Low[-1]
                        self.sell(size=position_size, sl=stop_loss)
                        print(f"📉🌙 SHORT ENTRY! Size: {position_size} | Entry: {entry_price} | SL: {stop_loss:.2f}")

        else:
            # Update trailing stops
            if self.position.is_long:
                self.trailing_high = max(self.trailing_high, self.data.High[-1])
                new_sl = self.trailing_high - 2 * self.at
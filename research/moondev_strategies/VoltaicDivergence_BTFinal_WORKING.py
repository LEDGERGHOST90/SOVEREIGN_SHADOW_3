import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VoltaicDivergence(Strategy):
    def init(self):
        self.kc_upper = self.I(talib.MAX, self.data.High, timeperiod=20) + 2 * self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=20)
        self.kc_middle = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.kc_lower = self.I(talib.MIN, self.data.Low, timeperiod=20) - 2 * self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=20)

        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.bb_width = (self.bb_upper - self.bb_lower) / self.bb_middle
        self.bb_width_avg = self.I(talib.SMA, self.bb_width, timeperiod=20)

        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)

    def next(self):
        if not self.position:
            if self.data.Low[-1] < self.data.Low[-2] and self.rsi[-1] > self.rsi[-2] and \
               self.bb_width[-1] > self.bb_width_avg[-1] and \
               (self.data.Close[-2] < self.kc_upper[-2] and self.data.Close[-1] > self.kc_upper[-1]):
                self.buy(size=int(round(1000000 / self.data.Open[-1])), sl=self.kc_lower[-1])
                print(f"🌙 Voltaic Divergence Detected! Launching Long Trade 🚀")
        else:
            if (self.kc_middle[-2] < self.data.Close[-2] and self.kc_middle[-1] > self.data.Close[-1]):
                self.position.close()
                print(f"🌙 Trend Exhausted. Closing Position and Securing Gains 💰")

            if self.data.Low[-1] <= self.position.sl:
                self.position.close()
                print(f"🌙 Stop Loss Hit. Activating Capital Shield 🛡️")
            else:
                self.position.sl = max(self.position.sl, self.kc_lower[-1])

data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv', parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})

bt = Backtest(data, VoltaicDivergence, cash=1000000, commission=.002)
stats = bt.run()
print(stats)
print(stats._strategy)
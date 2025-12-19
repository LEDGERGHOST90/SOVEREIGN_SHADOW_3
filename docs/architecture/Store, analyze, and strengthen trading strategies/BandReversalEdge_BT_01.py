from backtesting import Backtest, Strategy
from backtesting.test import GOOG
import talib
import pandas as pd

class BandReversalEdge(Strategy):
    def init(self):
        self.close = self.data.Close
        self.bollinger_upper, self.bollinger_middle, self.bollinger_lower = self.I(
            talib.BBANDS, self.close, timeperiod=50, nbdevup=2, nbdevdn=2, matype=0)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.close, timeperiod=14)

    def next(self):
        if not self.position:
            if self.close[-1] < self.bollinger_lower[-1]:
                print("🌙 Entering long position! �")
                stop_loss = self.close[-1] - 0.5 * self.atr[-1]
                self.buy(size=1000000, sl=stop_loss)
        else:
            if self.close[-1] > self.bollinger_upper[-1]:
                print("✨ Exiting position at target! 🌟")
                self.position.close()
            elif len(self.trades) > 0 and self.trades[-1].bars >= 3:
                print("🕒 Time-based exit triggered! ⏰")
                self.position.close()

def load_data():
    data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
    data = pd.read_csv(data_path, parse_dates=True, index_col=0)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    return data

data = load_data()
bt = Backtest(data, BandReversalEdge, cash=1000000, commission=.002)
stats = bt.run()
print(stats)
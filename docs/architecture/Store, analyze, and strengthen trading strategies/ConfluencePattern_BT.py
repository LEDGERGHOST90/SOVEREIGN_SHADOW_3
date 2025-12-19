import pandas as pd
import talib
from backtesting import Backtest, Strategy

class ConfluencePattern(Strategy):
    def init(self):
        # 🌙 Clean and standardize column names
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col.lower()])

        # 🌙 Ensure consistent column naming
        self.data.df.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'
        }, inplace=True)

        # 🌙 Initialize indicators using talib
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=50)
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close, 
                                               fastperiod=12, slowperiod=26, signalperiod=9)

    def next(self):
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]

        # 🌙 Entry logic with manual crossover detection
        if (price > self.ema50[-1] and price > self.ema200[-1] and
                self.rsi[-1] < 30 and
                (self.macd[-2] < self.macd_signal[-2] and self.macd[-1] > self.macd_signal[-1]) and
                volume > self.data.Volume[-2]):
            
            # 🌙 Fixed position sizing (whole units)
            position_size = int(1_000_000 / price)
            self.buy(size=position_size)
            print(f"🚀 Moon Entry: Buying {position_size} units at {price:.2f} 🌙")

        # 🌙 Exit logic with manual crossover detection
        elif (self.position and 
              ((self.macd_signal[-2] < self.macd[-2] and self.macd_signal[-1] > self.macd[-1]) or 
               self.rsi[-1] > 70)):
            self.position.close()
            print(f"🌙 Exit: Closing position at {price:.2f} 🚀")

# 🌙 Load data with proper error handling
try:
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    print("🌙 Data loaded successfully! ✨")
except Exception as e:
    print(f"🌙 ERROR loading data: {e}")
    raise

# 🌙 Run backtest with proper settings
bt = Backtest(data, ConfluencePattern, cash=1_000_000, commission=.002)
stats = bt.run()
print("🌙 Backtest complete! Here are the results:")
print(stats)
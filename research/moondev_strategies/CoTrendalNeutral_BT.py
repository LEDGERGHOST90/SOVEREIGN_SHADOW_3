import talib
import pandas as pd
from backtesting import Backtest, Strategy

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

# Define the CoTrendalNeutral strategy
class CoTrendalNeutral(Strategy):
    def init(self):
        self.spx_ma_short = self.I(talib.SMA, self.data.Close, timeperiod=50)
        self.spx_ma_long = self.I(talib.SMA, self.data.Close, timeperiod=200)
        self.vix_ma_short = self.I(talib.SMA, self.data.Close, timeperiod=50)
        self.vix_ma_long = self.I(talib.SMA, self.data.Close, timeperiod=200)
        self.take_profit = None  # Initialize take_profit as class attribute

    def next(self):
        spx_trend_up = self.data.Close[-1] > self.spx_ma_short[-1] > self.spx_ma_long[-1]
        vix_trend_down = self.data.Close[-1] < self.vix_ma_short[-1] < self.vix_ma_long[-1]

        # Long Entry (SPX)
        if spx_trend_up and vix_trend_down:
            rr_ratio = 3.0
            stop_loss = self.data.Close[-1] - (self.data.Close[-1] - self.spx_ma_short[-1])
            self.take_profit = self.data.Close[-1] + (rr_ratio * (self.data.Close[-1] - stop_loss))
            position_size = int(round(1000000 / self.data.Close[-1]))
            self.buy(size=position_size)
            print(f"🌙 🚀 Long Entry on SPX at {self.data.Close[-1]:.2f} with SL: {stop_loss:.2f}, TP: {self.take_profit:.2f} | Size: {position_size} units")

        # Short Entry (VIX)
        if not spx_trend_up and not vix_trend_down:
            rr_ratio = 3.0
            stop_loss = self.data.Close[-1] + (self.vix_ma_short[-1] - self.data.Close[-1])
            self.take_profit = self.data.Close[-1] - (rr_ratio * (stop_loss - self.data.Close[-1]))
            position_size = int(round(1000000 / self.data.Close[-1]))
            self.sell(size=position_size)
            print(f"🌙 🚀 Short Entry on VIX at {self.data.Close[-1]:.2f} with SL: {stop_loss:.2f}, TP: {self.take_profit:.2f} | Size: {position_size} units")

        # Exit logic
        if self.position.is_long and (not spx_trend_up or self.data.Close[-1] >= self.take_profit):
            self.position.close()
            print(f"✨ Exit Long Position at {self.data.Close[-1]:.2f}")

        if self.position.is_short and (spx_trend_up or self.data.Close[-1] <= self.take_profit):
            self.position.close()
            print(f"✨ Exit Short Position at {self.data.Close[-1]:.2f}")

# Run the backtest
bt = Backtest(data, CoTrendalNeutral, cash=1000000, commission=0.002)
stats = bt.run()
print(stats)
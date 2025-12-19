import pandas as pd
import talib
from backtesting import Backtest, Strategy

class BandStrengthMomentum(Strategy):
    strategy_name = "BandStrength Momentum"

    def init(self):
        # Clean and prepare data
        self.data.columns = self.data.columns.str.strip().str.lower()
        self.data = self.data.drop(columns=[col for col in self.data.columns if 'unnamed' in col.lower()])
        self.data.columns = ['open', 'high', 'low', 'close', 'volume']

        # Calculate Bollinger Bands
        self.upper_band, self.middle_band, self.lower_band = self.I(
            talib.BBANDS, self.data.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        # Calculate Relative Strength (RS)
        # For simplicity, we'll use RSI as a proxy for RS
        self.rs = self.I(talib.RSI, self.data.close, timeperiod=14)

    def next(self):
        price = self.data.close[-1]
        rs_value = self.rs[-1]

        # Long Entry
        if (self.data.close[-2] < self.lower_band[-2] and self.data.close[-1] > self.lower_band[-1]) and rs_value > 50:
            if self.data.open[-1] < self.data.close[-1]:  # Bullish candle
                stop_loss = self.lower_band[-1]
                take_profit = self.upper_band[-1]
                position_size = int(1_000_000 / price)
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                print(f"🌙 ✨ Moon Dev Debug: LONG ENTRY | Price: {price:.2f} | Size: {position_size} units | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

        # Short Entry
        elif (self.data.close[-2] > self.upper_band[-2] and self.data.close[-1] < self.upper_band[-1]) and rs_value < 50:
            if self.data.open[-1] > self.data.close[-1]:  # Bearish candle
                stop_loss = self.upper_band[-1]
                take_profit = self.lower_band[-1]
                position_size = int(1_000_000 / price)
                self.sell(size=position_size, sl=stop_loss, tp=take_profit)
                print(f"🌙 ✨ Moon Dev Debug: SHORT ENTRY | Price: {price:.2f} | Size: {position_size} units | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

# Load data
try:
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    print("🌙 ✨ Moon Dev Debug: Data loaded successfully!")
except Exception as e:
    print(f"🌙 ✨ Moon Dev Debug: Error loading data - {str(e)}")
    raise

# Run backtest
try:
    bt = Backtest(data, BandStrengthMomentum, cash=1_000_000, commission=.002)
    stats = bt.run()
    print("🌙 ✨ Moon Dev Debug: Backtest completed successfully!")
    print(stats)
except Exception as e:
    print(f"🌙 ✨ Moon Dev Debug: Backtest error - {str(e)}")
    raise
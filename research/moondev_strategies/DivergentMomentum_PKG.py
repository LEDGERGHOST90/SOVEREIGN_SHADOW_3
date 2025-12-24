import pandas as pd
from backtesting import Backtest, Strategy
import talib
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to match backtesting requirements
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Convert datetime and set index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class DivergentMomentum(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    rsi_period = 14
    ma_period = 50
    cci_period = 20
    swing_window = 5  # Swing low detection window

    def init(self):
        # Calculate indicators using TA-Lib
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.ma50 = self.I(talib.SMA, self.data.Close, self.ma_period)
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low, self.data.Close, self.cci_period)
        self.price_lows = self.I(talib.MIN, self.data.Low, self.swing_window)
        self.rsi_lows = self.I(talib.MIN, self.rsi, self.swing_window)

    def next(self):
        # Skip if not enough data
        if len(self.rsi) < self.swing_window + 2:
            return

        # Current values
        price_low_current = self.price_lows[-1]
        price_low_prev = self.price_lows[-2]
        rsi_low_current = self.rsi_lows[-1]
        rsi_low_prev = self.rsi_lows[-2]
        
        # Divergence detection
        bearish_price = price_low_current < price_low_prev
        bullish_rsi = rsi_low_current > rsi_low_prev
        divergence = bearish_price and bullish_rsi

        # Entry conditions
        if not self.position:
            if (self.rsi[-1] < 30 and
                divergence and
                self.data.Close[-1] > self.ma50[-1]):
                
                # Risk management calculations
                entry_price = self.data.Close[-1]
                stop_loss = price_low_current
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = (self.broker.equity * self.risk_percent) / risk_per_share
                    position_size = int(round(position_size))
                    
                    # Moon-themed debug print
                    print(f"🌙✨ Lunar Entry! Price: {entry_price:.2f}, Size: {position_size} contracts, SL: {stop_loss:.2f}")
                    
                    self.buy(size=position_size, sl=stop_loss)

        # Exit conditions
        else:
            if len(self.cci) > 2:
                current_cci = self.cci[-1]
                prev_cci = self.cci[-2]
                
                if current_cci > 100 and current_cci < prev_cci:
                    print(f"🚀🌙 CCI Reversal! Closing position at {self.data.Close[-1]:.2f}")
                    self.position.close()

# Run backtest
bt = Backtest(data, DivergentMomentum, cash=1_000_000, commission=.002)
stats = bt.run()

# Print full statistics
print("\n🌕🌖🌗🌘🌑🌒🌓🌔 FULL MOON STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
print(stats)
print(stats._strategy)
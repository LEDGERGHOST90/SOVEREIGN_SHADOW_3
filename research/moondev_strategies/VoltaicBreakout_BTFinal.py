Here's the debugged version of your backtest code with Moon Dev themed debug prints and proper position sizing:

```python
import pandas as pd
from backtesting import Backtest, Strategy
import talib

# Helper functions for Bollinger Bands
def bb_upper(close, timeperiod, nbdevup, nbdevdn):
    upper, _, _ = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
    return upper

def bb_lower(close, timeperiod, nbdevup, nbdevdn):
    _, _, lower = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
    return lower

class VoltaicBreakout(Strategy):
    risk_percentage = 0.01  # 1% risk per trade
    
    def init(self):
        # Calculate Bollinger Bands
        self.upper_band = self.I(bb_upper, self.data.Close, 20, 2, 2, name='Upper BB')
        self.lower_band = self.I(bb_lower, self.data.Close, 20, 2, 2, name='Lower BB')
        
        # Calculate ATR for volatility measurements
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR')
        
        # Calculate bandwidth and 30-day minimum bandwidth
        self.bandwidth = self.I(lambda u, l: u - l, self.upper_band, self.lower_band, name='Bandwidth')
        self.min_bandwidth_30day = self.I(talib.MIN, self.bandwidth, 2880, name='30D Min BW')  # 2880 bars = 30 days in 15m
        
        self.trailing_high = None  # Track highest high since entry

    def next(self):
        # Skip if not enough historical data
        if len(self.data) < 2880 + 2:
            return
        
        # Entry logic
        if not self.position:
            # Check volatility squeeze condition (previous bar had narrowest bandwidth)
            if self.bandwidth[-2] == self.min_bandwidth_30day[-2]:
                # Confirm breakout above upper band
                if self.data.Close[-2] > self.upper_band[-2]:
                    # Calculate position size with proper risk management
                    entry_price = self.data.Open[-1]
                    atr_value = self.atr[-2]  # Use previous bar's ATR
                    stop_loss = entry_price - 2 * atr_value
                    risk_per_share = entry_price - stop_loss
                    
                    if risk_per_share > 0:
                        position_size = int(round((self.equity * self.risk_percentage) / risk_per_share))
                        if position_size > 0:
                            print(f"🌙 MOON DEV BREAKOUT 🌙: Entering {position_size} shares at {entry_price} ✨")
                            self.buy(size=position_size, sl=stop_loss)
                            self.trailing_high = self.data.High[-1]

        # Exit logic
        else:
            # Update trailing high
            self.trailing_high = max(self.trailing_high, self.data.High[-1])
            
            # Calculate dynamic stop (2x current ATR from high)
            current_sl = self.trailing_high - 2 * self.atr[-1]
            self.position.sl = max(self.position.sl or 0, current_sl)
            
            # Check exit condition
            if self.data.Close[-1] < current_sl:
                print(f"🌙 MOON DEV TRAIL STOP 🌙: Exiting at {self.data.Close[-1]} 🛑")
                self.position.close()

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# Run backtest
bt = Backtest(data, VoltaicBreakout, cash=1_000_000, commission=.002)
stats = bt.run()
print("🌙 MO
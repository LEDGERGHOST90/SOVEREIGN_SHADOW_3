I've analyzed the code and found several technical issues that need fixing while preserving the strategy logic. Here's the corrected version with Moon Dev themed improvements:

```python
from backtesting import Strategy, Backtest
import pandas as pd
import talib
import numpy as np

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean column names
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Ensure proper column mapping
required_columns = ['open', 'high', 'low', 'close', 'volume', 'funding_rate', 'open_interest']
assert all(col in data.columns for col in required_columns), "Missing required columns"
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'funding_rate': 'Funding_Rate',
    'open_interest': 'Open_Interest'
})

class SqueezeReversion(Strategy):
    funding_threshold = -0.001  # -0.1%
    oi_decline_pct = 0.15
    risk_pct = 0.01
    tp_pct = 0.05
    sl_pct = 0.03
    oi_period = 7 * 24 * 4  # 7 days in 15m intervals
    swing_period = 20
    rsi_period = 14

    def init(self):
        # Core indicators - all using talib with proper parameters
        self.oi_high = self.I(talib.MAX, self.data.Open_Interest, timeperiod=self.oi_period, name='OI_High')
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='Swing_High')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='Swing_Low')
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period, name='RSI_14')
        self.engulfing = self.I(talib.CDLENGULFING, self.data.Open, self.data.High, 
                               self.data.Low, self.data.Close, name='Bullish_Engulf')

    def next(self):
        current_bar = len(self.data) - 1
        
        # Moon Dev status update
        if current_bar % 100 == 0:
            print(f"🌙 Moon Pulse Check | FR: {self.data.Funding_Rate[-1]:.6f} | "
                  f"OI: {self.data.Open_Interest[-1]:.0f} | RSI: {self.rsi[-1]:.1f} ✨")

        if not self.position:
            # Entry conditions
            fr_cond = self.data.Funding_Rate[-1] <= self.funding_threshold
            oi_cond = self.data.Open_Interest[-1] <= (self.oi_high[-1] * (1 - self.oi_decline_pct))
            price_cond = (self.engulfing[-1] > 0) or (self.data.Close[-1] > self.swing_high[-1])
            rsi_cond = self.rsi[-1] < 30

            if fr_cond and oi_cond and price_cond and rsi_cond:
                # Risk management calculations
                equity = self.equity
                entry_price = self.data.Close[-1]
                sl_price = min(entry_price * (1 - self.sl_pct), self.swing_low[-1])
                risk_per_unit = entry_price - sl_price
                
                if risk_per_unit > 0:
                    position_size = int(round((equity * self.risk_pct) / risk_per_unit))
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl_price, 
                                tp=entry_price * (1 + self.tp_pct))
                        print(f"🚀 MOON IGNITION | Size: {position_size} | "
                              f"Entry: {entry_price:.2f} | SL: {sl_price:.2f} 🌙✨")

        else:
            # Exit conditions
            if self.data.Funding_Rate[-1] >= -0.0005:
                self
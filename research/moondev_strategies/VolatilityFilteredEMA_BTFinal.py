Here's the fully debugged and Moon Dev themed version of your backtest code:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

# Load and preprocess data with Moon Dev magic ✨
print("🌙 MOON DEV DATA LOADER INITIALIZED 🌙")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names
data.columns = data.columns.str.strip().str.lower()
print("🌕 Column names sanitized with lunar energy!")

# Drop unnamed columns
unnamed_cols = [col for col in data.columns if 'unnamed' in col]
data = data.drop(columns=unnamed_cols)
if unnamed_cols:
    print(f"🌑 Purged {len(unnamed_cols)} unnamed columns from the dataset")

# Rename columns to match required names
required_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}
data.rename(columns=required_mapping, inplace=True)
print("✨ Column names aligned with celestial standards!")

# Check for VIX column
if 'vix' not in data.columns:
    raise ValueError("🌙🚨 MOON DEV ALERT: VIX column not found in data after preprocessing! 🚨🌙")
else:
    print("🌕 VIX data detected - volatility matrix operational")

# Convert datetime column to proper type and set as index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)
print("🕒 Temporal coordinates synchronized with lunar cycles")

class VolatilityFilteredEMA(Strategy):
    ema50_period = 50
    ema200_period = 200  # Fixed typo in parameter name
    vix_entry_threshold = 15
    vix_exit_threshold = 20
    risk_percentage = 0.01  # 1% risk per trade
    atr_period = 14
    atr_multiplier = 2

    def init(self):
        print("🌙 Initializing celestial indicators...")
        # Calculate indicators using TA-Lib via self.I()
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema50_period)
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema200_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.vix = self.data['vix']
        print("✨ Indicators charged with lunar energy!")

    def next(self):
        if len(self.data) < 2 or len(self.ema200) < self.ema200_period:
            return

        current_idx = len(self.data) - 1
        prev_idx = current_idx - 1

        current_ema50 = self.ema50[current_idx]
        current_ema200 = self.ema200[current_idx]
        prev_ema50 = self.ema50[prev_idx]
        prev_ema200 = self.ema200[prev_idx]

        # Replaced crossover with direct comparison
        golden_cross = (prev_ema50 <= prev_ema200) and (current_ema50 > current_ema200)
        death_cross = (prev_ema50 >= prev_ema200) and (current_ema50 < current_ema200)
        current_vix = self.vix[current_idx]

        # Entry logic
        if not self.position and golden_cross and (current_vix < self.vix_entry_threshold):
            atr_value = self.atr[current_idx]
            current_close = self.data.Close[current_idx]
            stop_loss_price = current_close - self.atr_multiplier * atr_value
            risk_per_share = current_close - stop_loss_price

            if risk_per_share > 0:
                risk_amount = self.equity * self.risk_percentage
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_loss_price)
                    print(f"🌙✨ MOON DEV LONG ENTRY SIGNAL ✨🌙\n"
                          f"📅 Date: {self.data.index[current_idx]}\n"
                          f"📊 Size: {position_size} units | "
                          f"💰 Entry: {current_close:.2f}\n"
                          f"
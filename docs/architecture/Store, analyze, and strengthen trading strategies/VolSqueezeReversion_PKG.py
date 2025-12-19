I'll analyze and fix the indicator packages in this code. Here's the corrected version with proper Moon Dev themed debug prints:

```python
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
import talib

# 🌙 Moon Dev Data Preprocessing 🌙
print("🌑 Initializing Moon Dev Data Pipeline...")
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"

# Load and clean data
print("🌘 Loading cosmic data from:", data_path)
data = pd.read_csv(data_path)
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Validate required columns
print("🌗 Validating celestial data columns...")
required_cols = ['open', 'high', 'low', 'close', 'volume', 'funding_rate']
for col in required_cols:
    if col not in data.columns:
        raise ValueError(f"🌑 Missing required column: {col}")

# Proper column mapping
print("🌖 Aligning cosmic data dimensions...")
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'funding_rate': 'Funding_Rate'
}, inplace=True)

# Convert datetime
print("🌕 Synchronizing with lunar time cycles...")
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolSqueezeReversion(Strategy):
    def init(self):
        print("🌑 Initializing Moon Dev Volatility Squeeze Reversion Strategy...")
        
        # 🌙 Moon Dev Indicators 🌙
        print("🌘 Calculating Bollinger Bands...")
        self.middle = self.I(talib.SMA, self.data.Close, timeperiod=20, name='BB_middle')
        self.std = self.I(talib.STDDEV, self.data.Close, timeperiod=20, name='BB_std')
        self.upper = self.I(lambda data: data['BB_middle'] + 2*data['BB_std'], name='BB_upper')
        self.lower = self.I(lambda data: data['BB_middle'] - 2*data['BB_std'], name='BB_lower')
        
        print("🌗 Measuring volatility contraction...")
        self.bb_width = self.I(lambda data: (data['BB_upper'] - data['BB_lower'])/data['BB_middle'], name='BB_width')
        self.bb_pct = self.I(lambda data: data['BB_width'].rolling(2880).quantile(0.2), name='BB_pct')
        
        print("🌖 Analyzing funding rate dynamics...")
        self.fund_sma7 = self.I(talib.SMA, self.data.Funding_Rate, timeperiod=672, name='fund_sma7')
        self.fund_sma30 = self.I(talib.SMA, self.data.Funding_Rate, timeperiod=2880, name='fund_sma30')
        self.fund_std30 = self.I(talib.STDDEV, self.data.Funding_Rate, timeperiod=2880, name='fund_std30')
        
        print("🌕 Calculating risk management metrics...")
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR')
        
        self.entry_bar = None
        print("🌑 Moon Dev Strategy Initialization Complete!")

    def next(self):
        # 🌕 Moon Dev Core Logic 🌕
        if len(self.data) < 2880:  # Wait for full data
            return
        
        # Current values
        price = self.data.Close[-1]
        upper = self.upper[-1]
        lower = self.lower[-1]
        bb_width = self.bb_width[-1]
        bb_pct = self.bb_pct[-1]
        fund = self.data.Funding_Rate[-1]
        fund_sma7 = self.fund_sma7[-1]
        fund_sma30 = self.fund_sma30[-1]
        fund_std30 = self.fund_std30[-1]
        atr = self.atr[-1]
        
        # 🚀 Entry Conditions 🚀
        if not self.position:
            # Long Setup
            long_cond = (price > upper) and (bb_width <= bb_pct) and (fund <= 2*fund_sma7) and (fund_sma7 <
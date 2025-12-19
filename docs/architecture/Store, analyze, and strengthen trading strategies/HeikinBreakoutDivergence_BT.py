```python
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Data handling and preparation
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'])

# Clean and prepare columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])

# Verify required columns
required_columns = ['open', 'high', 'low', 'close', 'volume', 'tick']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"🌙 CRITICAL ERROR: Missing required column '{col}' in data")

# Proper column mapping
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'tick': 'Tick'
}, inplace=True)

class HeikinBreakoutDivergence(Strategy):
    initial_equity = 1_000_000
    risk_per_trade = 0.02  # 2% risk per trade
    
    def init(self):
        print("🌙 Initializing Moon Dev's Cosmic Trader...")
        
        # Calculate Heikin-Ashi candles
        ha = ta.heikin_ashi(self.data.Open, self.data.High, self.data.Low, self.data.Close)
        self.ha_open = self.I(lambda: ha.HA_OPEN, name='HA_Open')
        self.ha_high = self.I(lambda: ha.HA_HIGH, name='HA_High')
        self.ha_low = self.I(lambda: ha.HA_LOW, name='HA_Low')
        self.ha_close = self.I(lambda: ha.HA_CLOSE, name='HA_Close')
        
        # Calculate Bollinger Bands (20-period, 2.5σ)
        self.bb_upper = self.I(talib.BBANDS, self.ha_close, 20, 2.5, 2.5, name='BB_Upper')[0]
        self.bb_lower = self.I(talib.BBANDS, self.ha_close, 20, 2.5, 2.5, name='BB_Lower')[2]
        
        # Fractal calculations (5-period swing high/low)
        self.fractal_high = self.I(talib.MAX, self.data.High, 5, name='Fractal_High')
        self.fractal_low = self.I(talib.MIN, self.data.Low, 5, name='Fractal_Low')
        
        print("✨ Indicators initialized: HA Candle | BBands | Fractal Levels | TICK Analysis")

    def next(self):
        current_close = self.data.Close[-1]
        ha_close = self.ha_close[-1]
        bb_upper = self.bb_upper[-1]
        bb_lower = self.bb_lower[-1]
        
        # Moon Dev's Cosmic Position Management
        if not self.position:
            # Long entry logic
            if ha_close > bb_upper:
                tick_increase = self.data.Tick[-1] > self.data.Tick[-2]
                price_increase = self.data.Low[-1] > self.data.Low[-2]
                if tick_increase and price_increase:
                    self.enter_long()
            
            # Short entry logic
            elif ha_close < bb_lower:
                tick_decrease = self.data.Tick[-1] < self.data.Tick[-2]
                price_decrease = self.data.High[-1] < self.data.High[-2]
                if tick_decrease and price_decrease:
                    self.enter_short()
        else:
            # Exit logic
            if self.position.is_long and (ha_close < bb_upper or 
                (self.data.Tick[-1] < self.data.Tick[-2] and 
                 self.data.High[-1] > self.data.High[-2])):
                self.position.close()
                print("🌙✨ Closing LONG: Signal Reversal Detected")
                
            elif self.position.is_short and (ha_close > bb_lower or 
                  (self.data.Tick[-1] > self.data.Tick[-2] and 
                   self.data.Low[-1] < self.data.Low[-2])):
                self.position.close()
                print("🌙✨ Closing SHORT: Signal Reversal Detected")

    def enter_long(self):
        account_
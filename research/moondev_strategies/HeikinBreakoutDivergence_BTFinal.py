I'll fix the incomplete code while maintaining the original strategy logic. Here's the complete, debugged version with Moon Dev themed prints:

```python
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy

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
        print("✨ Preparing celestial indicators for cosmic alignment...")
        
        # Calculate Heikin-Ashi candles
        ha = ta.heikin_ashi(self.data.Open, self.data.High, self.data.Low, self.data.Close)
        self.ha_open = self.I(lambda: ha.HA_OPEN, name='HA_Open')
        self.ha_high = self.I(lambda: ha.HA_HIGH, name='HA_High')
        self.ha_low = self.I(lambda: ha.HA_LOW, name='HA_Low')
        self.ha_close = self.I(lambda: ha.HA_CLOSE, name='HA_Close')
        
        # Calculate Bollinger Bands (20-period, 2.5σ)
        bb_upper, _, bb_lower = talib.BBANDS(self.ha_close, 20, 2.5, 2.5)
        self.bb_upper = self.I(lambda: bb_upper, name='BB_Upper')
        self.bb_lower = self.I(lambda: bb_lower, name='BB_Lower')
        
        # Fractal calculations (5-period swing high/low)
        self.fractal_high = self.I(talib.MAX, self.data.High, 5, name='Fractal_High')
        self.fractal_low = self.I(talib.MIN, self.data.Low, 5, name='Fractal_Low')
        
        print("✨ Cosmic indicators initialized:")
        print("   🌕 Heikin-Ashi Candle")
        print("   🌗 Bollinger Bands (20, 2.5σ)")
        print("   🌓 Fractal Levels (5-period)")
        print("   🌔 TICK Analysis")

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
                    print("🌙✨ Cosmic Alignment Detected: Entering LONG Position")
                    stop_price = self.fractal_low[-1]
                    risk_amount = self.initial_equity * self.risk_per_trade
                    position_size = round(risk_amount / (current_close - stop_price))
                    self.buy(size=position_size, sl=stop_price)
            
            # Short entry logic
            elif ha_close < bb_lower:
                tick_decrease = self.data.Tick[-1] < self.data.Tick[-2]
                price_decrease = self.data.High[-1] < self.data.High[-2]
                if tick_decrease and price_decrease:
                    print("🌙✨ Cosmic Alignment Detected: Entering SHORT Position")
                    stop_price = self.fractal_high[-1]
                    risk_amount = self.initial_equ
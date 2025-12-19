Here's the fixed code with all `backtesting.lib` imports and functions removed, and proper Moon Dev themed debug prints added:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names
data.columns = data.columns.str.strip().str.lower()

# Drop unnamed columns
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename and format columns
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Convert datetime and set index
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

class InverseVolumeDivergence(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    rsi_period = 14
    stoch_period = 14
    swing_period = 20
    
    def init(self):
        # Core indicators
        self.volume_sma = self.I(talib.SMA, self.data.Volume, self.swing_period)
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        
        # Stochastic oscillator
        stoch_k, stoch_d = talib.STOCH(self.data.High, self.data.Low, self.data.Close,
                                      fastk_period=self.stoch_period,
                                      slowk_period=3,
                                      slowd_period=3)
        self.stoch_k = self.I(lambda: stoch_k, name='Stoch%K')
        self.stoch_d = self.I(lambda: stoch_d, name='Stoch%D')
        
        # Swing points
        self.swing_highs = self.I(talib.MAX, self.data.High, self.swing_period)
        self.swing_lows = self.I(talib.MIN, self.data.Low, self.swing_period)
        
        # Candlestick patterns
        self.engulfing = self.I(talib.CDLENGULFING, self.data.Open, self.data.High, 
                               self.data.Low, self.data.Close)
        self.doji = self.I(talib.CDLDOJI, self.data.Open, self.data.High,
                          self.data.Low, self.data.Close)
        
        # Track swing points
        self.swing_high_list = []
        self.swing_low_list = []

    def next(self):
        # Wait for sufficient data
        if len(self.data) < self.swing_period + 2:
            return
        
        # Current market state
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        volume_sma = self.volume_sma[-1]
        
        # Detect new swing points
        if self.data.High[-1] == self.swing_highs[-1]:
            self.swing_high_list.append({
                'idx': len(self.data)-1,
                'price': self.data.High[-1],
                'rsi': self.rsi[-1],
                'stoch': self.stoch_k[-1]
            })
            if len(self.swing_high_list) > 2:
                self.swing_high_list.pop(0)
                
        if self.data.Low[-1] == self.swing_lows[-1]:
            self.swing_low_list.append({
                'idx': len(self.data)-1,
                'price': self.data.Low[-1],
                'rsi': self.rsi[-1],
                'stoch': self.stoch_k[-1]
            })
            if len(self.swing_low_list) > 2:
                self.swing_low_list.pop(0)
        
        # Divergence checks
        bearish_div = False
        bullish_div = False
        
        # Bearish divergence check (price ↗ vs indicators ↘)
        if len(self.swing_high_list) >= 2:
            last = self.swing_high_list[-1]
            prev = self.swing_high_list[-2]
            if (last['price'] > prev['price'] and 
                last['rsi'] < prev['rsi'] and 
                last['stoch'] < prev['stoch']):
                bearish_div = True
                print(f"🌙 Bearish divergence detected! Price {last['price']:.2f}↗ vs RSI {last['rsi']:.2f}↘")
        
        # Bullish divergence check (price ↘ vs indicators ↗
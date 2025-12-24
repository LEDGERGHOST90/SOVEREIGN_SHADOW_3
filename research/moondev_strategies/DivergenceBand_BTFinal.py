I'll help you debug and fix the code while maintaining the strategy logic. Here's the corrected version with Moon Dev themed debug prints and proper position sizing:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# Load and preprocess data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class DivergenceBand(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # MACD Divergence
        def calculate_macd_hist(close):
            macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            return hist
        self.macd_hist = self.I(calculate_macd_hist, self.data.Close)
        
        # RSI Confirmation
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        
        # Bollinger Bands
        def bollinger_upper(close):
            return talib.SMA(close, 20) + 2 * talib.STDDEV(close, 20)
        def bollinger_lower(close):
            return talib.SMA(close, 20) - 2 * talib.STDDEV(close, 20)
        self.middle_band = self.I(talib.SMA, self.data.Close, 20)
        self.upper_band = self.I(bollinger_upper, self.data.Close)
        self.lower_band = self.I(bollinger_lower, self.data.Close)
        
        # Swing Highs/Lows
        self.swing_high = self.I(talib.MAX, self.data.High, 5)
        self.swing_low = self.I(talib.MIN, self.data.Low, 5)
        
        # Track previous swings
        self.last_swing_high_price = None
        self.last_swing_high_macd = None
        self.last_swing_low_price = None
        self.last_swing_low_macd = None
        
        # Volatility filter
        self.bb_width = self.I(lambda u, l: u - l, self.upper_band, self.lower_band)
        self.bb_width_ma = self.I(talib.SMA, self.bb_width, 20)
        
    def next(self):
        # Moon Dev Debug Prints 🌙
        print(f"\n🌕 MOON DEV UPDATE: Close={self.data.Close[-1]} | RSI={self.rsi[-1]:.1f} | BB Width={self.bb_width[-1]:.1f}")
        
        # Calculate position size based on risk percentage
        risk_amount = self.equity * self.risk_percent
        position_size = risk_amount / (self.data.Close[-1] * 0.01)  # Assuming 1% stop loss
        position_size = round(position_size)  # Round to whole units
        
        # Exit conditions
        if self.position:
            # Trailing stop logic
            if self.position.is_long and (self.data.Close[-2] > self.lower_band[-2] and self.data.Close[-1] < self.lower_band[-1]):
                self.position.close()
                print(f"🌙✨ MOON DEV TRAILING STOP: Long closed at {self.data.Close[-1]}")
            elif self.position.is_short and (self.data.Close[-2] < self.upper_band[-2] and self.data.Close[-1] > self.upper_band[-1]):
                self.position.close()
                print(f"🌑💫 MOON DEV TRAILING STOP: Short closed at {self.data.Close[-1]}")
                
            # Volatility exit
            if self.bb_width[-1] < self.bb_width_ma[-1] * 0.5:
                self.position.close()
                print(f"🚀 MOON DEV VOLATILITY EXIT: BB Width {self.bb_width[-1]:.1f} < MA {self.bb_width_ma[-1]:.1f}")
        
        # Entry conditions
        else:
            #
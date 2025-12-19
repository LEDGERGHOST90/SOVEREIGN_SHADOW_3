Here's the complete implementation of the LiquidationReversion strategy following your specifications:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class LiquidationReversion(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Bollinger Bands (1-hour equivalent)
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 80, 2, 2, 0, name='BB_UPPER', which=0)
        self.bb_middle = self.I(talib.BBANDS, self.data.Close, 80, 2, 2, 0, name='BB_MID', which=1)
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, 80, 2, 2, 0, name='BB_LOWER', which=2)
        
        # Bollinger Bandwidth
        def calc_bandwidth(upper, mid, lower):
            return (upper - lower) / mid
        self.bb_width = self.I(calc_bandwidth, self.bb_upper, self.bb_middle, self.bb_lower, name='BB_WIDTH')
        
        # Rolling 10th percentile of bandwidth
        self.bb_low_vol = self.I(lambda width: width.rolling(200).quantile(0.1), self.bb_width, name='BB_LOW_VOL')
        
        # Keltner Channel
        self.ema = self.I(talib.EMA, self.data.Close, 20, name='EMA')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20, name='ATR')
        self.keltner_upper = self.I(lambda e, a: e + 2*a, self.ema, self.atr, name='KELTNER_UPPER')
        self.keltner_lower = self.I(lambda e, a: e - 2*a, self.ema, self.atr, name='KELTNER_LOWER')
        
        # Swing points
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='SWING_LOW')
        
    def next(self):
        price = self.data.Close[-1]
        swing_h = self.swing_high[-1]
        swing_l = self.swing_low[-1]
        
        if not self.position:
            # Long entry logic
            if price <= swing_l * 1.005 and self.bb_width[-1] < self.bb_low_vol[-1]:
                sl = swing_l * 0.995
                risk_amount = self.equity * self.risk_per_trade
                position_size = int(round(risk_amount / (price - sl)))
                if position_size > 0:
                    self.buy(size=position_size, sl=sl)
                    print(f"🌙✨ MOON DEV LONG! Entry: {price:.2f} | Size: {position_size} | SL: {sl:.2f} 🚀")
            
            # Short entry logic
            elif price >= swing_h * 0.995 and self.bb_width[-1] < self.bb_low_vol[-1]:
                sl = swing_h * 1.005
                risk_amount = self.equity * self.risk_per_trade
                position_size = int(round(risk_amount / (sl - price)))
                if position_size > 0:
                    self.sell(size=position_size, sl=sl)
                    print(f"🌙✨ MOON DEV SHORT! Entry: {price:.2f} | Size: {position_size} | SL: {sl:.2f} 🚀")
        
        # Exit logic
        elif self
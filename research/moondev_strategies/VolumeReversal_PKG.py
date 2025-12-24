Here's the fixed code with all the necessary changes to remove any `backtesting.lib` imports and functions, and to ensure proper indicator usage:

```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION FOR VOLUMEREVERSAL STRATEGY 🚀

import pandas as pd
import talib
from backtesting import Backtest, Strategy

# ======================
# 🌌 DATA PREPROCESSING
# ======================
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'])

# Clean column names 🌟
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map to proper columns 🗺️
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data.set_index('datetime', inplace=True)

# ======================
# 🌕 VOLUMEREVERSAL STRATEGY CLASS
# ======================
class VolumeReversal(Strategy):
    rsi_period = 14
    bb_period = 20
    bb_dev = 2
    swing_window = 20
    risk_pct = 0.01
    
    def init(self):
        # 🌗 BOLLINGER BANDS CALCULATION
        def bb_upper(close, period, dev):
            upper, _, _ = talib.BBANDS(close.values, period, dev, dev)
            return upper
        self.upper_bb = self.I(bb_upper, self.data.Close, self.bb_period, self.bb_dev, name='UPPER_BB')
        
        def bb_lower(close, period, dev):
            _, _, lower = talib.BBANDS(close.values, period, dev, dev)
            return lower
        self.lower_bb = self.I(bb_lower, self.data.Close, self.bb_period, self.bb_dev, name='LOWER_BB')
        
        # 🌓 VOLUME INDICATORS
        self.vol_ma = self.I(talib.SMA, self.data.Volume, self.bb_period, name='VOL_MA')
        self.bb_width = self.I(lambda: ((self.upper_bb - self.lower_bb) / self.upper_bb.mean()) * 100, name='BB_WIDTH')
        
        # 🌒 SWING POINTS
        self.swing_high = self.I(talib.MAX, self.data.High, self.swing_window, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, self.swing_window, name='SWING_LOW')
        
        # 🌔 MOMENTUM INDICATOR
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period, name='RSI')
        
        print("🌙 MOON DEV INDICATORS INITIALIZED! 🚀")

    def next(self):
        if self.position:
            return  # 🌑 Only one position at a time
            
        # 🌟 CURRENT VALUES
        price = self.data.Close[-1]
        rsi = self.rsi[-1]
        vol = self.data.Volume[-1]
        vol_ma = self.vol_ma[-1]
        bbw = self.bb_width[-1]
        sh = self.swing_high[-1]
        sl = self.swing_low[-1]

        # 🌪️ VOLUME SURGE CALCULATION
        vol_surge = ((vol - vol_ma)/vol_ma * 100) if vol_ma != 0 else 0

        # ======================
        # 🌕 ENTRY LOGIC
        # ======================
        if rsi > 70 and vol_surge > bbw:
            # 🌑 SHORT ENTRY
            stop_price = sh * 1.01
            risk = stop_price - price
            if risk <= 0: return
            
            position_size = int(round((self.equity * self.risk_pct) / risk))
            fib_exit = sl + 0.382*(sh - sl)
            self.sell(size=position_size, sl=stop_price, tp=fib_exit)
            print(f"🚀 MOON DEV SHORT! 🌑 | Entry: {price:.2f} | Size: {position_size} | SL: {stop_price:.2f}
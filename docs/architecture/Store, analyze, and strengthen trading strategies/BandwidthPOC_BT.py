```python
import numpy as np
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Load and preprocess data
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

class BandwidthPOC(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # Bollinger Bands (20,2)
        self.upper, self.mid, self.lower = self.I(talib.BBANDS, self.data.Close, 
                                                 timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        
        # Bollinger Band Width calculations
        self.bb_width = self.I(lambda u, m, l: (u - l)/m, self.upper, self.mid, self.lower)
        self.bbw_low_threshold = self.I(ta.percentile, self.bb_width, length=100, percentile=20)
        self.bbw_high_threshold = self.I(ta.percentile, self.bb_width, length=100, percentile=80)
        
        # Volume indicators
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 20)
        
        # POC calculation (simplified as max volume close)
        def calculate_poc(volume, close, window):
            poc = []
            for i in range(len(volume)):
                if i < window:
                    poc.append(np.nan)
                else:
                    window_vol = volume[i-window:i]
                    window_close = close[i-window:i]
                    poc.append(window_close[np.argmax(window_vol)])
            return poc
            
        self.poc = self.I(calculate_poc, self.data.Volume, self.data.Close, 50)
        
        print("🌙✨ Moon Dev Indicators Activated! BB Width, POC, and Volume Surge ready for launch! 🚀")

    def next(self):
        if len(self.data) < 100:  # Wait for indicators to warm up
            return

        # Current values
        price = self.data.Close[-1]
        bbw = self.bb_width[-1]
        vol = self.data.Volume[-1]
        vol_ma = self.volume_ma[-1]
        poc = self.poc[-1]

        # Moon Dev Debug Prints 🌙
        print(f"🌙 Current BB Width: {bbw:.4f} | POC: {poc:.2f} | Volume Ratio: {vol/vol_ma:.1f}x")

        # Entry logic
        if not self.position:
            # Long setup
            if (bbw < self.bbw_low_threshold[-1] and
                abs(price - poc)/poc < 0.01 and
                price > self.upper[-1] and
                vol > 1.5 * vol_ma):
                
                risk_amount = self.risk_percent * self.equity
                sl_price = self.mid[-1]
                risk_per_unit = price - sl_price
                
                if risk_per_unit > 0:
                    size = int(round(risk_amount / risk_per_unit))
                    self.buy(size=size, sl=sl_price, tp=price + 3*risk_per_unit)
                    print(f"🚀🌙 LONG LAUNCH! Size: {size} | Entry: {price:.2f} | SL: {sl_price:.2f} | TP: {price + 3*risk_per_unit:.2f}")

            # Short setup
            elif (bbw < self.bbw_low_threshold[-1] and
                  abs(price - poc)/poc < 0.01 and
                  price < self.lower[-1] and
                  vol > 1.5 * vol_ma):
                
                risk_amount = self.risk_percent * self.equity
                sl_price = self.mid[-1]
                risk_per_unit = sl_price - price
                
                if risk_per_unit > 0:
                    size = int(round(
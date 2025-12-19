Here's the complete fixed code with Moon Dev themed debug prints and all technical issues resolved:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class DeltaClusterReversal(Strategy):
    risk_percent = 0.01
    rr_ratio = 2
    swing_period = 20
    stoch_lookback = 5
    
    def init(self):
        # Moon Dev Indicator Initialization 🌙
        print("🌌 Initializing Moon Dev Trading Indicators...")
        
        # Calculate indicators using TA-Lib
        self.stoch_k, self.stoch_d = self.I(talib.STOCHRSI, self.data.Close, 
                                          timeperiod=5, fastk_period=3, fastd_period=3,
                                          name=['StochRSI K', 'StochRSI D'])
        
        # Calculate Cumulative Volume Delta (CVD)
        delta = self.data.Close - self.data.Open
        self.cvd = self.I(lambda: np.cumsum(np.sign(delta) * self.data.Volume), name='CVD')
        
        # Swing points using rolling max/min
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='Swing High')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='Swing Low')
        
        print("✨ Moon Dev Indicators Ready for Cosmic Trading! ✨")
        
    def next(self):
        if len(self.data) < self.swing_period + 1:
            return

        current_price = self.data.Close[-1]
        swing_low = self.swing_low[-1]
        swing_high = self.swing_high[-1]

        # Moon Dev Proximity Check 🌙
        near_swing_low = current_price <= swing_low * 1.005
        near_swing_high = current_price >= swing_high * 0.995

        # Moon Dev Divergence Detection ✨
        bull_div = (self.data.Low[-1] < self.data.Low[-2] and 
                   self.stoch_k[-1] > self.stoch_k[-2])
        bear_div = (self.data.High[-1] > self.data.High[-2] and 
                   self.stoch_k[-1] < self.stoch_k[-2])

        # Moon Dev CVD Confirmation 🚀
        cvd_trend = (self.cvd[-1] > self.cvd[-2] > self.cvd[-3]) if len(self.cvd) >= 3 else False

        # Moon Dev Entry Logic 🌗
        if not self.position:
            # Long entry
            if near_swing_low and bull_div and cvd_trend:
                sl = swing_low * 0.995
                risk = current_price - sl
                position_size = int(round((self.risk_percent * self.equity) / risk))
                if position_size > 0:
                    tp = current_price + risk * self.rr_ratio
                    self.buy(size=position_size, sl=sl, tp=tp)
                    print(f"🌙✨ Lunar BUY Signal Activated! | Size: {position_size} | Entry: {current_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")

            # Short entry
            elif near_swing_high and bear_div and not cvd_trend:
                sl = swing_high * 1.005
                risk = sl - current_price
                position_size = int(round((self.risk_percent * self.equity) / risk))
                if position_size > 0:
                    tp = current_price - risk * self.rr_ratio
                    self.sell(size=position_size, sl=sl, tp=tp)
                    print(f"🌙✨ Cosmic SELL Signal Engaged! | Size: {position_size} | Entry: {current_price:.2f} |
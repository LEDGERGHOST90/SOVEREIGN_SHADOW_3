Here's the fixed code with all backtesting.lib imports removed and replaced with proper implementations, along with Moon Dev themed debug prints: 🌙✨

```python
# 🌙 Moon Dev's VolumetricTrendRider Backtest Implementation 🚀
from backtesting import Backtest, Strategy
import talib
import pandas as pd

# Load and prepare cosmic data 🌌
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Cleanse data columns ✨
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolumetricTrendRider(Strategy):
    risk_percent = 0.01  # 1% cosmic risk allowance 🌠
    adx_threshold = 25
    emergency_adx = 20
    atr_multiplier = 3
    
    def init(self):
        # Celestial Indicators 🌕
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)
        self.obv_ma = self.I(talib.SMA, self.obv, timeperiod=20)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.ma200 = self.I(talib.SMA, self.data.Close, timeperiod=200)
        
        # Trailing stop variables 🌗
        self.max_high = 0
        self.min_low = float('inf')

    def next(self):
        current_close = self.data.Close[-1]
        current_adx = self.adx[-1]
        
        # Emergency black hole exit 🕳️
        if self.position and current_adx < self.emergency_adx:
            print(f"🌙 EMERGENCY EXIT! ADX {current_adx:.1f} < {self.emergency_adx} at {current_close} 🚨")
            self.position.close()
            return
            
        if not self.position:
            # Long entry constellation alignment 🌠
            obv_bullish = (self.obv[-2] < self.obv_ma[-2] and self.obv[-1] > self.obv_ma[-1])
            long_cond = (current_adx > self.adx_threshold and
                         obv_bullish and
                         current_close > self.ma200[-1])
            
            # Short entry dark matter alignment 🌑
            obv_bearish = (self.obv[-2] > self.obv_ma[-2] and self.obv[-1] < self.obv_ma[-1])
            short_cond = (current_adx > self.adx_threshold and
                          obv_bearish and
                          current_close < self.ma200[-1])
            
            if long_cond or short_cond:
                atr_value = self.atr[-1]
                risk_amount = self.equity * self.risk_percent
                position_size = int(round(risk_amount / (1.5 * atr_value)))
                
                if position_size > 0:
                    if long_cond:
                        self.buy(size=position_size, sl=current_close - 1.5*atr_value)
                        self.max_high = self.data.High[-1]
                        print(f"🚀 LIFT OFF! LONG {position_size} @ {current_close} | SL: {current_close - 1.5*atr_value:.1f} 🌙")
                    else:
                        self.sell(size=position_size, sl=current_close + 1.5*atr_value)
                        self.min_low = self.data.Low[-1]
                        print(f"🌑 DARK SIDE! SHORT {position_size} @ {current_close} | SL: {current_close + 1.5*atr_value:.1f} 🌙")

        # Chandelier Exit Protocol 🕯️
        if self.position.is_long:
            self.max_high = max(self.max_high, self.data.High[-1])
            trail = self.max_high - self.atr
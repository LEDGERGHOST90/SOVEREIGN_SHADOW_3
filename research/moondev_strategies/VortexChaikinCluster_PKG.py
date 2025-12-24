Here's the fixed code with all backtesting.lib imports removed and proper indicator implementations:

```python
import pandas as pd
import pandas_ta as ta
import talib
from backtesting import Strategy, Backtest
import numpy as np

# ========== MOON DEV DATA PREPARATION ========== 🌙
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'DateTime'
}, inplace=True)
data['DateTime'] = pd.to_datetime(data['DateTime'])
data.set_index('DateTime', inplace=True)

# ========== VORTEX CHAIKIN CLUSTER STRATEGY ========== 🚀
class VortexChaikinCluster(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # ===== MOON DEV INDICATORS ===== 🌙✨
        # Vortex Indicator (14-period)
        self.vi_plus, self.vi_minus = self.I(
            lambda high, low, close: ta.vortex(
                high=high, low=low, close=close, length=14
            ).values.T,
            self.data.High, self.data.Low, self.data.Close
        )
        
        # Chaikin Money Flow (20-period)
        self.cmf = self.I(talib.CMF, 
                         self.data.High, self.data.Low, self.data.Close, self.data.Volume,
                         timeperiod=20)
        
        # Keltner Channels Components
        self.ema20 = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.atr14 = self.I(talib.ATR, 
                           self.data.High, self.data.Low, self.data.Close,
                           timeperiod=14)
        self.kc_upper, self.kc_lower = self.I(
            lambda ema, atr: (ema + 2*atr, ema - 2*atr),
            self.ema20, self.atr14
        )
        
        # Volatility Filter (ATR 14 SMA 10)
        self.atr14_sma10 = self.I(talib.SMA, self.atr14, timeperiod=10)
        
    def next(self):
        # ===== MOON DEV TRADE LOGIC ===== 🌙💫
        if len(self.data) < 20:  # Ensure enough data points
            return
            
        current_close = self.data.Close[-1]
        volatility_ok = self.atr14[-1] > self.atr14_sma10[-1]
        
        # ===== POSITION MANAGEMENT =====
        if not self.position:
            if not volatility_ok:
                return  # Skip trades during low volatility
            
            # === LONG ENTRY === 🚀
            vi_bullish = (self.vi_plus[-1] > self.vi_minus[-1] and 
                        self.vi_plus[-2] <= self.vi_minus[-2])
            cmf_bullish = (self.cmf[-1] > 0 and self.cmf[-2] <= 0)
            price_above_kc = current_close > self.ema20[-1]
            
            if vi_bullish and cmf_bullish and price_above_kc:
                risk_amount = self.equity * self.risk_percent
                stop_price = self.kc_lower[-1]
                risk_per_share = current_close - stop_price
                
                if risk_per_share > 0:
                    size = int(round(risk_amount / risk_per_share))
                    if size > 0:
                        self.buy(size=size, sl=stop_price)
                        print(f"🌙 MOON ROCKET LAUNCH! 🚀 LONG {size} @ {current_close:.2f}"
                              f" | SL: {stop_price:.2f} | CMF: {self.cmf[-1]:.2f}")
            
            # === SHORT ENTRY === 🌪️
            vi_bearish = (self.vi_plus[-1] < self.vi_minus[-1] and 
                        self.vi_plus[-2] >= self.vi_minus[-2])
            cmf_bearish = (
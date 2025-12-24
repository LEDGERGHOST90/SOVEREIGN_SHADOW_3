Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed debug prints:

```python
# 🌙 Moon Dev's VolumetricVWAP Backtest 🌙
from backtesting import Backtest, Strategy
import talib
import pandas as pd
import numpy as np

class VolumetricVWAP(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    
    def init(self):
        # 🌌 Moon Dev Indicator Initialization Sequence Activated
        print("🌠 Initializing Moon Dev's Volumetric VWAP Strategy...")
        
        # 🌀 Calculate indicators using TA-Lib through self.I()
        typical_price = (self.data.High + self.data.Low + self.data.Close) / 3
        
        # 📊 VWAP Components
        typical_volume = typical_price * self.data.Volume
        self.sum_typical_vol = self.I(talib.SUM, typical_volume, timeperiod=20, name='SUM_TYP_VOL')
        self.sum_vol = self.I(talib.SUM, self.data.Volume, timeperiod=20, name='SUM_VOL')
        
        # 📈 Volatility Bands
        self.std_dev = self.I(talib.STDDEV, typical_price, timeperiod=20, nbdev=1, name='STDDEV_20')
        
        # 📉 Volume Surge Detection
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=960, name='VOL_MA_10D')  # 10 days in 15m intervals
        
        # 🛑 ATR for Risk Management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR_14')
        
        print("✨ Moon Dev Indicators Successfully Initialized!")

    def next(self):
        # ⚠️ Ensure enough data for calculations
        if len(self.data) < 960 or np.isnan(self.vol_ma[-1]):
            print("🌑 Waiting for sufficient data...")
            return
            
        # 🧮 Current Indicator Values
        vwap = self.sum_typical_vol[-1] / self.sum_vol[-1]
        upper_2std = vwap + 2*self.std_dev[-1]
        lower_2std = vwap - 2*self.std_dev[-1]
        upper_1std = vwap + self.std_dev[-1]
        lower_1std = vwap - self.std_dev[-1]
        
        # 🌊 Volume Surge Check
        volume_surge = self.data.Volume[-1] > 2*self.vol_ma[-1]
        
        # 📈📉 Entry/Exit Logic
        price = self.data.Close[-1]
        prev_price = self.data.Close[-2]
        
        if not self.position:
            # 🌕 Long Entry: Price breaks above upper band with volume surge
            if prev_price < upper_2std and price > upper_2std and volume_surge:
                print("🌖 Moon Dev Detected Potential Long Setup!")
                self.calculate_position_size(price, direction='long')
                
            # 🌑 Short Entry: Price breaks below lower band with volume surge
            elif prev_price > lower_2std and price < lower_2std and volume_surge:
                print("🌘 Moon Dev Detected Potential Short Setup!")
                self.calculate_position_size(price, direction='short')
        else:
            # 🎯 Check exit conditions
            if self.position.is_long and price <= upper_1std:
                self.position.close()
                print(f"🌗 Moon Dev Long Exit! ✨ Price: {price:.2f}")
            elif self.position.is_short and price >= lower_1std:
                self.position.close()
                print(f"🌓 Moon Dev Short Exit! 💨 Price: {price:.2f}")

    def calculate_position_size(self, entry_price, direction):
        """✨ Moon Dev's Risk-Managed Position Sizing ✨"""
        atr = self.atr[-1]
        stop_distance = 1.5 * atr
        risk_amount = self.equity * self.risk_per_trade
        
        if direction == 'long':
            stop_price = entry_price - stop_distance
        else:
            stop_price = entry_price + stop_distance
            
        risk_per_share = abs(entry_price - stop_price)
        position_size = int(round(risk_amount / risk_per_share))
        
        if position_size > 0:
            if direction == 'long':
                self.buy(size=position_size, sl=stop_price)
                print(f"🌕 Moon Dev Long
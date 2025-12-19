Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed enhancements: 🌙✨

```python
from backtesting import Backtest, Strategy
import pandas as pd
import pandas_ta as ta
import talib
import numpy as np

class VortexSurge(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    adx_threshold = 25
    exit_adx = 20
    volume_multiplier = 1.2
    atr_multiplier = 2
    
    def init(self):
        # Calculate indicators with proper self.I() wrapping
        self.vi_plus = self.I(self._calculate_vi_plus, self.data.High, self.data.Low, self.data.Close)
        self.vi_minus = self.I(self._calculate_vi_minus, self.data.High, self.data.Low, self.data.Close)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
    def _calculate_vi_plus(self, high, low, close):
        """Calculate Vortex Indicator (VI+) using pandas_ta"""
        vi = ta.vi(high=high, low=low, close=close, length=14)
        return vi['VIPT']
    
    def _calculate_vi_minus(self, high, low, close):
        """Calculate Vortex Indicator (VI-) using pandas_ta"""
        vi = ta.vi(high=high, low=low, close=close, length=14)
        return vi['VIMN']

    def next(self):
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Moon Dev debug prints 🌙
        if len(self.data) % 100 == 0:
            print(f"\n🌙 Moon Dev Status Update @ {self.data.index[-1]} ✨")
            print(f"   Close: {current_close:.2f}, VI+:{self.vi_plus[-1]:.2f}, VI-:{self.vi_minus[-1]:.2f}")
            print(f"   ADX: {self.adx[-1]:.2f}, Vol Ratio: {current_volume/self.vol_ma[-1]:.2f}x")
            print(f"   ATR: {self.atr[-1]:.2f}, Equity: {self.equity:.2f} 🌊")

        if not self.position:
            # Long entry condition (replaced crossover with manual check)
            if ((self.vi_plus[-2] < self.vi_minus[-2] and self.vi_plus[-1] > self.vi_minus[-1]) and
                self.adx[-1] > self.adx_threshold and
                current_volume > self.vol_ma[-1] * self.volume_multiplier):
                
                self._enter_trade('long', current_close)
            
            # Short entry condition (replaced crossover with manual check)
            elif ((self.vi_minus[-2] < self.vi_plus[-2] and self.vi_minus[-1] > self.vi_plus[-1]) and
                  self.adx[-1] > self.adx_threshold and
                  current_volume > self.vol_ma[-1] * self.volume_multiplier):
                
                self._enter_trade('short', current_close)
        
        else:
            # Exit condition for both long/short
            if self.adx[-1] < self.exit_adx:
                self.position.close()
                print(f"🌙🌊 ADX Collapse! Closing @ {current_close:.2f} (ADX: {self.adx[-1]:.2f}) ✨")

    def _enter_trade(self, direction, entry_price):
        """Moon Dev's Unified Trade Entry Logic 🚀"""
        atr_value = self.atr[-1]
        stop_loss = atr_value * self.atr_multiplier
        
        # Calculate position size with proper rounding
        risk_amount = self.equity * self.risk_percent
        position_size = risk_amount / (stop_loss if direction == 'long' else -stop_loss)
        position_size = int(round(position_size))
        
        if direction == 'long':
            sl_price = entry_price - stop_loss
            self.buy(size=position_size, sl=sl_price)
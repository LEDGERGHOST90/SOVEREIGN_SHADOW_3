Here's the fixed code with all backtesting.lib imports removed and replaced with proper implementations:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import pandas_ta as ta
import numpy as np
from backtesting import Backtest, Strategy

class LiquidationFracture(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    position_size = 1_000_000  # Initial equity (overridden by backtest)
    
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # Calculate indicators using TA-Lib with self.I()
        # Bollinger Bands components
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20, name='SMA20')
        self.stdev20 = self.I(talib.STDDEV, self.data.Close, timeperiod=20, nbdev=2, name='STDEV20')
        self.bb_upper = self.I(lambda sma, stdev: sma + 2*stdev, self.sma20, self.stdev20, name='BB_UPPER')
        self.bb_lower = self.I(lambda sma, stdev: sma - 2*stdev, self.sma20, self.stdev20, name='BB_LOWER')
        
        # Volatility and momentum
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14, name='RSI14')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR14')
        
        # Liquidity zones (proxy with swing highs/lows)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='SWING_LOW')
        
        # Volume analysis
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='VOLUME_MA20')
        
        print("🌙✨ Moon Dev Indicators Initialized! Ready to launch! 🚀")

    def next(self):
        # Skip initial bars without indicator data
        if len(self.data) < 20 or not all([self.sma20[-1], self.rsi[-1], self.atr[-1]]):
            return

        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Calculate BB squeeze condition
        bb_width_pct = (self.bb_upper[-1] - self.bb_lower[-1]) / self.sma20[-1] * 100
        squeeze_on = bb_width_pct < 1.5
        
        # Moon Dev themed debug prints 🌙
        print(f"🌙 Close: {current_close:.2f} | RSI: {self.rsi[-1]:.2f} | BB%: {bb_width_pct:.2f}% | Volume: {current_volume:.2f}/{self.volume_ma[-1]:.2f}")

        if not self.position:
            # Long entry conditions
            if (current_close > self.swing_high[-1] and
                current_volume > 1.2 * self.volume_ma[-1] and
                squeeze_on and
                40 < self.rsi[-1] < 60):
                
                self.enter_long()
            
            # Short entry conditions
            elif (current_close < self.swing_low[-1] and
                  current_volume > 1.2 * self.volume_ma[-1] and
                  squeeze_on and
                  40 < self.rsi[-1] < 60):
                
                self.enter_short()

        else:
            # Check exit conditions
            if self.position.is_long:
                if current_close >= self.position.tp:
                    print(f"🌙✨ PROFIT TAKEN! Riding moon dust back home! 🌕💫 (Price: {current_close:.2f})")
                    self.position.close()
            elif self.position.is_short:
                if current_close <= self.position.tp:
                    print(f"🌙✨ SHORT COVERED! Gravity works in space! 🌌⬇️ (Price: {current_close:.2f})")
                    self.position.close()

    def enter_long(self):
Here's the fixed code with all necessary replacements and Moon Dev themed improvements:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest

class LiquidationBandit(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    atr_period = 14
    swing_period = 20
    volume_multiplier = 1.5
    fib_levels = [0.382, 0.5, 0.618]

    def init(self):
        # Clean and prepare data 🌙 Lunar Data Preparation
        self.data.df.columns = self.data.df.columns.str.lower().str.strip()
        
        # Core indicators ✨ Moon-powered Indicators
        self.oi_pct = self.I(lambda x: x.pct_change(4)*100, 
                           self.data.OpenInterest, name='OI_PCT')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                        self.data.Close, timeperiod=self.atr_period)
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=14)
        
        # VWVB Calculation 🌙 Volatility-Weighted Value Bands
        self.vwvb_upper = self.I(lambda c,atr,vol: c + (atr * (vol/self.vol_sma)),
                           self.data.Close, self.atr, self.data.Volume, name='VWVB_UPPER')
        self.vwvb_lower = self.I(lambda c,atr,vol: c - (atr * (vol/self.vol_sma)),
                           self.data.Close, self.atr, self.data.Volume, name='VWVB_LOWER')
        
        # Swing detection ✨ Lunar Swing Points
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='SWING_LOW')
        
        # Trend filter 🚀 Moon Phase Trend
        self.sma_200 = self.I(talib.SMA, self.data.Close, timeperiod=200, name='SMA_200')

    def next(self):
        if self.position:
            return  # No pyramiding

        # Liquidation cluster detection 🌪️ Moonquake Detection
        oi_drop = self.oi_pct[-1] <= -10
        vol_surge = self.data.Volume[-1] > self.vol_sma[-1]*self.volume_multiplier
        
        if oi_drop and vol_surge:
            price = self.data.Close[-1]
            trend_dir = 'BEARISH' if price < self.sma_200[-1] else 'BULLISH'
            
            print(f"🌙 MOON DEV ALERT! Liquidation Cluster Detected")
            print(f"📉 OI Drop: {self.oi_pct[-1]:.2f}% | 📈 Volume Surge: {self.data.Volume[-1]:.2f}")
            
            # Long setup (Short squeeze) 🌕 Full Moon Setup
            if self.data.High[-1] > self.vwvb_upper[-1] and trend_dir == 'BEARISH':
                self.enter_long()
                
            # Short setup (Long liquidation) 🌑 New Moon Setup
            elif self.data.Low[-1] < self.vwvb_lower[-1] and trend_dir == 'BULLISH':
                self.enter_short()

    def enter_long(self):
        entry = self.vwvb_upper[-1]
        sl = max(self.vwvb_lower[-1], self.swing_low[-1])
        swing_range = self.swing_high[-1] - self.swing_low[-1]
        
        # Risk calculation 🔒 Moon Shield Protection
        risk_amount = self.risk_per_trade * self.equity
        risk_per_share = entry - sl
        position_size = int(round(risk_amount / risk_per_share))
        
        if position_size <= 0:
            print("🌘 Position size too small - Moon dust!")
            return
            
        # Fib targets 🌉 Moon Bridge Targets
        targets = [entry + swing_range * lvl for lvl in self.fib_levels]
        
        self.buy(size=position_size, sl=sl, tp=targets[0])
        print(f"🚀 LONG ENTRY! Size: {position_size}")
        print(f"🎯 Targets: {targets}")

    def enter_short(self):
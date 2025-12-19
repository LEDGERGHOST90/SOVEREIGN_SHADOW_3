Here's the fully debugged and Moon Dev optimized backtest code with all technical issues fixed while preserving the original strategy logic:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT - FIBRODELTA BREAKOUT STRATEGY 🚀✨

import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class FibroDeltaBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade (proper fraction for equity sizing)
    
    def init(self):
        # 🌌 INITIALIZING MOON DEV STRATEGY...
        print("🌠 PREPARING COSMIC INDICATORS...")
        
        # 🌀 Fibonacci Indicators (fixed indicator calculations)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='SWING HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='SWING LOW')
        
        # 🌊 Delta Volume Calculation (fixed function definition)
        def delta_vol(close, open_, vol):
            return np.where(close > open_, vol, -vol)
        self.delta = self.I(delta_vol, self.data.Close, self.data.Open, self.data.Volume, name='DELTA VOL')
        
        # 🌠 Cumulative Delta with Moon-themed smoothing
        self.cum_delta = self.I(lambda x: np.cumsum(x), self.delta, name='CUM DELTA')
        
        # 🎯 Divergence Detection (fixed indicator periods)
        self.price_high = self.I(talib.MAX, self.data.High, timeperiod=5, name='PRICE HIGH')
        self.delta_high = self.I(talib.MAX, self.cum_delta, timeperiod=5, name='DELTA HIGH')
        
        # 📊 Volume Imbalance Proxy (fixed SMA calculation)
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=50, name='VOL MA')

    def next(self):
        # 🌙 MOON DEV CORE LOGIC
        if len(self.data) < 50:  # Ensure warmup period
            return
            
        # 🌀 Fibonacci Cluster Calculation (fixed array indexing)
        sh = self.swing_high[-1]
        sl = self.swing_low[-1]
        fib38 = sl + 0.382*(sh - sl)
        fib618 = sl + 0.618*(sh - sl)
        current_close = self.data.Close[-1]
        
        # 🌓 Delta Divergence Check (fixed comparison logic)
        price_div = self.price_high[-1] > self.price_high[-2]
        delta_div = self.delta_high[-1] < self.delta_high[-2]
        
        # 🌌 Order Book Imbalance Proxy (fixed volume comparison)
        vol_imbalance = self.data.Volume[-1] > self.vol_ma[-1]
        
        # 🚀 Long Entry Logic (fixed position sizing)
        if (not self.position and
            current_close > fib618 and
            price_div and delta_div and
            vol_imbalance):
            
            # 🌙 Risk Calculation (proper integer rounding)
            stop_loss = sl
            risk = current_close - stop_loss
            position_size = int(round((self.risk_per_trade * self.equity) / risk))
            
            if position_size > 0:
                # 🎯 Take Profit Calculation (127% extension)
                tp = current_close + (sh - sl) * 0.272
                self.buy(size=position_size, sl=stop_loss, tp=tp)
                print(f"🌕 MOON DEV LONG SIGNAL! Size: {position_size:,} | Entry: {current_close:.2f} | SL: {stop_loss:.2f} | TP: {tp:.2f} 🌙")
        
        # 🌑 Short Entry Logic (fixed position sizing)
        elif (not self.position and
              current_close < fib38 and
              price_div and delta_div and
              vol_imbalance):
            
            # 🌙 Risk Calculation (proper integer rounding)
            stop_loss = sh
            risk = stop_loss - current_close
            position_size = int(round((self.risk_per_trade * self.equity) / risk))
            
            if position_size > 0:
                # 🎯 Take Profit Calculation
                tp = current_close - (sh - sl) * 0.272
                self.sell(size=position_size, sl=stop_loss, tp=tp)
                print(f"🌑 MOON DEV SHORT SIGNAL! Size: {position_size:,} |
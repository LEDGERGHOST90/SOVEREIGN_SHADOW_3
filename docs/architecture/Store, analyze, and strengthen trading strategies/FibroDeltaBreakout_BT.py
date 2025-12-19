Here's the complete backtesting implementation for the FibroDeltaBreakout strategy:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT - FIBRODELTA BREAKOUT STRATEGY 🚀

import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class FibroDeltaBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 Data Preparation Checks
        print("🌌 INITIALIZING MOON DEV STRATEGY...")
        
        # 🌀 Fibonacci Indicators
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='SWING HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='SWING LOW')
        
        # 🌊 Delta Volume Calculation
        def delta_vol(close, open, vol):
            return np.where(close > open, vol, -vol)
        self.delta = self.I(delta_vol, self.data.Close, self.data.Open, self.data.Volume, name='DELTA VOL')
        
        # 🌠 Cumulative Delta with Moon-themed smoothing
        self.cum_delta = self.I(lambda x: np.cumsum(x), self.delta, name='CUM DELTA')
        
        # 🎯 Divergence Detection
        self.price_high = self.I(talib.MAX, self.data.High, 5, name='PRICE HIGH')
        self.delta_high = self.I(talib.MAX, self.cum_delta, 5, name='DELTA HIGH')
        
        # 📊 Volume Imbalance Proxy
        self.vol_ma = self.I(talib.SMA, self.data.Volume, 50, name='VOL MA')

    def next(self):
        # 🌙 MOON DEV CORE LOGIC
        if len(self.data) < 50:  # Ensure warmup period
            return
            
        # 🌀 Fibonacci Cluster Calculation
        sh = self.swing_high[-1]
        sl = self.swing_low[-1]
        fib38 = sl + 0.382*(sh - sl)
        fib618 = sl + 0.618*(sh - sl)
        current_close = self.data.Close[-1]
        
        # 🌓 Delta Divergence Check
        price_div = self.price_high[-1] > self.price_high[-2]
        delta_div = self.delta_high[-1] < self.delta_high[-2]
        
        # 🌌 Order Book Imbalance Proxy
        vol_imbalance = self.data.Volume[-1] > self.vol_ma[-1]
        
        # 🚀 Long Entry Logic
        if (not self.position and
            current_close > fib618 and
            price_div and delta_div and
            vol_imbalance):
            
            # 🌙 Risk Calculation
            stop_loss = sl
            risk = current_close - stop_loss
            position_size = int(round((self.risk_per_trade * self.equity) / risk))
            
            if position_size > 0:
                # 🎯 Take Profit Calculation (127% extension)
                tp = current_close + (sh - sl) * 0.272
                self.buy(size=position_size, sl=stop_loss, tp=tp)
                print(f"🌕 MOON DEV LONG! Size: {position_size:,} | Entry: {current_close:.2f} 🌙")
        
        # 🌑 Short Entry Logic
        elif (not self.position and
              current_close < fib38 and
              price_div and delta_div and
              vol_imbalance):
            
            # 🌙 Risk Calculation
            stop_loss = sh
            risk = stop_loss - current_close
            position_size = int(round((self.risk_per_trade * self.equity) / risk))
            
            if position_size > 0:
                # 🎯 Take Profit Calculation
                tp = current_close - (sh - sl) * 0.272
                self.sell(size=position_size, sl=stop_loss, tp=tp)
                print(f"🌑 MOON DEV SHORT! Size: {position_size:,} | Entry: {current_close:.2f} 🌙")

# 🌙 DATA PREPARATION
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# 🧹 Data Cleaning Ritual
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if '
Here's the fully debugged and Moon Dev themed version of your ClusterBandwidth strategy code:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Moon Dev's ClusterBandwidth Strategy 🌙✨
class ClusterBandwidth(Strategy):
    def init(self):
        # Clean data columns (already preprocessed)
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        
        # ====== INDICATOR CALCULATION ======
        # Bollinger Bands (20,2)
        def bb_upper(close):
            upper, _, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            return upper
        self.upper = self.I(bb_upper, self.data.Close)
        
        def bb_lower(close):
            _, _, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            return lower
        self.lower = self.I(bb_lower, self.data.Close)
        
        # Bollinger Bandwidth calculations 🌗
        self.mid = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.bb_width = (self.upper - self.lower) / self.mid
        self.bb_width_avg = self.I(talib.SMA, self.bb_width, timeperiod=20)
        
        # Liquidation clusters using swing high/low 🌌
        self.cluster_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.cluster_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        # Volatility measurements 🌊
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # Volume confirmation 📊
        self.vol_avg = self.I(talib.SMA, self.data.Volume, timeperiod=20)

    def next(self):
        # ====== RISK MANAGEMENT ======
        current_equity = self.equity
        risk_per_trade = current_equity * 0.01  # 1% risk per trade 🛡️
        
        # ====== ENTRY LOGIC ======
        if not self.position:
            # Long entry conditions 🌕
            if (self.bb_width[-1] < self.bb_width_avg[-1] and
                self.data.Close[-1] > self.cluster_high[-1] and
                self.data.Volume[-1] > self.vol_avg[-1] and
                self.data.Close[-1] > self.mid[-1]):
                
                sl = self.data.Close[-1] - self.atr[-1]
                position_size = int(round(risk_per_trade / (self.data.Close[-1] - sl)))
                self.buy(size=position_size, sl=sl, tp=self.data.Close[-1] + 2*self.atr[-1], tag={
                    'type': 'long',
                    'cluster': self.cluster_high[-1],
                    'atr_entry': self.atr[-1],
                    'entry_price': self.data.Close[-1],
                    'sl': sl,
                    'tp': self.data.Close[-1] + 2*self.atr[-1]
                })
                print(f"🌙✨🚀 LONG ENTRY @ {self.data.Close[-1]:.2f} | Size: {position_size} | Moon Power Activated! 🌕")

            # Short entry conditions 🌑
            elif (self.bb_width[-1] < self.bb_width_avg[-1] and
                  self.data.Close[-1] < self.cluster_low[-1] and
                  self.data.Volume[-1] > self.vol_avg[-1] and
                  self.data.Close[-1] < self.mid[-1]):
                
                sl = self.data.Close[-1] + self.atr[-1]
                position_size = int(round(risk_per_trade / (sl - self.data.Close[-1])))
                self.sell(size=position_size, sl=sl, tp=self.data.Close[-1] - 2*self.atr[-1], tag={
                    'type': 'short',
                    'cluster': self.cluster_low[-1],
                    'atr_entry': self.atr[-1],
                    'entry_price': self.data.Close[-1],
                    'sl': sl,
                    'tp': self.data.Close[-1] - 2*self.atr[-1]
                })
                print(f
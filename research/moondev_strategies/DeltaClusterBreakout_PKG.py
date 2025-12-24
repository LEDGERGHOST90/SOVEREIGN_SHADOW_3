Here's the fixed code with all backtesting.lib references removed and replaced with proper Moon Dev themed implementations:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class DeltaClusterBreakout(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    cmo_period = 14
    swing_period = 20
    atr_period = 14
    pivot_window = 96  # 96*15m = 24h
    
    def init(self):
        # Clean data columns
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # Core Indicators 🌙
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='SWING HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='SWING LOW')
        self.cmo = self.I(talib.CMO, self.data.Close, timeperiod=self.cmo_period, name='CMO')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period, name='ATR')
        
        # Dynamic Pivot Points ✨
        prev_high = self.I(talib.MAX, self.data.High, timeperiod=self.pivot_window)
        prev_low = self.I(talib.MIN, self.data.Low, timeperiod=self.pivot_window)
        prev_close = self.I(talib.EMA, self.data.Close, timeperiod=self.pivot_window)
        self.pivot = (prev_high + prev_low + prev_close) / 3
        self.r1 = self.I(lambda x: x, (2 * self.pivot) - prev_low)
        self.s1 = self.I(lambda x: x, (2 * self.pivot) - prev_high)
        
        # Risk Management Trackers 🚀
        self.consecutive_losses = 0
        self.last_entry_bar = 0

    def next(self):
        # Skip trades after 3 consecutive losses 🌑
        if self.consecutive_losses >= 3:
            print("🌑🌙✨ Three cosmic losses! Entering cooldown phase...")
            return
        
        price = self.data.Close[-1]
        atr = self.atr[-1]
        min_stop = 1.5 * atr
        
        # Long Entry Constellation 🌟
        if not self.position and (self.data.Close[-2] < self.swing_high[-2] and self.data.Close[-1] > self.swing_high[-1]):
            if self.cmo[-1] > 50 and self.cmo[-2] <= 50:
                risk_amount = self.risk_pct * self.equity
                stop_price = price - min_stop
                position_size = int(round(risk_amount / (price - stop_price)))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_price, tp=price + 3*min_stop)
                    print(f"🚀🌙 LONG ENTRY @ {price:.2f} | Size: {position_size} | CMO: {self.cmo[-1]:.2f} | Cosmic Thrusters Engaged!")
        
        # Short Entry Nebula 🌌
        elif not self.position and (self.data.Close[-2] > self.swing_low[-2] and self.data.Close[-1] < self.swing_low[-1]):
            if self.cmo[-1] < -50 and self.cmo[-2] >= -50:
                risk_amount = self.risk_pct * self.equity
                stop_price = price + min_stop
                position_size = int(round(risk_amount / (stop_price - price)))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_price, tp=price - 3*min_stop)
                    print(f"🌠🌙 SHORT ENTRY @ {price:.2f} | Size: {position_size} | CMO: {self.cmo[-1]:.2f} | Gravitational Collapse Initiated!")
        
        # Trailing Stop Management 🌕
        for trade in self.trades:
            if trade.is_long:
                new_sl = max(trade.sl or 0, self.s1[-1])
                if new_sl > trade.s
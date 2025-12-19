I'll help fix the code while maintaining the strategy logic. Here's the corrected version with Moon Dev themed debug prints and proper position sizing:

```python
# -*- coding: utf-8 -*-
import backtrader as bt
import talib
import numpy as np

class DivergenceAnchor(bt.Strategy):
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('swing_period', 20),
        ('risk_percent', 0.01),
        ('rr_ratio', 2)
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'🌙 {dt.strftime("%Y-%m-%d %H:%M")} ✨ {txt}')

    def __init__(self):
        # MACD components using TA-Lib
        self.macd_line = self.I(lambda: talib.MACD(self.data.Close, 
                                                 self.p.macd_fast,
                                                 self.p.macd_slow,
                                                 self.p.macd_signal)[0],
                              name='MACD Line')
        self.macd_hist = self.I(lambda: talib.MACD(self.data.Close,
                                                  self.p.macd_fast,
                                                  self.p.macd_slow,
                                                  self.p.macd_signal)[2],
                               name='MACD Histogram')
        
        # Swing high/low indicators
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.p.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.p.swing_period)
        
        self.peaks = []  # Stores (price_high, macd_value) tuples
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'🚀 BUY EXECUTED - Size: {order.size} @ {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'🌑 SELL EXECUTED - Size: {order.size} @ {order.executed.price:.2f}')

    def next(self):
        # Moon Dev Divergence Detection System 🌙
        current_high = self.data.High[0]
        current_swing_high = self.swing_high[0]
        
        # Detect new swing high formation
        if current_high == current_swing_high:
            if len(self.peaks) >= 1:
                last_high, last_macd = self.peaks[-1]
                
                # Bearish divergence condition
                if (current_high > last_high) and (self.macd_line[0] < last_macd):
                    self.log(f'🔻 BEARISH DIVERGENCE DETECTED! Price ↗️ {current_high:.2f} vs {last_high:.2f}, MACD ↘️ {self.macd_line[0]:.2f} vs {last_macd:.2f}')
                    
                    if self.macd_hist[0] < 0:  # Confirm bearish momentum
                        self.log('📉 MACD Histogram confirms bearish momentum')
                        self.check_entry_conditions()

            # Update peaks array (keep last 2 peaks)
            self.peaks.append((current_high, self.macd_line[0]))
            if len(self.peaks) > 2:
                self.peaks.pop(0)

        # Exit conditions
        if self.position:
            self.check_exit_conditions()

    def check_entry_conditions(self):
        '''Moon Dev Entry Logic Validation 🌙'''
        current_low = self.data.Low[0]
        current_close = self.data.Close[0]
        support_level = self.swing_low[0]
        
        # Price action confirmation
        if current_close > support_level and current_low >= support_level:
            self.log(f'✨ PRICE BOUNCE CONFIRMED @ {support_level:.2f}')
            self.execute_long_entry(support_level)

    def execute_long_entry(self, support):
        '''Moon Dev Risk-Managed Entry 🚀'''
        account_value = self.broker.getvalue()
        risk_amount = account_value * self.p.risk_percent
        
        # Calculate stop loss 0.5% below support
        stop_loss = support * 0.995
        risk_per_unit = self.data.Close[0] - stop_loss
        
        # Calculate position size
        if risk_per_unit > 0:
            size = int(risk_amount / risk_per_unit)  # Convert to whole units
```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR VORTEXVOLUMEBREAKOUT STRATEGY 🚀✨

import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

class VortexVolumeBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 CALCULATE INDICATORS USING TA-LIB
        self.vi_plus, self.vi_minus = self.I(talib.VORTEX, 
                                           self.data.High, self.data.Low, self.data.Close, 
                                           14, name='Vortex')
        
        self.adx = self.I(talib.ADX,
                         self.data.High, self.data.Low, self.data.Close,
                         14, name='ADX')
        
        self.obv = self.I(talib.OBV,
                         self.data.Close, self.data.Volume,
                         name='OBV')
        
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='SwingHigh')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='SwingLow')
        
        # 🌙 MOON DEV DEBUG INIT
        print("✨🌙 VORTEX VOLUME BREAKOUT INITIALIZED! Indicators ready for launch! 🚀")

    def next(self):
        if len(self.data) < 20:  # Wait for indicators to warm up
            return

        # 🌙 CORE TRADE LOGIC
        price = self.data.Close[-1]
        adx_value = self.adx[-1]
        
        # 🛑 Exit conditions for open positions
        if self.position:
            if self.position.is_long:
                self.handle_long_exits(price, adx_value)
            else:
                self.handle_short_exits(price, adx_value)
        
        # 🚀 Entry conditions
        else:
            self.check_long_entry()
            self.check_short_entry()

    def check_long_entry(self):
        vi_bullish = crossover(self.vi_plus, self.vi_minus)
        obv_trend = self.obv[-1] > np.max(self.obv[-6:-1])  # Higher OBV highs
        adx_strong = self.adx[-1] > 30
        price_break = self.data.Close[-1] > self.swing_high[-1]

        if vi_bullish and obv_trend and adx_strong and price_break:
            sl = self.swing_low[-1]
            self.calculate_position_size(sl, long=True)

    def check_short_entry(self):
        vi_bearish = crossover(self.vi_minus, self.vi_plus)
        obv_trend = self.obv[-1] < np.min(self.obv[-6:-1])  # Lower OBV highs
        adx_strong = self.adx[-1] > 30
        price_break = self.data.Close[-1] < self.swing_low[-1]

        if vi_bearish and obv_trend and adx_strong and price_break:
            sl = self.swing_high[-1]
            self.calculate_position_size(sl, long=False)

    def calculate_position_size(self, sl_price, long=True):
        entry_price = self.data.Close[-1]
        risk_per_share = abs(entry_price - sl_price)
        
        if risk_per_share == 0:
            print("🌑 ZERO RISK TRADE DETECTED! Aborting launch sequence")
            return

        risk_amount = self.equity * self.risk_per_trade
        position_size = int(round(risk_amount / risk_per_share))
        
        if position_size > 0:
            if long:
                self.buy(size=position_size, sl=sl_price,
                        tag="🌙 BULLISH BREAKOUT! Entry: {:.2f} SL: {:.2f}".format(entry_price, sl_price))
                tp_price = entry_price + 2*(entry_price - sl_price)
                print(f"🚀 LONG LAUNCH! Size: {position_size} | TP: {tp_price:.2f}")
            else:
                self.sell(size=position_size, sl=sl_price,
                         tag="🌑 BEARISH BREAKDOWN! Entry: {:.2f} SL: {:.2f}".format(entry_price, sl_price))
                tp_price = entry_price - 2*(sl_price - entry_price)
                print(f"🌑 SHORT LAUNCH!
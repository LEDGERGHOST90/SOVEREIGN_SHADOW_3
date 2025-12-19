```python
# 🌙 Moon Dev Backtest AI Implementation for VortexKST Surge Strategy 🚀

import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib
import pandas_ta as ta

class VortexKSTSurge(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌕
    
    def init(self):
        # 🌙 Clean data and prepare indicators using self.I()
        self._prepare_indicators()
        
    def _prepare_indicators(self):
        # Vortex Indicator (14-period) ✨
        high = self.data.High.astype('float64')
        low = self.data.Low.astype('float64')
        close = self.data.Close.astype('float64')
        vortex = ta.vortex(high=high, low=low, close=close, length=14)
        self.vi_plus = self.I(lambda: vortex['VMP_14'], name='VI+')
        self.vi_minus = self.I(lambda: vortex['VMM_14'], name='VI-')

        # KST Oscillator 📈
        roc10 = talib.ROC(close, timeperiod=10)
        rcma1 = talib.SMA(roc10, 10)
        roc15 = talib.ROC(close, timeperiod=15)
        rcma2 = talib.SMA(roc15, 10)
        roc20 = talib.ROC(close, timeperiod=20)
        rcma3 = talib.SMA(roc20, 10)
        roc30 = talib.ROC(close, timeperiod=30)
        rcma4 = talib.SMA(roc30, 15)
        kst = rcma1 + rcma2 + rcma3 + rcma4
        signal = talib.SMA(kst, 9)
        self.kst_line = self.I(lambda: kst, name='KST')
        self.signal_line = self.I(lambda: signal, name='KST Signal')

        # Bollinger Bands (20,2) 🎯
        upper, _, lower = talib.BBANDS(close, 20, 2, 2)
        self.bb_upper = self.I(lambda: upper, name='BB Upper')
        self.bb_lower = self.I(lambda: lower, name='BB Lower')

        # Volume Surge Filter (20-day MA) 🌊
        vol_ma_period = 20 * 24 * 4  # 15m data → 1920 periods
        self.vol_ma = self.I(talib.SMA, self.data.Volume, vol_ma_period, name='Vol MA')

        # Swing High/Low for Stops (20-period) 🛑
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='Swing High')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='Swing Low')

    def next(self):
        # 🌙 Moon Dev Entry/Exit Logic ✨
        if not self.position:
            self._check_entries()
        else:
            self._check_exits()
            self._check_stop_loss()

    def _check_entries(self):
        # Long Entry Conditions 🚀
        vi_bullish = crossover(self.vi_plus, self.vi_minus)
        kst_bullish = crossover(self.kst_line, self.signal_line)
        vol_surge = self.data.Volume[-1] > 1.5 * self.vol_ma[-1]
        
        if vi_bullish and kst_bullish and vol_surge:
            self._enter_long()

        # Short Entry Conditions 🌪️
        vi_bearish = crossover(self.vi_minus, self.vi_plus)
        kst_bearish = crossover(self.signal_line, self.kst_line)
        
        if vi_bearish and kst_bearish and vol_surge:
            self._enter_short()

    def _enter_long(self):
        stop_price = self.swing_low[-1]
        risk = self.data.Close[-1] - stop_price
        if risk <= 0: return
        
        size = int(round((self.broker.get_value() * self.risk_percent) / risk))
        self.buy(size=size, sl=stop_price)
        print(f"🌙✨ LONG! 🚀 Size: {size}, Entry: {self.data.Close[-1]:.2f}, Stop: {stop_price:.2f}")
```python
# -*- coding: utf-8 -*-
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib
import numpy as np

class DivergentPulse(Strategy):
    risk_pct = 0.01
    atr_period = 14
    swing_window = 5
    
    def init(self):
        # Calculate core indicators 🌙
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close, 
                                               fastperiod=12, slowperiod=26, signalperiod=9)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=self.atr_period)
        
        # Swing detection indicators ✨
        self.price_highs = self.I(talib.MAX, self.data.High, timeperiod=self.swing_window)
        self.price_lows = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_window)
        self.macd_highs = self.I(talib.MAX, self.macd, timeperiod=self.swing_window)
        self.macd_lows = self.I(talib.MIN, self.macd, timeperiod=self.swing_window)
        self.rsi_highs = self.I(talib.MAX, self.rsi, timeperiod=self.swing_window)
        self.rsi_lows = self.I(talib.MIN, self.rsi, timeperiod=self.swing_window)
        
        # Track swing points and trade date 🗓️
        self.last_trade_date = None
        self.price_swings = []
        self.macd_swings = []
        self.rsi_swings = []

    def next(self):
        current_date = self.data.index[-1].date()
        if self.last_trade_date == current_date:
            return  # Moon Dev Rule: 1 trade per day 🌙
            
        # Detect new swings 🌊
        self._update_swings()
        
        # Check for divergences 🔄
        bull_div, bear_div = self._detect_divergence()
        
        # Execute trades with cosmic precision 🚀
        if bull_div and not self.position:
            self._enter_long()
        elif bear_div and not self.position:
            self._enter_short()

    def _update_swings(self):
        # Price swings
        if self.data.High[-1] == self.price_highs[-1]:
            self.price_swings.append(('high', self.data.High[-1]))
        if self.data.Low[-1] == self.price_lows[-1]:
            self.price_swings.append(('low', self.data.Low[-1]))
            
        # MACD swings
        if self.macd[-1] == self.macd_highs[-1]:
            self.macd_swings.append(('high', self.macd[-1]))
        if self.macd[-1] == self.macd_lows[-1]:
            self.macd_swings.append(('low', self.macd[-1]))
            
        # RSI swings
        if self.rsi[-1] == self.rsi_highs[-1]:
            self.rsi_swings.append(('high', self.rsi[-1]))
        if self.rsi[-1] == self.rsi_lows[-1]:
            self.rsi_swings.append(('low', self.rsi[-1]))

    def _detect_divergence(self):
        # Need at least two swings in all dimensions 📈
        if len(self.price_swings) < 2 or len(self.macd_swings) < 2 or len(self.rsi_swings) < 2:
            return False, False
            
        # Get last two valid swings 🔙🔚
        price_swing = self.price_swings[-2:]
        macd_swing = self.macd_swings[-2:]
        rsi_swing = self.rsi_swings[-2:]
        
        # Bullish divergence detection 🌕
        bull = (price_swing[-1][0] == 'low' and price_swing[-2][0] == 'low' and
                price_swing[-1][1] < price_swing[-2][1] and
                macd_swing[-1][1] > macd_swing[-2][1] and
                rsi_swing[-1][1] > rsi_swing[-2][1])
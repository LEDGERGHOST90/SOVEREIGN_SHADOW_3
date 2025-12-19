```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

class VoltaConverge(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    atr_period = 14
    rsi_period = 14
    swing_period = 5
    atr_threshold = 100  # Adjust based on asset volatility
    
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # Calculate indicators using TA-Lib
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        
        # MACD components
        self.macd_line = self.I(lambda c: talib.EMA(c, 12) - talib.EMA(c, 26), close)
        self.signal_line = self.I(talib.EMA, self.macd_line, 9)
        self.macd_hist = self.I(lambda m,s: m-s, self.macd_line, self.signal_line)
        
        # RSI and volatility
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        
        # Swing points
        self.swing_high = self.I(talib.MAX, high, self.swing_period)
        self.swing_low = self.I(talib.MIN, low, self.swing_period)
        self.macd_swing_high = self.I(talib.MAX, self.macd_line, self.swing_period)
        self.macd_swing_low = self.I(talib.MIN, self.macd_line, self.swing_period)
        
    def next(self):
        if self.position:
            return  # No new trades if position exists
            
        price = self.data.Close[-1]
        current_atr = self.atr[-1]
        
        # Get swing points
        price_swing_low = self.swing_low[-1]
        prev_price_swing_low = self.swing_low[-2] if len(self.swing_low) > 1 else None
        macd_swing_low = self.macd_swing_low[-1]
        prev_macd_swing_low = self.macd_swing_low[-2] if len(self.macd_swing_low) > 1 else None
        
        price_swing_high = self.swing_high[-1]
        prev_price_swing_high = self.swing_high[-2] if len(self.swing_high) > 1 else None
        macd_swing_high = self.macd_swing_high[-1]
        prev_macd_swing_high = self.macd_swing_high[-2] if len(self.macd_swing_high) > 1 else None
        
        # Divergence detection
        bullish_div = (prev_price_swing_low and price_swing_low < prev_price_swing_low and
                      macd_swing_low > prev_macd_swing_low)
        bearish_div = (prev_price_swing_high and price_swing_high > prev_price_swing_high and
                      macd_swing_high < prev_macd_swing_high)
        
        # RSI conditions
        rsi_oversold = self.rsi[-1] < 30 and self.rsi[-1] > self.rsi[-2]
        rsi_overbought = self.rsi[-1] > 70 and self.rsi[-1] < self.rsi[-2]
        
        # Entry logic
        if bullish_div and rsi_oversold and current_atr > self.atr_threshold:
            self.enter_long(price, current_atr)
            
        elif bearish_div and rsi_overbought and current_atr > self.atr_threshold:
            self.enter_short(price, current_atr)
            
    def enter_long(self, price, atr):
        sl = price - atr * 1
        tp = price + atr * 2
        risk_amount = self.equity * self.risk_per_trade
        position_size = int(round(risk_amount
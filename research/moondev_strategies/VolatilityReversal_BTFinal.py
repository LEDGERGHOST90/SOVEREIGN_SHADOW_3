I'll help fix the incomplete code and add Moon Dev themed debug prints. Here's the complete fixed version:

```python
# 🌙 Moon Dev's VolatilityReversal Backtest Script 🚀

import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class VolatilityReversal(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌊
    atr_multiplier = 1.5  # ATR expansion threshold ✨

    def init(self):
        # 🌗 Indicator Calculations using TA-Lib
        # MACD components
        macd, macd_signal, _ = talib.MACD(self.data.Close, 12, 26, 9)
        self.I(lambda: macd, name='MACD')
        self.I(lambda: macd_signal, name='MACD_Signal')

        # Bollinger Bands
        bb_upper, _, bb_lower = talib.BBANDS(self.data.Close, 20, 2)
        self.I(lambda: bb_upper, name='BB_Upper')
        self.I(lambda: bb_lower, name='BB_Lower')

        # RSI
        rsi = talib.RSI(self.data.Close, 14)
        self.I(lambda: rsi, name='RSI')

        # ATR and its moving average
        atr = talib.ATR(self.data.High, self.data.Low, self.data.Close, 14)
        self.I(lambda: atr, name='ATR')
        self.I(lambda: talib.SMA(atr, 14), name='ATR_MA')

        # Price Channel (20-period)
        self.I(lambda: talib.MAX(self.data.High, 20), name='Channel_High')
        self.I(lambda: talib.MIN(self.data.Low, 20), name='Channel_Low')

        # Swing Low (20-period)
        self.I(lambda: talib.MIN(self.data.Low, 20), name='Swing_Low')

        # Track equity peak for drawdown calculation
        self.peak_equity = self._broker.starting_cash
        self.max_drawdown = 0.15  # 15% max allowed 🌑

    def next(self):
        # 🌑 Check maximum drawdown limit
        current_equity = self.equity
        self.peak_equity = max(self.peak_equity, current_equity)
        drawdown = (self.peak_equity - current_equity) / self.peak_equity
        if drawdown >= self.max_drawdown:
            print(f"🌑🌑 MOON DEV EMERGENCY: Max Drawdown Breached {drawdown:.2%}! Stopping trading.")
            self.position.close()
            return

        # Entry Logic 🌙✨
        if not self.position:
            # MACD bullish crossover
            macd_cross = (self.data.MACD[-2] < self.data.MACD_Signal[-2] and 
                        self.data.MACD[-1] > self.data.MACD_Signal[-1])
            
            # Bollinger Band expansion (current width > previous width)
            bb_width = self.data.BB_Upper[-1] - self.data.BB_Lower[-1]
            bb_expansion = bb_width > (self.data.BB_Upper[-2] - self.data.BB_Lower[-2])
            
            # Oversold condition
            rsi_oversold = self.data.RSI[-1] < 30
            
            # Price near lower band
            price_position = self.data.Close[-1] <= self.data.BB_Lower[-1]

            if all([macd_cross, bb_expansion, rsi_oversold, price_position]):
                # 🚀 Calculate position size with proper rounding
                sl_level = min(self.data.Swing_Low[-1], self.data.BB_Lower[-1])
                risk_amount = self.risk_per_trade * self.equity
                risk_per_share = self.data.Open[-1] - sl_level
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl_level,
                                tp=self.data.Channel_High[-1])
                        print(f"🌙✨ MOON DEV ENTRY: Long {position_size} @ {self.data.Open[-1]:.2f} | SL: {sl_level:.2f} | TP: {self.data.Channel_High[-1]:.2f}")

        # Exit Logic 🚀🌊
        elif self.position:
            #
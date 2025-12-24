I'll help fix the incomplete code and ensure it meets all technical requirements. Here's the complete and debugged version with Moon Dev themed prints:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class FibroMACDReversal(Strategy):
    swing_period = 20
    risk_pct = 0.01
    fib_levels = [0.382, 0.5, 0.618]
    threshold_pct = 0.001

    def init(self):
        # Swing high/low indicators 🌓
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='SWING_LOW')
        
        # MACD indicators 🌗
        def _macd_line(close):
            macd, _, _ = talib.MACD(close, 12, 26, 9)
            return macd
        self.macd_line = self.I(_macd_line, self.data.Close, name='MACD_LINE')
        
        def _macd_signal(close):
            _, signal, _ = talib.MACD(close, 12, 26, 9)
            return signal
        self.macd_signal = self.I(_macd_signal, self.data.Close, name='MACD_SIGNAL')

    def next(self):
        if self.position:
            return  # No new trades if position exists 🚫

        current_close = self.data.Close[-1]
        swing_high = self.swing_high[-1]
        swing_low = self.swing_low[-1]
        price_range = swing_high - swing_low
        
        # Calculate Fibonacci levels 🌉
        fibs = [swing_high - price_range * level for level in self.fib_levels]
        
        # Check proximity to Fibonacci levels 🎯
        near_fib = any(abs(current_close - fib) <= current_close * self.threshold_pct for fib in fibs)
        
        # MACD crossover detection ✨
        curr_macd = self.macd_line[-1]
        curr_signal = self.macd_signal[-1]
        prev_macd = self.macd_line[-2] if len(self.macd_line) > 1 else None
        prev_signal = self.macd_signal[-2] if len(self.macd_signal) > 1 else None
        
        if not (near_fib and prev_macd and prev_signal):
            return  # Missing data or not near Fib level 🌌

        # Entry logic 🚀
        # Bullish crossover: MACD crosses above Signal
        if (prev_macd < prev_signal) and (curr_macd > curr_signal):
            self._enter_long(current_close, swing_low)
            
        # Bearish crossover: MACD crosses below Signal
        elif (prev_macd > prev_signal) and (curr_macd < curr_signal):
            self._enter_short(current_close, swing_high)

    def _enter_long(self, entry_price, swing_low):
        """Moon-powered long entry 🌕"""
        sl_price = swing_low * (1 - self.threshold_pct)
        risk_per_share = entry_price - sl_price
        if risk_per_share <= 0: return
        
        position_size = self._calculate_size(risk_per_share)
        if not position_size: return
        
        tp_price = entry_price + 2 * risk_per_share  # 1:2 RR 🌟
        self.buy(size=position_size, sl=sl_price, tp=tp_price)
        print(f"🌙✨ BULLISH REVERSAL! Long {position_size} @ {entry_price:.2f} | "
              f"SL: {sl_price:.2f} | TP: {tp_price:.2f} 🚀")

    def _enter_short(self, entry_price, swing_high):
        """Stellar short entry 🌠"""
        sl_price = swing_high * (1 + self.threshold_pct)
        risk_per_share = sl_price - entry_price
        if risk_per_share <= 0: return
        
        position_size = self._calculate_size(risk_per_share)
        if not position_size: return
        
        tp_price = entry_price - 2 * risk_per_share  # 1:2 RR 🌠
        self.sell(size=position_size, sl=sl_price, tp=tp_price)
        print(f"🌙✨ BEARISH REVERSAL
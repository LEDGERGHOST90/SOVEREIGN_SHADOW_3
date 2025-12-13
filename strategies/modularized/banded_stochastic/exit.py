#!/usr/bin/env python3
import pandas as pd
from strategies.modularized.base import BaseExitModule, ExitSignal, SignalType, ExitReason

class BandedStochasticExit(BaseExitModule):
    def __init__(self):
        super().__init__()
        self.take_profit = 2.0
        self.stop_loss = 1.0
    
    def generate_signal(self, df: pd.DataFrame, entry_price: float, position_side: str = "long") -> ExitSignal:
        current_price = df['close'].iloc[-1]
        pnl = self._calculate_pnl_percent(entry_price, current_price, position_side)
        
        # Stochastic for exit
        high, low, close = df['high'], df['low'], df['close']
        lowest_low = low.rolling(14).min()
        highest_high = high.rolling(14).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        current_k = k.iloc[-1]
        
        if pnl >= self.take_profit:
            return ExitSignal(SignalType.SELL, ExitReason.TAKE_PROFIT, pnl, current_price, f"TP: {pnl:.2f}%")
        if pnl <= -self.stop_loss:
            return ExitSignal(SignalType.SELL, ExitReason.STOP_LOSS, pnl, current_price, f"SL: {pnl:.2f}%")
        if current_k > 80 and pnl > 0:
            return ExitSignal(SignalType.SELL, ExitReason.SIGNAL_EXIT, pnl, current_price, f"Stoch overbought: {current_k:.1f}")
        
        return ExitSignal(SignalType.HOLD, ExitReason.SIGNAL_EXIT, pnl, current_price, f"Hold: {pnl:.2f}%")

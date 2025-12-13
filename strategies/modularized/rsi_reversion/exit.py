#!/usr/bin/env python3
"""
🏴 RSI Reversion - Exit Module
"""

import pandas as pd
from strategies.modularized.base import BaseExitModule, ExitSignal, SignalType, ExitReason


class RSIReversionExit(BaseExitModule):
    def __init__(self, take_profit: float = 2.5, stop_loss: float = 1.5, rsi_exit: int = 60):
        super().__init__()
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.rsi_exit = rsi_exit
    
    def generate_signal(self, df: pd.DataFrame, entry_price: float, position_side: str = "long") -> ExitSignal:
        current_price = df['close'].iloc[-1]
        pnl = self._calculate_pnl_percent(entry_price, current_price, position_side)
        
        # RSI calculation
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if pnl >= self.take_profit:
            return ExitSignal(SignalType.SELL, ExitReason.TAKE_PROFIT, pnl, current_price, f"TP: {pnl:.2f}%")
        if pnl <= -self.stop_loss:
            return ExitSignal(SignalType.SELL, ExitReason.STOP_LOSS, pnl, current_price, f"SL: {pnl:.2f}%")
        if current_rsi > self.rsi_exit and pnl > 0:
            return ExitSignal(SignalType.SELL, ExitReason.SIGNAL_EXIT, pnl, current_price, f"RSI exit: {current_rsi:.1f}")
        
        return ExitSignal(SignalType.HOLD, ExitReason.SIGNAL_EXIT, pnl, current_price, f"Hold: RSI {current_rsi:.1f}")

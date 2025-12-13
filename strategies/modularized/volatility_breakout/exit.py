#!/usr/bin/env python3
import pandas as pd
from strategies.modularized.base import BaseExitModule, ExitSignal, SignalType, ExitReason


class VolatilityBreakoutExit(BaseExitModule):
    def __init__(self, take_profit: float = 3.0, stop_loss: float = 1.5):
        super().__init__()
        self.take_profit = take_profit
        self.stop_loss = stop_loss
    
    def generate_signal(self, df: pd.DataFrame, entry_price: float, position_side: str = "long") -> ExitSignal:
        current_price = df['close'].iloc[-1]
        pnl = self._calculate_pnl_percent(entry_price, current_price, position_side)
        
        if pnl >= self.take_profit:
            return ExitSignal(SignalType.SELL, ExitReason.TAKE_PROFIT, pnl, current_price, f"TP: {pnl:.2f}%")
        if pnl <= -self.stop_loss:
            return ExitSignal(SignalType.SELL, ExitReason.STOP_LOSS, pnl, current_price, f"SL: {pnl:.2f}%")
        
        return ExitSignal(SignalType.HOLD, ExitReason.SIGNAL_EXIT, pnl, current_price, f"Hold: {pnl:.2f}%")

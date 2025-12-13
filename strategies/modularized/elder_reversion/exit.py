#!/usr/bin/env python3
"""
🏴 Elder Reversion - Exit Module
Exit signal generation

Exit Logic:
- Take Profit: 2% profit target
- Stop Loss: 1% loss limit
- Signal Exit: Bull Power turns positive (reversion complete)
"""

import pandas as pd
from strategies.modularized.base import BaseExitModule, ExitSignal, SignalType, ExitReason


class ElderReversionExit(BaseExitModule):
    """
    Elder Ray Exit Module
    
    Exit conditions:
    1. Take Profit: +2% from entry
    2. Stop Loss: -1% from entry
    3. Signal Exit: Bull Power > 0 (reversion to mean complete)
    """
    
    def __init__(
        self,
        take_profit_percent: float = 2.0,
        stop_loss_percent: float = 1.0,
        ema_period: int = 13
    ):
        super().__init__()
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.ema_period = ema_period
    
    def generate_signal(
        self,
        df: pd.DataFrame,
        entry_price: float,
        position_side: str = "long"
    ) -> ExitSignal:
        """
        Generate exit signal
        
        Args:
            df: OHLCV DataFrame
            entry_price: Entry price of position
            position_side: "long" or "short"
            
        Returns:
            ExitSignal object
        """
        current_price = df['close'].iloc[-1]
        pnl_percent = self._calculate_pnl_percent(entry_price, current_price, position_side)
        
        # Calculate Elder Ray for signal exit
        ema_13 = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        bull_power = df['high'] - ema_13
        current_bull = bull_power.iloc[-1]
        
        # 1. Take Profit
        if pnl_percent >= self.take_profit_percent:
            return ExitSignal(
                signal=SignalType.SELL,
                reason=ExitReason.TAKE_PROFIT,
                pnl_percent=pnl_percent,
                price=current_price,
                reasoning=f"Take profit target reached: {pnl_percent:.2f}% >= {self.take_profit_percent}%"
            )
        
        # 2. Stop Loss
        if pnl_percent <= -self.stop_loss_percent:
            return ExitSignal(
                signal=SignalType.SELL,
                reason=ExitReason.STOP_LOSS,
                pnl_percent=pnl_percent,
                price=current_price,
                reasoning=f"Stop loss triggered: {pnl_percent:.2f}% <= -{self.stop_loss_percent}%"
            )
        
        # 3. Signal Exit - Bull Power positive (reversion complete)
        if current_bull > 0 and pnl_percent > 0:
            return ExitSignal(
                signal=SignalType.SELL,
                reason=ExitReason.SIGNAL_EXIT,
                pnl_percent=pnl_percent,
                price=current_price,
                reasoning=f"Reversion complete: Bull Power positive ({current_bull:.4f}), locking in {pnl_percent:.2f}% profit"
            )
        
        # Hold position
        return ExitSignal(
            signal=SignalType.HOLD,
            reason=ExitReason.SIGNAL_EXIT,
            pnl_percent=pnl_percent,
            price=current_price,
            reasoning=f"Hold: Bull Power still negative ({current_bull:.4f}), P&L: {pnl_percent:.2f}%"
        )

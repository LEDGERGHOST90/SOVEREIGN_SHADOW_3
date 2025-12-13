#!/usr/bin/env python3
"""
🏴 Trend Follow EMA - Exit Module
Trend following exit using EMA breaks and trailing stops
"""

import pandas as pd
from strategies.modularized.base import BaseExitModule, ExitSignal, SignalType, ExitReason


class TrendFollowEMAExit(BaseExitModule):
    """
    Trend Follow EMA Exit Module
    
    Exit conditions:
    1. Take Profit: 4% (trend riding target)
    2. Stop Loss: 2%
    3. Signal Exit: Price closes below EMA-21 (trend break)
    4. Trailing Stop: After 2% profit, trail at 1%
    """
    
    def __init__(
        self,
        take_profit_percent: float = 4.0,
        stop_loss_percent: float = 2.0,
        trailing_trigger: float = 2.0,
        trailing_distance: float = 1.0,
        ema_period: int = 21
    ):
        super().__init__()
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.trailing_trigger = trailing_trigger
        self.trailing_distance = trailing_distance
        self.ema_period = ema_period
        self.highest_pnl = 0  # Track highest P&L for trailing
    
    def generate_signal(
        self,
        df: pd.DataFrame,
        entry_price: float,
        position_side: str = "long"
    ) -> ExitSignal:
        current_price = df['close'].iloc[-1]
        pnl_percent = self._calculate_pnl_percent(entry_price, current_price, position_side)
        
        # Update highest P&L
        if pnl_percent > self.highest_pnl:
            self.highest_pnl = pnl_percent
        
        # Calculate EMA for signal exit
        ema_21 = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        current_ema = ema_21.iloc[-1]
        
        # 1. Take Profit
        if pnl_percent >= self.take_profit_percent:
            self.highest_pnl = 0  # Reset
            return ExitSignal(
                signal=SignalType.SELL,
                reason=ExitReason.TAKE_PROFIT,
                pnl_percent=pnl_percent,
                price=current_price,
                reasoning=f"Take profit: {pnl_percent:.2f}% >= {self.take_profit_percent}%"
            )
        
        # 2. Trailing Stop
        if self.highest_pnl >= self.trailing_trigger:
            trailing_stop = self.highest_pnl - self.trailing_distance
            if pnl_percent <= trailing_stop:
                self.highest_pnl = 0  # Reset
                return ExitSignal(
                    signal=SignalType.SELL,
                    reason=ExitReason.TRAILING_STOP,
                    pnl_percent=pnl_percent,
                    price=current_price,
                    reasoning=f"Trailing stop hit: P&L {pnl_percent:.2f}% fell from high of {self.highest_pnl:.2f}%"
                )
        
        # 3. Stop Loss
        if pnl_percent <= -self.stop_loss_percent:
            self.highest_pnl = 0  # Reset
            return ExitSignal(
                signal=SignalType.SELL,
                reason=ExitReason.STOP_LOSS,
                pnl_percent=pnl_percent,
                price=current_price,
                reasoning=f"Stop loss: {pnl_percent:.2f}% <= -{self.stop_loss_percent}%"
            )
        
        # 4. Signal Exit - Price below EMA-21
        if current_price < current_ema:
            if pnl_percent > 0:
                self.highest_pnl = 0  # Reset
                return ExitSignal(
                    signal=SignalType.SELL,
                    reason=ExitReason.SIGNAL_EXIT,
                    pnl_percent=pnl_percent,
                    price=current_price,
                    reasoning=f"Trend break: Price ${current_price:,.2f} below EMA-21 ${current_ema:,.2f}"
                )
        
        return ExitSignal(
            signal=SignalType.HOLD,
            reason=ExitReason.SIGNAL_EXIT,
            pnl_percent=pnl_percent,
            price=current_price,
            reasoning=f"Hold: Trend intact, P&L: {pnl_percent:.2f}%"
        )

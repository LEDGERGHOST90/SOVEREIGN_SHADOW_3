#!/usr/bin/env python3
"""
RSI Reversion Strategy - Exit Module

Exit Logic:
- RSI > 70 (overbought - reversal complete)
- Take Profit: 2%
- Stop Loss: 1%
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import ExitModule, ExitSignal


class RSIReversionExit(ExitModule):
    """RSI mean reversion exit logic"""
    
    def __init__(
        self,
        take_profit_percent: float = 2.0,
        stop_loss_percent: float = 1.0,
        rsi_period: int = 14,
        overbought_level: int = 70
    ):
        super().__init__()
        self.name = "rsi_reversion_exit"
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.rsi_period = rsi_period
        self.overbought_level = overbought_level
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> ExitSignal:
        """Generate exit signal"""
        
        # Calculate RSI
        rsi = self._calculate_rsi(df, self.rsi_period)
        current_rsi = rsi.iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Calculate PnL
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price) * 100
        
        # Take profit
        if pnl_percent >= self.take_profit_percent:
            return ExitSignal(
                signal="SELL",
                reason="TAKE_PROFIT",
                pnl=pnl,
                pnl_percent=pnl_percent
            )
        
        # Stop loss
        if pnl_percent <= -self.stop_loss_percent:
            return ExitSignal(
                signal="SELL",
                reason="STOP_LOSS",
                pnl=pnl,
                pnl_percent=pnl_percent
            )
        
        # Signal exit: RSI overbought (reversal complete)
        if current_rsi > self.overbought_level:
            return ExitSignal(
                signal="SELL",
                reason="SIGNAL_EXIT",
                pnl=pnl,
                pnl_percent=pnl_percent
            )
        
        # Hold position
        return ExitSignal(
            signal="HOLD",
            reason="CONDITIONS_NOT_MET",
            pnl=pnl,
            pnl_percent=pnl_percent
        )

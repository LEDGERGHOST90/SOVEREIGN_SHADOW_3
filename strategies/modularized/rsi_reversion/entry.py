#!/usr/bin/env python3
"""
🏴 RSI Reversion - Entry Module
"""

import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType


class RSIReversionEntry(BaseEntryModule):
    """RSI oversold bounce entry"""
    
    def __init__(self, rsi_period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__()
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.indicators_required = [f'rsi_{rsi_period}']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.rsi_period + 5:
            return Signal(signal=SignalType.NEUTRAL, confidence=0, price=df['close'].iloc[-1] if len(df) > 0 else 0)
        
        rsi = self._calculate_rsi(df['close'], self.rsi_period)
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        current_price = df['close'].iloc[-1]
        
        indicators = {'rsi': current_rsi, 'prev_rsi': prev_rsi}
        
        # BUY: RSI was oversold and is now rising
        if current_rsi < 40 and current_rsi > prev_rsi and prev_rsi < self.oversold:
            confidence = min(70 + (self.oversold - prev_rsi) * 2, 95)
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=f"RSI bouncing from oversold: {prev_rsi:.1f} → {current_rsi:.1f}",
                indicators=indicators
            )
        
        # Alternative: Strong oversold
        if current_rsi < 25:
            return Signal(
                signal=SignalType.BUY,
                confidence=60,
                price=current_price,
                reasoning=f"RSI extremely oversold: {current_rsi:.1f}",
                indicators=indicators
            )
        
        return Signal(
            signal=SignalType.NEUTRAL,
            confidence=0,
            price=current_price,
            reasoning=f"RSI neutral at {current_rsi:.1f}",
            indicators=indicators
        )

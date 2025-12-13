#!/usr/bin/env python3
"""
🏴 Bollinger Bounce - Entry Module
"""

import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType


class BollingerBounceEntry(BaseEntryModule):
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__()
        self.period = period
        self.std_dev = std_dev
        self.indicators_required = ['bollinger_bands']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.period + 5:
            return Signal(signal=SignalType.NEUTRAL, confidence=0, price=df['close'].iloc[-1] if len(df) > 0 else 0)
        
        middle, upper, lower = self._calculate_bollinger_bands(df['close'], self.period, self.std_dev)
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        
        current_lower = lower.iloc[-1]
        prev_lower = lower.iloc[-2]
        current_middle = middle.iloc[-1]
        bandwidth = (upper.iloc[-1] - current_lower) / current_middle * 100
        
        indicators = {
            'bb_upper': upper.iloc[-1],
            'bb_middle': current_middle,
            'bb_lower': current_lower,
            'bandwidth': bandwidth
        }
        
        # BUY: Price touched lower band and is bouncing
        if prev_price <= prev_lower and current_price > current_lower:
            confidence = min(70 + bandwidth * 2, 95)
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=f"Bollinger bounce: Price bouncing off lower band, bandwidth: {bandwidth:.1f}%",
                indicators=indicators
            )
        
        # BUY: Price below lower band (oversold)
        if current_price < current_lower:
            return Signal(
                signal=SignalType.BUY,
                confidence=65,
                price=current_price,
                reasoning=f"Price below lower Bollinger Band - mean reversion setup",
                indicators=indicators
            )
        
        return Signal(signal=SignalType.NEUTRAL, confidence=0, price=current_price, indicators=indicators)

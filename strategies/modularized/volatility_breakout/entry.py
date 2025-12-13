#!/usr/bin/env python3
"""
🏴 Volatility Breakout - Entry Module
Breakout after low volatility compression
"""

import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType


class VolatilityBreakoutEntry(BaseEntryModule):
    def __init__(self, atr_period: int = 14, lookback: int = 20):
        super().__init__()
        self.atr_period = atr_period
        self.lookback = lookback
        self.indicators_required = ['atr']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < max(self.atr_period, self.lookback) + 10:
            return Signal(signal=SignalType.NEUTRAL, confidence=0, price=df['close'].iloc[-1] if len(df) > 0 else 0)
        
        atr = self._calculate_atr(df, self.atr_period)
        current_atr = atr.iloc[-1]
        avg_atr = atr.iloc[-self.lookback:].mean()
        atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1
        
        current_price = df['close'].iloc[-1]
        prev_high = df['high'].iloc[-self.lookback:-1].max()
        prev_low = df['low'].iloc[-self.lookback:-1].min()
        
        indicators = {
            'atr': current_atr,
            'avg_atr': avg_atr,
            'atr_ratio': atr_ratio,
            'prev_high': prev_high,
            'prev_low': prev_low
        }
        
        # Low volatility compression AND price breaking above recent high
        if atr_ratio < 0.8 and current_price > prev_high:
            confidence = min(70 + (0.8 - atr_ratio) * 100, 95)
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=f"Volatility breakout: ATR compressed ({atr_ratio:.2f}x avg), breaking ${prev_high:,.2f}",
                indicators=indicators
            )
        
        # Already breaking out with expanding ATR
        if current_price > prev_high and atr_ratio > 1.2:
            return Signal(
                signal=SignalType.BUY,
                confidence=60,
                price=current_price,
                reasoning=f"Momentum breakout: Price above resistance with expanding volatility",
                indicators=indicators
            )
        
        return Signal(signal=SignalType.NEUTRAL, confidence=0, price=current_price, indicators=indicators)

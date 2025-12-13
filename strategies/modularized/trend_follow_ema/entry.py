#!/usr/bin/env python3
"""
🏴 Trend Follow EMA - Entry Module
Trend following entry using EMA crossovers and alignment

Logic:
- BUY when: EMA-9 > EMA-21 > EMA-50 AND Price > EMA-9
- Confirms strong uptrend with all EMAs aligned
"""

import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType


class TrendFollowEMAEntry(BaseEntryModule):
    """
    Trend Follow EMA Entry Module
    
    Uses triple EMA alignment for trend confirmation:
    - Fast EMA (9) > Medium EMA (21) > Slow EMA (50)
    - Price above all EMAs
    """
    
    def __init__(self, fast: int = 9, medium: int = 21, slow: int = 50):
        super().__init__()
        self.fast = fast
        self.medium = medium
        self.slow = slow
        self.indicators_required = [f'ema_{fast}', f'ema_{medium}', f'ema_{slow}']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.slow + 10:
            return Signal(
                signal=SignalType.NEUTRAL,
                confidence=0,
                price=df['close'].iloc[-1] if len(df) > 0 else 0,
                reasoning="Insufficient data"
            )
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(df['close'], self.fast)
        ema_medium = self._calculate_ema(df['close'], self.medium)
        ema_slow = self._calculate_ema(df['close'], self.slow)
        
        current_price = df['close'].iloc[-1]
        fast_val = ema_fast.iloc[-1]
        medium_val = ema_medium.iloc[-1]
        slow_val = ema_slow.iloc[-1]
        
        # Previous values for crossover detection
        prev_fast = ema_fast.iloc[-2]
        prev_medium = ema_medium.iloc[-2]
        
        indicators = {
            f'ema_{self.fast}': fast_val,
            f'ema_{self.medium}': medium_val,
            f'ema_{self.slow}': slow_val,
            'price': current_price
        }
        
        # Check EMA alignment (bullish stack)
        ema_aligned = fast_val > medium_val > slow_val
        price_above_emas = current_price > fast_val
        
        # Check for recent crossover (stronger signal)
        recent_crossover = prev_fast <= prev_medium and fast_val > medium_val
        
        if ema_aligned and price_above_emas:
            if recent_crossover:
                confidence = 85
                reasoning = "Fresh bullish EMA crossover with perfect alignment"
            else:
                # Check trend strength
                trend_strength = ((fast_val - slow_val) / slow_val) * 100
                confidence = min(60 + trend_strength * 2, 90)
                reasoning = f"Strong uptrend: EMAs perfectly aligned, trend strength: {trend_strength:.2f}%"
            
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=reasoning,
                indicators=indicators
            )
        
        # Potential setup - price approaching aligned EMAs
        if ema_aligned and current_price > medium_val:
            return Signal(
                signal=SignalType.NEUTRAL,
                confidence=30,
                price=current_price,
                reasoning="EMAs aligned but price not above fast EMA - wait for confirmation",
                indicators=indicators
            )
        
        return Signal(
            signal=SignalType.NEUTRAL,
            confidence=0,
            price=current_price,
            reasoning="No trend alignment detected",
            indicators=indicators
        )

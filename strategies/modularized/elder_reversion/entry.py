#!/usr/bin/env python3
"""
🏴 Elder Reversion - Entry Module
Entry signal generation using Elder Ray indicator

Logic:
- BUY when: Bull Power < 0 AND Price > EMA-13 (bearish exhaustion in uptrend)
- Confidence based on magnitude of bull power divergence
"""

import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType


class ElderReversionEntry(BaseEntryModule):
    """
    Elder Ray Entry Module
    
    The Elder Ray indicator consists of:
    - Bull Power = High - EMA(13)
    - Bear Power = Low - EMA(13)
    
    Entry Logic:
    - BUY: Bull Power < 0 AND Price > EMA-13
      (Short-term bearish in longer-term uptrend = reversion opportunity)
    """
    
    def __init__(self, ema_period: int = 13):
        super().__init__()
        self.ema_period = ema_period
        self.indicators_required = ['elder_ray', f'ema_{ema_period}']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """
        Generate entry signal
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Signal object
        """
        if len(df) < self.ema_period + 10:
            return Signal(
                signal=SignalType.NEUTRAL,
                confidence=0,
                price=df['close'].iloc[-1] if len(df) > 0 else 0,
                reasoning="Insufficient data for EMA calculation"
            )
        
        # Calculate EMA-13
        ema_13 = self._calculate_ema(df['close'], self.ema_period)
        
        # Calculate Elder Ray
        bull_power = df['high'] - ema_13
        bear_power = df['low'] - ema_13
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_ema = ema_13.iloc[-1]
        current_bull = bull_power.iloc[-1]
        current_bear = bear_power.iloc[-1]
        
        # Previous values for trend confirmation
        prev_bull = bull_power.iloc[-2]
        prev_bear = bear_power.iloc[-2]
        
        indicators = {
            'ema_13': current_ema,
            'bull_power': current_bull,
            'bear_power': current_bear,
            'price_vs_ema': (current_price - current_ema) / current_ema * 100
        }
        
        # Entry conditions
        # 1. Bull power is negative (short-term weakness)
        # 2. Price is above EMA-13 (longer-term uptrend)
        # 3. Bonus: Bull power rising from even lower (recovery starting)
        
        if current_bull < 0 and current_price > current_ema:
            # Calculate confidence
            # More negative bull power = stronger signal (more oversold)
            bull_magnitude = abs(current_bull / current_price) * 100
            confidence = min(50 + bull_magnitude * 100, 95)
            
            # Bonus for improving bull power
            if current_bull > prev_bull:
                confidence = min(confidence + 10, 95)
                reasoning = f"Elder Bull Power negative ({current_bull:.4f}) and rising, price above EMA-13 - recovery starting"
            else:
                reasoning = f"Elder Bull Power negative ({current_bull:.4f}), price above EMA-13 - mean reversion setup"
            
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=reasoning,
                indicators=indicators
            )
        
        # Alternative: Strong bear exhaustion
        if current_bear > prev_bear and prev_bear < 0 and current_price > current_ema:
            confidence = 45  # Lower confidence for this setup
            return Signal(
                signal=SignalType.BUY,
                confidence=confidence,
                price=current_price,
                reasoning=f"Bear power improving ({current_bear:.4f}), price above EMA - potential reversal",
                indicators=indicators
            )
        
        return Signal(
            signal=SignalType.NEUTRAL,
            confidence=0,
            price=current_price,
            reasoning="No Elder Reversion setup detected",
            indicators=indicators
        )

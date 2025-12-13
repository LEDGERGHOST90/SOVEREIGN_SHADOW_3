#!/usr/bin/env python3
"""
RSI Reversion Strategy - Entry Module

Entry Logic:
- RSI < 30 (oversold)
- RSI rising (reversal starting)
- Works best in choppy_volatile, choppy_calm, and ranging markets
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import EntryModule, EntrySignal


class RSIReversionEntry(EntryModule):
    """RSI mean reversion entry logic"""
    
    def __init__(self, rsi_period: int = 14, oversold_level: int = 30):
        super().__init__()
        self.name = "rsi_reversion_entry"
        self.indicators_required = ['rsi']
        self.rsi_period = rsi_period
        self.oversold_level = oversold_level
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signal(self, df: pd.DataFrame) -> EntrySignal:
        """
        Generate entry signal based on RSI
        
        Entry conditions:
        1. RSI < 30 (oversold)
        2. RSI rising (reversal starting)
        """
        # Calculate RSI
        rsi = self._calculate_rsi(df, self.rsi_period)
        
        # Current values
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        current_price = df['close'].iloc[-1]
        
        # Entry signal: RSI oversold but rising
        if current_rsi < self.oversold_level and current_rsi > prev_rsi:
            # Confidence based on:
            # - How oversold (lower = better)
            # - How fast it's rising
            oversold_depth = self.oversold_level - current_rsi
            rsi_rise = current_rsi - prev_rsi
            
            confidence = min(
                oversold_depth * 2 +  # Depth of oversold
                rsi_rise * 10,         # Speed of reversal
                100
            )
            
            reasoning = (
                f"RSI oversold reversal: RSI={current_rsi:.1f} (rising from {prev_rsi:.1f}), "
                f"oversold by {oversold_depth:.1f} points"
            )
            
            return EntrySignal(
                signal="BUY",
                confidence=confidence,
                price=current_price,
                reasoning=reasoning,
                indicators={
                    'rsi': current_rsi,
                    'rsi_prev': prev_rsi,
                    'oversold_level': self.oversold_level
                }
            )
        
        # No entry signal
        return EntrySignal(
            signal="NEUTRAL",
            confidence=0.0,
            price=current_price,
            reasoning=f"No entry: RSI={current_rsi:.1f}, not oversold or not rising",
            indicators={'rsi': current_rsi}
        )

#!/usr/bin/env python3
import pandas as pd
from strategies.modularized.base import BaseEntryModule, Signal, SignalType

class BandedStochasticEntry(BaseEntryModule):
    def __init__(self):
        super().__init__()
        self.indicators_required = ['stochastic', 'bollinger_bands']
    
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < 30:
            return Signal(signal=SignalType.NEUTRAL, confidence=0, price=df['close'].iloc[-1] if len(df) > 0 else 0)
        
        k, d = self._calculate_stochastic(df, 14, 3)
        middle, upper, lower = self._calculate_bollinger_bands(df['close'], 20, 2.0)
        
        current_price = df['close'].iloc[-1]
        current_k, current_d = k.iloc[-1], d.iloc[-1]
        prev_k, prev_d = k.iloc[-2], d.iloc[-2]
        current_lower = lower.iloc[-1]
        
        indicators = {'stoch_k': current_k, 'stoch_d': current_d, 'bb_lower': current_lower}
        
        # BUY: Stochastic oversold + price near lower BB + K crossing above D
        if current_k < 30 and current_price <= current_lower * 1.01 and prev_k <= prev_d and current_k > current_d:
            return Signal(signal=SignalType.BUY, confidence=80, price=current_price,
                         reasoning=f"Banded Stochastic: K={current_k:.1f} crossing D, price at lower BB", indicators=indicators)
        
        if current_k < 20 and current_price < current_lower:
            return Signal(signal=SignalType.BUY, confidence=65, price=current_price,
                         reasoning=f"Oversold: Stoch {current_k:.1f}, below lower BB", indicators=indicators)
        
        return Signal(signal=SignalType.NEUTRAL, confidence=0, price=current_price, indicators=indicators)

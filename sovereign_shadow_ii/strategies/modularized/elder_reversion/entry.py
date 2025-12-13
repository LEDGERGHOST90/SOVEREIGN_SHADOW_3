#!/usr/bin/env python3
"""
Elder Reversion Strategy - Entry Module

Entry Logic:
- Bull Power < 0 (bears exhausted)
- Price above EMA-13 (maintains uptrend context)
- Works best in choppy_volatile and choppy_calm regimes
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import EntryModule, EntrySignal


class ElderReversionEntry(EntryModule):
    """Elder Ray Reversion entry logic"""
    
    def __init__(self, ema_period: int = 13):
        super().__init__()
        self.name = "elder_reversion_entry"
        self.indicators_required = ['elder_ray', 'ema_13']
        self.ema_period = ema_period
    
    def generate_signal(self, df: pd.DataFrame) -> EntrySignal:
        """
        Generate entry signal based on Elder Ray
        
        Entry conditions:
        1. Bull Power < 0 (exhaustion)
        2. Price > EMA-13 (uptrend context)
        3. Bull Power rising (reversal starting)
        """
        # Calculate EMA-13
        ema_13 = df['close'].ewm(span=self.ema_period).mean()
        
        # Calculate Elder Ray
        bull_power = df['high'] - ema_13
        bear_power = df['low'] - ema_13
        
        # Current values
        current_bull = bull_power.iloc[-1]
        prev_bull = bull_power.iloc[-2]
        current_price = df['close'].iloc[-1]
        current_ema = ema_13.iloc[-1]
        
        # Entry signal: Bull Power negative but rising, price above EMA
        if current_bull < 0 and current_bull > prev_bull and current_price > current_ema:
            # Confidence based on:
            # - How negative bull power is (more negative = stronger reversal potential)
            # - How much it's rising
            # - Distance from EMA
            
            bull_depth = abs(current_bull)
            bull_rise = current_bull - prev_bull
            ema_distance = ((current_price - current_ema) / current_ema) * 100
            
            # Normalize to 0-100 confidence
            confidence = min(
                (bull_depth / current_price * 10000) +  # Depth of exhaustion
                (bull_rise / current_price * 5000) +     # Speed of reversal
                (ema_distance * 10),                     # Trend strength
                100
            )
            
            reasoning = (
                f"Elder Ray reversal: Bull Power={current_bull:.2f} (rising from {prev_bull:.2f}), "
                f"Price ${current_price:.2f} above EMA-13 ${current_ema:.2f} by {ema_distance:.2f}%"
            )
            
            return EntrySignal(
                signal="BUY",
                confidence=confidence,
                price=current_price,
                reasoning=reasoning,
                indicators={
                    'bull_power': current_bull,
                    'bear_power': bear_power.iloc[-1],
                    'ema_13': current_ema,
                    'price_vs_ema': ema_distance
                }
            )
        
        # No entry signal
        return EntrySignal(
            signal="NEUTRAL",
            confidence=0.0,
            price=current_price,
            reasoning=f"No entry: Bull Power={current_bull:.2f}, Price vs EMA={current_price > current_ema}",
            indicators={
                'bull_power': current_bull,
                'bear_power': bear_power.iloc[-1],
                'ema_13': current_ema
            }
        )


if __name__ == "__main__":
    # Test the entry module
    import numpy as np
    
    print("\n" + "="*70)
    print("🧪 TESTING ELDER REVERSION ENTRY MODULE")
    print("="*70)
    
    # Create sample data with reversion pattern
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
    
    # Simulate pullback then bounce
    prices = []
    base = 99000
    for i in range(50):
        if i < 20:
            # Uptrend
            prices.append(base + i * 50 + np.random.normal(0, 100))
        elif i < 35:
            # Pullback
            prices.append(base + 1000 - (i-20) * 30 + np.random.normal(0, 100))
        else:
            # Bounce
            prices.append(base + 550 + (i-35) * 40 + np.random.normal(0, 100))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p - 50 for p in prices],
        'high': [p + 100 for p in prices],
        'low': [p - 100 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 50)
    })
    
    # Test entry module
    entry = ElderReversionEntry()
    signal = entry.generate_signal(df)
    
    print(f"\n📊 Signal: {signal.signal}")
    print(f"   Confidence: {signal.confidence:.1f}%")
    print(f"   Price: ${signal.price:,.2f}")
    print(f"   Reasoning: {signal.reasoning}")
    print(f"\n🔍 Indicators:")
    for key, value in signal.indicators.items():
        print(f"   {key}: {value:.2f}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)

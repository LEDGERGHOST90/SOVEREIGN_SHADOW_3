import pandas as pd
import numpy as np

class GapTradingEntry:
    def __init__(self):
        self.name = "gap_trading_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 5:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Detect gap: Open of current > High of prev (Gap Up)
        # OR Open of current < Low of prev (Gap Down)
        
        # Crypto runs 24/7 so traditional gaps are rare except on CME futures
        # or due to maintenance/outages.
        # However, we can trade "liquidity voids" or small gaps on lower timeframes
        
        prev_high = df['high'].iloc[-2]
        curr_open = df['open'].iloc[-1]
        
        # Gap Up
        if curr_open > prev_high:
             # Strategy: Fade the gap (Bet on fill)
             # Wait for price to start filling?
             # Simplified: If gap is large (> 0.5%), sell to fill
             gap_pct = (curr_open - prev_high) / prev_high
             if gap_pct > 0.005:
                  # This would be a short strategy, we only have BUY implemented in loop usually
                  # Let's implement Buy the Gap Fill (after fill, bounce?)
                  pass
                  
        # Gap Down (Buy to fill)
        prev_low = df['low'].iloc[-2]
        if curr_open < prev_low:
             gap_pct = (prev_low - curr_open) / curr_open
             if gap_pct > 0.005:
                  return {
                    'signal': 'BUY',
                    'confidence': 70,
                    'price': df['close'].iloc[-1],
                    'reasoning': f'Gap Down ({gap_pct*100:.2f}%) - Playing Gap Fill'
                }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

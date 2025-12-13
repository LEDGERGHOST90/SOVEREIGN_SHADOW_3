import pandas as pd
import numpy as np

class FairValueGapEntry:
    def __init__(self):
        self.name = "fvg_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 5:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Bullish FVG:
        # Candle 1 High < Candle 3 Low
        # Gap exists between 1 and 3
        
        c1_high = df['high'].iloc[-3]
        c3_low = df['low'].iloc[-1]
        c2_body_green = df['close'].iloc[-2] > df['open'].iloc[-2]
        
        has_gap = c3_low > c1_high
        
        curr_price = df['close'].iloc[-1]
        
        # We are looking for price to re-enter this gap to buy
        # This logic is slightly different: we detect the gap creation usually
        # To trade it, we wait for retrace.
        # Simplified: If we are IN a bullish FVG created recently
        
        # Check if previous candle created FVG
        # Actually, let's look for a retest of an FVG created by candles -4, -3, -2
        
        fvg_high = df['low'].iloc[-2] # Candle 3 of the formation (t-2)
        fvg_low = df['high'].iloc[-4] # Candle 1 of the formation (t-4)
        
        # Valid FVG if low > high
        if fvg_high > fvg_low:
             # Check if current price dips into it
             if fvg_low <= curr_price <= fvg_high:
                  return {
                    'signal': 'BUY',
                    'confidence': 75,
                    'price': curr_price,
                    'reasoning': f'Retest of Bullish FVG ({fvg_low:.2f}-{fvg_high:.2f})'
                }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

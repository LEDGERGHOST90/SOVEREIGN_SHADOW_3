import pandas as pd
import numpy as np

class ChangeOfCharacterEntry:
    def __init__(self):
        self.name = "choch_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # CHoCH: First internal structure break indicating reversal
        # E.g. In downtrend (Lower Highs, Lower Lows), price breaks above last Lower High
        
        # Simplified logic:
        # Detect downtrend: EMA(20) slope negative
        ema = df['close'].ewm(span=20).mean()
        is_downtrend = ema.iloc[-1] < ema.iloc[-5]
        
        if not is_downtrend:
             return {'signal': 'NEUTRAL', 'confidence': 0}
             
        # Identify last Lower High
        # Look for local maximum in last 10 candles
        highs = df['high'].iloc[-10:-1]
        local_max = highs.max()
        
        curr_close = df['close'].iloc[-1]
        
        # Break above local max
        if curr_close > local_max:
             return {
                'signal': 'BUY',
                'confidence': 75,
                'price': curr_close,
                'reasoning': f'CHoCH: Break above recent Lower High ({local_max:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

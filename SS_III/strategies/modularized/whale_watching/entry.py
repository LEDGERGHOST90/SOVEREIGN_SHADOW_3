import pandas as pd
import numpy as np

class WhaleWatchingEntry:
    def __init__(self):
        self.name = "whale_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 5:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Detect massive volume spike (> 5x avg)
        avg_vol = df['volume'].rolling(window=20).mean()
        curr_vol = df['volume'].iloc[-1]
        
        is_spike = curr_vol > (avg_vol.iloc[-1] * 5)
        is_green = df['close'].iloc[-1] > df['open'].iloc[-1]
        
        if is_spike and is_green:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': df['close'].iloc[-1],
                'reasoning': 'Whale Volume Spike (5x Avg)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

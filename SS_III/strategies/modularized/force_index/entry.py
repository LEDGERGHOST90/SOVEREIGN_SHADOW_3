import pandas as pd
import numpy as np

class ForceIndexEntry:
    def __init__(self):
        self.name = "force_index_entry"
        self.period = 13
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Force Index = Volume * (Close - Prev Close)
        fi = df['volume'] * df['close'].diff()
        fi_ema = fi.ewm(span=self.period).mean()
        
        # Bullish: FI crosses above 0
        curr_fi = fi_ema.iloc[-1]
        prev_fi = fi_ema.iloc[-2]
        
        if prev_fi < 0 and curr_fi > 0:
             return {
                'signal': 'BUY',
                'confidence': 65,
                'price': df['close'].iloc[-1],
                'reasoning': f'Force Index Crossover (Zero Line)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

import pandas as pd
import numpy as np

class LiquidityGrabEntry:
    def __init__(self):
        self.name = "liquidity_grab_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Liquidity Grab (Turtle Soup):
        # Price sweeps recent low but closes back inside range
        
        recent_low = df['low'].iloc[-self.lookback:-1].min()
        curr_low = df['low'].iloc[-1]
        curr_close = df['close'].iloc[-1]
        
        # Sweep: Low is lower than recent low
        swept = curr_low < recent_low
        # Reclaim: Close is higher than recent low
        reclaimed = curr_close > recent_low
        
        if swept and reclaimed:
             return {
                'signal': 'BUY',
                'confidence': 85,
                'price': curr_close,
                'reasoning': f'Liquidity Grab below {recent_low:.2f} and reclaim'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

import pandas as pd
import numpy as np

class BreakOfStructureEntry:
    def __init__(self):
        self.name = "bos_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # BOS: Price breaks above recent significant high (uptrend)
        # Identify recent high (e.g., max of t-20 to t-5)
        
        recent_window = df['high'].iloc[-self.lookback:-5]
        recent_high = recent_window.max()
        
        curr_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        
        # Breakout: Current close > recent high AND previous close < recent high
        # (Fresh breakout)
        
        if prev_close < recent_high and curr_close > recent_high:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': curr_close,
                'reasoning': f'Break of Structure above {recent_high:.2f}'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

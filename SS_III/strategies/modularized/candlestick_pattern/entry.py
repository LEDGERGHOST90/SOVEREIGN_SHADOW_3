import pandas as pd
import numpy as np

class CandlestickPatternEntry:
    def __init__(self):
        self.name = "candlestick_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 3:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Hammer Detection
        # Small body, long lower wick, little/no upper wick
        o = df['open'].iloc[-1]
        c = df['close'].iloc[-1]
        h = df['high'].iloc[-1]
        l = df['low'].iloc[-1]
        
        body = abs(c - o)
        total_range = h - l
        lower_wick = min(o, c) - l
        
        # Avoid division by zero
        if total_range == 0:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        is_hammer = (lower_wick > 2 * body) and (body < 0.3 * total_range)
        
        # Bullish Engulfing
        # Prev red, curr green, curr body engulfs prev body
        prev_o = df['open'].iloc[-2]
        prev_c = df['close'].iloc[-2]
        is_prev_red = prev_c < prev_o
        is_curr_green = c > o
        
        is_engulfing = is_prev_red and is_curr_green and (o < prev_c) and (c > prev_o)
        
        if is_hammer or is_engulfing:
             pattern = "Hammer" if is_hammer else "Engulfing"
             return {
                'signal': 'BUY',
                'confidence': 65,
                'price': c,
                'reasoning': f'Bullish Pattern: {pattern}'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

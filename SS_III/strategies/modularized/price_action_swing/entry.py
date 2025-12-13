import pandas as pd
import numpy as np

class PriceActionSwingEntry:
    def __init__(self):
        self.name = "pa_swing_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 5:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Identify Higher Low (HL) after Higher High (HH) in uptrend
        # Simplified logic: 
        # t-3 was a low
        # t-2 was higher low
        # t-1 confirmed upward move
        
        l1 = df['low'].iloc[-3]
        l2 = df['low'].iloc[-2]
        c2 = df['close'].iloc[-2]
        c1 = df['close'].iloc[-1]
        
        # Bullish Engulfing or simple reversal pattern at swing low
        # If Lows are increasing and we have a strong green candle
        is_higher_low = l2 > l1
        is_green = c1 > df['open'].iloc[-1]
        strong_close = c1 > df['high'].iloc[-2]
        
        if is_higher_low and is_green and strong_close:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': c1,
                'reasoning': 'Higher Low with strong close (Swing Entry)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

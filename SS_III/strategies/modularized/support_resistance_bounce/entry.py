import pandas as pd
import numpy as np

class SupportResistanceBounceEntry:
    def __init__(self):
        self.name = "sr_bounce_entry"
        self.lookback = 50
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Identify Support (Min of lookback)
        past_window = df['low'].iloc[-self.lookback:]
        support_level = past_window.min()
        
        current_price = df['close'].iloc[-1]
        current_low = df['low'].iloc[-1]
        
        # Check if we are near support (within 1%)
        near_support = abs(current_low - support_level) / support_level < 0.01
        
        # Check for bounce (Green candle)
        is_green = df['close'].iloc[-1] > df['open'].iloc[-1]
        
        if near_support and is_green:
             return {
                'signal': 'BUY',
                'confidence': 75,
                'price': current_price,
                'reasoning': f'Bounce off support {support_level:.2f}'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

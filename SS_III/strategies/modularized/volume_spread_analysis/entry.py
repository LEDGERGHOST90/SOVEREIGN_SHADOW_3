import pandas as pd
import numpy as np

class VolumeSpreadAnalysisEntry:
    def __init__(self):
        self.name = "vsa_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # VSA: No Demand or Stopping Volume
        # Stopping Volume: Down candle, High Vol, Close off lows (or mid/high)
        # Sign of strength
        
        curr_close = df['close'].iloc[-1]
        curr_open = df['open'].iloc[-1]
        curr_high = df['high'].iloc[-1]
        curr_low = df['low'].iloc[-1]
        curr_vol = df['volume'].iloc[-1]
        
        avg_vol = df['volume'].iloc[-self.lookback:-1].mean()
        
        # Down candle
        is_red = curr_close < curr_open
        
        # High Volume (Ultra High)
        high_vol = curr_vol > (avg_vol * 2.0)
        
        # Close off lows (lower wick existence)
        range_len = curr_high - curr_low
        if range_len == 0: return {'signal': 'NEUTRAL', 'confidence': 0}
        
        close_pos = (curr_close - curr_low) / range_len
        # Closes in top 50%
        strong_close = close_pos > 0.5
        
        if is_red and high_vol and strong_close:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': curr_close,
                'reasoning': 'VSA: Stopping Volume (High Vol, Red Candle, Strong Close)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

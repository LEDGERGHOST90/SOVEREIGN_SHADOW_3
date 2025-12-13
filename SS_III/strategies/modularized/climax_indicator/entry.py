import pandas as pd
import numpy as np

class ClimaxIndicatorEntry:
    def __init__(self):
        self.name = "climax_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 20:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Buying Climax:
        # Huge Volume + Wide Range Candle + Upper Wick > Body
        
        curr_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].iloc[-20:-1].mean()
        
        curr_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        avg_range = (df['high'] - df['low']).iloc[-20:-1].mean()
        
        high = df['high'].iloc[-1]
        low = df['low'].iloc[-1]
        close = df['close'].iloc[-1]
        open_ = df['open'].iloc[-1]
        
        upper_wick = high - max(open_, close)
        body = abs(close - open_)
        
        # Conditions
        vol_spike = curr_vol > (avg_vol * 3)
        range_spike = curr_range > (avg_range * 2)
        rejection = upper_wick > body
        
        # This is usually a reversal signal (Sell), but let's define "Climax" logic
        # If we see a SELLING climax (bottom), we BUY
        
        lower_wick = min(open_, close) - low
        rejection_bottom = lower_wick > body
        
        if vol_spike and range_spike and rejection_bottom:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': close,
                'reasoning': 'Selling Climax (Volume Spike + Rejection)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

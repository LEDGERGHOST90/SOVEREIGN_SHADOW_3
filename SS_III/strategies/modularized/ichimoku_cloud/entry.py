import pandas as pd
import numpy as np

class IchimokuCloudEntry:
    def __init__(self):
        self.name = "ichimoku_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 52:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Conversion Line (Tenkan-sen): (9-period high + 9-period low)/2
        nine_period_high = df['high'].rolling(window=9).max()
        nine_period_low = df['low'].rolling(window=9).min()
        tenkan_sen = (nine_period_high + nine_period_low) / 2
        
        # Base Line (Kijun-sen): (26-period high + 26-period low)/2
        period26_high = df['high'].rolling(window=26).max()
        period26_low = df['low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        # Leading Span A (Senkou Span A): (Conversion Line + Base Line)/2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Leading Span B (Senkou Span B): (52-period high + 52-period low)/2
        period52_high = df['high'].rolling(window=52).max()
        period52_low = df['low'].rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
        
        # Current values
        curr_price = df['close'].iloc[-1]
        curr_span_a = senkou_span_a.iloc[-1]
        curr_span_b = senkou_span_b.iloc[-1]
        
        # TK Cross (Tenkan > Kijun) AND Price > Cloud
        is_tk_cross = tenkan_sen.iloc[-1] > kijun_sen.iloc[-1]
        is_above_cloud = curr_price > max(curr_span_a, curr_span_b)
        
        if is_tk_cross and is_above_cloud:
             return {
                'signal': 'BUY',
                'confidence': 90,
                'price': curr_price,
                'reasoning': 'TK Cross above Cloud'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

import pandas as pd
import numpy as np

class DonchianChannelEntry:
    def __init__(self):
        self.name = "donchian_entry"
        self.period = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Donchian Channel High
        # Lookback excluding current candle for signal generation to avoid look-ahead bias if using closed candles
        # But for breakout, we want to know if CURRENT price exceeds PREVIOUS N high
        
        prev_highs = df['high'].iloc[-self.period-1:-1]
        upper_channel = prev_highs.max()
        
        curr_price = df['close'].iloc[-1]
        
        if curr_price > upper_channel:
             return {
                'signal': 'BUY',
                'confidence': 85,
                'price': curr_price,
                'reasoning': f'New {self.period}-period High (Donchian Breakout)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

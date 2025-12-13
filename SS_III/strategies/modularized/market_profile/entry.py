import pandas as pd
import numpy as np

class MarketProfileEntry:
    def __init__(self):
        self.name = "market_profile_entry"
    
    def generate_signal(self, df):
        # Market Profile normally requires TPO (Time Price Opportunity) data
        # Proxy: Use Value Area High/Low from OHLC distribution
        
        if df.empty or len(df) < 24: # Need a full day
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate previous day's value area
        yesterday = df.iloc[-48:-24] # Assuming 1h candles, getting previous day
        if yesterday.empty:
             return {'signal': 'NEUTRAL', 'confidence': 0}
             
        # Value Area is roughly 70% of volume around the mean/mode
        mean_price = yesterday['close'].mean()
        std_price = yesterday['close'].std()
        
        vah = mean_price + std_price # Value Area High Proxy
        val = mean_price - std_price # Value Area Low Proxy
        
        curr_price = df['close'].iloc[-1]
        
        # Strategy: Rejection from VAL (Buy)
        is_near_val = abs(curr_price - val) / val < 0.005
        is_rejection = df['close'].iloc[-1] > df['open'].iloc[-1] # Green candle
        
        if is_near_val and is_rejection:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': curr_price,
                'reasoning': f'Rejection from Value Area Low Proxy ({val:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

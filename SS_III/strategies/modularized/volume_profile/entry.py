import pandas as pd
import numpy as np

class VolumeProfileEntry:
    def __init__(self):
        self.name = "volume_profile_entry"
        self.lookback = 100
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Simplified Volume Profile: Find High Volume Node (POC approximation)
        # Bin prices and sum volume
        window = df.iloc[-self.lookback:]
        price_bins = pd.cut(window['close'], bins=20)
        vol_profile = window.groupby(price_bins)['volume'].sum()
        
        # Point of Control (Highest Volume Bin)
        poc_bin = vol_profile.idxmax()
        poc_price = poc_bin.mid
        
        curr_price = df['close'].iloc[-1]
        
        # If price bounces off POC from above (Support)
        # Check if we were above POC, dipped near it, and are now moving up
        
        is_near_poc = abs(curr_price - poc_price) / poc_price < 0.005
        is_green = df['close'].iloc[-1] > df['open'].iloc[-1]
        
        if is_near_poc and is_green:
             return {
                'signal': 'BUY',
                'confidence': 75,
                'price': curr_price,
                'reasoning': f'Bounce off Volume POC (~{poc_price:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

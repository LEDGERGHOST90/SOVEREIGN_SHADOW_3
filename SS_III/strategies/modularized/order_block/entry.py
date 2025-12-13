import pandas as pd
import numpy as np

class OrderBlockEntry:
    def __init__(self):
        self.name = "order_block_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Bullish Order Block: Last down candle before strong up move
        # Simplified detection: 
        # Find strongest green candle (largest body) in lookback
        # The red candle immediately preceding it is the OB
        
        opens = df['open']
        closes = df['close']
        body_sizes = closes - opens
        
        # Look at last 20 candles
        window_bodies = body_sizes.iloc[-self.lookback:]
        strongest_idx = window_bodies.idxmax()
        
        if pd.isna(strongest_idx) or strongest_idx == df.index[0]:
             return {'signal': 'NEUTRAL', 'confidence': 0}
             
        # Get integer location
        try:
             idx_loc = df.index.get_loc(strongest_idx)
        except:
             return {'signal': 'NEUTRAL', 'confidence': 0}
             
        if idx_loc < 1:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Check preceding candle
        prev_open = df['open'].iloc[idx_loc-1]
        prev_close = df['close'].iloc[idx_loc-1]
        
        is_red = prev_close < prev_open
        
        if is_red:
             ob_high = prev_open
             ob_low = prev_close # or prev_low
             
             curr_price = df['close'].iloc[-1]
             
             # Retest of OB
             if ob_low <= curr_price <= ob_high:
                  return {
                    'signal': 'BUY',
                    'confidence': 80,
                    'price': curr_price,
                    'reasoning': f'Retest of Order Block ({ob_low:.2f}-{ob_high:.2f})'
                }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

import pandas as pd
import numpy as np

class BreakoutRetestEntry:
    def __init__(self):
        self.name = "breakout_retest_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback + 5:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Identify Resistance (Max of lookback excluding last few candles to see breakout)
        # We look at window [t-25 : t-5] for resistance
        past_window = df['high'].iloc[-(self.lookback+5):-5]
        resistance_level = past_window.max()
        
        # Check if we broke out in last 5 candles
        recent_highs = df['high'].iloc[-5:]
        broke_out = recent_highs.max() > resistance_level
        
        # Check if current price is retesting (within 0.5% of resistance)
        current_price = df['close'].iloc[-1]
        retest_zone_upper = resistance_level * 1.005
        retest_zone_lower = resistance_level * 0.995
        
        is_retesting = retest_zone_lower <= current_price <= retest_zone_upper
        
        if broke_out and is_retesting:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': current_price,
                'reasoning': f'Breakout above {resistance_level:.2f} and retest at {current_price:.2f}'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

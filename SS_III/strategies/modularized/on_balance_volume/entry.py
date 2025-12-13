import pandas as pd
import numpy as np

class OnBalanceVolumeEntry:
    def __init__(self):
        self.name = "obv_entry"
        self.lookback = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # OBV Trend confirmation
        # Price making higher highs AND OBV making higher highs
        
        # Calculate OBV
        # Direction
        direction = np.sign(df['close'].diff())
        direction.iloc[0] = 0
        obv = (direction * df['volume']).cumsum()
        
        # Check slope
        obv_slope = obv.iloc[-1] - obv.iloc[-self.lookback]
        price_slope = df['close'].iloc[-1] - df['close'].iloc[-self.lookback]
        
        if obv_slope > 0 and price_slope > 0:
             # Check for recent breakout in OBV
             recent_obv_high = obv.iloc[-self.lookback:-1].max()
             if obv.iloc[-1] > recent_obv_high:
                  return {
                    'signal': 'BUY',
                    'confidence': 65,
                    'price': df['close'].iloc[-1],
                    'reasoning': 'OBV Breakout confirming Price Trend'
                }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

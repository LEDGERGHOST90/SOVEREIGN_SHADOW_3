import pandas as pd
import numpy as np

class EaseOfMovementEntry:
    def __init__(self):
        self.name = "emv_entry"
        self.period = 14
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # EMV = ((High + Low)/2 - (PrevHigh + PrevLow)/2) / (Volume / (High - Low))
        # Smoothed EMV usually
        
        dm = ((df['high'] + df['low'])/2) - ((df['high'].shift(1) + df['low'].shift(1))/2)
        br = (df['volume'] / 100000000) / (df['high'] - df['low']) # Scale volume
        emv = dm / br
        
        sma_emv = emv.rolling(window=self.period).mean()
        
        # Bullish: EMV crossing above 0
        curr_emv = sma_emv.iloc[-1]
        prev_emv = sma_emv.iloc[-2]
        
        if prev_emv < 0 and curr_emv > 0:
             return {
                'signal': 'BUY',
                'confidence': 60,
                'price': df['close'].iloc[-1],
                'reasoning': 'Ease of Movement turned positive'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

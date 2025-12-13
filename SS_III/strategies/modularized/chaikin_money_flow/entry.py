import pandas as pd
import numpy as np

class ChaikinMoneyFlowEntry:
    def __init__(self):
        self.name = "cmf_entry"
        self.period = 20
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # CMF Calculation
        # MFM = ((Close - Low) - (High - Close)) / (High - Low)
        # MFV = MFM * Volume
        # CMF = Sum(MFV, 20) / Sum(Vol, 20)
        
        close = df['close']
        low = df['low']
        high = df['high']
        vol = df['volume']
        
        mfm = ((close - low) - (high - close)) / (high - low)
        mfm = mfm.fillna(0) # Handle division by zero
        mfv = mfm * vol
        
        cmf = mfv.rolling(window=self.period).sum() / vol.rolling(window=self.period).sum()
        
        curr_cmf = cmf.iloc[-1]
        
        # Bullish: CMF crosses above 0
        prev_cmf = cmf.iloc[-2]
        
        if prev_cmf < 0 and curr_cmf > 0.05: # Strong cross
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': close.iloc[-1],
                'reasoning': f'Chaikin Money Flow turned positive ({curr_cmf:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

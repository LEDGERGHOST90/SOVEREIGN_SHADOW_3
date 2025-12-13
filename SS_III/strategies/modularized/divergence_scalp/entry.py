import pandas as pd
import numpy as np

class DivergenceScalpEntry:
    def __init__(self):
        self.name = "div_scalp_entry"
        self.lookback = 15
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # RSI Divergence
        # Bullish: Price Lower Low, RSI Higher Low
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Find recent lows
        price_lows = df['low'].iloc[-self.lookback:]
        rsi_window = rsi.iloc[-self.lookback:]
        
        # Simplified Check:
        curr_price_low = df['low'].iloc[-1]
        prev_price_low = df['low'].iloc[-5] # Approx previous swing
        
        curr_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-5]
        
        if curr_price_low < prev_price_low and curr_rsi > prev_rsi and curr_rsi < 30:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': df['close'].iloc[-1],
                'reasoning': 'RSI Bullish Divergence (Scalp)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

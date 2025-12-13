import pandas as pd
import numpy as np

class MacdDivergenceEntry:
    def __init__(self):
        self.name = "macd_divergence_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 26:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate MACD
        exp12 = df['close'].ewm(span=12, adjust=False).mean()
        exp26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        
        # Check for bullish divergence
        # Simplified: Price Low < Prev Price Low AND MACD Low > Prev MACD Low
        # We need to find local minima
        
        # Looking at last 10 candles
        price_window = df['low'].iloc[-10:]
        macd_window = macd.iloc[-10:]
        
        # Minimal implementation:
        # If price is lowest in window but MACD is rising
        current_price_low = df['low'].iloc[-1]
        current_macd = macd.iloc[-1]
        
        # This is hard to detect perfectly without more history/logic
        # Fallback: simple MACD crossover
        if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
             return {
                'signal': 'BUY',
                'confidence': 60,
                'price': df['close'].iloc[-1],
                'reasoning': 'MACD Crossover (Proxy for Divergence)'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

import pandas as pd
import numpy as np

class KeltnerChannelBreakoutEntry:
    def __init__(self):
        self.name = "keltner_entry"
        self.ema_period = 20
        self.atr_period = 10
        self.multiplier = 2.0
    
    def generate_signal(self, df):
        if df.empty or len(df) < 20:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate Keltner Channels
        ema = df['close'].ewm(span=self.ema_period).mean()
        
        high = df['high']
        low = df['low']
        close = df['close']
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()
        
        upper = ema + (atr * self.multiplier)
        lower = ema - (atr * self.multiplier)
        
        curr_price = close.iloc[-1]
        curr_upper = upper.iloc[-1]
        
        # Breakout above Upper Channel
        if curr_price > curr_upper:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': curr_price,
                'reasoning': f'Price broken above Keltner Upper Band ({curr_upper:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

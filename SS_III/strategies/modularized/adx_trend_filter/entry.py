import pandas as pd
import numpy as np

class AdxTrendFilterEntry:
    def __init__(self):
        self.name = "adx_entry"
        self.period = 14
    
    def generate_signal(self, df):
        if df.empty or len(df) < 28:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate ADX (Approximation or simplified DI+/DI-)
        # True Range
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        
        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Convert to Series
        plus_dm_s = pd.Series(plus_dm, index=df.index)
        minus_dm_s = pd.Series(minus_dm, index=df.index)
        
        # Smooth
        plus_di = 100 * (plus_dm_s.rolling(window=self.period).mean() / atr)
        minus_di = 100 * (minus_dm_s.rolling(window=self.period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=self.period).mean()
        
        curr_adx = adx.iloc[-1]
        curr_plus = plus_di.iloc[-1]
        curr_minus = minus_di.iloc[-1]
        
        # Strong Trend (ADX > 25) AND Bullish (DI+ > DI-)
        if curr_adx > 25 and curr_plus > curr_minus:
             return {
                'signal': 'BUY',
                'confidence': min(curr_adx, 100),
                'price': close.iloc[-1],
                'reasoning': f'Strong Trend (ADX {curr_adx:.1f}) and Bullish DI'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

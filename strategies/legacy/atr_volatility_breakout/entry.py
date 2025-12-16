class AtrVolatilityBreakoutEntry:
    def __init__(self):
        self.name = "atr_breakout_entry"
        self.period = 14
        self.multiplier = 3.0
    
    def generate_signal(self, df):
        if df.empty or len(df) < 20:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Keltner Channel logic: EMA + N * ATR
        ema = df['close'].ewm(span=20).mean()
        
        # Calculate ATR
        high = df['high']
        low = df['low']
        close = df['close']
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        
        upper_band = ema + (atr * self.multiplier)
        
        curr_price = df['close'].iloc[-1]
        curr_upper = upper_band.iloc[-1]
        
        if curr_price > curr_upper:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': curr_price,
                'reasoning': f'Volatility Breakout above {curr_upper:.2f}'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

class DynamicCrossfireEntry:
    def __init__(self):
        self.name = "dynamic_crossfire_entry"
        self.indicators = ['ema_9', 'ema_21', 'rsi_14']
    
    def generate_signal(self, df):
        """
        Entry Logic: EMA 9 crosses above EMA 21 AND RSI > 50
        """
        if df is None or len(df) < 21:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        ema_9 = df['close'].ewm(span=9).mean()
        ema_21 = df['close'].ewm(span=21).mean()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Check crossover
        prev_ema_9 = ema_9.iloc[-2]
        prev_ema_21 = ema_21.iloc[-2]
        curr_ema_9 = ema_9.iloc[-1]
        curr_ema_21 = ema_21.iloc[-1]
        
        crossover = prev_ema_9 <= prev_ema_21 and curr_ema_9 > curr_ema_21
        
        if crossover and current_rsi > 50:
            return {
                'signal': 'BUY',
                'confidence': 80,
                'price': df['close'].iloc[-1],
                'reasoning': 'EMA 9 crossed above EMA 21 with RSI > 50'
            }
        
        return {'signal': 'NEUTRAL', 'confidence': 0}

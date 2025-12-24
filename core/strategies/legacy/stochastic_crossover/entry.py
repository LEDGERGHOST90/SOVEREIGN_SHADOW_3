class StochasticCrossoverEntry:
    def __init__(self):
        self.name = "stoch_cross_entry"
        self.k_period = 14
        self.d_period = 3
    
    def generate_signal(self, df):
        if df.empty or len(df) < 20:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate Stochastic
        low_min = df['low'].rolling(window=self.k_period).min()
        high_max = df['high'].rolling(window=self.k_period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=self.d_period).mean()
        
        curr_k = k_percent.iloc[-1]
        curr_d = d_percent.iloc[-1]
        prev_k = k_percent.iloc[-2]
        prev_d = d_percent.iloc[-2]
        
        # Bullish Cross in Oversold (< 20)
        if prev_k < prev_d and curr_k > curr_d and curr_k < 20:
             return {
                'signal': 'BUY',
                'confidence': 85,
                'price': df['close'].iloc[-1],
                'reasoning': f'Stochastic Golden Cross in Oversold (K:{curr_k:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

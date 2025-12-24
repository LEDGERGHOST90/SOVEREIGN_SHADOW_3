class FibonacciRetracementEntry:
    def __init__(self):
        self.name = "fib_retracement_entry"
        self.lookback = 100
        self.fib_levels = [0.382, 0.5, 0.618]
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Identify Trend (High/Low of lookback)
        window = df.iloc[-self.lookback:]
        high_price = window['high'].max()
        low_price = window['low'].min()
        
        diff = high_price - low_price
        
        current_price = df['close'].iloc[-1]
        
        # Calculate levels (assuming uptrend context for buy)
        # Retracement from High
        level_618 = high_price - (diff * 0.618)
        level_500 = high_price - (diff * 0.5)
        level_382 = high_price - (diff * 0.382)
        
        # Check if near any golden zone level (within 0.5%)
        is_near_618 = abs(current_price - level_618) / level_618 < 0.005
        is_near_500 = abs(current_price - level_500) / level_500 < 0.005
        
        if is_near_618 or is_near_500:
             return {
                'signal': 'BUY',
                'confidence': 70,
                'price': current_price,
                'reasoning': f'Price near Fib Golden Pocket ({level_618:.2f} - {level_500:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}

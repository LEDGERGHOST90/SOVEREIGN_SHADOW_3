class ElderReversionEntry:
    def __init__(self):
        self.name = "elder_reversion_entry"
        self.indicators = ['elder_ray', 'ema_13']
    
    def generate_signal(self, df):
        """
        Entry Logic: Bull Power < 0 AND Price above EMA-13
        Returns: {'signal': 'BUY'|'NEUTRAL', 'confidence': 0-100, 'price': float}
        """
        if df.empty or len(df) < 14:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate Elder Ray
        ema_13 = df['close'].ewm(span=13).mean()
        bull_power = df['high'] - ema_13
        
        current_bull = bull_power.iloc[-1]
        current_price = df['close'].iloc[-1]
        current_ema = ema_13.iloc[-1]
        
        if current_bull < 0 and current_price > current_ema:
            confidence = min(abs(current_bull / current_price) * 1000, 100)
            return {
                'signal': 'BUY',
                'confidence': confidence,
                'price': current_price,
                'reasoning': f'Elder Bull Power negative ({current_bull:.4f}), price above EMA-13'
            }
        
        return {'signal': 'NEUTRAL', 'confidence': 0}

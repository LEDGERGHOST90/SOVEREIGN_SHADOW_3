class FibonacciRetracementExit:
    def __init__(self):
        self.name = "fib_retracement_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Target recent high (0% retracement)
        if pnl_percent >= 5.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        # Stop below 0.786 level (approx -2.5%)
        if pnl_percent <= -2.5:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

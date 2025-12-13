class PriceActionSwingExit:
    def __init__(self):
        self.name = "pa_swing_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Target previous swing high (approx 3-5%)
        if pnl_percent >= 4.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        # Stop below swing low
        if pnl_percent <= -2.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

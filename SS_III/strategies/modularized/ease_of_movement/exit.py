class EaseOfMovementExit:
    def __init__(self):
        self.name = "emv_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        if pnl_percent >= 3.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        if pnl_percent <= -1.5:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

class AtrVolatilityBreakoutExit:
    def __init__(self):
        self.name = "atr_breakout_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Ride the trend until reversal
        if pnl_percent >= 6.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        if pnl_percent <= -2.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

class ParabolicSarExit:
    def __init__(self):
        self.name = "parabolic_sar_exit"
    
    def generate_signal(self, df, entry_price):
        ema_20 = df['close'].ewm(span=20).mean()
        curr_price = df['close'].iloc[-1]
        curr_ema = ema_20.iloc[-1]
        
        pnl_percent = ((curr_price - entry_price) / entry_price) * 100
        
        # Exit if Price flips back below EMA
        if curr_price < curr_ema:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -1.5:
             return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
             
        if pnl_percent >= 4.0:
             return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

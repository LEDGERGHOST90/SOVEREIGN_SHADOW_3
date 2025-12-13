class KeltnerChannelBreakoutExit:
    def __init__(self):
        self.name = "keltner_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        ema = df['close'].ewm(span=20).mean()
        curr_ema = ema.iloc[-1]
        
        # Exit if price drops back below EMA (trend over)
        if current_price < curr_ema:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -1.5:
             return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
             
        if pnl_percent >= 5.0:
             return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

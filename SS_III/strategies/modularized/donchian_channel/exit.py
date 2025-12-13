class DonchianChannelExit:
    def __init__(self):
        self.name = "donchian_exit"
        self.exit_period = 10
    
    def generate_signal(self, df, entry_price):
        # Exit if price hits N-period low
        prev_lows = df['low'].iloc[-self.exit_period-1:-1]
        lower_channel = prev_lows.min()
        
        curr_price = df['close'].iloc[-1]
        pnl_percent = ((curr_price - entry_price) / entry_price) * 100
        
        if curr_price < lower_channel:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -2.0:
             return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

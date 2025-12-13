class IchimokuCloudExit:
    def __init__(self):
        self.name = "ichimoku_exit"
    
    def generate_signal(self, df, entry_price):
        # Re-calculate minimal needed components for exit
        period26_high = df['high'].rolling(window=26).max()
        period26_low = df['low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        curr_price = df['close'].iloc[-1]
        curr_kijun = kijun_sen.iloc[-1]
        
        pnl_percent = ((curr_price - entry_price) / entry_price) * 100
        
        # Exit if Price crosses below Kijun-sen
        if curr_price < curr_kijun:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -2.0:
             return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
             
        if pnl_percent >= 6.0:
             return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

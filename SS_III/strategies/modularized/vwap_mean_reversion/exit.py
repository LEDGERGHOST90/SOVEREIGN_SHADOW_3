class VwapMeanReversionExit:
    def __init__(self):
        self.name = "vwap_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        v = df['volume']
        p = df['close']
        vwma = (p * v).rolling(window=20).sum() / v.rolling(window=20).sum()
        curr_vwma = vwma.iloc[-1]
        
        # Exit on touch of VWAP
        if current_price >= curr_vwma:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -2.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

class CandlestickPatternExit:
    def __init__(self):
        self.name = "candlestick_exit"
    
    def generate_signal(self, df, entry_price):
        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Quick scalp targets for candlestick patterns
        if pnl_percent >= 2.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        if pnl_percent <= -1.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

class DynamicCrossfireExit:
    def __init__(self):
        self.name = "dynamic_crossfire_exit"
    
    def generate_signal(self, df, entry_price):
        """
        Exit Logic: EMA 9 crosses below EMA 21 OR TP/SL
        """
        if df is None or len(df) < 21:
            return {'signal': 'HOLD', 'pnl': 0}

        current_price = df['close'].iloc[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # TP/SL
        if pnl_percent >= 3.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        if pnl_percent <= -1.5:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
            
        # Crossover exit
        ema_9 = df['close'].ewm(span=9).mean()
        ema_21 = df['close'].ewm(span=21).mean()
        
        prev_ema_9 = ema_9.iloc[-2]
        prev_ema_21 = ema_21.iloc[-2]
        curr_ema_9 = ema_9.iloc[-1]
        curr_ema_21 = ema_21.iloc[-1]
        
        crossunder = prev_ema_9 >= prev_ema_21 and curr_ema_9 < curr_ema_21
        
        if crossunder:
            return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

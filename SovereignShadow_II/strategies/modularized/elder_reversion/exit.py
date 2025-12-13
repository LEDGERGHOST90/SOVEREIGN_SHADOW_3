class ElderReversionExit:
    def __init__(self):
        self.name = "elder_reversion_exit"
    
    def generate_signal(self, df, entry_price):
        """
        Exit Logic: Bull Power > 0 OR Take Profit 2% OR Stop Loss 1%
        """
        if df is None or len(df) < 13:
            return {'signal': 'HOLD', 'pnl': 0}

        ema_13 = df['close'].ewm(span=13).mean()
        bull_power = df['high'] - ema_13
        current_price = df['close'].iloc[-1]
        
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Take profit
        if pnl_percent >= 2.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
        
        # Stop loss
        if pnl_percent <= -1.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
        
        # Bull power positive (trend reversal complete)
        if bull_power.iloc[-1] > 0:
            return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
        
        return {'signal': 'HOLD', 'pnl': pnl_percent}

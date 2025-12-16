class StochasticCrossoverExit:
    def __init__(self):
        self.name = "stoch_cross_exit"
        self.k_period = 14
        self.d_period = 3
    
    def generate_signal(self, df, entry_price):
        # Calculate Stochastic
        low_min = df['low'].rolling(window=self.k_period).min()
        high_max = df['high'].rolling(window=self.k_period).max()
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        curr_k = k_percent.iloc[-1]
        
        pnl_percent = ((df['close'].iloc[-1] - entry_price) / entry_price) * 100
        
        # Exit on Overbought (> 80) or Stop Loss
        if curr_k > 80:
             return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}
             
        if pnl_percent <= -1.5:
             return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}
             
        if pnl_percent >= 3.0:
             return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}
            
        return {'signal': 'HOLD', 'pnl': pnl_percent}

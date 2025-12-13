class BetaWeightedDeltaExit:
    def __init__(self):
        self.name = "beta_delta_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class VolatilityArbitrageExit:
    def __init__(self):
        self.name = "vol_arb_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

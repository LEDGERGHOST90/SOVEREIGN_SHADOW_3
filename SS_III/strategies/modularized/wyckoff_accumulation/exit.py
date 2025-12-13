class WyckoffAccumulationExit:
    def __init__(self):
        self.name = "wyckoff_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class TriangularArbitrageExit:
    def __init__(self):
        self.name = "tri_arb_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

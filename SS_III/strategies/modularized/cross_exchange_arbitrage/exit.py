class CrossExchangeArbitrageExit:
    def __init__(self):
        self.name = "cross_exchange_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

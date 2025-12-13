class PerpetualBasisTradeExit:
    def __init__(self):
        self.name = "basis_trade_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

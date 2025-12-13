class CashAndCarryArbitrageExit:
    def __init__(self):
        self.name = "cash_carry_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

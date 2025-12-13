class CurrencyStrengthExit:
    def __init__(self):
        self.name = "currency_strength_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

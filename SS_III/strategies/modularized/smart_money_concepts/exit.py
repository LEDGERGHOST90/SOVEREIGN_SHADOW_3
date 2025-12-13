class SmartMoneyConceptsExit:
    def __init__(self):
        self.name = "smc_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

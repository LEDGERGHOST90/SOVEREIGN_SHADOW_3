class IntermarketCorrelationExit:
    def __init__(self):
        self.name = "correlation_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

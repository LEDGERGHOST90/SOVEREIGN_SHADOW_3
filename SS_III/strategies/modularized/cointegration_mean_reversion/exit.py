class CointegrationMeanReversionExit:
    def __init__(self):
        self.name = "coint_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

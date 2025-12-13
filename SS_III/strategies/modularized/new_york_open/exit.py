class NewYorkOpenExit:
    def __init__(self):
        self.name = "ny_open_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

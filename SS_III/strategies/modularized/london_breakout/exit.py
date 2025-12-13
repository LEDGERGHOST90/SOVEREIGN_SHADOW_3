class LondonBreakoutExit:
    def __init__(self):
        self.name = "london_bo_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

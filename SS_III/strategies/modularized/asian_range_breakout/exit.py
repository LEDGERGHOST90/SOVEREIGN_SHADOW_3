class AsianRangeBreakoutExit:
    def __init__(self):
        self.name = "asian_range_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

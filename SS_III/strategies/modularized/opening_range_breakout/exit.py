class OpeningRangeBreakoutExit:
    def __init__(self):
        self.name = "orb_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

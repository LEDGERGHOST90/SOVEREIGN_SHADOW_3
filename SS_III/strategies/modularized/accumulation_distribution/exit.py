class AccumulationDistributionExit:
    def __init__(self):
        self.name = "ad_line_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class TimeAndSalesExit:
    def __init__(self):
        self.name = "tape_reading_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class LargeOrderDetectionExit:
    def __init__(self):
        self.name = "large_order_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

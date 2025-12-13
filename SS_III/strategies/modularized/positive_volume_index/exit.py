class PositiveVolumeIndexExit:
    def __init__(self):
        self.name = "pvi_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

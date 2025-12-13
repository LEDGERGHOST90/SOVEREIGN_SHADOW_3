class NegativeVolumeIndexExit:
    def __init__(self):
        self.name = "nvi_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

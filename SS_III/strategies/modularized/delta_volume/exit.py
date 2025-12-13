class DeltaVolumeExit:
    def __init__(self):
        self.name = "delta_volume_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

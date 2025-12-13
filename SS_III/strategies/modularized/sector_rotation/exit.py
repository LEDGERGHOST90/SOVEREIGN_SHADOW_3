class SectorRotationExit:
    def __init__(self):
        self.name = "sector_rotation_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class PowerHourMomentumExit:
    def __init__(self):
        self.name = "power_hour_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

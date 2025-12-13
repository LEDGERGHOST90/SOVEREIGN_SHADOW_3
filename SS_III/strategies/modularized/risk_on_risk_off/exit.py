class RiskOnRiskOffExit:
    def __init__(self):
        self.name = "roro_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

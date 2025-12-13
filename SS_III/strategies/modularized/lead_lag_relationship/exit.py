class LeadLagRelationshipExit:
    def __init__(self):
        self.name = "lead_lag_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

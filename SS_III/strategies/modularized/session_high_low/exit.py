class SessionHighLowExit:
    def __init__(self):
        self.name = "session_hl_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

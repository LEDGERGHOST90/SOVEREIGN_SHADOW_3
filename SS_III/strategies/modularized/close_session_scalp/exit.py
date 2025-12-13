class CloseSessionScalpExit:
    def __init__(self):
        self.name = "close_scalp_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

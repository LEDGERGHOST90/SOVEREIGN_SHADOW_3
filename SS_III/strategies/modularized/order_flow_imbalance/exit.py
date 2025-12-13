class OrderFlowImbalanceExit:
    def __init__(self):
        self.name = "order_flow_exit"
    
    def generate_signal(self, df, entry_price):
        return {'signal': 'HOLD', 'pnl': 0}

class RiskOnRiskOffRisk:
    def __init__(self):
        self.max_position_size = 0.10
    
    def calculate_position_size(self, portfolio_value, current_price, atr):
        return {
            'position_value_usd': 0,
            'quantity': 0,
            'stop_loss_price': 0,
            'take_profit_price': 0
        }

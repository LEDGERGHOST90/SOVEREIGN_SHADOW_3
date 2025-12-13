class BreakOfStructureRisk:
    def __init__(self):
        self.max_position_size = 0.10
        self.stop_loss_percent = 1.5
        self.take_profit_percent = 4.0
    
    def calculate_position_size(self, portfolio_value, current_price, atr):
        risk_amount = portfolio_value * 0.01
        stop_distance = current_price * (self.stop_loss_percent / 100)
        if stop_distance == 0: stop_distance = 0.01 * current_price
        
        position_value = risk_amount / (stop_distance / current_price)
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)
        
        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent/100),
            'take_profit_price': current_price * (1 + self.take_profit_percent/100)
        }

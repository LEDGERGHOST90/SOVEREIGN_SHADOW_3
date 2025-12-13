class ElderReversionRisk:
    def __init__(self):
        self.max_position_size = 0.10  # 10% of portfolio
        self.stop_loss_percent = 1.0
        self.take_profit_percent = 2.0
    
    def calculate_position_size(self, portfolio_value, current_price, atr):
        """
        Position sizing based on volatility (ATR)
        """
        # Risk 1% of portfolio per trade
        risk_amount = portfolio_value * 0.01
        
        # Calculate position size based on stop loss distance
        # Stop loss distance is 1% of price if strict percentage, or could use ATR based.
        # The prompt hardcodes stop_loss_percent = 1.0 in __init__ but the function signature accepts ATR.
        # I will use the prompt's logic:
        
        stop_distance = current_price * (self.stop_loss_percent / 100)
        
        # Avoid division by zero
        if stop_distance == 0:
            return {
                'position_value_usd': 0,
                'quantity': 0,
                'stop_loss_price': 0,
                'take_profit_price': 0
            }

        position_value = risk_amount / (stop_distance / current_price)
        
        # Cap at 10% of portfolio
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)
        
        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent/100),
            'take_profit_price': current_price * (1 + self.take_profit_percent/100)
        }

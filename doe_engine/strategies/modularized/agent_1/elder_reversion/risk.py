#!/usr/bin/env python3
"""
Elder Reversion Strategy - Risk Module
Agent 1 Strategy #1
"""

from typing import Dict


class ElderReversionRisk:
    def __init__(self):
        self.max_position_size = 0.10  # 10% of portfolio
        self.stop_loss_percent = 1.0
        self.take_profit_percent = 2.0

    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: float
    ) -> Dict:
        """Position sizing based on volatility (ATR)"""
        risk_amount = portfolio_value * 0.01
        stop_distance = current_price * (self.stop_loss_percent / 100)
        position_value = risk_amount / (stop_distance / current_price)
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)

        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent / 100),
            'take_profit_price': current_price * (1 + self.take_profit_percent / 100)
        }

#!/usr/bin/env python3
from typing import Optional
from strategies.modularized.base import BaseRiskModule, PositionSizing


class BollingerBounceRisk(BaseRiskModule):
    def __init__(self):
        super().__init__(max_position_size=0.08, risk_per_trade=0.01, stop_loss_percent=1.0, take_profit_percent=2.0)
    
    def calculate_position_size(self, portfolio_value: float, current_price: float, atr: Optional[float] = None) -> PositionSizing:
        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = current_price * (self.stop_loss_percent / 100)
        stop_loss_price = current_price * (1 - self.stop_loss_percent / 100)
        position_value = min(risk_amount / (stop_distance / current_price), portfolio_value * self.max_position_size)
        take_profit_price = current_price * (1 + self.take_profit_percent / 100)
        rr = (take_profit_price - current_price) / (current_price - stop_loss_price)
        return PositionSizing(round(position_value, 2), position_value / current_price, round(stop_loss_price, 2), round(take_profit_price, 2), round(rr, 2), self.risk_per_trade * 100)

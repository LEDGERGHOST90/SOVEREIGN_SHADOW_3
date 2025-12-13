#!/usr/bin/env python3
"""
🏴 Trend Follow EMA - Risk Module
Position sizing for trend following
"""

from typing import Optional
from strategies.modularized.base import BaseRiskModule, PositionSizing


class TrendFollowEMARisk(BaseRiskModule):
    def __init__(self):
        super().__init__(
            max_position_size=0.12,  # 12% for trend trades
            risk_per_trade=0.015,  # 1.5% risk
            stop_loss_percent=2.0,
            take_profit_percent=4.0
        )
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: Optional[float] = None
    ) -> PositionSizing:
        risk_amount = portfolio_value * self.risk_per_trade
        
        if atr is not None:
            stop_distance = atr * 2.0  # 2x ATR for trend trades
            stop_loss_price = current_price - stop_distance
        else:
            stop_distance = current_price * (self.stop_loss_percent / 100)
            stop_loss_price = current_price * (1 - self.stop_loss_percent / 100)
        
        stop_percent = stop_distance / current_price
        position_value = risk_amount / stop_percent if stop_percent > 0 else 0
        
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)
        
        quantity = position_value / current_price if current_price > 0 else 0
        take_profit_price = current_price * (1 + self.take_profit_percent / 100)
        
        reward = take_profit_price - current_price
        risk = current_price - stop_loss_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return PositionSizing(
            position_value_usd=round(position_value, 2),
            quantity=quantity,
            stop_loss_price=round(stop_loss_price, 2),
            take_profit_price=round(take_profit_price, 2),
            risk_reward_ratio=round(risk_reward_ratio, 2),
            risk_percent=self.risk_per_trade * 100
        )

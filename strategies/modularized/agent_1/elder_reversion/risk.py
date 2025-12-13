from __future__ import annotations

from typing import Dict, Any


class Risk:
    """ElderReversion risk skill."""

    def __init__(
        self,
        *,
        risk_per_trade: float = 0.01,
        max_position_size: float = 0.10,
        stop_loss_percent: float = 1.0,
        take_profit_percent: float = 2.0,
    ):
        self.risk_per_trade = float(risk_per_trade)
        self.max_position_size = float(max_position_size)
        self.stop_loss_percent = float(stop_loss_percent)
        self.take_profit_percent = float(take_profit_percent)

    def calculate_position_size(self, portfolio_value: float, current_price: float, atr: float) -> Dict[str, Any]:
        portfolio_value = float(portfolio_value)
        current_price = float(current_price)

        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = current_price * (self.stop_loss_percent / 100.0)
        stop_distance = max(stop_distance, max(float(atr), 0.0) * 0.5, 1e-9)

        position_value = risk_amount / (stop_distance / current_price)
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)

        qty = position_value / current_price
        return {
            "position_value_usd": position_value,
            "quantity": qty,
            "stop_loss_price": current_price * (1 - self.stop_loss_percent / 100.0),
            "take_profit_price": current_price * (1 + self.take_profit_percent / 100.0),
        }

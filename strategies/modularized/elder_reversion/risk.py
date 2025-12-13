#!/usr/bin/env python3
"""
🏴 Elder Reversion - Risk Module
Position sizing and risk management

Risk Parameters:
- Max Position Size: 10% of portfolio
- Risk per Trade: 1% of portfolio
- Stop Loss: 1%
- Take Profit: 2% (2:1 R:R)
"""

from typing import Optional
from strategies.modularized.base import BaseRiskModule, PositionSizing


class ElderReversionRisk(BaseRiskModule):
    """
    Elder Reversion Risk Module
    
    Position sizing based on:
    1. Fixed risk per trade (1% of portfolio)
    2. Stop loss distance
    3. Optional ATR adjustment for volatility
    """
    
    def __init__(
        self,
        max_position_size: float = 0.10,  # 10% of portfolio
        risk_per_trade: float = 0.01,  # 1% risk per trade
        stop_loss_percent: float = 1.0,
        take_profit_percent: float = 2.0
    ):
        super().__init__(
            max_position_size=max_position_size,
            risk_per_trade=risk_per_trade,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent
        )
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: Optional[float] = None
    ) -> PositionSizing:
        """
        Calculate position size
        
        Position sizing formula:
        Risk Amount = Portfolio * Risk Per Trade
        Position Size = Risk Amount / Stop Loss Distance
        
        Args:
            portfolio_value: Total portfolio value in USD
            current_price: Current asset price
            atr: Optional ATR for volatility adjustment
            
        Returns:
            PositionSizing object
        """
        # Calculate risk amount (1% of portfolio)
        risk_amount = portfolio_value * self.risk_per_trade
        
        # Calculate stop loss distance
        if atr is not None:
            # Use ATR-based stop loss (1.5x ATR)
            stop_distance = atr * 1.5
            stop_loss_price = current_price - stop_distance
        else:
            # Use fixed percentage stop loss
            stop_distance = current_price * (self.stop_loss_percent / 100)
            stop_loss_price = current_price * (1 - self.stop_loss_percent / 100)
        
        # Calculate position size in USD
        # Position Size = Risk Amount / (Stop Distance as % of price)
        stop_percent = stop_distance / current_price
        position_value = risk_amount / stop_percent if stop_percent > 0 else 0
        
        # Cap at max position size
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)
        
        # Calculate quantity
        quantity = position_value / current_price if current_price > 0 else 0
        
        # Calculate take profit price
        take_profit_price = current_price * (1 + self.take_profit_percent / 100)
        
        # Calculate risk/reward ratio
        reward = take_profit_price - current_price
        risk = current_price - stop_loss_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return PositionSizing(
            position_value_usd=round(position_value, 2),
            quantity=quantity,
            stop_loss_price=round(stop_loss_price, 2),
            take_profit_price=round(take_profit_price, 2),
            risk_reward_ratio=round(risk_reward_ratio, 2),
            risk_percent=self.risk_per_trade * 100,
            metadata={
                'risk_amount_usd': risk_amount,
                'stop_distance': stop_distance,
                'atr_used': atr is not None,
                'capped_at_max': position_value >= max_value
            }
        )

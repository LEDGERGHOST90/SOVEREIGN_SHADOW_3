"""
🛡️ Risk Manager

Risk management and safety rules for the Sovereign Shadow Trading Empire.

Rules:
    - Max daily loss: $100
    - Max position size: $415 (25% of hot wallet)
    - Stop loss: 5% per trade
    - Consecutive loss limit: 3 trades
    - Ledger vault: READ-ONLY (never auto-trade)
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("shadow_sdk.utils.risk")


class RiskManager:
    """
    🛡️ Risk Management System
    
    Enforces safety rules and monitors portfolio risk.
    
    Example:
        >>> risk_mgr = RiskManager(max_daily_loss=100, max_position=415)
        >>> if risk_mgr.can_trade(amount=100):
        >>>     # Execute trade
        >>>     risk_mgr.record_trade(profit=-5.0, success=False)
    """
    
    def __init__(self, max_daily_loss: float = 100, max_position_size: float = 415, 
                 stop_loss_percent: float = 0.05, consecutive_loss_limit: int = 3):
        """
        Initialize risk manager.
        
        Args:
            max_daily_loss: Maximum allowed daily loss in dollars
            max_position_size: Maximum position size in dollars
            stop_loss_percent: Stop loss percentage (0.05 = 5%)
            consecutive_loss_limit: Max consecutive losses before halt
        """
        from .. import CAPITAL_LEDGER, CAPITAL_COINBASE
        
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size
        self.stop_loss_percent = stop_loss_percent
        self.consecutive_loss_limit = consecutive_loss_limit
        
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_reset = datetime.now()
        
        self.is_trading_enabled = True
        self.halt_reason: Optional[str] = None
        
        logger.info(f"🛡️ RiskManager initialized: Max loss ${max_daily_loss}, Max position ${max_position_size}")
    
    def can_trade(self, amount: float) -> bool:
        """
        Check if a trade can be executed based on risk rules.
        
        Args:
            amount: Proposed trade amount in dollars
        
        Returns:
            True if trade is allowed, False otherwise
        """
        # Reset daily counters if new day
        self._check_daily_reset()
        
        # Check if trading is enabled
        if not self.is_trading_enabled:
            logger.warning(f"⚠️ Trading halted: {self.halt_reason}")
            return False
        
        # Check position size limit
        if amount > self.max_position_size:
            logger.warning(f"⚠️ Position size ${amount:.2f} exceeds limit ${self.max_position_size:.2f}")
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            self._halt_trading(f"Daily loss limit reached: ${abs(self.daily_pnl):.2f}")
            return False
        
        # Check consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            self._halt_trading(f"Consecutive loss limit reached: {self.consecutive_losses} losses")
            return False
        
        return True
    
    def record_trade(self, profit: float, success: bool):
        """
        Record a trade result.
        
        Args:
            profit: Profit/loss from trade (negative for loss)
            success: Whether trade was successful
        """
        self.daily_pnl += profit
        self.daily_trades += 1
        
        if success:
            self.consecutive_losses = 0
            logger.info(f"✅ Trade success: +${profit:.2f} | Daily P&L: ${self.daily_pnl:.2f}")
        else:
            self.consecutive_losses += 1
            logger.warning(f"❌ Trade loss: ${profit:.2f} | Consecutive losses: {self.consecutive_losses}")
        
        # Check if we've hit limits after this trade
        if self.daily_pnl <= -self.max_daily_loss:
            self._halt_trading(f"Daily loss limit reached after trade: ${abs(self.daily_pnl):.2f}")
        
        if self.consecutive_losses >= self.consecutive_loss_limit:
            self._halt_trading(f"Consecutive loss limit reached: {self.consecutive_losses} losses")
    
    def calculate_position_size(self, risk_score: float, base_amount: float = 100) -> float:
        """
        Calculate optimal position size based on risk score.
        
        Args:
            risk_score: Risk score (0.0 to 1.0)
            base_amount: Base position amount
        
        Returns:
            Calculated position size
        """
        # Lower risk = larger position
        multiplier = 1.0 - risk_score
        position = base_amount * multiplier
        
        # Enforce max position size
        return min(position, self.max_position_size)
    
    def calculate_stop_loss(self, position_size: float) -> float:
        """Calculate stop loss amount for a position."""
        return position_size * self.stop_loss_percent
    
    def _check_daily_reset(self):
        """Reset daily counters if it's a new day."""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            logger.info(f"📅 Daily reset: Previous P&L ${self.daily_pnl:.2f}, {self.daily_trades} trades")
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.consecutive_losses = 0
            self.last_reset = now
            self.is_trading_enabled = True
            self.halt_reason = None
    
    def _halt_trading(self, reason: str):
        """Halt all trading."""
        self.is_trading_enabled = False
        self.halt_reason = reason
        logger.error(f"🛑 TRADING HALTED: {reason}")
    
    def enable_trading(self):
        """Manually re-enable trading."""
        self.is_trading_enabled = True
        self.halt_reason = None
        logger.info("✅ Trading re-enabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current risk management status."""
        return {
            "is_trading_enabled": self.is_trading_enabled,
            "halt_reason": self.halt_reason,
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "consecutive_losses": self.consecutive_losses,
            "max_daily_loss": self.max_daily_loss,
            "max_position_size": self.max_position_size,
            "remaining_daily_loss": self.max_daily_loss + self.daily_pnl if self.daily_pnl < 0 else self.max_daily_loss
        }


#!/usr/bin/env python3
"""
🛡️ RISK MANAGEMENT SYSTEM - SOVEREIGNSHADOW.AI
Institutional-grade risk management for all environments
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger("risk_manager")

@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    portfolio_value: float
    daily_pnl: float
    total_pnl: float
    max_drawdown: float
    current_drawdown: float
    sharpe_ratio: float
    win_rate: float
    daily_trades: int
    consecutive_losses: int
    position_exposure: float
    correlation_risk: float

@dataclass
class RiskAlert:
    """Risk alert data structure"""
    alert_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: datetime
    action_required: str
    auto_triggered: bool = False

class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.initial_capital = config.get('starting_capital', 1000)
        self.max_position_size = config.get('max_position_size', 0.02)
        self.max_daily_trades = config.get('max_daily_trades', 10)
        self.daily_loss_limit = config.get('daily_loss_limit', 0.02)
        self.max_drawdown_limit = config.get('max_drawdown', 0.05)
        self.stop_loss = config.get('stop_loss', 0.02)
        self.take_profit = config.get('take_profit', 0.01)
        self.consecutive_loss_limit = config.get('consecutive_loss_limit', 3)
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.peak_portfolio_value = self.initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        self.active_positions = {}
        self.risk_alerts = []
        
        # Performance tracking
        self.trade_history = []
        self.daily_returns = []
        self.volatility_window = 30  # days
        
    def validate_trade(self, trade_signal: Dict) -> Tuple[bool, str, Optional[RiskAlert]]:
        """Validate a trade against risk parameters"""
        
        # Check daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            alert = RiskAlert(
                alert_type="daily_trade_limit",
                severity="high",
                message=f"Daily trade limit reached: {self.daily_trades}/{self.max_daily_trades}",
                timestamp=datetime.now(),
                action_required="Stop trading for the day"
            )
            return False, "Daily trade limit exceeded", alert
        
        # Check daily loss limit
        current_portfolio_value = self.initial_capital + self.total_pnl
        daily_loss_threshold = -self.daily_loss_limit * current_portfolio_value
        
        if self.daily_pnl <= daily_loss_threshold:
            alert = RiskAlert(
                alert_type="daily_loss_limit",
                severity="critical",
                message=f"Daily loss limit exceeded: ${self.daily_pnl:.2f}",
                timestamp=datetime.now(),
                action_required="Emergency stop trading",
                auto_triggered=True
            )
            return False, "Daily loss limit exceeded", alert
        
        # Check consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            alert = RiskAlert(
                alert_type="consecutive_losses",
                severity="high",
                message=f"Consecutive losses limit reached: {self.consecutive_losses}",
                timestamp=datetime.now(),
                action_required="Trading halt until cooldown period"
            )
            return False, "Too many consecutive losses", alert
        
        # Check position size
        position_value = trade_signal.get('quantity', 0) * trade_signal.get('buy_price', 0)
        max_position_value = current_portfolio_value * self.max_position_size
        
        if position_value > max_position_value:
            alert = RiskAlert(
                alert_type="position_size",
                severity="medium",
                message=f"Position size exceeds limit: ${position_value:.2f} > ${max_position_value:.2f}",
                timestamp=datetime.now(),
                action_required="Reduce position size"
            )
            return False, "Position size exceeds limit", alert
        
        # Check maximum drawdown
        if self.current_drawdown >= self.max_drawdown_limit:
            alert = RiskAlert(
                alert_type="max_drawdown",
                severity="critical",
                message=f"Maximum drawdown exceeded: {self.current_drawdown:.2%}",
                timestamp=datetime.now(),
                action_required="Emergency stop trading",
                auto_triggered=True
            )
            return False, "Maximum drawdown exceeded", alert
        
        # Check correlation risk
        correlation_risk = self._calculate_correlation_risk(trade_signal)
        if correlation_risk > 0.7:  # High correlation threshold
            alert = RiskAlert(
                alert_type="correlation_risk",
                severity="medium",
                message=f"High correlation risk detected: {correlation_risk:.2%}",
                timestamp=datetime.now(),
                action_required="Diversify positions"
            )
            return False, "High correlation risk", alert
        
        return True, "Trade approved", None
    
    def update_trade_result(self, trade_result: Dict):
        """Update risk metrics after trade execution"""
        self.daily_trades += 1
        
        profit = trade_result.get('profit', 0)
        self.daily_pnl += profit
        self.total_pnl += profit
        
        # Update consecutive losses
        if profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Update portfolio value and drawdown
        current_portfolio_value = self.initial_capital + self.total_pnl
        
        if current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_portfolio_value
        
        self.current_drawdown = (self.peak_portfolio_value - current_portfolio_value) / self.peak_portfolio_value
        
        if self.current_drawdown > self.max_drawdown:
            self.max_drawdown = self.current_drawdown
        
        # Record trade
        self.trade_history.append({
            'timestamp': datetime.now().isoformat(),
            'profit': profit,
            'portfolio_value': current_portfolio_value,
            'drawdown': self.current_drawdown
        })
        
        # Check for risk alerts
        self._check_risk_alerts()
    
    def _calculate_correlation_risk(self, trade_signal: Dict) -> float:
        """Calculate correlation risk with existing positions"""
        if not self.active_positions:
            return 0.0
        
        # Simplified correlation calculation
        # In a real system, this would use historical price data
        currency = trade_signal.get('currency', '')
        similar_positions = sum(1 for pos in self.active_positions.values() 
                               if pos.get('currency', '') == currency)
        
        return similar_positions / len(self.active_positions) if self.active_positions else 0.0
    
    def _check_risk_alerts(self):
        """Check for risk conditions and generate alerts"""
        current_portfolio_value = self.initial_capital + self.total_pnl
        
        # Check drawdown alerts
        if self.current_drawdown > 0.03:  # 3% drawdown
            alert = RiskAlert(
                alert_type="drawdown_warning",
                severity="medium",
                message=f"Portfolio drawdown: {self.current_drawdown:.2%}",
                timestamp=datetime.now(),
                action_required="Monitor positions closely"
            )
            self.risk_alerts.append(alert)
        
        # Check daily loss alerts
        if self.daily_pnl < -0.01 * current_portfolio_value:  # 1% daily loss
            alert = RiskAlert(
                alert_type="daily_loss_warning",
                severity="medium",
                message=f"Daily loss: ${self.daily_pnl:.2f}",
                timestamp=datetime.now(),
                action_required="Consider reducing position sizes"
            )
            self.risk_alerts.append(alert)
        
        # Check volatility alerts
        if len(self.daily_returns) >= 5:
            volatility = self._calculate_volatility()
            if volatility > 0.05:  # 5% daily volatility
                alert = RiskAlert(
                    alert_type="high_volatility",
                    severity="medium",
                    message=f"High volatility detected: {volatility:.2%}",
                    timestamp=datetime.now(),
                    action_required="Reduce position sizes or halt trading"
                )
                self.risk_alerts.append(alert)
    
    def _calculate_volatility(self) -> float:
        """Calculate portfolio volatility"""
        if len(self.daily_returns) < 2:
            return 0.0
        
        # Simple volatility calculation
        returns = self.daily_returns[-self.volatility_window:]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return variance ** 0.5
    
    def should_stop_trading(self) -> Tuple[bool, str, Optional[RiskAlert]]:
        """Check if trading should be stopped"""
        
        # Check daily loss limit
        current_portfolio_value = self.initial_capital + self.total_pnl
        daily_loss_threshold = -self.daily_loss_limit * current_portfolio_value
        
        if self.daily_pnl <= daily_loss_threshold:
            alert = RiskAlert(
                alert_type="daily_loss_stop",
                severity="critical",
                message=f"Daily loss limit exceeded: ${self.daily_pnl:.2f}",
                timestamp=datetime.now(),
                action_required="Emergency stop trading",
                auto_triggered=True
            )
            return True, "Daily loss limit exceeded", alert
        
        # Check maximum drawdown
        if self.current_drawdown >= self.max_drawdown_limit:
            alert = RiskAlert(
                alert_type="drawdown_stop",
                severity="critical",
                message=f"Maximum drawdown exceeded: {self.current_drawdown:.2%}",
                timestamp=datetime.now(),
                action_required="Emergency stop trading",
                auto_triggered=True
            )
            return True, "Maximum drawdown exceeded", alert
        
        # Check consecutive losses
        if self.consecutive_losses >= self.consecutive_loss_limit:
            alert = RiskAlert(
                alert_type="consecutive_loss_stop",
                severity="high",
                message=f"Consecutive losses limit reached: {self.consecutive_losses}",
                timestamp=datetime.now(),
                action_required="Trading halt until cooldown period"
            )
            return True, "Too many consecutive losses", alert
        
        return False, "Trading can continue", None
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Get current risk metrics"""
        current_portfolio_value = self.initial_capital + self.total_pnl
        win_rate = self._calculate_win_rate()
        
        return RiskMetrics(
            portfolio_value=current_portfolio_value,
            daily_pnl=self.daily_pnl,
            total_pnl=self.total_pnl,
            max_drawdown=self.max_drawdown,
            current_drawdown=self.current_drawdown,
            sharpe_ratio=self._calculate_sharpe_ratio(),
            win_rate=win_rate,
            daily_trades=self.daily_trades,
            consecutive_losses=self.consecutive_losses,
            position_exposure=self._calculate_position_exposure(),
            correlation_risk=self._calculate_correlation_risk({})
        )
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from trade history"""
        if not self.trade_history:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trade_history if trade.get('profit', 0) > 0)
        return winning_trades / len(self.trade_history)
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        if len(self.daily_returns) < 2:
            return 0.0
        
        mean_return = sum(self.daily_returns) / len(self.daily_returns)
        volatility = self._calculate_volatility()
        
        if volatility == 0:
            return 0.0
        
        return mean_return / volatility
    
    def _calculate_position_exposure(self) -> float:
        """Calculate current position exposure"""
        if not self.active_positions:
            return 0.0
        
        total_exposure = sum(pos.get('value', 0) for pos in self.active_positions.values())
        current_portfolio_value = self.initial_capital + self.total_pnl
        
        return total_exposure / current_portfolio_value if current_portfolio_value > 0 else 0.0
    
    def reset_daily_metrics(self):
        """Reset daily metrics (called at start of new trading day)"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        
        # Add daily return to history
        if self.total_pnl != 0:
            daily_return = self.daily_pnl / (self.initial_capital + self.total_pnl - self.daily_pnl)
            self.daily_returns.append(daily_return)
            
            # Keep only recent returns
            if len(self.daily_returns) > self.volatility_window:
                self.daily_returns = self.daily_returns[-self.volatility_window:]
    
    def get_active_alerts(self) -> List[RiskAlert]:
        """Get active risk alerts"""
        # Filter alerts from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        return [alert for alert in self.risk_alerts if alert.timestamp > cutoff_time]
    
    def export_risk_report(self) -> Dict:
        """Export comprehensive risk report"""
        metrics = self.get_risk_metrics()
        active_alerts = self.get_active_alerts()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'risk_metrics': {
                'portfolio_value': metrics.portfolio_value,
                'daily_pnl': metrics.daily_pnl,
                'total_pnl': metrics.total_pnl,
                'max_drawdown': metrics.max_drawdown,
                'current_drawdown': metrics.current_drawdown,
                'sharpe_ratio': metrics.sharpe_ratio,
                'win_rate': metrics.win_rate,
                'daily_trades': metrics.daily_trades,
                'consecutive_losses': metrics.consecutive_losses,
                'position_exposure': metrics.position_exposure,
                'correlation_risk': metrics.correlation_risk
            },
            'active_alerts': [
                {
                    'type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'action_required': alert.action_required,
                    'auto_triggered': alert.auto_triggered
                }
                for alert in active_alerts
            ],
            'risk_limits': {
                'max_position_size': self.max_position_size,
                'max_daily_trades': self.max_daily_trades,
                'daily_loss_limit': self.daily_loss_limit,
                'max_drawdown_limit': self.max_drawdown_limit,
                'consecutive_loss_limit': self.consecutive_loss_limit
            }
        }

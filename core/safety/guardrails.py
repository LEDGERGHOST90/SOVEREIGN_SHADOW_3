#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - SAFETY GUARDRAILS
Critical safety checks and risk limits

MANDATORY BEFORE ANY LIVE TRADING:
1. Environment validation
2. Position size limits
3. Stop loss enforcement
4. Daily loss limits
5. API key validation

Author: SovereignShadow Trading System
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyStatus(str, Enum):
    """Safety check status"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SafetyCheck:
    """Result of a safety check"""
    name: str
    status: SafetyStatus
    message: str
    details: Dict[str, Any] = None


class SafetyGuardrails:
    """
    Safety guardrails for autonomous trading
    
    Features:
    - Pre-trade validation
    - Position size enforcement
    - Daily loss limits
    - Cooldown periods
    - Environment validation
    """
    
    # Hard limits - CANNOT be overridden
    ABSOLUTE_MAX_POSITION_SIZE = 0.20  # 20% absolute max
    ABSOLUTE_MAX_DAILY_LOSS = 0.10  # 10% daily loss = stop trading
    ABSOLUTE_MIN_STOP_LOSS = 0.005  # 0.5% minimum stop loss
    
    def __init__(
        self,
        max_position_size: float = 0.10,
        max_daily_loss: float = 0.03,
        max_single_trade_loss: float = 0.02,
        cooldown_seconds: int = 300,
        max_trades_per_day: int = 20,
        max_open_positions: int = 3
    ):
        """
        Initialize safety guardrails
        
        Args:
            max_position_size: Max position as % of portfolio (0.10 = 10%)
            max_daily_loss: Max daily loss before stopping (0.03 = 3%)
            max_single_trade_loss: Max loss per trade (0.02 = 2%)
            cooldown_seconds: Minimum time between trades
            max_trades_per_day: Maximum trades per day
            max_open_positions: Maximum concurrent positions
        """
        # Enforce absolute limits
        self.max_position_size = min(max_position_size, self.ABSOLUTE_MAX_POSITION_SIZE)
        self.max_daily_loss = min(max_daily_loss, self.ABSOLUTE_MAX_DAILY_LOSS)
        self.max_single_trade_loss = max_single_trade_loss
        self.cooldown_seconds = cooldown_seconds
        self.max_trades_per_day = max_trades_per_day
        self.max_open_positions = max_open_positions
        
        # State tracking
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.last_trade_time: Optional[datetime] = None
        self.violations: List[SafetyCheck] = []
        
        logger.info(f"""
🛡️  SAFETY GUARDRAILS ACTIVE
=============================
Max Position Size: {self.max_position_size * 100}%
Max Daily Loss: {self.max_daily_loss * 100}%
Max Single Trade Loss: {self.max_single_trade_loss * 100}%
Cooldown: {self.cooldown_seconds}s
Max Trades/Day: {self.max_trades_per_day}
Max Open Positions: {self.max_open_positions}
=============================
""")
    
    def validate_environment(self) -> SafetyCheck:
        """Validate environment for trading"""
        issues = []
        
        # Check for required environment variables
        env = os.getenv('ENV', 'development')
        if env == 'production':
            if os.getenv('ALLOW_LIVE_TRADING') != 'YES_I_UNDERSTAND_THE_RISKS':
                issues.append("Production mode requires ALLOW_LIVE_TRADING flag")
        
        # Check for API keys (should exist but not be empty)
        required_keys = ['COINBASE_API_KEY', 'COINBASE_API_SECRET']
        for key in required_keys:
            value = os.getenv(key)
            if value and len(value) < 10:
                issues.append(f"{key} appears invalid (too short)")
        
        # Check for dangerous settings
        if os.getenv('DISABLE_STOP_LOSS') == '1':
            issues.append("CRITICAL: Stop loss is disabled!")
        
        if issues:
            return SafetyCheck(
                name="environment_validation",
                status=SafetyStatus.FAILED,
                message=f"Environment validation failed: {', '.join(issues)}",
                details={'issues': issues}
            )
        
        return SafetyCheck(
            name="environment_validation",
            status=SafetyStatus.PASSED,
            message="Environment validated successfully"
        )
    
    def validate_trade(
        self,
        portfolio_value: float,
        position_value: float,
        stop_loss_distance: float,
        open_positions: int,
        asset: str
    ) -> Tuple[bool, List[SafetyCheck]]:
        """
        Validate a proposed trade
        
        Args:
            portfolio_value: Current portfolio value
            position_value: Proposed position value
            stop_loss_distance: Stop loss as % of entry price
            open_positions: Current number of open positions
            asset: Asset being traded
            
        Returns:
            (is_valid, list of safety checks)
        """
        checks = []
        is_valid = True
        
        # 1. Position size check
        position_percent = position_value / portfolio_value if portfolio_value > 0 else 1
        if position_percent > self.max_position_size:
            checks.append(SafetyCheck(
                name="position_size",
                status=SafetyStatus.FAILED,
                message=f"Position too large: {position_percent*100:.1f}% > {self.max_position_size*100}% max",
                details={'requested': position_percent, 'max': self.max_position_size}
            ))
            is_valid = False
        else:
            checks.append(SafetyCheck(
                name="position_size",
                status=SafetyStatus.PASSED,
                message=f"Position size OK: {position_percent*100:.1f}%"
            ))
        
        # 2. Stop loss check
        if stop_loss_distance < self.ABSOLUTE_MIN_STOP_LOSS:
            checks.append(SafetyCheck(
                name="stop_loss",
                status=SafetyStatus.FAILED,
                message=f"Stop loss too tight: {stop_loss_distance*100:.2f}% < {self.ABSOLUTE_MIN_STOP_LOSS*100}% min",
                details={'requested': stop_loss_distance, 'min': self.ABSOLUTE_MIN_STOP_LOSS}
            ))
            is_valid = False
        else:
            checks.append(SafetyCheck(
                name="stop_loss",
                status=SafetyStatus.PASSED,
                message=f"Stop loss OK: {stop_loss_distance*100:.2f}%"
            ))
        
        # 3. Single trade risk check
        trade_risk = position_percent * stop_loss_distance
        if trade_risk > self.max_single_trade_loss:
            checks.append(SafetyCheck(
                name="trade_risk",
                status=SafetyStatus.WARNING,
                message=f"Trade risk high: {trade_risk*100:.2f}% > {self.max_single_trade_loss*100}% target"
            ))
        
        # 4. Max positions check
        if open_positions >= self.max_open_positions:
            checks.append(SafetyCheck(
                name="max_positions",
                status=SafetyStatus.BLOCKED,
                message=f"Max positions reached: {open_positions} >= {self.max_open_positions}"
            ))
            is_valid = False
        
        # 5. Cooldown check
        if self.last_trade_time:
            time_since = (datetime.utcnow() - self.last_trade_time).total_seconds()
            if time_since < self.cooldown_seconds:
                remaining = self.cooldown_seconds - time_since
                checks.append(SafetyCheck(
                    name="cooldown",
                    status=SafetyStatus.BLOCKED,
                    message=f"Cooldown active: {remaining:.0f}s remaining"
                ))
                is_valid = False
        
        # 6. Daily trade limit
        if self.trades_today >= self.max_trades_per_day:
            checks.append(SafetyCheck(
                name="daily_trades",
                status=SafetyStatus.BLOCKED,
                message=f"Daily trade limit reached: {self.trades_today}"
            ))
            is_valid = False
        
        # 7. Daily loss limit
        daily_loss_percent = abs(self.daily_pnl) / portfolio_value if self.daily_pnl < 0 and portfolio_value > 0 else 0
        if daily_loss_percent >= self.max_daily_loss:
            checks.append(SafetyCheck(
                name="daily_loss",
                status=SafetyStatus.BLOCKED,
                message=f"Daily loss limit reached: {daily_loss_percent*100:.2f}%"
            ))
            is_valid = False
        
        return is_valid, checks
    
    def record_trade(self, pnl: float):
        """Record a completed trade"""
        self.trades_today += 1
        self.daily_pnl += pnl
        self.last_trade_time = datetime.utcnow()
    
    def reset_daily(self):
        """Reset daily counters (call at midnight)"""
        self.trades_today = 0
        self.daily_pnl = 0.0
        logger.info("🔄 Daily safety counters reset")
    
    def get_limits_summary(self) -> Dict[str, Any]:
        """Get current limits and usage"""
        return {
            'limits': {
                'max_position_size': self.max_position_size,
                'max_daily_loss': self.max_daily_loss,
                'max_single_trade_loss': self.max_single_trade_loss,
                'cooldown_seconds': self.cooldown_seconds,
                'max_trades_per_day': self.max_trades_per_day,
                'max_open_positions': self.max_open_positions
            },
            'current': {
                'trades_today': self.trades_today,
                'daily_pnl': self.daily_pnl,
                'last_trade': self.last_trade_time.isoformat() if self.last_trade_time else None,
                'cooldown_remaining': max(0, self.cooldown_seconds - (datetime.utcnow() - self.last_trade_time).total_seconds()) if self.last_trade_time else 0
            }
        }
    
    def emergency_stop(self, reason: str):
        """Trigger emergency stop"""
        logger.critical(f"🚨 EMERGENCY STOP: {reason}")
        self.max_trades_per_day = 0  # Prevent any more trades
        self.violations.append(SafetyCheck(
            name="emergency_stop",
            status=SafetyStatus.BLOCKED,
            message=f"Emergency stop triggered: {reason}"
        ))


class PreflightChecklist:
    """
    Pre-flight checklist before starting trading
    """
    
    @staticmethod
    def run_all_checks() -> Tuple[bool, List[SafetyCheck]]:
        """Run all pre-flight checks"""
        checks = []
        all_passed = True
        
        # 1. Environment check
        env_check = PreflightChecklist._check_environment()
        checks.append(env_check)
        if env_check.status == SafetyStatus.FAILED:
            all_passed = False
        
        # 2. Configuration check
        config_check = PreflightChecklist._check_configuration()
        checks.append(config_check)
        if config_check.status == SafetyStatus.FAILED:
            all_passed = False
        
        # 3. API connectivity check (placeholder)
        api_check = PreflightChecklist._check_api_connectivity()
        checks.append(api_check)
        if api_check.status == SafetyStatus.FAILED:
            all_passed = False
        
        # Print results
        print("\n🛫 PRE-FLIGHT CHECKLIST")
        print("=" * 40)
        for check in checks:
            status_emoji = {
                SafetyStatus.PASSED: "✅",
                SafetyStatus.WARNING: "⚠️",
                SafetyStatus.FAILED: "❌",
                SafetyStatus.BLOCKED: "🚫"
            }
            print(f"{status_emoji[check.status]} {check.name}: {check.message}")
        print("=" * 40)
        print(f"Result: {'ALL CHECKS PASSED' if all_passed else 'CHECKS FAILED'}")
        
        return all_passed, checks
    
    @staticmethod
    def _check_environment() -> SafetyCheck:
        """Check environment settings"""
        env = os.getenv('ENV', 'development')
        is_production = env == 'production'
        
        if is_production:
            has_flag = os.getenv('ALLOW_LIVE_TRADING') == 'YES_I_UNDERSTAND_THE_RISKS'
            if not has_flag:
                return SafetyCheck(
                    name="environment",
                    status=SafetyStatus.FAILED,
                    message="Production mode without ALLOW_LIVE_TRADING flag"
                )
        
        return SafetyCheck(
            name="environment",
            status=SafetyStatus.PASSED,
            message=f"Environment: {env}"
        )
    
    @staticmethod
    def _check_configuration() -> SafetyCheck:
        """Check configuration files"""
        # Check for required configs
        required_files = []  # Add required config files here
        
        missing = [f for f in required_files if not os.path.exists(f)]
        if missing:
            return SafetyCheck(
                name="configuration",
                status=SafetyStatus.FAILED,
                message=f"Missing config files: {missing}"
            )
        
        return SafetyCheck(
            name="configuration",
            status=SafetyStatus.PASSED,
            message="Configuration OK"
        )
    
    @staticmethod
    def _check_api_connectivity() -> SafetyCheck:
        """Check API connectivity"""
        # Placeholder - actual implementation would test exchange APIs
        return SafetyCheck(
            name="api_connectivity",
            status=SafetyStatus.PASSED,
            message="API connectivity OK (placeholder)"
        )


# Default safety configuration
DEFAULT_SAFE_LIMITS = {
    'max_position_size': 0.10,  # 10%
    'max_daily_loss': 0.03,  # 3%
    'max_single_trade_loss': 0.02,  # 2%
    'cooldown_seconds': 300,  # 5 minutes
    'max_trades_per_day': 20,
    'max_open_positions': 3
}

# Conservative limits for beginners
CONSERVATIVE_LIMITS = {
    'max_position_size': 0.05,  # 5%
    'max_daily_loss': 0.02,  # 2%
    'max_single_trade_loss': 0.01,  # 1%
    'cooldown_seconds': 600,  # 10 minutes
    'max_trades_per_day': 10,
    'max_open_positions': 2
}


if __name__ == "__main__":
    # Run pre-flight checks
    passed, checks = PreflightChecklist.run_all_checks()
    
    # Create guardrails
    guardrails = SafetyGuardrails(**DEFAULT_SAFE_LIMITS)
    
    # Test trade validation
    is_valid, trade_checks = guardrails.validate_trade(
        portfolio_value=10000,
        position_value=800,
        stop_loss_distance=0.01,
        open_positions=0,
        asset="BTC/USDT"
    )
    
    print("\n🔒 Trade Validation:")
    for check in trade_checks:
        print(f"  {check.status.value}: {check.message}")

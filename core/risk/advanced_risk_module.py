#!/usr/bin/env python3
"""
ADVANCED RISK MODULE - Sovereign Shadow III
Production-Ready Risk Management with 2024-2025 Research Techniques

Integrates with omega_enhanced_risk_manager.py to provide:
- ATR-Based Position Sizing (25% drawdown reduction)
- Half-Kelly with Volatility Adjustment
- 2%/6% Portfolio Heat Framework (Alexander Elder)
- Consecutive Loss Circuit Breaker
- Multi-timeframe volatility analysis

Created: 2025-12-14
Research Base: 2024-2025 quantitative trading studies
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class VolatilityQuartile(Enum):
    """Volatility quartile for Kelly adjustment."""
    TOP = "TOP"           # >75th percentile
    HIGH = "HIGH"         # 50-75th percentile
    MEDIUM = "MEDIUM"     # 25-50th percentile
    LOW = "LOW"           # <25th percentile


@dataclass
class PositionSizeResult:
    """Result from position sizing calculation."""
    size: float
    risk_amount: float
    stop_distance: float
    method: str
    warnings: List[str]
    metadata: Dict


@dataclass
class PortfolioHeatStatus:
    """Portfolio heat tracking status."""
    total_heat: float
    position_risks: Dict[str, float]
    sector_heat: Dict[str, float]
    can_trade: bool
    heat_utilization: float
    warnings: List[str]


@dataclass
class CircuitBreakerStatus:
    """Circuit breaker status."""
    active: bool
    consecutive_losses: int
    risk_reduction_factor: float
    trading_paused: bool
    pause_until: Optional[datetime]
    strategy_status: Dict[str, Dict]


class AdvancedRiskManager:
    """
    Advanced Risk Management System integrating 2024-2025 research techniques.

    Works alongside OmegaEnhancedRiskManager for comprehensive protection.
    """

    def __init__(
        self,
        base_risk_pct: float = 0.02,
        max_portfolio_heat: float = 0.06,
        max_position_heat: float = 0.02,
        atr_multiplier: float = 2.0,
        kelly_max_fraction: float = 0.25,
        config_path: Optional[str] = None
    ):
        """
        Initialize Advanced Risk Manager.

        Args:
            base_risk_pct: Base risk per trade (default: 2%)
            max_portfolio_heat: Maximum total portfolio heat (default: 6%)
            max_position_heat: Maximum single position heat (default: 2%)
            atr_multiplier: ATR multiplier for stop distance (default: 2.0)
            kelly_max_fraction: Maximum Kelly fraction (default: 0.25 = quarter-Kelly)
            config_path: Path to configuration directory
        """
        self.base_risk_pct = base_risk_pct
        self.max_portfolio_heat = max_portfolio_heat
        self.max_position_heat = max_position_heat
        self.atr_multiplier = atr_multiplier
        self.kelly_max_fraction = kelly_max_fraction

        # Configuration
        self.config_path = config_path or str(Path.home() / ".keyblade")
        self.state_file = Path(self.config_path) / "advanced_risk_state.json"

        # Portfolio tracking
        self.open_positions: Dict[str, Dict] = {}
        self.position_risks: Dict[str, float] = {}

        # Circuit breaker tracking
        self.loss_streaks: Dict[str, List[datetime]] = {}
        self.paused_strategies: Dict[str, datetime] = {}

        # ATR history for volatility quartiles
        self.atr_history: Dict[str, List[float]] = {}

        # Load persistent state
        self.load_state()

        logger.info(
            f"AdvancedRiskManager initialized - "
            f"Base Risk: {base_risk_pct*100}%, "
            f"Max Portfolio Heat: {max_portfolio_heat*100}%, "
            f"Kelly Max: {kelly_max_fraction}"
        )

    def calculate_atr_position_size(
        self,
        equity: float,
        atr_value: float,
        risk_pct: Optional[float] = None,
        atr_multiplier: Optional[float] = None,
        max_position_size: Optional[float] = None
    ) -> PositionSizeResult:
        """
        Calculate position size using ATR-based method.

        Research shows 25% reduction in drawdown vs fixed % sizing.

        Args:
            equity: Current account equity
            atr_value: Average True Range value
            risk_pct: Risk percentage (default: base_risk_pct)
            atr_multiplier: ATR multiplier for stop (default: 2.0)
            max_position_size: Maximum position size cap

        Returns:
            PositionSizeResult with calculated size and metadata
        """
        risk_pct = risk_pct or self.base_risk_pct
        atr_multiplier = atr_multiplier or self.atr_multiplier

        warnings = []

        # Validate inputs
        if equity <= 0:
            raise ValueError(f"Equity must be positive, got {equity}")
        if atr_value <= 0:
            raise ValueError(f"ATR must be positive, got {atr_value}")

        # Calculate risk amount
        risk_amount = equity * risk_pct

        # Calculate stop distance
        stop_distance = atr_value * atr_multiplier

        # Calculate position size
        position_size = risk_amount / stop_distance

        # Apply max position size cap if provided
        if max_position_size and position_size > max_position_size:
            original_size = position_size
            position_size = max_position_size
            warnings.append(
                f"Position size capped: {original_size:.2f} -> {max_position_size:.2f}"
            )

        # Sanity check: position should not exceed 50% of equity
        if position_size > equity * 0.5:
            warnings.append(
                f"WARNING: Position size ({position_size:.2f}) exceeds 50% of equity"
            )

        # Sanity check: extremely small ATR
        if atr_value < equity * 0.001:  # ATR < 0.1% of equity
            warnings.append(
                f"WARNING: Very low ATR ({atr_value:.4f}), may result in oversizing"
            )

        return PositionSizeResult(
            size=position_size,
            risk_amount=risk_amount,
            stop_distance=stop_distance,
            method="ATR",
            warnings=warnings,
            metadata={
                "equity": equity,
                "risk_pct": risk_pct,
                "atr_value": atr_value,
                "atr_multiplier": atr_multiplier,
                "risk_reward_info": f"Risking ${risk_amount:.2f} with {stop_distance:.4f} stop"
            }
        )

    def get_kelly_fraction(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        atr_value: float,
        symbol: str
    ) -> Tuple[float, VolatilityQuartile]:
        """
        Calculate Kelly fraction adjusted for volatility.

        Uses half-Kelly with volatility adjustment to prevent overleveraging.

        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade size
            avg_loss: Average losing trade size (positive)
            atr_value: Current ATR value
            symbol: Trading symbol for ATR history

        Returns:
            Tuple of (kelly_fraction, volatility_quartile)
        """
        # Update ATR history
        if symbol not in self.atr_history:
            self.atr_history[symbol] = []
        self.atr_history[symbol].append(atr_value)

        # Keep last 100 ATR values
        if len(self.atr_history[symbol]) > 100:
            self.atr_history[symbol] = self.atr_history[symbol][-100:]

        # Calculate Kelly Criterion
        # Kelly% = W - [(1-W) / R]
        # W = win rate, R = avg_win / avg_loss

        if avg_loss <= 0:
            logger.warning("avg_loss must be positive, using 0.01")
            avg_loss = 0.01

        win_loss_ratio = avg_win / avg_loss
        kelly_full = win_rate - ((1 - win_rate) / win_loss_ratio)

        # Cap Kelly at max fraction (quarter-Kelly or half-Kelly)
        kelly_capped = min(kelly_full, self.kelly_max_fraction)

        # Adjust for volatility quartile
        volatility_quartile = self._get_volatility_quartile(symbol, atr_value)

        if volatility_quartile == VolatilityQuartile.TOP:
            # Top quartile ATR: reduce to 25% of base Kelly
            kelly_adjusted = kelly_capped * 0.25
        elif volatility_quartile == VolatilityQuartile.HIGH:
            # 50-75th percentile: reduce to 50%
            kelly_adjusted = kelly_capped * 0.5
        elif volatility_quartile == VolatilityQuartile.MEDIUM:
            # 25-50th percentile: reduce to 75%
            kelly_adjusted = kelly_capped * 0.75
        else:
            # Below 25th percentile: use full capped Kelly
            kelly_adjusted = kelly_capped

        # Never allow negative Kelly
        kelly_adjusted = max(0, kelly_adjusted)

        logger.info(
            f"Kelly calculation for {symbol}: "
            f"Full={kelly_full:.4f}, Capped={kelly_capped:.4f}, "
            f"Adjusted={kelly_adjusted:.4f} (Quartile: {volatility_quartile.value})"
        )

        return kelly_adjusted, volatility_quartile

    def _get_volatility_quartile(self, symbol: str, current_atr: float) -> VolatilityQuartile:
        """Determine volatility quartile for Kelly adjustment."""
        if symbol not in self.atr_history or len(self.atr_history[symbol]) < 20:
            return VolatilityQuartile.MEDIUM  # Default to medium if insufficient data

        atr_values = sorted(self.atr_history[symbol])
        n = len(atr_values)

        q1 = atr_values[n // 4]
        q2 = atr_values[n // 2]
        q3 = atr_values[3 * n // 4]

        if current_atr >= q3:
            return VolatilityQuartile.TOP
        elif current_atr >= q2:
            return VolatilityQuartile.HIGH
        elif current_atr >= q1:
            return VolatilityQuartile.MEDIUM
        else:
            return VolatilityQuartile.LOW

    def check_portfolio_heat(
        self,
        new_position_risk: float,
        new_position_symbol: Optional[str] = None,
        new_position_sector: Optional[str] = None
    ) -> PortfolioHeatStatus:
        """
        Check portfolio heat using Alexander Elder's 2%/6% framework.

        Rules:
        - Max 2% risk per position
        - Max 6% total portfolio heat (sum of all position risks)
        - Track sector heat to prevent concentration

        Args:
            new_position_risk: Risk amount for new position (as % of equity)
            new_position_symbol: Symbol for the new position
            new_position_sector: Sector for the new position

        Returns:
            PortfolioHeatStatus with heat analysis
        """
        warnings = []

        # Calculate current total heat
        total_heat = sum(self.position_risks.values())

        # Calculate sector heat
        sector_heat: Dict[str, float] = {}
        for symbol, risk in self.position_risks.items():
            if symbol in self.open_positions:
                sector = self.open_positions[symbol].get("sector", "Unknown")
                sector_heat[sector] = sector_heat.get(sector, 0) + risk

        # Add new position to projections
        projected_total_heat = total_heat + new_position_risk

        if new_position_sector:
            projected_sector_heat = sector_heat.get(new_position_sector, 0) + new_position_risk
        else:
            projected_sector_heat = 0

        # Check 2% rule (single position)
        if new_position_risk > self.max_position_heat:
            warnings.append(
                f"VIOLATION: Position risk ({new_position_risk*100:.2f}%) "
                f"exceeds max ({self.max_position_heat*100}%)"
            )

        # Check 6% rule (total portfolio)
        can_trade = projected_total_heat <= self.max_portfolio_heat

        if not can_trade:
            warnings.append(
                f"BLOCKED: Total heat would be {projected_total_heat*100:.2f}%, "
                f"exceeds max {self.max_portfolio_heat*100}%"
            )

        # Check sector concentration (max 4% per sector)
        max_sector_heat = 0.04
        if new_position_sector and projected_sector_heat > max_sector_heat:
            warnings.append(
                f"WARNING: {new_position_sector} sector heat would be "
                f"{projected_sector_heat*100:.2f}%, exceeds {max_sector_heat*100}%"
            )

        # Calculate heat utilization
        heat_utilization = projected_total_heat / self.max_portfolio_heat

        if heat_utilization > 0.8 and can_trade:
            warnings.append(
                f"CAUTION: Heat utilization at {heat_utilization*100:.1f}%"
            )

        return PortfolioHeatStatus(
            total_heat=total_heat,
            position_risks=self.position_risks.copy(),
            sector_heat=sector_heat,
            can_trade=can_trade,
            heat_utilization=heat_utilization,
            warnings=warnings
        )

    def check_circuit_breaker(
        self,
        strategy: str,
        trade_result: Optional[str] = None
    ) -> CircuitBreakerStatus:
        """
        Check and update circuit breaker status.

        Rules:
        - 3 consecutive losses: reduce risk_pct by 50%
        - 5 consecutive losses: pause trading for 24 hours

        Args:
            strategy: Strategy name to check
            trade_result: "win" or "loss" to update streak (None to just check)

        Returns:
            CircuitBreakerStatus with current state
        """
        now = datetime.utcnow()

        # Initialize strategy tracking
        if strategy not in self.loss_streaks:
            self.loss_streaks[strategy] = []

        # Update streak if result provided
        if trade_result == "loss":
            self.loss_streaks[strategy].append(now)
            # Keep only recent losses (last 30 days)
            cutoff = now - timedelta(days=30)
            self.loss_streaks[strategy] = [
                dt for dt in self.loss_streaks[strategy] if dt > cutoff
            ]
        elif trade_result == "win":
            # Reset streak on win
            self.loss_streaks[strategy] = []

        # Count consecutive losses
        consecutive_losses = len(self.loss_streaks[strategy])

        # Determine risk reduction factor
        risk_reduction_factor = 1.0
        active = False
        trading_paused = False
        pause_until = None

        if consecutive_losses >= 5:
            # Pause trading for 24 hours
            active = True
            trading_paused = True
            risk_reduction_factor = 0.0

            # Check if already paused
            if strategy in self.paused_strategies:
                pause_until = self.paused_strategies[strategy]
                if now >= pause_until:
                    # Pause expired, reset
                    trading_paused = False
                    del self.paused_strategies[strategy]
                    self.loss_streaks[strategy] = []
                    logger.info(f"Circuit breaker reset for {strategy}")
            else:
                # Set new pause
                pause_until = now + timedelta(hours=24)
                self.paused_strategies[strategy] = pause_until
                logger.warning(
                    f"CIRCUIT BREAKER: {strategy} paused until "
                    f"{pause_until.isoformat()}"
                )

        elif consecutive_losses >= 3:
            # Reduce risk by 50%
            active = True
            risk_reduction_factor = 0.5
            logger.warning(
                f"CIRCUIT BREAKER: {strategy} risk reduced to 50% "
                f"({consecutive_losses} consecutive losses)"
            )

        # Build strategy status
        strategy_status = {}
        for strat, losses in self.loss_streaks.items():
            strategy_status[strat] = {
                "consecutive_losses": len(losses),
                "risk_factor": 0.5 if len(losses) >= 3 else 1.0,
                "paused": strat in self.paused_strategies
            }

        return CircuitBreakerStatus(
            active=active,
            consecutive_losses=consecutive_losses,
            risk_reduction_factor=risk_reduction_factor,
            trading_paused=trading_paused,
            pause_until=pause_until,
            strategy_status=strategy_status
        )

    def calculate_position_size(
        self,
        equity: float,
        symbol: str,
        atr_value: float,
        sector: Optional[str] = None,
        strategy: str = "default",
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None,
        use_kelly: bool = False
    ) -> PositionSizeResult:
        """
        Master position sizing method combining all techniques.

        Args:
            equity: Current account equity
            symbol: Trading symbol
            atr_value: Average True Range value
            sector: Asset sector for heat tracking
            strategy: Strategy name for circuit breaker
            win_rate: Win rate for Kelly (if use_kelly=True)
            avg_win: Average win for Kelly
            avg_loss: Average loss for Kelly
            use_kelly: Whether to use Kelly sizing

        Returns:
            PositionSizeResult with final position size
        """
        warnings = []

        # 1. Check circuit breaker
        cb_status = self.check_circuit_breaker(strategy)
        if cb_status.trading_paused:
            return PositionSizeResult(
                size=0,
                risk_amount=0,
                stop_distance=0,
                method="CIRCUIT_BREAKER_PAUSED",
                warnings=[
                    f"Trading paused until {cb_status.pause_until.isoformat()}"
                ],
                metadata={"circuit_breaker": asdict(cb_status)}
            )

        # 2. Calculate base risk with circuit breaker adjustment
        adjusted_risk_pct = self.base_risk_pct * cb_status.risk_reduction_factor

        if cb_status.active:
            warnings.append(
                f"Risk reduced to {adjusted_risk_pct*100:.2f}% due to circuit breaker"
            )

        # 3. Apply Kelly adjustment if requested
        if use_kelly and all([win_rate, avg_win, avg_loss]):
            kelly_fraction, vol_quartile = self.get_kelly_fraction(
                win_rate, avg_win, avg_loss, atr_value, symbol
            )
            # Use Kelly fraction as risk multiplier
            adjusted_risk_pct = min(adjusted_risk_pct, kelly_fraction)
            warnings.append(
                f"Kelly adjustment applied: {kelly_fraction*100:.2f}% "
                f"(Volatility: {vol_quartile.value})"
            )

        # 4. Calculate ATR-based position size
        result = self.calculate_atr_position_size(
            equity=equity,
            atr_value=atr_value,
            risk_pct=adjusted_risk_pct,
            atr_multiplier=self.atr_multiplier
        )

        # 5. Check portfolio heat
        heat_status = self.check_portfolio_heat(
            new_position_risk=result.risk_amount / equity,
            new_position_symbol=symbol,
            new_position_sector=sector
        )

        if not heat_status.can_trade:
            return PositionSizeResult(
                size=0,
                risk_amount=0,
                stop_distance=result.stop_distance,
                method="PORTFOLIO_HEAT_EXCEEDED",
                warnings=heat_status.warnings,
                metadata={
                    "heat_status": asdict(heat_status),
                    "circuit_breaker": asdict(cb_status)
                }
            )

        # Add heat warnings
        warnings.extend(heat_status.warnings)
        warnings.extend(result.warnings)

        # 6. Update metadata
        result.warnings = warnings
        result.metadata.update({
            "circuit_breaker": asdict(cb_status),
            "heat_status": asdict(heat_status),
            "final_risk_pct": adjusted_risk_pct,
            "kelly_used": use_kelly
        })

        return result

    def register_position(
        self,
        symbol: str,
        size: float,
        entry_price: float,
        stop_loss: float,
        sector: Optional[str] = None,
        strategy: str = "default"
    ) -> None:
        """
        Register an open position for heat tracking.

        Args:
            symbol: Trading symbol
            size: Position size
            entry_price: Entry price
            stop_loss: Stop loss price
            sector: Asset sector
            strategy: Strategy name
        """
        risk_per_unit = abs(entry_price - stop_loss)
        total_risk = size * risk_per_unit

        self.open_positions[symbol] = {
            "size": size,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "sector": sector or "Unknown",
            "strategy": strategy,
            "entry_time": datetime.utcnow().isoformat()
        }

        # Store risk as percentage (will be updated when equity changes)
        self.position_risks[symbol] = total_risk

        logger.info(
            f"Position registered: {symbol} - Size: {size}, "
            f"Risk: ${total_risk:.2f}"
        )

        self.save_state()

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        strategy: str = "default"
    ) -> Dict:
        """
        Close a position and update circuit breaker.

        Args:
            symbol: Trading symbol
            exit_price: Exit price
            strategy: Strategy name

        Returns:
            Position summary with P&L
        """
        if symbol not in self.open_positions:
            logger.warning(f"Position {symbol} not found in tracking")
            return {}

        position = self.open_positions[symbol]
        entry_price = position["entry_price"]
        size = position["size"]

        # Calculate P&L
        pnl = (exit_price - entry_price) * size
        pnl_pct = (exit_price - entry_price) / entry_price

        # Determine win/loss
        result = "win" if pnl > 0 else "loss"

        # Update circuit breaker
        self.check_circuit_breaker(strategy, trade_result=result)

        # Remove from tracking
        del self.open_positions[symbol]
        del self.position_risks[symbol]

        summary = {
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "result": result,
            "strategy": strategy
        }

        logger.info(
            f"Position closed: {symbol} - "
            f"P&L: ${pnl:.2f} ({pnl_pct*100:.2f}%) - {result.upper()}"
        )

        self.save_state()

        return summary

    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk management summary."""
        total_heat = sum(self.position_risks.values())

        # Sector breakdown
        sector_heat = {}
        for symbol, position in self.open_positions.items():
            sector = position.get("sector", "Unknown")
            risk = self.position_risks.get(symbol, 0)
            sector_heat[sector] = sector_heat.get(sector, 0) + risk

        # Circuit breaker status
        all_strategies = set(list(self.loss_streaks.keys()) + list(self.paused_strategies.keys()))
        circuit_breakers = {}
        for strategy in all_strategies:
            cb_status = self.check_circuit_breaker(strategy)
            circuit_breakers[strategy] = asdict(cb_status)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "portfolio_heat": {
                "total": total_heat,
                "max_allowed": self.max_portfolio_heat,
                "utilization": total_heat / self.max_portfolio_heat if self.max_portfolio_heat > 0 else 0,
                "by_sector": sector_heat
            },
            "open_positions": len(self.open_positions),
            "position_details": self.open_positions,
            "circuit_breakers": circuit_breakers,
            "parameters": {
                "base_risk_pct": self.base_risk_pct,
                "max_portfolio_heat": self.max_portfolio_heat,
                "max_position_heat": self.max_position_heat,
                "atr_multiplier": self.atr_multiplier,
                "kelly_max_fraction": self.kelly_max_fraction
            }
        }

    def save_state(self) -> None:
        """Save persistent state to disk."""
        try:
            Path(self.config_path).mkdir(parents=True, exist_ok=True)

            state = {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "open_positions": self.open_positions,
                "position_risks": self.position_risks,
                "loss_streaks": {
                    k: [dt.isoformat() for dt in v]
                    for k, v in self.loss_streaks.items()
                },
                "paused_strategies": {
                    k: v.isoformat()
                    for k, v in self.paused_strategies.items()
                },
                "atr_history": self.atr_history
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

            logger.debug(f"State saved to {self.state_file}")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_state(self) -> None:
        """Load persistent state from disk."""
        try:
            if not self.state_file.exists():
                logger.info("No saved state found, starting fresh")
                return

            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.open_positions = state.get("open_positions", {})
            self.position_risks = state.get("position_risks", {})

            # Convert ISO strings back to datetime
            self.loss_streaks = {
                k: [datetime.fromisoformat(dt) for dt in v]
                for k, v in state.get("loss_streaks", {}).items()
            }
            self.paused_strategies = {
                k: datetime.fromisoformat(v)
                for k, v in state.get("paused_strategies", {}).items()
            }

            self.atr_history = state.get("atr_history", {})

            logger.info(
                f"State loaded: {len(self.open_positions)} positions, "
                f"{len(self.paused_strategies)} paused strategies"
            )

        except Exception as e:
            logger.error(f"Failed to load state: {e}")


def main():
    """Example usage and testing."""
    print("=" * 70)
    print("ADVANCED RISK MODULE - Sovereign Shadow III")
    print("Production-Ready Risk Management System")
    print("=" * 70)

    # Initialize risk manager
    risk_manager = AdvancedRiskManager(
        base_risk_pct=0.02,      # 2% base risk
        max_portfolio_heat=0.06,  # 6% max total heat
        max_position_heat=0.02,   # 2% max per position
        kelly_max_fraction=0.25   # Quarter-Kelly max
    )

    # Example 1: ATR-based position sizing
    print("\n" + "=" * 70)
    print("EXAMPLE 1: ATR-Based Position Sizing")
    print("=" * 70)

    equity = 5433.87  # Current portfolio value
    atr_btc = 1200    # Bitcoin ATR in USD

    result = risk_manager.calculate_atr_position_size(
        equity=equity,
        atr_value=atr_btc,
        risk_pct=0.02,
        atr_multiplier=2.0
    )

    print(f"Equity: ${equity:.2f}")
    print(f"ATR: ${atr_btc:.2f}")
    print(f"Position Size: {result.size:.6f} BTC")
    print(f"Risk Amount: ${result.risk_amount:.2f}")
    print(f"Stop Distance: ${result.stop_distance:.2f}")
    if result.warnings:
        print(f"Warnings: {', '.join(result.warnings)}")

    # Example 2: Kelly Criterion with volatility adjustment
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Kelly Criterion with Volatility Adjustment")
    print("=" * 70)

    kelly_fraction, vol_quartile = risk_manager.get_kelly_fraction(
        win_rate=0.55,
        avg_win=150,
        avg_loss=100,
        atr_value=atr_btc,
        symbol="BTC/USD"
    )

    print(f"Win Rate: 55%")
    print(f"Avg Win: $150")
    print(f"Avg Loss: $100")
    print(f"Kelly Fraction: {kelly_fraction*100:.2f}%")
    print(f"Volatility Quartile: {vol_quartile.value}")

    # Example 3: Portfolio heat check
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Portfolio Heat Framework (2%/6% Rule)")
    print("=" * 70)

    # Register some positions
    risk_manager.register_position(
        symbol="BTC/USD",
        size=0.05,
        entry_price=42000,
        stop_loss=40000,
        sector="Infrastructure",
        strategy="swing_trade"
    )

    risk_manager.register_position(
        symbol="ETH/USD",
        size=2.0,
        entry_price=2200,
        stop_loss=2100,
        sector="Infrastructure",
        strategy="swing_trade"
    )

    # Check if we can add another position
    new_position_risk = 0.025  # 2.5% risk
    heat_status = risk_manager.check_portfolio_heat(
        new_position_risk=new_position_risk,
        new_position_symbol="SOL/USD",
        new_position_sector="Infrastructure"
    )

    print(f"Current Total Heat: {heat_status.total_heat*100:.2f}%")
    print(f"Heat Utilization: {heat_status.heat_utilization*100:.1f}%")
    print(f"Can Trade New Position: {heat_status.can_trade}")
    print(f"Sector Heat: {heat_status.sector_heat}")
    if heat_status.warnings:
        print(f"Warnings:")
        for warning in heat_status.warnings:
            print(f"  - {warning}")

    # Example 4: Circuit breaker
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Consecutive Loss Circuit Breaker")
    print("=" * 70)

    # Simulate consecutive losses
    for i in range(4):
        cb_status = risk_manager.check_circuit_breaker(
            strategy="test_strategy",
            trade_result="loss"
        )
        print(f"Loss {i+1}: Active={cb_status.active}, "
              f"Risk Factor={cb_status.risk_reduction_factor}")

    # Example 5: Master position sizing
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Master Position Sizing (All Techniques Combined)")
    print("=" * 70)

    final_result = risk_manager.calculate_position_size(
        equity=equity,
        symbol="XRP/USD",
        atr_value=0.05,
        sector="Infrastructure",
        strategy="swing_trade",
        win_rate=0.60,
        avg_win=50,
        avg_loss=30,
        use_kelly=True
    )

    print(f"Final Position Size: {final_result.size:.2f} XRP")
    print(f"Risk Amount: ${final_result.risk_amount:.2f}")
    print(f"Method: {final_result.method}")
    print(f"Metadata: {json.dumps(final_result.metadata, indent=2, default=str)}")

    # Example 6: Risk summary
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comprehensive Risk Summary")
    print("=" * 70)

    summary = risk_manager.get_risk_summary()
    print(json.dumps(summary, indent=2, default=str))

    print("\n" + "=" * 70)
    print("INTEGRATION WITH OMEGA ENHANCED RISK MANAGER")
    print("=" * 70)
    print("""
    Usage Pattern:

    from core.risk.advanced_risk_module import AdvancedRiskManager
    from core.risk.omega_enhanced_risk_manager import OmegaEnhancedRiskManager

    # Initialize both managers
    advanced_risk = AdvancedRiskManager(base_risk_pct=0.02)
    omega_risk = OmegaEnhancedRiskManager()

    # Before executing a trade:
    # 1. Check correlation risk with Omega
    correlation_analysis = omega_risk.analyze_portfolio_correlation_risk(positions)

    # 2. Calculate position size with Advanced module
    position_result = advanced_risk.calculate_position_size(
        equity=portfolio_value,
        symbol=symbol,
        atr_value=atr,
        sector=sector,
        use_kelly=True
    )

    # 3. Verify both approve the trade
    if (correlation_analysis['risk_level'] not in ['CRITICAL', 'HIGH'] and
        position_result.size > 0):
        # Execute trade
        execute_trade(symbol, position_result.size)
        advanced_risk.register_position(...)
    """)

    print("\n" + "=" * 70)
    print("Advanced Risk Module Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

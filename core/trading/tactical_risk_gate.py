#!/usr/bin/env python3
"""
🛡️ Tactical Risk Gate - Enforces LSR thresholds, funding divergence, and health factor floors

Validates all tactical scalp trades against:
- Long/Short Ratio positioning guards
- Funding rate divergence filters
- Open Interest risk adjustments
- Aave Health Factor floors
- Sovereign Shadow global safety limits

Part of the Sovereign Shadow Trading System
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class MarketPositioning:
    """Current market positioning data"""
    asset: str
    long_pct: float
    short_pct: float
    timestamp: datetime
    
    @property
    def short_heavy(self) -> bool:
        return self.short_pct > self.long_pct


@dataclass
class FundingData:
    """Funding rate data across exchanges"""
    asset: str
    binance_bps: float
    okx_bps: float
    timestamp: datetime
    
    @property
    def spread_bps(self) -> float:
        return self.binance_bps - self.okx_bps
    
    @property
    def has_divergence(self) -> bool:
        return abs(self.spread_bps) >= 0.25


@dataclass
class TradeRequest:
    """Incoming trade request to validate"""
    strategy_name: str
    asset: str
    side: str  # "long" or "short"
    notional_usd: float
    stop_loss_bps: float
    entry_price: float
    conditions_met: Dict[str, bool]
    timestamp: datetime


@dataclass
class ValidationResult:
    """Result of risk gate validation"""
    approved: bool
    reason: str
    size_adjustment: float = 1.0  # Multiplier for position size
    stop_adjustment_bps: Optional[float] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class TacticalRiskGate:
    """
    Enforces risk rules for tactical scalping strategies.
    
    Three-layer validation:
    1. Sovereign Shadow global limits (hard stops)
    2. Tactical config guards (positioning, funding, OI)
    3. Real-time market conditions (health factor, volatility)
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/Volumes/LegacySafe/SovereignShadow/config/tactical_scalp_config.json"
        self.config = self._load_config()
        
        # Sovereign Shadow hard limits (from CLAUDE.md)
        self.GLOBAL_MAX_POSITION_USD = 415.0  # 25% of $1,660 hot wallet
        self.GLOBAL_MAX_STOP_LOSS_PCT = 5.0
        self.GLOBAL_DAILY_LOSS_LIMIT_USD = 100.0
        self.GLOBAL_MAX_CONCURRENT_TRADES = 3
        
        # Session tracking
        self.session_trades: List[Dict] = []
        self.session_pnl_usd: float = 0.0
        self.consecutive_losses: int = 0
        self.session_start = datetime.now()
        
        # Market data cache (populated by external feeds)
        self.positioning_cache: Dict[str, MarketPositioning] = {}
        self.funding_cache: Dict[str, FundingData] = {}
        self.aave_health_factor: Optional[float] = None
        self.oi_change_24h_pct: Optional[float] = None
        
        logger.info(f"🛡️ Tactical Risk Gate initialized with config: {self.config_path}")
    
    def _load_config(self) -> Dict:
        """Load tactical scalp configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Loaded tactical config: {config.get('session_name', 'unknown')}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load tactical config: {e}")
            return {"enabled": False, "strategies": {}}
    
    def update_positioning(self, asset: str, long_pct: float, short_pct: float):
        """Update market positioning data"""
        self.positioning_cache[asset] = MarketPositioning(
            asset=asset,
            long_pct=long_pct,
            short_pct=short_pct,
            timestamp=datetime.now()
        )
        logger.debug(f"📊 Updated {asset} positioning: {long_pct:.1f}% long / {short_pct:.1f}% short")
    
    def update_funding(self, asset: str, binance_bps: float, okx_bps: float):
        """Update funding rate data"""
        self.funding_cache[asset] = FundingData(
            asset=asset,
            binance_bps=binance_bps,
            okx_bps=okx_bps,
            timestamp=datetime.now()
        )
        logger.debug(f"💸 Updated {asset} funding: Binance {binance_bps:.2f} bps, OKX {okx_bps:.2f} bps (spread: {binance_bps - okx_bps:.2f})")
    
    def update_aave_health_factor(self, hf: float):
        """Update Aave health factor"""
        self.aave_health_factor = hf
        logger.debug(f"💊 Updated Aave Health Factor: {hf:.2f}")
    
    def update_oi_change(self, change_pct: float):
        """Update 24h Open Interest change"""
        self.oi_change_24h_pct = change_pct
        logger.debug(f"📈 Updated OI 24h change: {change_pct:+.2f}%")
    
    def validate_trade(self, request: TradeRequest) -> ValidationResult:
        """
        Main validation gate - checks all rules before trade approval.
        
        Returns ValidationResult with:
        - approved: bool
        - reason: str
        - size_adjustment: float (multiplier)
        - stop_adjustment_bps: Optional[float]
        - warnings: List[str]
        """
        
        # Layer 1: Global Sovereign Shadow limits (HARD STOPS)
        layer1 = self._validate_global_limits(request)
        if not layer1.approved:
            return layer1
        
        # Layer 2: Tactical config guards (positioning, funding, OI)
        layer2 = self._validate_tactical_guards(request)
        if not layer2.approved:
            return layer2
        
        # Layer 3: Real-time market conditions
        layer3 = self._validate_market_conditions(request)
        if not layer3.approved:
            return layer3
        
        # Layer 4: Kill switch / session limits
        layer4 = self._validate_kill_switch()
        if not layer4.approved:
            return layer4
        
        # Combine adjustments and warnings
        final_size_adj = layer1.size_adjustment * layer2.size_adjustment * layer3.size_adjustment
        all_warnings = layer1.warnings + layer2.warnings + layer3.warnings + layer4.warnings
        
        stop_adj = layer2.stop_adjustment_bps or layer3.stop_adjustment_bps or request.stop_loss_bps
        
        result = ValidationResult(
            approved=True,
            reason="✅ All risk gates passed",
            size_adjustment=final_size_adj,
            stop_adjustment_bps=stop_adj,
            warnings=all_warnings
        )
        
        logger.info(f"🟢 Trade approved: {request.asset} {request.side} ${request.notional_usd * final_size_adj:.2f} (adj: {final_size_adj:.2f}×)")
        return result
    
    def _validate_global_limits(self, request: TradeRequest) -> ValidationResult:
        """Layer 1: Sovereign Shadow hard limits"""
        
        warnings = []
        size_adj = 1.0
        
        # 1. Max position size check
        if request.notional_usd > self.GLOBAL_MAX_POSITION_USD:
            return ValidationResult(
                approved=False,
                reason=f"❌ Position size ${request.notional_usd:.2f} exceeds global max ${self.GLOBAL_MAX_POSITION_USD:.2f}"
            )
        
        # 2. Stop loss check
        if request.stop_loss_bps > self.GLOBAL_MAX_STOP_LOSS_PCT * 100:
            return ValidationResult(
                approved=False,
                reason=f"❌ Stop loss {request.stop_loss_bps} bps exceeds global max {self.GLOBAL_MAX_STOP_LOSS_PCT}%"
            )
        
        # 3. Daily loss limit check
        if abs(self.session_pnl_usd) >= self.GLOBAL_DAILY_LOSS_LIMIT_USD:
            return ValidationResult(
                approved=False,
                reason=f"❌ Daily loss limit hit: ${abs(self.session_pnl_usd):.2f} >= ${self.GLOBAL_DAILY_LOSS_LIMIT_USD:.2f}"
            )
        
        # 4. Max concurrent trades check
        active_trades = [t for t in self.session_trades if t.get("status") == "open"]
        if len(active_trades) >= self.GLOBAL_MAX_CONCURRENT_TRADES:
            return ValidationResult(
                approved=False,
                reason=f"❌ Max concurrent trades reached: {len(active_trades)}/{self.GLOBAL_MAX_CONCURRENT_TRADES}"
            )
        
        # 5. Adjust size if approaching daily limit
        remaining_room = self.GLOBAL_DAILY_LOSS_LIMIT_USD - abs(self.session_pnl_usd)
        max_loss_on_trade = request.notional_usd * (request.stop_loss_bps / 10000)
        
        if max_loss_on_trade > remaining_room * 0.5:
            size_adj = 0.5
            warnings.append(f"⚠️ Size reduced 50% - approaching daily loss limit (${remaining_room:.2f} remaining)")
        
        return ValidationResult(
            approved=True,
            reason="✅ Global limits OK",
            size_adjustment=size_adj,
            warnings=warnings
        )
    
    def _validate_tactical_guards(self, request: TradeRequest) -> ValidationResult:
        """Layer 2: Tactical positioning and funding guards"""
        
        warnings = []
        size_adj = 1.0
        stop_adj = request.stop_loss_bps
        
        # 1. LSR (Long/Short Ratio) guard - don't short into heavy shorts
        if request.side == "short":
            lsr_guards = self.config.get("global_filters", {}).get("lsr_guard", {})
            asset_guard = lsr_guards.get(request.asset, {})
            no_short_threshold = asset_guard.get("no_short_if_short_notional_pct")
            
            if no_short_threshold and request.asset in self.positioning_cache:
                positioning = self.positioning_cache[request.asset]
                
                # Check if data is fresh (< 2 minutes old)
                if (datetime.now() - positioning.timestamp).seconds > 120:
                    warnings.append(f"⚠️ Positioning data for {request.asset} is stale")
                
                if positioning.short_pct >= no_short_threshold:
                    return ValidationResult(
                        approved=False,
                        reason=f"❌ LSR guard: {request.asset} shorts at {positioning.short_pct:.1f}% >= threshold {no_short_threshold}% (don't fight squeeze)"
                    )
        
        # 2. Funding divergence filter
        if request.asset in self.funding_cache:
            funding = self.funding_cache[request.asset]
            funding_config = self.config.get("global_filters", {}).get("funding_divergence", {}).get(request.asset, {})
            
            if funding_config:
                spread_config = funding_config.get("binance_minus_okx_bps", {})
                min_spread = spread_config.get("min_spread", 0)
                bias = spread_config.get("bias", "")
                
                # Check if data is fresh
                if (datetime.now() - funding.timestamp).seconds > 300:
                    warnings.append(f"⚠️ Funding data for {request.asset} is stale")
                
                # If positive spread and "long_dips_only", block shorts
                if funding.spread_bps >= min_spread and bias == "long_dips_only" and request.side == "short":
                    return ValidationResult(
                        approved=False,
                        reason=f"❌ Funding divergence: {request.asset} spread {funding.spread_bps:.2f} bps suggests long bias only"
                    )
                
                if funding.has_divergence:
                    warnings.append(f"📡 Funding divergence detected: {funding.spread_bps:+.2f} bps")
        
        # 3. Open Interest risk adjustment
        if self.oi_change_24h_pct is not None:
            oi_config = self.config.get("global_filters", {}).get("oi_risk", {})
            threshold = oi_config.get("oi_change_24h_pct_threshold", 3.0)
            
            if self.oi_change_24h_pct > threshold:
                size_adj *= oi_config.get("factor", 0.8)
                warnings.append(f"⚠️ OI spiked {self.oi_change_24h_pct:+.1f}% - size reduced to {size_adj:.1f}× (stop-run risk)")
        
        # 4. Strategy-specific guards
        strategy_config = self.config.get("strategies", {}).get(request.strategy_name, {})
        if strategy_config:
            guards = strategy_config.get("guards", {})
            
            # Check guard conditions
            if guards and request.asset in self.positioning_cache:
                positioning = self.positioning_cache[request.asset]
                
                if request.side == "short":
                    guard_threshold = guards.get("short_notional_pct_lte")
                    if guard_threshold and positioning.short_pct > guard_threshold:
                        return ValidationResult(
                            approved=False,
                            reason=f"❌ Strategy guard: {request.asset} shorts {positioning.short_pct:.1f}% > {guard_threshold}%"
                        )
            
            # Apply strategy stop adjustments
            stops_config = strategy_config.get("stops", {})
            if stops_config:
                base_bps = stops_config.get("base_bps")
                widen_to = stops_config.get("widen_to_bps")
                widen_conditions = stops_config.get("widen_conditions", [])
                
                # Check if we need to widen stops
                should_widen = False
                for condition in widen_conditions:
                    if "short_notional_pct" in condition and request.asset in self.positioning_cache:
                        positioning = self.positioning_cache[request.asset]
                        if positioning.short_pct > 54:
                            should_widen = True
                            break
                
                if should_widen and widen_to:
                    stop_adj = widen_to
                    warnings.append(f"🛡️ Stop widened to {widen_to} bps due to conditions")
        
        return ValidationResult(
            approved=True,
            reason="✅ Tactical guards OK",
            size_adjustment=size_adj,
            stop_adjustment_bps=stop_adj,
            warnings=warnings
        )
    
    def _validate_market_conditions(self, request: TradeRequest) -> ValidationResult:
        """Layer 3: Real-time market conditions"""
        
        warnings = []
        size_adj = 1.0
        
        # 1. Aave Health Factor floor
        hf_config = self.config.get("global_filters", {}).get("aave_health_factor", {})
        min_hf_for_entry = hf_config.get("min_for_new_entries", 2.20)
        flatten_hf = hf_config.get("flatten_all_if_below", 2.00)
        
        if self.aave_health_factor is not None:
            if self.aave_health_factor < flatten_hf:
                return ValidationResult(
                    approved=False,
                    reason=f"❌ CRITICAL: Aave HF {self.aave_health_factor:.2f} < {flatten_hf:.2f} - flatten all positions!"
                )
            
            if self.aave_health_factor < min_hf_for_entry:
                return ValidationResult(
                    approved=False,
                    reason=f"❌ Aave HF {self.aave_health_factor:.2f} < minimum {min_hf_for_entry:.2f} for new entries"
                )
            
            if self.aave_health_factor < min_hf_for_entry + 0.3:
                warnings.append(f"⚠️ Aave HF {self.aave_health_factor:.2f} close to minimum - proceed carefully")
        
        # 2. Capital deployment limits
        cap_config = self.config.get("capital_deployment", {})
        daily_cap = cap_config.get("daily_cap_trades", 6)
        
        trades_today = len([t for t in self.session_trades 
                           if (datetime.now() - t.get("timestamp", self.session_start)).days == 0])
        
        if trades_today >= daily_cap:
            return ValidationResult(
                approved=False,
                reason=f"❌ Daily trade cap reached: {trades_today}/{daily_cap} trades"
            )
        
        # 3. Consecutive loss protection
        stop_conditions = cap_config.get("stop_conditions", [])
        if "second_net_loss_in_row" in stop_conditions and self.consecutive_losses >= 2:
            return ValidationResult(
                approved=False,
                reason=f"❌ Consecutive loss limit: {self.consecutive_losses} losses in row"
            )
        
        return ValidationResult(
            approved=True,
            reason="✅ Market conditions OK",
            size_adjustment=size_adj,
            warnings=warnings
        )
    
    def _validate_kill_switch(self) -> ValidationResult:
        """Layer 4: Kill switch / emergency halt conditions"""
        
        warnings = []
        
        if not self.config.get("enabled", True):
            return ValidationResult(
                approved=False,
                reason="❌ Tactical scalping disabled in config"
            )
        
        kill_config = self.config.get("kill_switch", {})
        
        # 1. Session drawdown check
        max_dd_pct = kill_config.get("session_max_drawdown_pct", 1.2)
        dd_pct = abs(self.session_pnl_usd / 1660.0 * 100)  # % of hot wallet
        
        if dd_pct >= max_dd_pct:
            return ValidationResult(
                approved=False,
                reason=f"❌ KILL SWITCH: Session drawdown {dd_pct:.2f}% >= {max_dd_pct}%"
            )
        
        # 2. Max consecutive losses
        max_losses = kill_config.get("max_consecutive_losses", 5)
        if self.consecutive_losses >= max_losses:
            return ValidationResult(
                approved=False,
                reason=f"❌ KILL SWITCH: {self.consecutive_losses} consecutive losses >= {max_losses}"
            )
        
        # 3. Aave critical HF (double-check here too)
        if self.aave_health_factor is not None and self.aave_health_factor < 2.00:
            return ValidationResult(
                approved=False,
                reason=f"❌ KILL SWITCH: Aave HF {self.aave_health_factor:.2f} below critical threshold"
            )
        
        return ValidationResult(
            approved=True,
            reason="✅ Kill switch OK",
            warnings=warnings
        )
    
    def record_trade_result(self, trade_id: str, pnl_usd: float, was_loss: bool):
        """Record trade outcome for session tracking"""
        self.session_pnl_usd += pnl_usd
        
        if was_loss:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Update trade in session log
        for trade in self.session_trades:
            if trade.get("id") == trade_id:
                trade["pnl_usd"] = pnl_usd
                trade["status"] = "closed"
                trade["closed_at"] = datetime.now()
                break
        
        logger.info(f"📝 Trade {trade_id} closed: ${pnl_usd:+.2f} | Session P&L: ${self.session_pnl_usd:+.2f} | Streak: {self.consecutive_losses} losses")
    
    def add_trade_to_session(self, trade_id: str, request: TradeRequest):
        """Add new trade to session tracking"""
        self.session_trades.append({
            "id": trade_id,
            "strategy": request.strategy_name,
            "asset": request.asset,
            "side": request.side,
            "notional_usd": request.notional_usd,
            "entry_price": request.entry_price,
            "stop_loss_bps": request.stop_loss_bps,
            "timestamp": request.timestamp,
            "status": "open"
        })
        logger.debug(f"➕ Added trade {trade_id} to session ({len([t for t in self.session_trades if t['status'] == 'open'])} open)")
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        open_trades = [t for t in self.session_trades if t.get("status") == "open"]
        closed_trades = [t for t in self.session_trades if t.get("status") == "closed"]
        
        return {
            "session_pnl_usd": self.session_pnl_usd,
            "consecutive_losses": self.consecutive_losses,
            "open_trades": len(open_trades),
            "closed_trades": len(closed_trades),
            "total_trades": len(self.session_trades),
            "session_duration_min": (datetime.now() - self.session_start).seconds / 60,
            "aave_health_factor": self.aave_health_factor,
            "oi_change_24h_pct": self.oi_change_24h_pct
        }
    
    def should_halt_trading(self) -> Tuple[bool, str]:
        """
        Check if trading should be halted entirely.
        Returns (should_halt: bool, reason: str)
        """
        
        kill_config = self.config.get("kill_switch", {})
        halt_conditions = kill_config.get("halt_conditions", [])
        
        # Check each halt condition
        for condition in halt_conditions:
            if "btc_breaks_and_holds" in condition:
                # This would be checked by external price monitor
                continue
            
            if "aave_hf_below" in condition:
                if self.aave_health_factor is not None and self.aave_health_factor < 2.00:
                    return True, f"Aave HF {self.aave_health_factor:.2f} below 2.00"
            
            if "priority_fee_feed_down" in condition:
                # External feed monitor would set this
                continue
            
            if "funding_feed_diverged" in condition:
                # Check funding data freshness
                for asset, funding_data in self.funding_cache.items():
                    if (datetime.now() - funding_data.timestamp).seconds > 600:  # 10 min
                        return True, f"Funding feed for {asset} stale > 10 min"
        
        return False, ""


def demo_usage():
    """Demonstration of risk gate usage"""
    
    # Initialize gate
    gate = TacticalRiskGate()
    
    # Simulate market data updates
    gate.update_positioning("BTC", long_pct=43.8, short_pct=56.2)
    gate.update_funding("BTC", binance_bps=2.9, okx_bps=-0.7)
    gate.update_aave_health_factor(2.45)
    gate.update_oi_change(2.98)
    
    # Create a trade request
    request = TradeRequest(
        strategy_name="BTC_range_scalp",
        asset="BTC",
        side="long",
        notional_usd=25.0,
        stop_loss_bps=28,
        entry_price=106800,
        conditions_met={"reclaim": True, "delta_positive": True},
        timestamp=datetime.now()
    )
    
    # Validate
    result = gate.validate_trade(request)
    
    print(f"\n{'='*60}")
    print(f"Trade Validation Result")
    print(f"{'='*60}")
    print(f"Approved: {result.approved}")
    print(f"Reason: {result.reason}")
    print(f"Size adjustment: {result.size_adjustment:.2f}×")
    print(f"Adjusted notional: ${request.notional_usd * result.size_adjustment:.2f}")
    print(f"Stop: {result.stop_adjustment_bps or request.stop_loss_bps} bps")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  {warning}")
    
    print(f"\nSession Stats:")
    stats = gate.get_session_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    demo_usage()


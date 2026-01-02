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
import pandas as pd
from core.risk.advanced_risk_module import SentinelAdvancedRiskModule
from core.filters.market_filters import OracleMarketFilters
from core.regime.hmm_regime_detector import RegimeHMMDetector
from core.agents.reflect_agent import ReflectAgent
from core.ml.freqai_scaffold import AdaptFreqAIScaffold
from core.ml.orderbook_rl_scaffold import DepthOrderBookRLEnv
from core.signals.onchain_signals import FlowOnChainSignals

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

        # Initialize Sentinel Advanced Risk Module
        self.sentinel_risk_module = SentinelAdvancedRiskModule(self.config.get("sentinel_config", {}))
        # Initialize Oracle Market Filters Module
        self.oracle_market_filters = OracleMarketFilters(self.config.get("oracle_config", {}))
        # Initialize Regime HMM Detector Module
        self.regime_hmm_detector = RegimeHMMDetector(self.config.get("regime_config", {}))
        # Initialize Reflect Agent
        self.reflect_agent = ReflectAgent(self.config.get("reflect_config", {"initial_capital": 1660.0}))
        # Initialize Adapt FreqAI Scaffold
        self.adapt_freqai_scaffold = AdaptFreqAIScaffold(self.config.get("freqai_config", {}))
        # Initialize Depth Order Book RL Environment
        self.depth_rl_env = DepthOrderBookRLEnv(self.config.get("depth_config", {}))
        # Initialize Flow On-Chain Signals Module
        self.flow_onchain_signals = FlowOnChainSignals(self.config.get("flow_config", {}))

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

    def update_sentinel_price_data(self, asset: str, close_price: float, high_price: float, low_price: float):
        self.sentinel_risk_module.update_price_data(asset, close_price, high_price, low_price)
        logger.debug(f"SENTINEL: Updated price data for {asset}.")

    def get_atr_stop_loss(self, asset: str, multiplier: float = 2.0) -> Optional[float]:
        return self.sentinel_risk_module.calculate_atr_stop_loss(asset, multiplier)

    def get_kelly_bet_size(self, win_probability: float, payout_ratio: float, current_capital: float) -> float:
        return self.sentinel_risk_module.calculate_kelly_bet_size(win_probability, payout_ratio, current_capital)

    def is_sentinel_breaker_active(self, asset: str) -> bool:
        return self.sentinel_risk_module.is_breaker_active(asset)

    def update_oracle_fng_data(self, force_fetch: bool = False):
        self.oracle_market_filters.fetch_fear_greed_index(force_fetch=force_fetch)

    def get_oracle_fng_signal(self) -> str:
        return self.oracle_market_filters.get_fear_greed_signal()

    def update_oracle_dxy_data(self, force_fetch: bool = False):
        self.oracle_market_filters.fetch_dxy_index(force_fetch=force_fetch)

    def get_oracle_dxy_signal(self) -> str:
        return self.oracle_market_filters.get_dxy_strength_signal()

    def train_regime_detector(self, historical_data: pd.DataFrame):
        self.regime_hmm_detector.train_model(historical_data.copy())
        logger.info("REGIME HMM Detector training initiated.")

    def get_current_regime(self, latest_data: pd.DataFrame) -> str:
        return self.regime_hmm_detector.predict_regime(latest_data.copy())

    def train_freqai_model(self, data: pd.DataFrame):
        self.adapt_freqai_scaffold.train_model(data.copy())
        logger.info("ADAPT FreqAI model training initiated.")

    def get_freqai_signal(self, current_features: pd.DataFrame) -> Optional[Any]:
        return self.adapt_freqai_scaffold.predict_signal(current_features.copy())

    def run_depth_rl_simulation(self, initial_state: Optional[Dict] = None) -> Dict:
        # Simplified: In a real scenario, initial_state would be derived from live data
        obs, info = self.depth_rl_env.reset()
        if initial_state:
            # For a real env, you'd likely update the internal state based on initial_state
            pass 

        total_reward = 0.0
        final_portfolio_value = info["portfolio_value"]

        for _ in range(self.depth_rl_env.max_steps):
            # Simple random agent for demonstration within TacticalRiskGate
            action_type = np.random.randint(0, 3)  # 0:HOLD, 1:BUY, 2:SELL
            price_offset = np.random.randint(-self.depth_rl_env.num_levels, self.depth_rl_env.num_levels + 1)
            quantity_fraction = np.random.rand(1)

            action = {
                "action_type": action_type,
                "price_level_offset": price_offset,
                "quantity_fraction": quantity_fraction
            }
            obs, reward, terminated, truncated, info = self.depth_rl_env.step(action)
            total_reward += reward
            final_portfolio_value = info["portfolio_value"]

            if terminated or truncated:
                break
        
        self.depth_rl_env.close()
        return {"total_reward": total_reward, "final_portfolio_value": final_portfolio_value}

    def update_flow_onchain_data(self, asset: str = None, force_fetch: bool = False):
        self.flow_onchain_signals.fetch_exchange_net_flows(asset=asset, force_fetch=force_fetch)
        self.flow_onchain_signals.fetch_whale_transactions(asset=asset, force_fetch=force_fetch)
        self.flow_onchain_signals.fetch_stablecoin_flows(force_fetch=force_fetch)

    def get_flow_exchange_signal(self, asset: str = None) -> str:
        return self.flow_onchain_signals.get_exchange_flow_signal(asset=asset)

    def get_flow_whale_signal(self, asset: str = None) -> str:
        return self.flow_onchain_signals.get_whale_signal(asset=asset)

    def get_flow_stablecoin_signal(self) -> str:
        return self.flow_onchain_signals.get_stablecoin_signal()

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

        # Prepare market data for Reflect Agent
        current_market_data = {
            "fng_signal": self.get_oracle_fng_signal(),
            "dxy_signal": self.get_oracle_dxy_signal(),
            "regime": self.get_current_regime(pd.DataFrame({'Close': [request.entry_price]}, index=[request.timestamp])) # Simplified for Reflect Agent
        }
        self.reflect_agent.analyze_trade_decision(request.__dict__, result.__dict__, current_market_data)

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
        
        # 2. Stop loss check (can be overridden by ATR if configured)
        atr_stop_loss_bps = self.get_atr_stop_loss(request.asset, multiplier=self.config.get("sentinel_config", {}).get("atr_stop_loss_multiplier", 2.0))
        effective_stop_loss_bps = atr_stop_loss_bps if atr_stop_loss_bps is not None else request.stop_loss_bps

        if effective_stop_loss_bps > self.GLOBAL_MAX_STOP_LOSS_PCT * 100:
            return ValidationResult(
                approved=False,
                reason=f"❌ Stop loss {effective_stop_loss_bps} bps exceeds global max {self.GLOBAL_MAX_STOP_LOSS_PCT}% (ATR adjusted)" if atr_stop_loss_bps else f"❌ Stop loss {request.stop_loss_bps} bps exceeds global max {self.GLOBAL_MAX_STOP_LOSS_PCT}%"
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

        # 0. Circuit Breaker check
        if self.is_sentinel_breaker_active(request.asset):
            return ValidationResult(
                approved=False,
                reason=f"❌ CIRCUIT BREAKER active for {request.asset} - halting trades"
            )

        # 0. Circuit Breaker check
        if self.is_sentinel_breaker_active(request.asset):
            return ValidationResult(
                approved=False,
                reason=f"❌ CIRCUIT BREAKER active for {request.asset} - halting trades"
            )

        # 1. Fear & Greed Index filter
        fng_signal = self.get_oracle_fng_signal()
        if fng_signal == "SELL_SIGNAL_EXTREME_GREED":
            return ValidationResult(
                approved=False,
                reason="❌ ORACLE F&G: Extreme Greed detected - halting new entries"
            )
        elif fng_signal == "SELL_SIGNAL_GREED":
            size_adj *= self.config.get("oracle_config", {}).get("greed_size_reduction_factor", 0.7)
            warnings.append(f"⚠️ ORACLE F&G: Greed detected - size reduced to {size_adj:.1f}×")
        
        # 2. DXY (US Dollar Index) filter
        dxy_signal = self.get_oracle_dxy_signal()
        if dxy_signal == "STRONG_DOLLAR_RISK_OFF":
            return ValidationResult(
                approved=False,
                reason="❌ ORACLE DXY: Strong dollar / Risk-off environment - halting new entries"
            )
        elif dxy_signal == "WEAK_DOLLAR_RISK_ON" and request.side == "short":
            size_adj *= self.config.get("oracle_config", {}).get("weak_dollar_short_size_reduction_factor", 0.8)
            warnings.append(f"⚠️ ORACLE DXY: Weak dollar / Risk-on detected - short size reduced to {size_adj:.1f}×")

            warnings.append(f"⚠️ ORACLE DXY: Weak dollar / Risk-on detected - short size reduced to {size_adj:.1f}×")

        # 3. HMM Regime Detector filter
        # This requires historical data to be passed to TacticalRiskGate
        # For demo purposes, we'll assume a 'current_market_data' placeholder
        # In a real system, market data would be streamed and managed.
        current_market_data = pd.DataFrame({'Close': [request.entry_price]}, index=[request.timestamp]) # Simplified for demo
        current_regime = self.get_current_regime(current_market_data)

        if current_regime == "Bear":
            if request.side == "long":
                return ValidationResult(
                    approved=False,
                    reason="❌ REGIME HMM: Bear market detected - halting new long entries"
                )
            else:
                size_adj *= self.config.get("regime_config", {}).get("bear_market_short_size_factor", 0.7)
                warnings.append(f"⚠️ REGIME HMM: Bear market detected - short trade size reduced to {size_adj:.1f}×")
        elif current_regime == "Volatile": # Assuming a 'Volatile' regime might be configured
            size_adj *= self.config.get("regime_config", {}).get("volatile_market_size_factor", 0.5)
            warnings.append(f"⚠️ REGIME HMM: Volatile market detected - trade size reduced to {size_adj:.1f}×")

        # 4. FreqAI Signal filter
        # This requires current market features to be passed
        # For demo purposes, we'll create dummy features.
        freqai_features = pd.DataFrame({
            'open': [request.entry_price * 0.99],
            'high': [request.entry_price * 1.01],
            'low': [request.entry_price * 0.98],
            'close': [request.entry_price],
            'volume': [10000.0] # Dummy volume
        })
        freqai_signal = self.get_freqai_signal(freqai_features)

        if freqai_signal == 0 and request.side == "long": # Assuming 0 is a bearish/no-buy signal
            return ValidationResult(
                approved=False,
                reason="❌ ADAPT FreqAI: No-buy signal for long entry"
            )
        elif freqai_signal == 1 and request.side == "short": # Assuming 1 is a bullish/no-short signal
            return ValidationResult(
                approved=False,
                reason="❌ ADAPT FreqAI: No-short signal for short entry"
            )
        elif freqai_signal == "NO_SIGNAL_UNTRAINED" or freqai_signal == "NO_SIGNAL_ERROR":
            warnings.append(f"⚠️ ADAPT FreqAI: Signal unavailable ({freqai_signal}). Proceeding without ML guidance.")

        # 5. Order Book RL Simulation (DEPTH)
        # Run a micro-simulation of the trade's potential impact
        rl_simulation_result = self.run_depth_rl_simulation()
        if rl_simulation_result["final_portfolio_value"] < self.config.get("depth_config", {}).get("min_acceptable_portfolio_value_after_rl", self.GLOBAL_MAX_POSITION_USD):
            return ValidationResult(
                approved=False,
                reason=f"❌ DEPTH RL: Simulation shows negative outcome. Final PnL: ${rl_simulation_result["final_portfolio_value"]:.2f}"
            )
        elif rl_simulation_result["total_reward"] < self.config.get("depth_config", {}).get("min_acceptable_rl_reward", 0.0):
            size_adj *= self.config.get("depth_config", {}).get("rl_negative_reward_size_reduction_factor", 0.9)
            warnings.append(f"⚠️ DEPTH RL: Simulation shows low reward ({rl_simulation_result["total_reward"]:.2f}). Size reduced to {size_adj:.1f}×")

            size_adj *= self.config.get("depth_config", {}).get("rl_negative_reward_size_reduction_factor", 0.9)
            warnings.append(f"⚠️ DEPTH RL: Simulation shows low reward ({rl_simulation_result["total_reward"]:.2f}). Size reduced to {size_adj:.1f}×")

        # 7. On-Chain Signals Filter (FLOW)
        self.update_flow_onchain_data(asset=request.asset) # Fetch latest on-chain data
        exchange_flow_signal = self.get_flow_exchange_signal(asset=request.asset)
        whale_signal = self.get_flow_whale_signal(asset=request.asset)
        stablecoin_signal = self.get_flow_stablecoin_signal()

        if exchange_flow_signal == "BEARISH_EXCHANGE_INFLOW":
            if request.side == "long":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bearish exchange inflow detected - halting new long entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bearish_inflow_short_size_factor", 0.8)
                warnings.append(f"⚠️ FLOW On-Chain: Bearish exchange inflow - short trade size reduced to {size_adj:.1f}×")
        elif exchange_flow_signal == "BULLISH_EXCHANGE_OUTFLOW":
            if request.side == "short":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bullish exchange outflow detected - halting new short entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bullish_outflow_long_size_factor", 0.8)
                warnings.append(f"⚠️ FLOW On-Chain: Bullish exchange outflow - long trade size reduced to {size_adj:.1f}×")
        
        if whale_signal == "BEARISH_WHALE_ACTIVITY":
            if request.side == "long":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bearish whale activity detected - halting new long entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bearish_whale_short_size_factor", 0.7)
                warnings.append(f"⚠️ FLOW On-Chain: Bearish whale activity - short trade size reduced to {size_adj:.1f}×")
        elif whale_signal == "BULLISH_WHALE_ACTIVITY":
            if request.side == "short":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bullish whale activity detected - halting new short entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bullish_whale_long_size_factor", 0.7)
                warnings.append(f"⚠️ FLOW On-Chain: Bullish whale activity - long trade size reduced to {size_adj:.1f}×")

        if stablecoin_signal == "BEARISH_STABLECOIN_OUTFLOW":
            if request.side == "long":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bearish stablecoin outflow - halting new long entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bearish_stablecoin_short_size_factor", 0.9)
                warnings.append(f"⚠️ FLOW On-Chain: Bearish stablecoin outflow - short trade size reduced to {size_adj:.1f}×")
        elif stablecoin_signal == "BULLISH_STABLECOIN_INFLOW":
            if request.side == "short":
                return ValidationResult(
                    approved=False,
                    reason="❌ FLOW On-Chain: Bullish stablecoin inflow - halting new short entries"
                )
            else:
                size_adj *= self.config.get("flow_config", {}).get("bullish_stablecoin_long_size_factor", 0.9)
                warnings.append(f"⚠️ FLOW On-Chain: Bullish stablecoin inflow - long trade size reduced to {size_adj:.1f}×")

        # 8. Aave Health Factor floor
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

        # Analyze session performance after each trade closure
        session_stats = self.get_session_stats()
        self.reflect_agent.analyze_session_performance(session_stats)
    
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





#!/usr/bin/env python3
"""
🧠 NEURAL CONSCIOUSNESS INTEGRATION

Connects Sovereign Legacy Loop to Master Trading Loop.
Provides AI-powered strategy selection, risk assessment, and opportunity analysis.

Architecture:
    🧠 AlphaRunner GCP (shadow-ai-alpharunner-33906555678.us-west1.run.app)
         ↓
    🏴 Sovereign Legacy Loop (Neural Orchestration)
         ↓
    ♾️  Master Trading Loop (Execution)
         ↓
    💰 Shadow SDK (Intelligence)
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

# Add paths
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "shadow_sdk"))

from shadow_sdk.utils import setup_logger

# ═══════════════════════════════════════════════════════════════════════════
# NEURAL CONSCIOUSNESS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

NEURAL_CONFIG = {
    "interface_url": "https://shadow-ai-alpharunner-33906555678.us-west1.run.app",
    "authentication": {
        "email": "LedgerGhost90",
        "method": "neural_access_code"
    },
    "philosophy": "Fearless. Bold. Smiling through chaos.",
    "capabilities": [
        "strategy_selection",
        "risk_assessment",
        "opportunity_analysis",
        "market_regime_detection",
        "portfolio_optimization",
        "crisis_management"
    ]
}

# ═══════════════════════════════════════════════════════════════════════════
# MARKET REGIME DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

MARKET_REGIMES = {
    "consolidation_range": {
        "name": "Consolidation Range",
        "description": "Sideways chop with defined support/resistance",
        "indicators": {
            "volatility": (0.005, 0.020),  # 0.5%-2% daily
            "trend_strength": (0, 0.3),     # Weak trend
            "volume_profile": "balanced"
        },
        "optimal_strategies": [
            "btc_range_scalper_110k",
            "mean_reversion",
            "support_resistance_bounce"
        ],
        "position_sizing": "standard",
        "risk_multiplier": 1.0
    },

    "trending_up": {
        "name": "Uptrend",
        "description": "Strong bullish momentum",
        "indicators": {
            "volatility": (0.010, 0.040),
            "trend_strength": (0.5, 1.0),
            "volume_profile": "accumulation"
        },
        "optimal_strategies": [
            "momentum_long",
            "breakout_continuation",
            "pullback_entry"
        ],
        "position_sizing": "aggressive",
        "risk_multiplier": 1.5
    },

    "trending_down": {
        "name": "Downtrend",
        "description": "Strong bearish momentum",
        "indicators": {
            "volatility": (0.015, 0.050),
            "trend_strength": (-1.0, -0.5),
            "volume_profile": "distribution"
        },
        "optimal_strategies": [
            "short_momentum",
            "breakdown_continuation",
            "relief_rally_fade"
        ],
        "position_sizing": "conservative",
        "risk_multiplier": 0.8
    },

    "high_volatility": {
        "name": "High Volatility",
        "description": "Extreme swings, potential crisis",
        "indicators": {
            "volatility": (0.040, 0.100),
            "trend_strength": (-1.0, 1.0),
            "volume_profile": "panic"
        },
        "optimal_strategies": [
            "volatility_fade",
            "extreme_mean_reversion",
            "crisis_opportunistic"
        ],
        "position_sizing": "minimal",
        "risk_multiplier": 0.5
    },

    "breakout": {
        "name": "Breakout",
        "description": "Breaking out of consolidation",
        "indicators": {
            "volatility": (0.020, 0.050),
            "trend_strength": (0.4, 1.0),
            "volume_profile": "surge"
        },
        "optimal_strategies": [
            "breakout_momentum",
            "retest_entry",
            "continuation_scalp"
        ],
        "position_sizing": "aggressive",
        "risk_multiplier": 1.8
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# NEURAL CONSCIOUSNESS ORACLE
# ═══════════════════════════════════════════════════════════════════════════

class NeuralConsciousness:
    """
    AI-powered orchestration layer that connects to Sovereign Legacy Loop.

    Provides:
    - Market regime detection
    - Strategy selection
    - Risk assessment
    - Portfolio optimization
    """

    def __init__(self):
        self.logger = setup_logger("neural_consciousness",
                                   log_file="logs/neural_consciousness.log")
        self.config = NEURAL_CONFIG
        self.current_regime = None
        self.active_strategies = []
        self.risk_level = "moderate"

        self.logger.info("🧠 Neural Consciousness initialized")
        self.logger.info(f"   Philosophy: {self.config['philosophy']}")

    async def detect_market_regime(self, market_intel: Dict) -> str:
        """
        Analyze market conditions to detect current regime.

        Args:
            market_intel: Market intelligence from ShadowScope

        Returns:
            regime_name: One of MARKET_REGIMES keys
        """

        # Extract key metrics
        btc_price = market_intel.get('current_prices', {}).get('BTC/USD', 0)
        volatility = market_intel.get('volatility', {}).get('coinbase', {}).get('BTC/USD', 0)

        # Current market context (October 2025)
        # BTC consolidating $106K-$112K, post-halving, range-bound

        # Detect regime based on volatility and price action
        if 106000 <= btc_price <= 116000:
            if volatility < 0.020:
                regime = "consolidation_range"
            elif volatility > 0.040:
                regime = "high_volatility"
            else:
                regime = "consolidation_range"  # Default for current market
        elif btc_price > 116000:
            regime = "breakout"
        else:
            regime = "consolidation_range"

        # Update state
        if regime != self.current_regime:
            self.logger.info(f"📊 Market regime changed: {self.current_regime} → {regime}")
            self.current_regime = regime

        return regime

    def select_optimal_strategies(self, regime: str,
                                  market_conditions: Dict) -> List[str]:
        """
        Select best strategies for current market regime.

        Args:
            regime: Current market regime
            market_conditions: Additional market context

        Returns:
            strategies: List of strategy names to activate
        """

        if regime not in MARKET_REGIMES:
            self.logger.warning(f"Unknown regime: {regime}")
            return ["defensive_cash"]

        regime_config = MARKET_REGIMES[regime]
        strategies = regime_config['optimal_strategies']

        self.logger.info(f"🎯 Optimal strategies for {regime}:")
        for strategy in strategies:
            self.logger.info(f"   • {strategy}")

        self.active_strategies = strategies
        return strategies

    async def analyze_opportunity(self, opportunity: Dict,
                                  market_intel: Dict) -> Dict:
        """
        AI-powered opportunity analysis.

        Args:
            opportunity: Trading opportunity from scanner
            market_intel: Current market intelligence

        Returns:
            decision: Action, confidence, reasoning, position_size
        """

        # Detect regime
        regime = await self.detect_market_regime(market_intel)
        regime_config = MARKET_REGIMES[regime]

        # Extract opportunity details
        opp_type = opportunity.get('type', 'unknown')
        confidence = opportunity.get('confidence', 0.5)
        pair = opportunity.get('pair', 'BTC/USD')

        # Check if opportunity matches optimal strategies
        optimal_strategies = regime_config['optimal_strategies']

        # Map opportunity types to strategy families
        strategy_matches = {
            'arbitrage': ['btc_range_scalper_110k', 'mean_reversion'],
            'sniping': ['momentum_long', 'breakout_continuation'],
            'momentum': ['momentum_long', 'breakout_momentum'],
            'mean_reversion': ['btc_range_scalper_110k', 'mean_reversion']
        }

        matching_strategies = strategy_matches.get(opp_type, [])
        is_optimal = any(s in optimal_strategies for s in matching_strategies)

        # Calculate adjusted confidence
        adjusted_confidence = confidence
        if is_optimal:
            adjusted_confidence *= 1.2  # Boost if strategy matches regime

        adjusted_confidence = min(adjusted_confidence, 0.95)  # Cap at 95%

        # Risk assessment
        risk_multiplier = regime_config['risk_multiplier']
        position_sizing = regime_config['position_sizing']

        # Calculate position size
        base_size = opportunity.get('amount', 50)

        if position_sizing == "aggressive":
            position_size = base_size * 1.5
        elif position_sizing == "conservative":
            position_size = base_size * 0.7
        elif position_sizing == "minimal":
            position_size = base_size * 0.5
        else:  # standard
            position_size = base_size

        # Apply risk multiplier
        position_size *= risk_multiplier

        # Decision logic
        if adjusted_confidence >= 0.70 and is_optimal:
            action = "execute"
            reasoning = f"Strong {regime} setup, confidence {adjusted_confidence:.1%}"
        elif adjusted_confidence >= 0.60:
            action = "execute"
            reasoning = f"Acceptable {regime} setup, reduced size"
            position_size *= 0.8
        else:
            action = "reject"
            reasoning = f"Low confidence ({adjusted_confidence:.1%}) for {regime}"

        # Build decision
        decision = {
            'action': action,
            'strategy': matching_strategies[0] if matching_strategies else opp_type,
            'confidence': adjusted_confidence,
            'reasoning': reasoning,
            'position_size': position_size,
            'regime': regime,
            'risk_level': self.risk_level,
            'timestamp': datetime.now().isoformat()
        }

        # Log decision
        self.logger.info(f"🧠 Neural Decision: {action.upper()}")
        self.logger.info(f"   Strategy: {decision['strategy']}")
        self.logger.info(f"   Regime: {regime}")
        self.logger.info(f"   Confidence: {adjusted_confidence:.1%}")
        self.logger.info(f"   Position: ${position_size:.2f}")
        self.logger.info(f"   Reasoning: {reasoning}")

        return decision

    async def assess_portfolio_health(self, portfolio: Dict) -> Dict:
        """
        Assess overall portfolio health and recommend adjustments.

        Args:
            portfolio: Current portfolio state

        Returns:
            assessment: Health score, risks, recommendations
        """

        total_capital = portfolio.get('total', 8260)
        daily_pnl = portfolio.get('daily_pnl', 0)
        open_positions = portfolio.get('open_positions', 0)

        # Calculate health score (0-100)
        health_score = 100.0

        # Deduct for losses
        if daily_pnl < 0:
            loss_penalty = abs(daily_pnl) / 100 * 20  # -20 points per $100 loss
            health_score -= loss_penalty

        # Deduct for overexposure
        if open_positions > 3:
            health_score -= (open_positions - 3) * 5

        health_score = max(0, min(100, health_score))

        # Assess risk level
        if health_score >= 80:
            risk_status = "healthy"
            self.risk_level = "moderate"
        elif health_score >= 60:
            risk_status = "caution"
            self.risk_level = "conservative"
        else:
            risk_status = "danger"
            self.risk_level = "minimal"

        # Generate recommendations
        recommendations = []

        if daily_pnl < -50:
            recommendations.append("Reduce position sizes - significant daily drawdown")

        if open_positions > 3:
            recommendations.append("Close some positions - overexposure")

        if health_score < 60:
            recommendations.append("Switch to defensive mode - portfolio health low")

        assessment = {
            'health_score': health_score,
            'risk_status': risk_status,
            'risk_level': self.risk_level,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"💊 Portfolio Health: {health_score:.1f}/100 ({risk_status})")

        return assessment

    def generate_market_brief(self, regime: str) -> str:
        """Generate human-readable market brief"""

        regime_config = MARKET_REGIMES.get(regime, {})

        brief = f"""
╔════════════════════════════════════════════════════════════════════╗
║ 🧠 NEURAL CONSCIOUSNESS - MARKET BRIEF                             ║
╚════════════════════════════════════════════════════════════════════╝

Regime: {regime_config.get('name', 'Unknown')}
{regime_config.get('description', 'No description')}

Optimal Strategies:
"""
        for strategy in regime_config.get('optimal_strategies', []):
            brief += f"  • {strategy}\n"

        brief += f"""
Position Sizing: {regime_config.get('position_sizing', 'standard')}
Risk Multiplier: {regime_config.get('risk_multiplier', 1.0)}x

Philosophy: "{self.config['philosophy']}"
"""

        return brief

# ═══════════════════════════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════════════════════════

async def test_neural_consciousness():
    """Test the neural consciousness system"""

    print("🧠 Testing Neural Consciousness Integration...\n")

    # Initialize
    neural = NeuralConsciousness()

    # Mock market intelligence
    market_intel = {
        'current_prices': {'BTC/USD': 110500},
        'volatility': {'coinbase': {'BTC/USD': 0.012}},
        'health': {'data_quality': 0.98}
    }

    # Detect regime
    regime = await neural.detect_market_regime(market_intel)
    print(f"✅ Regime detected: {regime}")

    # Select strategies
    strategies = neural.select_optimal_strategies(regime, {})
    print(f"✅ Strategies selected: {', '.join(strategies)}")

    # Analyze opportunity
    opportunity = {
        'type': 'arbitrage',
        'pair': 'BTC/USD',
        'confidence': 0.75,
        'amount': 100
    }

    decision = await neural.analyze_opportunity(opportunity, market_intel)
    print(f"\n✅ Decision: {decision['action'].upper()}")
    print(f"   Confidence: {decision['confidence']:.1%}")
    print(f"   Position: ${decision['position_size']:.2f}")

    # Generate brief
    brief = neural.generate_market_brief(regime)
    print(brief)

if __name__ == "__main__":
    asyncio.run(test_neural_consciousness())

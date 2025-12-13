#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - AI Strategy Selector (Orchestration Layer)

This is the Orchestration Layer of the D.O.E. Pattern:
- Selects optimal strategy based on current regime
- Uses performance history for intelligent selection
- Implements self-annealing through learning loop

Selection Algorithm:
1. Get current market regime from Regime Detector
2. Query Performance Tracker for top strategies in this regime
3. Apply confidence weighting based on trade count
4. Select strategy with highest expected value
5. Fallback to safe defaults if insufficient data
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
import random

from .regime_detector import MarketRegime, RegimeAnalysis, get_regime_detector
from .performance_tracker import PerformanceTracker, get_performance_tracker

logger = logging.getLogger(__name__)


@dataclass
class StrategyRecommendation:
    """Container for strategy recommendation"""
    strategy_name: str
    regime: MarketRegime
    confidence: float  # 0-100
    expected_win_rate: float
    expected_pnl_percent: float
    risk_level: str  # low, medium, high
    reasoning: List[str]
    position_size_multiplier: float  # 0.5 = half size, 1.0 = normal, 1.5 = 1.5x
    timeframe: str
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['regime'] = self.regime.value
        return result


# Default strategy configurations for when no performance data exists
DEFAULT_STRATEGIES = {
    MarketRegime.TRENDING_BULLISH: [
        {
            "name": "TrendFollowEMA",
            "type": "trend_following",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 55,
            "risk_level": "medium"
        },
        {
            "name": "MomentumScalp",
            "type": "momentum",
            "timeframes": ["5m", "15m"],
            "expected_win_rate": 52,
            "risk_level": "high"
        },
        {
            "name": "BreakoutRetest",
            "type": "breakout",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 48,
            "risk_level": "medium"
        }
    ],
    MarketRegime.TRENDING_BEARISH: [
        {
            "name": "TrendFollowEMA",
            "type": "trend_following",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 55,
            "risk_level": "medium"
        },
        {
            "name": "BollingerBounce",
            "type": "mean_reversion",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 50,
            "risk_level": "medium"
        }
    ],
    MarketRegime.CHOPPY_VOLATILE: [
        {
            "name": "ElderReversion",
            "type": "mean_reversion",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 58,
            "risk_level": "medium"
        },
        {
            "name": "BandedStochastic",
            "type": "oscillator",
            "timeframes": ["15m", "30m"],
            "expected_win_rate": 55,
            "risk_level": "medium"
        },
        {
            "name": "RSIReversion",
            "type": "mean_reversion",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 52,
            "risk_level": "low"
        }
    ],
    MarketRegime.CHOPPY_CALM: [
        {
            "name": "SupportResistanceBounce",
            "type": "range",
            "timeframes": ["1h", "4h"],
            "expected_win_rate": 60,
            "risk_level": "low"
        },
        {
            "name": "VWAPMeanReversion",
            "type": "mean_reversion",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 55,
            "risk_level": "low"
        }
    ],
    MarketRegime.BREAKOUT_POTENTIAL: [
        {
            "name": "VolatilityBreakout",
            "type": "breakout",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 45,
            "risk_level": "high"
        },
        {
            "name": "ChoppyBreakout",
            "type": "breakout",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 42,
            "risk_level": "high"
        }
    ],
    MarketRegime.CAPITULATION: [
        {
            "name": "RSIReversion",
            "type": "mean_reversion",
            "timeframes": ["1h", "4h"],
            "expected_win_rate": 62,
            "risk_level": "high"
        },
        {
            "name": "DivergenceScalp",
            "type": "divergence",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 55,
            "risk_level": "high"
        }
    ],
    MarketRegime.EUPHORIA: [
        {
            "name": "RSIReversion",
            "type": "mean_reversion",
            "timeframes": ["1h", "4h"],
            "expected_win_rate": 60,
            "risk_level": "high"
        },
        {
            "name": "BollingerBounce",
            "type": "mean_reversion",
            "timeframes": ["15m", "1h"],
            "expected_win_rate": 55,
            "risk_level": "high"
        }
    ],
    MarketRegime.UNKNOWN: [
        {
            "name": "RSIReversion",
            "type": "mean_reversion",
            "timeframes": ["1h"],
            "expected_win_rate": 50,
            "risk_level": "low"
        }
    ]
}


class AIStrategySelector:
    """
    Selects optimal trading strategy based on:
    1. Current market regime
    2. Historical performance data
    3. Confidence/trade count weighting
    4. Risk management constraints
    """

    def __init__(
        self,
        performance_tracker: Optional[PerformanceTracker] = None,
        min_trades_for_confidence: int = 10
    ):
        """
        Initialize the AI Strategy Selector.

        Args:
            performance_tracker: Performance tracker instance
            min_trades_for_confidence: Minimum trades needed for high confidence
        """
        self.tracker = performance_tracker or get_performance_tracker()
        self.min_trades = min_trades_for_confidence

        # Selection weights
        self.weights = {
            'win_rate': 0.40,
            'avg_pnl': 0.30,
            'sharpe_ratio': 0.20,
            'trade_count_confidence': 0.10
        }

        # Risk constraints
        self.max_drawdown_threshold = 15.0  # Skip strategies with >15% drawdown
        self.min_win_rate_threshold = 35.0  # Skip strategies with <35% win rate

        logger.info("AIStrategySelector initialized")

    def select_strategy(
        self,
        regime: MarketRegime,
        portfolio_value: float,
        current_positions: int = 0,
        max_positions: int = 3,
        risk_tolerance: str = "medium"
    ) -> StrategyRecommendation:
        """
        Select optimal strategy for current market conditions.

        Args:
            regime: Current market regime
            portfolio_value: Current portfolio value in USD
            current_positions: Number of open positions
            max_positions: Maximum allowed positions
            risk_tolerance: "low", "medium", or "high"

        Returns:
            StrategyRecommendation with selected strategy details
        """
        reasoning = []

        # Check if we can open new positions
        if current_positions >= max_positions:
            return StrategyRecommendation(
                strategy_name="WAIT",
                regime=regime,
                confidence=100,
                expected_win_rate=0,
                expected_pnl_percent=0,
                risk_level="none",
                reasoning=["Maximum positions reached"],
                position_size_multiplier=0,
                timeframe="N/A"
            )

        reasoning.append(f"Regime: {regime.value}")
        reasoning.append(f"Risk tolerance: {risk_tolerance}")

        # Get strategies from performance tracker
        tracked_strategies = self.tracker.get_top_strategies_for_regime(
            regime.value,
            limit=10,
            min_trades=3
        )

        if tracked_strategies and len(tracked_strategies) > 0:
            # Use performance-based selection
            recommendation = self._select_from_performance(
                tracked_strategies,
                regime,
                risk_tolerance,
                reasoning
            )
        else:
            # Use default strategies
            reasoning.append("No performance data - using defaults")
            recommendation = self._select_from_defaults(
                regime,
                risk_tolerance,
                reasoning
            )

        # Adjust position size based on confidence
        recommendation.position_size_multiplier = self._calculate_position_multiplier(
            recommendation.confidence,
            risk_tolerance,
            portfolio_value
        )

        logger.info(
            f"Strategy selected: {recommendation.strategy_name} "
            f"(confidence: {recommendation.confidence:.1f}%)"
        )

        return recommendation

    def _select_from_performance(
        self,
        strategies: List[Dict],
        regime: MarketRegime,
        risk_tolerance: str,
        reasoning: List[str]
    ) -> StrategyRecommendation:
        """Select strategy based on historical performance"""

        # Filter out poor performers
        filtered = []
        for s in strategies:
            # Skip if max drawdown too high
            if s.get('max_drawdown_percent', 0) > self.max_drawdown_threshold:
                continue

            # Skip if win rate too low
            if s.get('win_rate', 0) < self.min_win_rate_threshold:
                continue

            # Apply risk tolerance filter
            profit_factor = s.get('profit_factor', 1)
            if risk_tolerance == "low" and profit_factor < 1.2:
                continue

            filtered.append(s)

        if not filtered:
            reasoning.append("All tracked strategies filtered out - using defaults")
            return self._select_from_defaults(regime, risk_tolerance, reasoning)

        # Score each strategy
        scored = []
        for s in filtered:
            score = self._calculate_strategy_score(s)
            scored.append((s, score))

        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select top strategy
        best = scored[0][0]

        # Calculate confidence based on trade count
        trade_count = best.get('total_trades', 0)
        confidence = min(trade_count / self.min_trades * 50 + 50, 95)

        reasoning.append(f"Selected from {len(filtered)} tracked strategies")
        reasoning.append(f"Historical win rate: {best.get('win_rate', 0):.1f}%")
        reasoning.append(f"Historical PnL: {best.get('avg_pnl_percent', 0):.2f}%")
        reasoning.append(f"Trade count: {trade_count}")

        # Determine risk level
        if best.get('max_drawdown_percent', 0) > 10:
            risk_level = "high"
        elif best.get('win_rate', 0) > 55:
            risk_level = "low"
        else:
            risk_level = "medium"

        return StrategyRecommendation(
            strategy_name=best['strategy_name'],
            regime=regime,
            confidence=confidence,
            expected_win_rate=best.get('win_rate', 50),
            expected_pnl_percent=best.get('avg_pnl_percent', 0),
            risk_level=risk_level,
            reasoning=reasoning,
            position_size_multiplier=1.0,
            timeframe="15m"  # Default, will be overridden by strategy config
        )

    def _select_from_defaults(
        self,
        regime: MarketRegime,
        risk_tolerance: str,
        reasoning: List[str]
    ) -> StrategyRecommendation:
        """Select strategy from default configurations"""

        defaults = DEFAULT_STRATEGIES.get(regime, DEFAULT_STRATEGIES[MarketRegime.UNKNOWN])

        # Filter by risk tolerance
        if risk_tolerance == "low":
            suitable = [s for s in defaults if s['risk_level'] in ['low', 'medium']]
        elif risk_tolerance == "high":
            suitable = defaults
        else:
            suitable = [s for s in defaults if s['risk_level'] in ['low', 'medium']]

        if not suitable:
            suitable = defaults

        # Select highest expected win rate
        selected = max(suitable, key=lambda x: x['expected_win_rate'])

        reasoning.append(f"Using default strategy for {regime.value}")
        reasoning.append(f"Expected win rate: {selected['expected_win_rate']}%")

        return StrategyRecommendation(
            strategy_name=selected['name'],
            regime=regime,
            confidence=50,  # Lower confidence for defaults
            expected_win_rate=selected['expected_win_rate'],
            expected_pnl_percent=0,  # Unknown
            risk_level=selected['risk_level'],
            reasoning=reasoning,
            position_size_multiplier=0.75,  # Conservative for untested
            timeframe=selected['timeframes'][0]
        )

    def _calculate_strategy_score(self, strategy: Dict) -> float:
        """
        Calculate composite score for strategy ranking.

        Score = (win_rate * 0.4) + (avg_pnl_normalized * 0.3) +
                (sharpe_normalized * 0.2) + (confidence * 0.1)
        """
        win_rate = strategy.get('win_rate', 50) / 100

        # Normalize avg_pnl to 0-1 scale (assuming -5% to 5% range)
        avg_pnl = strategy.get('avg_pnl_percent', 0)
        avg_pnl_normalized = (avg_pnl + 5) / 10
        avg_pnl_normalized = max(0, min(1, avg_pnl_normalized))

        # Normalize sharpe to 0-1 scale (assuming -2 to 3 range)
        sharpe = strategy.get('sharpe_ratio', 0)
        sharpe_normalized = (sharpe + 2) / 5
        sharpe_normalized = max(0, min(1, sharpe_normalized))

        # Confidence based on trade count
        trade_count = strategy.get('total_trades', 0)
        confidence = min(trade_count / self.min_trades, 1)

        score = (
            win_rate * self.weights['win_rate'] +
            avg_pnl_normalized * self.weights['avg_pnl'] +
            sharpe_normalized * self.weights['sharpe_ratio'] +
            confidence * self.weights['trade_count_confidence']
        )

        return score

    def _calculate_position_multiplier(
        self,
        confidence: float,
        risk_tolerance: str,
        portfolio_value: float
    ) -> float:
        """Calculate position size multiplier based on confidence and risk"""

        # Base multiplier from confidence
        base = 0.5 + (confidence / 200)  # 0.5 to 1.0

        # Risk tolerance adjustment
        risk_multipliers = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.3
        }

        multiplier = base * risk_multipliers.get(risk_tolerance, 1.0)

        # Cap at reasonable bounds
        return max(0.25, min(1.5, multiplier))

    def get_all_strategies_for_regime(self, regime: MarketRegime) -> List[Dict]:
        """Get all available strategies for a regime (tracked + defaults)"""

        result = []

        # Get tracked strategies
        tracked = self.tracker.get_top_strategies_for_regime(
            regime.value, limit=20, min_trades=1
        )

        for s in tracked:
            result.append({
                "name": s['strategy_name'],
                "source": "performance_tracker",
                "win_rate": s.get('win_rate', 0),
                "trades": s.get('total_trades', 0),
                "score": s.get('score', 0)
            })

        # Add defaults that aren't already tracked
        defaults = DEFAULT_STRATEGIES.get(regime, [])
        tracked_names = {s['strategy_name'] for s in tracked}

        for d in defaults:
            if d['name'] not in tracked_names:
                result.append({
                    "name": d['name'],
                    "source": "default",
                    "win_rate": d['expected_win_rate'],
                    "trades": 0,
                    "score": 0
                })

        return result

    def update_rankings(self):
        """Update strategy rankings for all regimes"""
        for regime in MarketRegime:
            if regime != MarketRegime.UNKNOWN:
                self.tracker.update_strategy_rankings(regime.value)
        logger.info("Strategy rankings updated for all regimes")


# Singleton instance
_selector_instance: Optional[AIStrategySelector] = None


def get_strategy_selector() -> AIStrategySelector:
    """Get or create the global AIStrategySelector instance"""
    global _selector_instance
    if _selector_instance is None:
        _selector_instance = AIStrategySelector()
    return _selector_instance


if __name__ == "__main__":
    # Test the strategy selector
    logging.basicConfig(level=logging.INFO)

    selector = AIStrategySelector()

    # Test selection for different regimes
    test_regimes = [
        MarketRegime.TRENDING_BULLISH,
        MarketRegime.CHOPPY_VOLATILE,
        MarketRegime.BREAKOUT_POTENTIAL
    ]

    print("\n=== STRATEGY SELECTOR TEST ===\n")

    for regime in test_regimes:
        recommendation = selector.select_strategy(
            regime=regime,
            portfolio_value=10000,
            current_positions=0,
            max_positions=3,
            risk_tolerance="medium"
        )

        print(f"Regime: {regime.value}")
        print(f"  Strategy: {recommendation.strategy_name}")
        print(f"  Confidence: {recommendation.confidence:.1f}%")
        print(f"  Expected Win Rate: {recommendation.expected_win_rate:.1f}%")
        print(f"  Risk Level: {recommendation.risk_level}")
        print(f"  Position Size: {recommendation.position_size_multiplier:.2f}x")
        print(f"  Reasoning:")
        for reason in recommendation.reasoning:
            print(f"    - {reason}")
        print()

    print("AIStrategySelector test complete!")

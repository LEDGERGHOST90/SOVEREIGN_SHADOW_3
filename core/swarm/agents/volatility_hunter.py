#!/usr/bin/env python3
"""
VOLATILITY HUNTER - Specialized agent for trading volatility spikes
Detects rapid price movements and volatility expansion
"""

import sys
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from collections import deque

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents_highlevel.trading_agent import TradingAgent, AgentBrain, MarketData, DecisionType

logger = logging.getLogger(__name__)


class VolatilityBrain(AgentBrain):
    """
    Advanced brain for volatility detection and trading
    Tracks price movements and calculates volatility metrics
    """

    def __init__(self, personality: str, lookback_periods: int = 20):
        self.personality = personality
        self.lookback_periods = lookback_periods
        self.price_history: deque = deque(maxlen=lookback_periods)
        self.volume_history: deque = deque(maxlen=lookback_periods)
        self.volatility_threshold = 0.015  # 1.5% volatility threshold
        self.learning_rate = 0.01
        self.memory = []

    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Analyze market volatility and price action"""

        # Add to history
        self.price_history.append(market_data.price)
        self.volume_history.append(market_data.volume)

        # Need minimum data points
        if len(self.price_history) < 5:
            return {
                "volatility": 0.0,
                "volatility_state": "unknown",
                "price_trend": "neutral",
                "volume_trend": "normal",
                "confidence": 0.0,
                "signal": "wait"
            }

        # Calculate volatility metrics
        volatility = self._calculate_volatility()
        price_change = self._calculate_price_change()
        volume_spike = self._detect_volume_spike()

        # Determine state
        volatility_state = self._classify_volatility(volatility)
        price_trend = "up" if price_change > 0.005 else "down" if price_change < -0.005 else "neutral"

        # Generate trading signal
        signal, confidence = self._generate_signal(
            volatility=volatility,
            volatility_state=volatility_state,
            price_change=price_change,
            volume_spike=volume_spike
        )

        return {
            "volatility": volatility,
            "volatility_state": volatility_state,
            "price_change": price_change,
            "price_trend": price_trend,
            "volume_spike": volume_spike,
            "volume_trend": "high" if volume_spike else "normal",
            "confidence": confidence,
            "signal": signal
        }

    def _calculate_volatility(self) -> float:
        """Calculate realized volatility from price history"""
        if len(self.price_history) < 2:
            return 0.0

        # Calculate returns
        returns = []
        prices = list(self.price_history)
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)

        # Calculate standard deviation (volatility)
        if not returns:
            return 0.0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5

        return volatility

    def _calculate_price_change(self) -> float:
        """Calculate recent price change percentage"""
        if len(self.price_history) < 2:
            return 0.0

        recent_price = self.price_history[-1]
        old_price = self.price_history[0]

        return (recent_price - old_price) / old_price

    def _detect_volume_spike(self) -> bool:
        """Detect if current volume is significantly elevated"""
        if len(self.volume_history) < 5:
            return False

        current_volume = self.volume_history[-1]
        avg_volume = sum(list(self.volume_history)[:-1]) / (len(self.volume_history) - 1)

        # Volume spike if current > 1.5x average
        return current_volume > (avg_volume * 1.5) if avg_volume > 0 else False

    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility > 0.03:  # 3%+
            return "extreme"
        elif volatility > 0.015:  # 1.5%+
            return "high"
        elif volatility > 0.008:  # 0.8%+
            return "medium"
        else:
            return "low"

    def _generate_signal(self, volatility: float, volatility_state: str,
                        price_change: float, volume_spike: bool) -> tuple[str, float]:
        """Generate trading signal based on volatility analysis"""

        # HIGH VOLATILITY + VOLUME SPIKE = Trade opportunity
        if volatility_state in ["high", "extreme"] and volume_spike:
            if price_change > 0.01:  # 1%+ up move
                # Volatility expansion on upside - ride momentum
                confidence = min(0.7 + (volatility * 10), 0.95)
                return "buy", confidence
            elif price_change < -0.01:  # 1%+ down move
                # Volatility expansion on downside - fade the move
                confidence = min(0.6 + (volatility * 10), 0.90)
                return "sell", confidence

        # EXTREME VOLATILITY without volume = Likely reversal
        elif volatility_state == "extreme" and not volume_spike:
            if price_change < -0.02:  # 2%+ down without volume
                # Likely capitulation - buy the dip
                confidence = 0.75
                return "buy", confidence

        # MEDIUM VOLATILITY + STRONG TREND = Trend continuation
        elif volatility_state == "medium" and abs(price_change) > 0.015:
            if price_change > 0:
                confidence = 0.55
                return "buy", confidence
            else:
                confidence = 0.55
                return "sell", confidence

        # LOW VOLATILITY = Wait for setup
        return "hold", 0.3

    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Learn from trading outcomes"""
        self.memory.append({
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc)
        })

        # Keep only last 1000 outcomes
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]

        # Adaptive threshold adjustment based on success
        if outcome.get("profitable", False):
            # Successful trades - can be slightly more aggressive
            self.volatility_threshold *= 0.99
        else:
            # Failed trades - be more selective
            self.volatility_threshold *= 1.01

        # Keep threshold in reasonable range
        self.volatility_threshold = max(0.01, min(self.volatility_threshold, 0.025))


class VolatilityHunter(TradingAgent):
    """
    Specialized agent for volatility trading
    Hunts for volatility spikes and expansion events
    """

    def __init__(self, agent_id: str, personality: str = "aggressive_opportunist",
                 lookback_periods: int = 20):
        # Initialize parent with volatility specialization
        super().__init__(
            agent_id=agent_id,
            personality=personality,
            specialization="volatility_hunter"
        )

        # Replace brain with specialized VolatilityBrain
        self.brain = VolatilityBrain(personality, lookback_periods)

        # Volatility hunter specific settings
        self.volatility_trades = 0
        self.volatility_wins = 0
        self.last_volatility_level = 0.0

        logger.info(f"Created VolatilityHunter agent '{agent_id}' with {personality} personality")

    async def _apply_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Apply volatility hunting strategy"""

        # Store current volatility
        self.last_volatility_level = analysis.get("volatility", 0.0)

        # Get signal from volatility brain
        signal = analysis.get("signal", "hold")
        confidence = analysis.get("confidence", 0.3)
        volatility_state = analysis.get("volatility_state", "unknown")

        # Build reasoning
        reasoning_parts = [
            f"Volatility: {self.last_volatility_level:.2%} ({volatility_state})",
            f"Price change: {analysis.get('price_change', 0):.2%}",
        ]

        if analysis.get("volume_spike", False):
            reasoning_parts.append("Volume SPIKE detected")

        reasoning = " | ".join(reasoning_parts)

        # Return decision
        return {
            "action": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "expected_profit": self._estimate_profit(analysis)
        }

    def _estimate_profit(self, analysis: Dict[str, Any]) -> float:
        """Estimate expected profit from volatility trade"""
        volatility = analysis.get("volatility", 0.0)

        # Higher volatility = higher profit potential
        if volatility > 0.03:  # Extreme
            return 0.025  # 2.5% target
        elif volatility > 0.015:  # High
            return 0.015  # 1.5% target
        elif volatility > 0.008:  # Medium
            return 0.008  # 0.8% target
        else:
            return 0.003  # 0.3% target

    async def _update_performance(self, decision) -> None:
        """Update performance with volatility-specific metrics"""
        # Call parent performance update
        await super()._update_performance(decision)

        # Track volatility trades
        if decision.decision_type != DecisionType.HOLD:
            self.volatility_trades += 1

            # Count wins (simple heuristic based on expected profit)
            if decision.expected_profit and decision.expected_profit > 0.01:
                self.volatility_wins += 1

    def get_volatility_stats(self) -> Dict[str, Any]:
        """Get volatility hunter specific statistics"""
        win_rate = (self.volatility_wins / self.volatility_trades) if self.volatility_trades > 0 else 0.0

        return {
            "agent_id": self.agent_id,
            "specialization": "volatility_hunter",
            "volatility_trades": self.volatility_trades,
            "volatility_wins": self.volatility_wins,
            "volatility_win_rate": win_rate,
            "last_volatility_level": self.last_volatility_level,
            "current_threshold": self.brain.volatility_threshold
        }


# Factory function
def create_volatility_hunter(agent_id: str, personality: str = "aggressive_opportunist",
                            lookback_periods: int = 20) -> VolatilityHunter:
    """Create a VolatilityHunter agent"""
    return VolatilityHunter(
        agent_id=agent_id,
        personality=personality,
        lookback_periods=lookback_periods
    )


# Test
if __name__ == "__main__":
    import asyncio

    async def test_volatility_hunter():
        """Test the volatility hunter agent"""
        print("=" * 70)
        print("🎯 TESTING VOLATILITY HUNTER AGENT")
        print("=" * 70)

        # Create agent
        hunter = create_volatility_hunter("vhunter_1", "aggressive_opportunist")

        # Initialize
        await hunter.initialize()
        hunter.set_capital_allocation(10000.0)

        print(f"\n✅ Agent created: {hunter.agent_id}")
        print(f"   Personality: {hunter.personality}")
        print(f"   Specialization: {hunter.specialization}")
        print(f"   Capital: ${hunter.capital_allocation:,.2f}")

        # Simulate volatile market data
        print("\n🔄 Simulating volatile market conditions...\n")

        base_price = 200.0
        prices = [
            200.0, 201.0, 202.5, 204.0, 206.0,  # Uptrend
            205.0, 203.0, 200.0, 197.0, 195.0,  # Volatility spike down
            196.0, 198.0, 200.0, 202.0, 204.0,  # Recovery
        ]

        volumes = [
            1000, 1100, 1200, 1500, 2000,  # Volume building
            3500, 4000, 3800, 3000, 2500,  # Volume spike
            1800, 1500, 1200, 1000, 1000,  # Volume normalizing
        ]

        decisions = []
        for i, (price, volume) in enumerate(zip(prices, volumes)):
            market_data = MarketData(
                symbol="TEST/USDT",
                price=price,
                volume=volume,
                timestamp=datetime.now(timezone.utc),
                exchange="test",
                bid=price - 0.5,
                ask=price + 0.5,
                spread=1.0
            )

            decision = await hunter.process(market_data)

            if decision and decision.decision_type != DecisionType.HOLD:
                decisions.append(decision)
                print(f"📊 Tick {i+1}: ${price:.2f} | Vol: {volume:,}")
                print(f"   🎯 DECISION: {decision.decision_type.value.upper()}")
                print(f"   💪 Confidence: {decision.confidence:.1%}")
                print(f"   💭 Reasoning: {decision.reasoning}")
                print(f"   💰 Amount: ${decision.amount:.2f}")
                print()

        # Stats
        print("=" * 70)
        print("📊 VOLATILITY HUNTER STATISTICS")
        print("=" * 70)

        perf = hunter.get_performance_summary()
        vol_stats = hunter.get_volatility_stats()

        print(f"Total Decisions: {perf['decision_count']}")
        print(f"Volatility Trades: {vol_stats['volatility_trades']}")
        print(f"Volatility Win Rate: {vol_stats['volatility_win_rate']:.1%}")
        print(f"Last Volatility: {vol_stats['last_volatility_level']:.2%}")

        print("\n✅ TEST COMPLETE!")

    asyncio.run(test_volatility_hunter())

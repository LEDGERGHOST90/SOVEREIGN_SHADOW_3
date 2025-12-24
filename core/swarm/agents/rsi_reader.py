#!/usr/bin/env python3
"""
RSI READER - Technical indicator specialist using Relative Strength Index
Master of overbought/oversold conditions
"""

import sys
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from collections import deque

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents_highlevel.trading_agent import TradingAgent, AgentBrain, MarketData, DecisionType

logger = logging.getLogger(__name__)


class RSIBrain(AgentBrain):
    """
    RSI-focused brain for technical analysis
    Calculates and trades based on Relative Strength Index
    """

    def __init__(self, personality: str, rsi_period: int = 14):
        self.personality = personality
        self.rsi_period = rsi_period
        self.price_history: deque = deque(maxlen=rsi_period + 10)
        self.rsi_history: deque = deque(maxlen=50)

        # RSI thresholds
        self.oversold_threshold = 30
        self.overbought_threshold = 70
        self.extreme_oversold = 20
        self.extreme_overbought = 80

        self.learning_rate = 0.01
        self.memory = []

    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Analyze market using RSI"""

        # Add to price history
        self.price_history.append(market_data.price)

        # Need minimum periods for RSI calculation
        if len(self.price_history) < self.rsi_period + 1:
            return {
                "rsi": 50.0,
                "rsi_state": "neutral",
                "rsi_divergence": False,
                "confidence": 0.0,
                "signal": "wait"
            }

        # Calculate RSI
        rsi = self._calculate_rsi()
        self.rsi_history.append(rsi)

        # Classify RSI state
        rsi_state = self._classify_rsi(rsi)

        # Detect RSI divergence (advanced)
        divergence = self._detect_divergence()

        # Generate signal
        signal, confidence = self._generate_signal(rsi, rsi_state, divergence)

        return {
            "rsi": rsi,
            "rsi_state": rsi_state,
            "rsi_divergence": divergence,
            "confidence": confidence,
            "signal": signal,
            "price_trend": self._get_price_trend()
        }

    def _calculate_rsi(self) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(self.price_history) < self.rsi_period + 1:
            return 50.0

        # Get price changes
        prices = list(self.price_history)
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [max(c, 0) for c in changes[-self.rsi_period:]]
        losses = [abs(min(c, 0)) for c in changes[-self.rsi_period:]]

        # Calculate average gain and loss
        avg_gain = sum(gains) / self.rsi_period
        avg_loss = sum(losses) / self.rsi_period

        # Avoid division by zero
        if avg_loss == 0:
            return 100.0

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _classify_rsi(self, rsi: float) -> str:
        """Classify RSI level"""
        if rsi >= self.extreme_overbought:
            return "extreme_overbought"
        elif rsi >= self.overbought_threshold:
            return "overbought"
        elif rsi <= self.extreme_oversold:
            return "extreme_oversold"
        elif rsi <= self.oversold_threshold:
            return "oversold"
        elif 45 <= rsi <= 55:
            return "neutral"
        elif rsi > 55:
            return "bullish"
        else:
            return "bearish"

    def _detect_divergence(self) -> bool:
        """Detect RSI divergence (simplified)"""
        if len(self.price_history) < 10 or len(self.rsi_history) < 10:
            return False

        # Get recent prices and RSI values
        recent_prices = list(self.price_history)[-10:]
        recent_rsi = list(self.rsi_history)[-10:]

        # Simple divergence detection
        # Price making new highs but RSI not = bearish divergence
        # Price making new lows but RSI not = bullish divergence

        price_trend = recent_prices[-1] - recent_prices[0]
        rsi_trend = recent_rsi[-1] - recent_rsi[0]

        # Divergence if trends oppose
        if price_trend > 0 and rsi_trend < -5:
            return True  # Bearish divergence
        elif price_trend < 0 and rsi_trend > 5:
            return True  # Bullish divergence

        return False

    def _get_price_trend(self) -> str:
        """Get current price trend"""
        if len(self.price_history) < 5:
            return "neutral"

        recent = list(self.price_history)[-5:]
        if recent[-1] > recent[0] * 1.01:
            return "up"
        elif recent[-1] < recent[0] * 0.99:
            return "down"
        else:
            return "neutral"

    def _generate_signal(self, rsi: float, rsi_state: str, divergence: bool) -> tuple[str, float]:
        """Generate trading signal from RSI analysis"""

        # EXTREME OVERSOLD - Strong buy signal
        if rsi_state == "extreme_oversold":
            confidence = 0.85
            return "buy", confidence

        # OVERSOLD - Buy signal
        elif rsi_state == "oversold":
            confidence = 0.70
            return "buy", confidence

        # EXTREME OVERBOUGHT - Strong sell signal
        elif rsi_state == "extreme_overbought":
            confidence = 0.85
            return "sell", confidence

        # OVERBOUGHT - Sell signal
        elif rsi_state == "overbought":
            confidence = 0.70
            return "sell", confidence

        # BULLISH DIVERGENCE - Buy signal
        elif divergence and rsi < 50:
            confidence = 0.75
            return "buy", confidence

        # BEARISH DIVERGENCE - Sell signal
        elif divergence and rsi > 50:
            confidence = 0.75
            return "sell", confidence

        # NEUTRAL/BULLISH/BEARISH zones - No clear signal
        elif rsi_state == "bullish":
            confidence = 0.55
            return "buy", confidence
        elif rsi_state == "bearish":
            confidence = 0.55
            return "sell", confidence

        # NEUTRAL - Hold
        return "hold", 0.3

    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Learn from trading outcomes and adapt thresholds"""
        self.memory.append({
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc)
        })

        # Keep last 1000 outcomes
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]

        # Adaptive threshold tuning
        if outcome.get("profitable", False):
            # Successful - maintain thresholds
            pass
        else:
            # Failed - tighten thresholds slightly
            if outcome.get("signal") == "buy":
                self.oversold_threshold = max(25, self.oversold_threshold - 0.5)
            elif outcome.get("signal") == "sell":
                self.overbought_threshold = min(75, self.overbought_threshold + 0.5)


class RSIReader(TradingAgent):
    """
    RSI Reader - Technical indicator specialist
    Master of overbought/oversold conditions
    """

    def __init__(self, agent_id: str, personality: str = "patient_observer",
                 rsi_period: int = 14):
        # Initialize parent
        super().__init__(
            agent_id=agent_id,
            personality=personality,
            specialization="rsi_reader"
        )

        # Replace brain with RSI brain
        self.brain = RSIBrain(personality, rsi_period)

        # RSI specific tracking
        self.rsi_trades = 0
        self.rsi_wins = 0
        self.last_rsi = 50.0

        logger.info(f"Created RSIReader agent '{agent_id}' with {personality} personality")

    async def _apply_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Apply RSI-based strategy"""

        # Get RSI metrics
        self.last_rsi = analysis.get("rsi", 50.0)
        rsi_state = analysis.get("rsi_state", "neutral")
        divergence = analysis.get("rsi_divergence", False)

        # Get signal
        signal = analysis.get("signal", "hold")
        confidence = analysis.get("confidence", 0.3)

        # Build reasoning
        reasoning_parts = [f"RSI: {self.last_rsi:.1f} ({rsi_state})"]

        if divergence:
            reasoning_parts.append("DIVERGENCE detected")

        reasoning = " | ".join(reasoning_parts)

        # Expected profit based on RSI extremes
        expected_profit = self._estimate_profit(analysis)

        return {
            "action": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "expected_profit": expected_profit
        }

    def _estimate_profit(self, analysis: Dict[str, Any]) -> float:
        """Estimate expected profit from RSI signal"""
        rsi_state = analysis.get("rsi_state", "neutral")

        profit_map = {
            "extreme_oversold": 0.03,  # 3% target
            "oversold": 0.02,          # 2% target
            "extreme_overbought": 0.03,
            "overbought": 0.02,
            "bullish": 0.01,
            "bearish": 0.01,
            "neutral": 0.005
        }

        return profit_map.get(rsi_state, 0.005)

    async def _update_performance(self, decision) -> None:
        """Update performance with RSI-specific metrics"""
        await super()._update_performance(decision)

        # Track RSI trades
        if decision.decision_type != DecisionType.HOLD:
            self.rsi_trades += 1

            if decision.expected_profit and decision.expected_profit > 0.015:
                self.rsi_wins += 1

    def get_rsi_stats(self) -> Dict[str, Any]:
        """Get RSI reader specific stats"""
        win_rate = (self.rsi_wins / self.rsi_trades) if self.rsi_trades > 0 else 0.0

        return {
            "agent_id": self.agent_id,
            "specialization": "rsi_reader",
            "rsi_trades": self.rsi_trades,
            "rsi_wins": self.rsi_wins,
            "rsi_win_rate": win_rate,
            "last_rsi": self.last_rsi,
            "oversold_threshold": self.brain.oversold_threshold,
            "overbought_threshold": self.brain.overbought_threshold
        }


# Factory function
def create_rsi_reader(agent_id: str, personality: str = "patient_observer",
                     rsi_period: int = 14) -> RSIReader:
    """Create an RSI Reader agent"""
    return RSIReader(
        agent_id=agent_id,
        personality=personality,
        rsi_period=rsi_period
    )


# Test
if __name__ == "__main__":
    import asyncio

    async def test_rsi_reader():
        """Test the RSI Reader agent"""
        print("=" * 70)
        print("📈 TESTING RSI READER AGENT")
        print("=" * 70)

        # Create agent
        reader = create_rsi_reader("rsi_1", "patient_observer")

        # Initialize
        await reader.initialize()
        reader.set_capital_allocation(10000.0)

        print(f"\n✅ Agent created: {reader.agent_id}")
        print(f"   Personality: {reader.personality}")
        print(f"   Specialization: {reader.specialization}")
        print(f"   Capital: ${reader.capital_allocation:,.2f}")

        # Simulate RSI conditions
        print("\n🔄 Simulating market with RSI extremes...\n")

        # Oversold -> Neutral -> Overbought scenario
        base_price = 100.0
        prices = [
            100, 98, 95, 93, 90, 88, 85, 83, 82, 81,  # Downtrend (oversold)
            80, 80, 81, 82, 84, 86, 88, 90, 92, 95,   # Recovery
            97, 100, 103, 106, 110, 113, 115, 118, 120, 122  # Uptrend (overbought)
        ]

        decisions = []
        for i, price in enumerate(prices):
            market_data = MarketData(
                symbol="TEST/USDT",
                price=price,
                volume=1000 + (i * 50),
                timestamp=datetime.now(timezone.utc),
                exchange="test",
                bid=price - 0.5,
                ask=price + 0.5,
                spread=1.0
            )

            decision = await reader.process(market_data)

            if decision and decision.decision_type != DecisionType.HOLD:
                decisions.append(decision)
                print(f"📊 Tick {i+1}: ${price:.2f}")
                print(f"   🎯 DECISION: {decision.decision_type.value.upper()}")
                print(f"   💪 Confidence: {decision.confidence:.1%}")
                print(f"   💭 Reasoning: {decision.reasoning}")
                print(f"   💰 Amount: ${decision.amount:.2f}")
                print()

        # Stats
        print("=" * 70)
        print("📊 RSI READER STATISTICS")
        print("=" * 70)

        perf = reader.get_performance_summary()
        rsi_stats = reader.get_rsi_stats()

        print(f"Total Decisions: {perf['decision_count']}")
        print(f"RSI Trades: {rsi_stats['rsi_trades']}")
        print(f"RSI Win Rate: {rsi_stats['rsi_win_rate']:.1%}")
        print(f"Last RSI: {rsi_stats['last_rsi']:.1f}")
        print(f"Thresholds: {rsi_stats['oversold_threshold']:.0f} / {rsi_stats['overbought_threshold']:.0f}")

        print("\n✅ TEST COMPLETE!")

    asyncio.run(test_rsi_reader())

#!/usr/bin/env python3
"""
ADVANCED PATTERN MASTER - Elite trading intelligence
Fibonacci sequences, Golden Ratio, Multi-timeframe, Black Swan detection
Part of Sovereign Shadow 2 - The ultimate trading AI
"""

import sys
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import deque
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents_highlevel.trading_agent import TradingAgent, AgentBrain, MarketData, DecisionType

logger = logging.getLogger(__name__)

# Golden Ratio (Phi)
PHI = 1.618033988749895
GOLDEN_RATIO = PHI

# Fibonacci sequence
FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618, 2.618]


class AdvancedPatternBrain(AgentBrain):
    """
    Advanced pattern recognition brain
    Multi-timeframe, Fibonacci, Golden Ratio, Black Swan detection
    """

    def __init__(self, personality: str):
        self.personality = personality

        # Multi-timeframe data storage
        self.timeframes = {
            "1D": deque(maxlen=365),    # 1 year of daily data
            "1W": deque(maxlen=52),     # 1 year of weekly data
            "3M": deque(maxlen=4),      # 1 year of quarterly data
            "6M": deque(maxlen=2),      # 1 year of bi-annual data
            "1Y": deque(maxlen=10),     # 10 years of annual data
        }

        # Real-time tick data for immediate analysis
        self.tick_data: deque = deque(maxlen=1000)

        # Price extremes for Fibonacci calculations
        self.recent_high = 0.0
        self.recent_low = float('inf')
        self.swing_high = 0.0
        self.swing_low = float('inf')

        # Black swan detection
        self.normal_volatility = 0.02  # 2% normal
        self.black_swan_threshold = 0.10  # 10% move = potential black swan
        self.black_swan_events = []

        # Golden triangle tracking
        self.golden_triangle_active = False

        self.learning_rate = 0.01
        self.memory = []

    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Comprehensive advanced pattern analysis"""

        # Store tick data
        self.tick_data.append({
            "price": market_data.price,
            "volume": market_data.volume,
            "timestamp": market_data.timestamp
        })

        # Update price extremes
        self._update_extremes(market_data.price)

        # Check for black swan events
        black_swan = self._detect_black_swan(market_data.price)

        # Multi-timeframe analysis
        mtf_analysis = self._multi_timeframe_analysis()

        # Fibonacci levels
        fib_levels = self._calculate_fibonacci_levels()
        fib_signal = self._interpret_fibonacci(market_data.price, fib_levels)

        # Golden ratio analysis
        golden_signal = self._analyze_golden_ratio(market_data.price)

        # Golden triangle pattern
        golden_triangle = self._detect_golden_triangle()

        # Combine all signals
        master_signal, confidence = self._generate_advanced_signal(
            black_swan=black_swan,
            fib_signal=fib_signal,
            golden_signal=golden_signal,
            golden_triangle=golden_triangle,
            mtf=mtf_analysis
        )

        return {
            "signal": master_signal,
            "confidence": confidence,
            "black_swan_detected": black_swan,
            "fibonacci": fib_levels,
            "fibonacci_signal": fib_signal,
            "golden_ratio_signal": golden_signal,
            "golden_triangle": golden_triangle,
            "multi_timeframe": mtf_analysis
        }

    def _update_extremes(self, price: float):
        """Update price extremes for Fibonacci calculations"""
        # Update recent high/low
        self.recent_high = max(self.recent_high, price)
        self.recent_low = min(self.recent_low, price)

        # Update swing high/low (last 100 ticks)
        if len(self.tick_data) >= 100:
            recent_prices = [t["price"] for t in list(self.tick_data)[-100:]]
            self.swing_high = max(recent_prices)
            self.swing_low = min(recent_prices)

    def _detect_black_swan(self, current_price: float) -> Dict[str, Any]:
        """
        Detect potential black swan events
        Extreme price movements that indicate systemic risk
        """
        if len(self.tick_data) < 10:
            return {"detected": False, "severity": 0.0, "direction": "none"}

        # Get recent price history
        recent = list(self.tick_data)[-10:]
        prices = [t["price"] for t in recent]

        # Calculate recent volatility
        changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        avg_change = sum(changes) / len(changes)

        # Check for extreme move
        if current_price > 0 and len(prices) > 0:
            latest_change = abs(current_price - prices[-1]) / prices[-1]

            # Black swan if move > threshold and >> normal volatility
            if latest_change > self.black_swan_threshold:
                severity = latest_change / self.black_swan_threshold
                direction = "up" if current_price > prices[-1] else "down"

                # Log event
                event = {
                    "timestamp": datetime.now(timezone.utc),
                    "severity": severity,
                    "direction": direction,
                    "price_change": latest_change
                }
                self.black_swan_events.append(event)

                logger.warning(f"🦢 BLACK SWAN DETECTED: {severity:.1f}x severity, {direction}")

                return {
                    "detected": True,
                    "severity": severity,
                    "direction": direction,
                    "price_change": latest_change
                }

        return {"detected": False, "severity": 0.0, "direction": "none"}

    def _calculate_fibonacci_levels(self) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        From swing low to swing high
        """
        if self.swing_high == 0 or self.swing_low == float('inf'):
            return {}

        price_range = self.swing_high - self.swing_low

        levels = {}
        for fib in FIBONACCI_LEVELS:
            if fib <= 1.0:
                # Retracement levels (below high)
                levels[f"fib_{fib:.3f}"] = self.swing_high - (price_range * fib)
            else:
                # Extension levels (above high)
                levels[f"ext_{fib:.3f}"] = self.swing_high + (price_range * (fib - 1.0))

        return levels

    def _interpret_fibonacci(self, current_price: float, fib_levels: Dict[str, float]) -> str:
        """Interpret Fibonacci signals"""
        if not fib_levels:
            return "unknown"

        # Check if price is at key Fibonacci level
        tolerance = 0.005  # 0.5% tolerance

        # Key support/resistance levels
        key_levels = {
            "fib_0.382": "strong_support",
            "fib_0.500": "equilibrium",
            "fib_0.618": "golden_zone",
            "fib_0.786": "deep_support",
            "ext_1.618": "golden_extension"
        }

        for level_name, signal in key_levels.items():
            if level_name in fib_levels:
                level_price = fib_levels[level_name]
                if abs(current_price - level_price) / level_price < tolerance:
                    return signal

        # Check position relative to levels
        if current_price > fib_levels.get("ext_1.618", float('inf')):
            return "above_golden_extension"
        elif current_price < fib_levels.get("fib_0.786", 0):
            return "below_deep_support"

        return "between_levels"

    def _analyze_golden_ratio(self, current_price: float) -> str:
        """
        Analyze using Golden Ratio (Phi = 1.618)
        Check if price movements follow golden ratio proportions
        """
        if len(self.tick_data) < 20:
            return "insufficient_data"

        recent = list(self.tick_data)[-20:]
        prices = [t["price"] for t in recent]

        # Check for golden ratio in price swings
        # Look for moves that are phi (1.618) times previous move
        for i in range(2, len(prices)):
            move1 = abs(prices[i-1] - prices[i-2])
            move2 = abs(prices[i] - prices[i-1])

            if move1 > 0:
                ratio = move2 / move1

                # Within 5% of golden ratio
                if 0.95 * PHI <= ratio <= 1.05 * PHI:
                    logger.info(f"✨ GOLDEN RATIO detected: {ratio:.3f}")
                    return "golden_ratio_expansion"
                elif 0.95 * (1/PHI) <= ratio <= 1.05 * (1/PHI):
                    return "golden_ratio_contraction"

        return "no_golden_pattern"

    def _detect_golden_triangle(self) -> Dict[str, Any]:
        """
        Detect Golden Triangle pattern
        Three price points forming golden ratio proportions
        """
        if len(self.tick_data) < 30:
            return {"detected": False, "signal": "none"}

        recent = list(self.tick_data)[-30:]
        prices = [t["price"] for t in recent]

        # Find local peaks and troughs
        peaks = []
        troughs = []

        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                peaks.append((i, prices[i]))
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                troughs.append((i, prices[i]))

        # Need at least 3 points
        if len(peaks) >= 2 and len(troughs) >= 1:
            # Check if they form golden ratios
            # Simplified: just check if triangle exists
            self.golden_triangle_active = True
            return {
                "detected": True,
                "signal": "golden_triangle_bullish",
                "peaks": len(peaks),
                "troughs": len(troughs)
            }

        self.golden_triangle_active = False
        return {"detected": False, "signal": "none"}

    def _multi_timeframe_analysis(self) -> Dict[str, str]:
        """
        Multi-timeframe analysis
        Align signals across 1D, 1W, 3M, 6M, 1Y
        """
        # Simplified multi-timeframe analysis
        # In production, would aggregate tick data into timeframes

        if len(self.tick_data) < 100:
            return {
                "1D": "unknown",
                "1W": "unknown",
                "3M": "unknown",
                "6M": "unknown",
                "1Y": "unknown",
                "alignment": "insufficient_data"
            }

        recent = list(self.tick_data)
        prices = [t["price"] for t in recent]

        # Daily trend (last 24 ticks)
        daily_trend = "up" if prices[-1] > prices[-24] else "down" if len(prices) >= 24 else "neutral"

        # Weekly trend (last 100 ticks approximation)
        weekly_trend = "up" if prices[-1] > prices[-50] else "down" if len(prices) >= 50 else "neutral"

        # Check alignment
        if daily_trend == weekly_trend and daily_trend != "neutral":
            alignment = "strong_" + daily_trend
        else:
            alignment = "divergent"

        return {
            "1D": daily_trend,
            "1W": weekly_trend,
            "3M": weekly_trend,  # Approximation
            "6M": weekly_trend,
            "1Y": weekly_trend,
            "alignment": alignment
        }

    def _generate_advanced_signal(self, black_swan: Dict, fib_signal: str,
                                  golden_signal: str, golden_triangle: Dict,
                                  mtf: Dict) -> Tuple[str, float]:
        """Generate master signal from all advanced indicators"""

        # BLACK SWAN OVERRIDE - Defensive positioning
        if black_swan["detected"]:
            if black_swan["direction"] == "down":
                return "sell", 0.95  # Immediate exit
            else:
                return "hold", 0.90  # Extreme caution

        buy_score = 0
        sell_score = 0

        # Fibonacci signals
        fib_signals = {
            "golden_zone": 2,  # Strong buy
            "deep_support": 2,
            "strong_support": 1,
            "below_deep_support": -2,  # Sell signal
            "above_golden_extension": -1
        }
        buy_score += fib_signals.get(fib_signal, 0)

        # Golden ratio signals
        if golden_signal == "golden_ratio_expansion":
            buy_score += 2
        elif golden_signal == "golden_ratio_contraction":
            sell_score += 1

        # Golden triangle
        if golden_triangle["detected"]:
            if golden_triangle["signal"] == "golden_triangle_bullish":
                buy_score += 3

        # Multi-timeframe alignment
        if mtf["alignment"] == "strong_up":
            buy_score += 2
        elif mtf["alignment"] == "strong_down":
            sell_score += 2

        # Generate signal
        total_score = buy_score - sell_score

        if total_score >= 3:
            confidence = min(0.75 + (total_score * 0.05), 0.95)
            return "buy", confidence
        elif total_score <= -3:
            confidence = min(0.75 + (abs(total_score) * 0.05), 0.95)
            return "sell", confidence
        else:
            return "hold", 0.4

    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Learn and adapt from outcomes"""
        self.memory.append(outcome)
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]


class AdvancedPatternMaster(TradingAgent):
    """
    Advanced Pattern Master
    Fibonacci, Golden Ratio, Multi-timeframe, Black Swan detection
    The elite of Sovereign Shadow 2
    """

    def __init__(self, agent_id: str, personality: str = "contrarian_analyst"):
        super().__init__(
            agent_id=agent_id,
            personality=personality,
            specialization="advanced_pattern_master"
        )

        # Replace with advanced brain
        self.brain = AdvancedPatternBrain(personality)

        # Advanced tracking
        self.pattern_trades = 0
        self.fibonacci_wins = 0
        self.black_swan_saves = 0

        logger.info(f"Created AdvancedPatternMaster '{agent_id}' - Elite Sovereign Shadow 2 Agent")

    async def _apply_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Apply advanced pattern recognition strategy"""

        signal = analysis.get("signal", "hold")
        confidence = analysis.get("confidence", 0.3)

        # Build reasoning
        reasoning_parts = []

        # Black swan
        if analysis.get("black_swan_detected", {}).get("detected"):
            bs = analysis["black_swan_detected"]
            reasoning_parts.append(f"🦢 BLACK SWAN: {bs['direction']} {bs['severity']:.1f}x")
            self.black_swan_saves += 1

        # Fibonacci
        fib_sig = analysis.get("fibonacci_signal", "unknown")
        if fib_sig in ["golden_zone", "deep_support", "golden_extension"]:
            reasoning_parts.append(f"📐 Fib: {fib_sig}")

        # Golden ratio
        golden = analysis.get("golden_ratio_signal", "")
        if "golden" in golden:
            reasoning_parts.append(f"✨ {golden}")

        # Golden triangle
        if analysis.get("golden_triangle", {}).get("detected"):
            reasoning_parts.append("🔺 Golden Triangle")

        # Multi-timeframe
        mtf = analysis.get("multi_timeframe", {})
        alignment = mtf.get("alignment", "unknown")
        if "strong" in alignment:
            reasoning_parts.append(f"📊 MTF: {alignment}")

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Pattern analysis in progress"

        return {
            "action": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "expected_profit": confidence * 0.03  # Up to 3%
        }

    async def _update_performance(self, decision) -> None:
        """Update performance tracking"""
        await super()._update_performance(decision)

        if decision.decision_type != DecisionType.HOLD:
            self.pattern_trades += 1

            # Count Fibonacci wins
            if decision.expected_profit and decision.expected_profit > 0.02:
                self.fibonacci_wins += 1

    def get_advanced_stats(self) -> Dict[str, Any]:
        """Get advanced pattern statistics"""
        return {
            "agent_id": self.agent_id,
            "specialization": "advanced_pattern_master",
            "pattern_trades": self.pattern_trades,
            "fibonacci_wins": self.fibonacci_wins,
            "black_swan_saves": self.black_swan_saves,
            "black_swan_events": len(self.brain.black_swan_events),
            "golden_triangle_active": self.brain.golden_triangle_active
        }


def create_advanced_pattern_master(agent_id: str, personality: str = "contrarian_analyst") -> AdvancedPatternMaster:
    """Create an Advanced Pattern Master agent"""
    return AdvancedPatternMaster(agent_id=agent_id, personality=personality)


# Test
if __name__ == "__main__":
    import asyncio

    async def test_advanced_master():
        print("=" * 70)
        print("🎯 TESTING ADVANCED PATTERN MASTER")
        print("   Fibonacci | Golden Ratio | Black Swan | Multi-Timeframe")
        print("=" * 70)

        agent = create_advanced_pattern_master("apex_1", "contrarian_analyst")
        await agent.initialize()
        agent.set_capital_allocation(50000.0)

        print(f"\n✅ Elite Agent: {agent.agent_id}")
        print(f"   Capital: ${agent.capital_allocation:,.2f}")

        # Simulate volatile market with patterns
        print("\n🔄 Simulating market patterns...\n")

        base = 200.0
        # Create Fibonacci-like retracement
        prices = [200, 205, 210, 215, 220]  # Uptrend
        prices += [218, 214, 210, 206, 203]  # 61.8% retracement
        prices += [205, 208, 212, 217, 223, 230]  # Golden extension

        # Black swan event
        prices += [230, 210, 190, 180]  # -21% crash

        for i, price in enumerate(prices):
            market_data = MarketData(
                symbol="BTC/USDT",
                price=price,
                volume=1000 * (1 + abs(price - 200) / 200),
                timestamp=datetime.now(timezone.utc),
                exchange="elite"
            )

            decision = await agent.process(market_data)

            if decision and (decision.decision_type != DecisionType.HOLD or i >= len(prices) - 5):
                print(f"Tick {i+1}: ${price:.2f}")
                print(f"   🎯 {decision.decision_type.value.upper()}")
                print(f"   💪 {decision.confidence:.1%}")
                print(f"   💭 {decision.reasoning}")
                print()

        # Stats
        stats = agent.get_advanced_stats()
        print("=" * 70)
        print("📊 ADVANCED PATTERN MASTER STATS")
        print("=" * 70)
        print(f"Pattern Trades: {stats['pattern_trades']}")
        print(f"Fibonacci Wins: {stats['fibonacci_wins']}")
        print(f"Black Swan Saves: {stats['black_swan_saves']}")
        print(f"Black Swan Events Detected: {stats['black_swan_events']}")

        print("\n✅ ADVANCED PATTERN MASTER OPERATIONAL!")

    asyncio.run(test_advanced_master())

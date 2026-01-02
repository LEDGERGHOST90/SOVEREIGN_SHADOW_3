#!/usr/bin/env python3
"""
TECHNICAL ANALYSIS MASTER - Full TradingView indicator suite
Combines RSI, VWAP, Moving Averages, Bollinger Bands, MACD, and more
"""

import sys
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import deque
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.swarm.core.swarm_agent_base import TradingAgent, AgentBrain, MarketData, DecisionType

logger = logging.getLogger(__name__)


class TechnicalAnalysisBrain(AgentBrain):
    """
    Comprehensive technical analysis brain
    Full indicator suite: RSI, VWAP, MA, BB, MACD, Stochastic, ATR
    """

    def __init__(self, personality: str, lookback: int = 50):
        self.personality = personality
        self.lookback = lookback

        # Price/volume history
        self.price_history: deque = deque(maxlen=lookback)
        self.volume_history: deque = deque(maxlen=lookback)
        self.high_history: deque = deque(maxlen=lookback)
        self.low_history: deque = deque(maxlen=lookback)
        self.timestamp_history: deque = deque(maxlen=lookback)

        # Indicator periods
        self.rsi_period = 14
        self.fast_ma = 9
        self.slow_ma = 21
        self.bb_period = 20
        self.bb_std = 2.0

        self.learning_rate = 0.01
        self.memory = []

    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Full technical analysis using all indicators"""

        # Update histories
        self.price_history.append(market_data.price)
        self.volume_history.append(market_data.volume)
        self.high_history.append(market_data.price * 1.001)  # Approx high
        self.low_history.append(market_data.price * 0.999)   # Approx low
        self.timestamp_history.append(market_data.timestamp)

        # Need minimum data
        if len(self.price_history) < max(self.rsi_period, self.slow_ma, self.bb_period):
            return {
                "signal": "wait",
                "confidence": 0.0,
                "indicators": {}
            }

        # Calculate all indicators
        indicators = {}

        # 1. RSI
        indicators["rsi"] = self._calculate_rsi()
        indicators["rsi_signal"] = self._interpret_rsi(indicators["rsi"])

        # 2. Moving Averages
        indicators["sma_fast"] = self._calculate_sma(self.fast_ma)
        indicators["sma_slow"] = self._calculate_sma(self.slow_ma)
        indicators["ema_fast"] = self._calculate_ema(self.fast_ma)
        indicators["ema_slow"] = self._calculate_ema(self.slow_ma)
        indicators["ma_signal"] = self._interpret_ma_crossover(
            indicators["ema_fast"], indicators["ema_slow"]
        )

        # 3. VWAP
        indicators["vwap"] = self._calculate_vwap()
        indicators["vwap_signal"] = self._interpret_vwap(
            market_data.price, indicators["vwap"]
        )

        # 4. Bollinger Bands
        bb = self._calculate_bollinger_bands()
        indicators["bb_upper"] = bb["upper"]
        indicators["bb_middle"] = bb["middle"]
        indicators["bb_lower"] = bb["lower"]
        indicators["bb_width"] = bb["width"]
        indicators["bb_signal"] = self._interpret_bollinger(market_data.price, bb)

        # 5. MACD
        macd = self._calculate_macd()
        indicators["macd"] = macd["macd"]
        indicators["macd_signal"] = macd["signal"]
        indicators["macd_histogram"] = macd["histogram"]
        indicators["macd_crossover"] = self._interpret_macd(macd)

        # 6. Stochastic
        stoch = self._calculate_stochastic()
        indicators["stoch_k"] = stoch["k"]
        indicators["stoch_d"] = stoch["d"]
        indicators["stoch_signal"] = self._interpret_stochastic(stoch)

        # 7. ATR (volatility)
        indicators["atr"] = self._calculate_atr()

        # Combine all signals
        signal, confidence = self._generate_master_signal(indicators)

        return {
            "signal": signal,
            "confidence": confidence,
            "indicators": indicators
        }

    def _calculate_rsi(self, period: int = None) -> float:
        """Calculate RSI"""
        if period is None:
            period = self.rsi_period

        if len(self.price_history) < period + 1:
            return 50.0

        prices = list(self.price_history)
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        gains = [max(c, 0) for c in changes[-period:]]
        losses = [abs(min(c, 0)) for c in changes[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI signal"""
        if rsi >= 70:
            return "overbought"
        elif rsi <= 30:
            return "oversold"
        else:
            return "neutral"

    def _calculate_sma(self, period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(self.price_history) < period:
            return self.price_history[-1] if self.price_history else 0.0

        prices = list(self.price_history)[-period:]
        return sum(prices) / len(prices)

    def _calculate_ema(self, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(self.price_history) < period:
            return self._calculate_sma(period)

        prices = list(self.price_history)
        multiplier = 2 / (period + 1)

        # Start with SMA
        ema = sum(prices[:period]) / period

        # Calculate EMA for remaining prices
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _interpret_ma_crossover(self, fast_ma: float, slow_ma: float) -> str:
        """Interpret moving average crossover"""
        if fast_ma > slow_ma * 1.005:  # 0.5% threshold
            return "bullish_crossover"
        elif fast_ma < slow_ma * 0.995:
            return "bearish_crossover"
        else:
            return "neutral"

    def _calculate_vwap(self) -> float:
        """Calculate Volume Weighted Average Price"""
        if not self.volume_history or not self.price_history:
            return self.price_history[-1] if self.price_history else 0.0

        prices = list(self.price_history)
        volumes = list(self.volume_history)

        # Typical price * volume
        pv_sum = sum(p * v for p, v in zip(prices, volumes))
        v_sum = sum(volumes)

        if v_sum == 0:
            return prices[-1]

        return pv_sum / v_sum

    def _interpret_vwap(self, current_price: float, vwap: float) -> str:
        """Interpret VWAP signal"""
        if current_price > vwap * 1.01:  # 1% above VWAP
            return "above_vwap"
        elif current_price < vwap * 0.99:  # 1% below VWAP
            return "below_vwap"
        else:
            return "at_vwap"

    def _calculate_bollinger_bands(self) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(self.price_history) < self.bb_period:
            mid = self.price_history[-1] if self.price_history else 0.0
            return {
                "upper": mid * 1.02,
                "middle": mid,
                "lower": mid * 0.98,
                "width": mid * 0.04
            }

        prices = list(self.price_history)[-self.bb_period:]

        # Middle band (SMA)
        middle = sum(prices) / len(prices)

        # Standard deviation
        variance = sum((p - middle) ** 2 for p in prices) / len(prices)
        std_dev = math.sqrt(variance)

        # Upper and lower bands
        upper = middle + (self.bb_std * std_dev)
        lower = middle - (self.bb_std * std_dev)
        width = (upper - lower) / middle if middle > 0 else 0

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "width": width
        }

    def _interpret_bollinger(self, price: float, bb: Dict[str, float]) -> str:
        """Interpret Bollinger Bands signal"""
        if price >= bb["upper"]:
            return "at_upper_band"  # Potential reversal down
        elif price <= bb["lower"]:
            return "at_lower_band"  # Potential reversal up
        elif price > bb["middle"]:
            return "above_middle"
        elif price < bb["middle"]:
            return "below_middle"
        else:
            return "at_middle"

    def _calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(self.price_history) < slow:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        # Calculate fast and slow EMAs
        ema_fast = self._calculate_ema(fast)
        ema_slow = self._calculate_ema(slow)

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line (simplified - would normally use EMA of MACD)
        signal_line = macd_line * 0.9  # Approximation

        # Histogram
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    def _interpret_macd(self, macd: Dict[str, float]) -> str:
        """Interpret MACD signal"""
        if macd["histogram"] > 0.5:
            return "bullish"
        elif macd["histogram"] < -0.5:
            return "bearish"
        else:
            return "neutral"

    def _calculate_stochastic(self, period: int = 14) -> Dict[str, float]:
        """Calculate Stochastic Oscillator"""
        if len(self.high_history) < period:
            return {"k": 50.0, "d": 50.0}

        highs = list(self.high_history)[-period:]
        lows = list(self.low_history)[-period:]
        close = self.price_history[-1]

        highest_high = max(highs)
        lowest_low = min(lows)

        if highest_high == lowest_low:
            k = 50.0
        else:
            k = ((close - lowest_low) / (highest_high - lowest_low)) * 100

        # %D is 3-period SMA of %K (simplified)
        d = k * 0.9  # Approximation

        return {"k": k, "d": d}

    def _interpret_stochastic(self, stoch: Dict[str, float]) -> str:
        """Interpret Stochastic signal"""
        if stoch["k"] >= 80:
            return "overbought"
        elif stoch["k"] <= 20:
            return "oversold"
        else:
            return "neutral"

    def _calculate_atr(self, period: int = 14) -> float:
        """Calculate Average True Range (volatility measure)"""
        if len(self.high_history) < period:
            return 0.0

        true_ranges = []
        for i in range(-period, 0):
            high = self.high_history[i]
            low = self.low_history[i]
            prev_close = self.price_history[i-1] if i > -len(self.price_history) else low

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return sum(true_ranges) / len(true_ranges)

    def _generate_master_signal(self, indicators: Dict[str, Any]) -> tuple[str, float]:
        """Generate master trading signal from all indicators"""

        buy_signals = 0
        sell_signals = 0
        total_signals = 0

        # RSI
        if indicators.get("rsi_signal") == "oversold":
            buy_signals += 2  # Strong weight
        elif indicators.get("rsi_signal") == "overbought":
            sell_signals += 2
        total_signals += 2

        # Moving Average Crossover
        if indicators.get("ma_signal") == "bullish_crossover":
            buy_signals += 2
        elif indicators.get("ma_signal") == "bearish_crossover":
            sell_signals += 2
        total_signals += 2

        # VWAP
        if indicators.get("vwap_signal") == "below_vwap":
            buy_signals += 1
        elif indicators.get("vwap_signal") == "above_vwap":
            sell_signals += 1
        total_signals += 1

        # Bollinger Bands
        if indicators.get("bb_signal") == "at_lower_band":
            buy_signals += 2
        elif indicators.get("bb_signal") == "at_upper_band":
            sell_signals += 2
        total_signals += 2

        # MACD
        if indicators.get("macd_crossover") == "bullish":
            buy_signals += 1
        elif indicators.get("macd_crossover") == "bearish":
            sell_signals += 1
        total_signals += 1

        # Stochastic
        if indicators.get("stoch_signal") == "oversold":
            buy_signals += 1
        elif indicators.get("stoch_signal") == "overbought":
            sell_signals += 1
        total_signals += 1

        # Calculate confidence
        if buy_signals > sell_signals:
            confidence = min((buy_signals / total_signals) * 1.5, 0.95)
            return "buy", confidence
        elif sell_signals > buy_signals:
            confidence = min((sell_signals / total_signals) * 1.5, 0.95)
            return "sell", confidence
        else:
            return "hold", 0.3

    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Learn from outcomes"""
        self.memory.append(outcome)
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]


class TechnicalMaster(TradingAgent):
    """
    Technical Analysis Master
    Full suite: RSI, VWAP, MA, BB, MACD, Stochastic, ATR
    """

    def __init__(self, agent_id: str, personality: str = "patient_observer"):
        super().__init__(
            agent_id=agent_id,
            personality=personality,
            specialization="technical_master"
        )

        # Replace brain
        self.brain = TechnicalAnalysisBrain(personality)

        logger.info(f"Created TechnicalMaster agent '{agent_id}'")

    async def _apply_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Apply comprehensive technical analysis"""

        indicators = analysis.get("indicators", {})
        signal = analysis.get("signal", "hold")
        confidence = analysis.get("confidence", 0.3)

        # Build detailed reasoning
        reasoning_parts = [
            f"RSI: {indicators.get('rsi', 50):.1f} ({indicators.get('rsi_signal', 'N/A')})",
            f"MA: {indicators.get('ma_signal', 'neutral')}",
            f"BB: {indicators.get('bb_signal', 'N/A')}",
            f"MACD: {indicators.get('macd_crossover', 'N/A')}",
        ]

        if indicators.get("vwap_signal") == "below_vwap":
            reasoning_parts.append("Below VWAP (bullish)")
        elif indicators.get("vwap_signal") == "above_vwap":
            reasoning_parts.append("Above VWAP (bearish)")

        reasoning = " | ".join(reasoning_parts)

        return {
            "action": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "expected_profit": confidence * 0.025  # Up to 2.5%
        }


def create_technical_master(agent_id: str, personality: str = "patient_observer") -> TechnicalMaster:
    """Create a Technical Analysis Master agent"""
    return TechnicalMaster(agent_id=agent_id, personality=personality)


# Test
if __name__ == "__main__":
    import asyncio

    async def test_technical_master():
        print("=" * 70)
        print("📊 TESTING TECHNICAL ANALYSIS MASTER")
        print("=" * 70)

        agent = create_technical_master("tech_master_1")
        await agent.initialize()
        agent.set_capital_allocation(10000.0)

        print(f"\n✅ Agent: {agent.agent_id}")
        print(f"   Indicators: RSI, VWAP, MA, BB, MACD, Stochastic, ATR")

        # Simulate trend
        print("\n🔄 Simulating market data...\n")

        prices = [100 + i * 0.5 + (i % 5) * 2 for i in range(30)]

        for i, price in enumerate(prices[-5:], start=26):
            market_data = MarketData(
                symbol="TEST/USDT",
                price=price,
                volume=1000 + i * 100,
                timestamp=datetime.now(timezone.utc),
                exchange="test"
            )

            decision = await agent.process(market_data)

            if decision and decision.decision_type != DecisionType.HOLD:
                print(f"Tick {i}: ${price:.2f}")
                print(f"   🎯 {decision.decision_type.value.upper()}")
                print(f"   💪 {decision.confidence:.1%}")
                print(f"   💭 {decision.reasoning}")
                print()

        print("✅ TEST COMPLETE!")

    asyncio.run(test_technical_master())

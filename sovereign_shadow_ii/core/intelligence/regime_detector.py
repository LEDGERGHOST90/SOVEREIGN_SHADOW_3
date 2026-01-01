#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - Market Regime Detector (Directive Layer)

This is the Directive Layer of the D.O.E. Pattern:
- Classifies current market conditions into regimes
- Runs on 5-minute intervals
- Provides context for AI Strategy Selector

Market Regimes:
1. trending_bullish - Strong upward momentum
2. trending_bearish - Strong downward momentum
3. choppy_volatile - High volatility, no clear trend
4. choppy_calm - Low volatility, ranging market
5. breakout_potential - Consolidation before likely breakout
6. capitulation - Extreme fear, potential reversal
7. euphoria - Extreme greed, potential top
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class MarketRegime(str, Enum):
    """Market regime classifications"""
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    CHOPPY_VOLATILE = "choppy_volatile"
    CHOPPY_CALM = "choppy_calm"
    BREAKOUT_POTENTIAL = "breakout_potential"
    CAPITULATION = "capitulation"
    EUPHORIA = "euphoria"
    UNKNOWN = "unknown"


@dataclass
class RegimeAnalysis:
    """Container for regime analysis results"""
    regime: MarketRegime
    confidence: float  # 0-100
    sub_regime: Optional[str] = None
    trend_strength: float = 0  # -100 to 100 (negative = bearish)
    volatility_percentile: float = 0  # 0-100
    momentum_score: float = 0  # -100 to 100
    volume_profile: str = "normal"  # low, normal, high, climax
    key_levels: Dict[str, float] = None
    timestamp: str = None
    reasoning: List[str] = None

    def __post_init__(self):
        if self.key_levels is None:
            self.key_levels = {}
        if self.reasoning is None:
            self.reasoning = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class MarketRegimeDetector:
    """
    Detects market regime based on multiple indicators.

    Uses:
    - ADX for trend strength
    - ATR percentile for volatility classification
    - RSI for momentum/extremes
    - Moving average relationships
    - Volume analysis
    - Bollinger Band width for consolidation detection
    """

    def __init__(self):
        """Initialize the regime detector"""
        self.current_regime: Optional[RegimeAnalysis] = None
        self.regime_history: List[RegimeAnalysis] = []
        self.max_history = 288  # 24 hours at 5-min intervals

        # Thresholds for regime classification
        self.thresholds = {
            # ADX thresholds
            'adx_trending': 25,  # Above = trending
            'adx_strong_trend': 40,  # Above = strong trend

            # RSI thresholds
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'rsi_extreme_fear': 20,
            'rsi_extreme_greed': 80,

            # Volatility percentile thresholds
            'volatility_low': 25,  # Below = calm
            'volatility_high': 75,  # Above = volatile

            # Bollinger Band width for breakout detection
            'bb_squeeze_percentile': 20,  # Below = potential breakout

            # Volume thresholds
            'volume_climax_multiplier': 3.0,  # 3x average = climax
        }

        logger.info("MarketRegimeDetector initialized")

    def analyze(
        self,
        ohlcv_data: List[Dict],
        symbol: str = "BTC/USD"
    ) -> RegimeAnalysis:
        """
        Analyze market data and detect current regime.

        Args:
            ohlcv_data: List of OHLCV candles with keys:
                        [open, high, low, close, volume, timestamp]
            symbol: Trading pair for context

        Returns:
            RegimeAnalysis with detected regime and confidence
        """
        if len(ohlcv_data) < 50:
            logger.warning("Insufficient data for regime analysis (need 50+ candles)")
            return RegimeAnalysis(
                regime=MarketRegime.UNKNOWN,
                confidence=0,
                reasoning=["Insufficient data"]
            )

        try:
            # Calculate all indicators
            indicators = self._calculate_indicators(ohlcv_data)

            # Detect regime based on indicators
            regime, confidence, reasoning = self._classify_regime(indicators)

            # Build analysis result
            analysis = RegimeAnalysis(
                regime=regime,
                confidence=confidence,
                trend_strength=indicators['trend_strength'],
                volatility_percentile=indicators['volatility_percentile'],
                momentum_score=indicators['momentum_score'],
                volume_profile=indicators['volume_profile'],
                key_levels=indicators['key_levels'],
                reasoning=reasoning
            )

            # Update history
            self.current_regime = analysis
            self.regime_history.append(analysis)
            if len(self.regime_history) > self.max_history:
                self.regime_history.pop(0)

            logger.info(f"Regime detected: {regime.value} (confidence: {confidence:.1f}%)")

            return analysis

        except Exception as e:
            logger.error(f"Regime analysis failed: {e}")
            return RegimeAnalysis(
                regime=MarketRegime.UNKNOWN,
                confidence=0,
                reasoning=[f"Analysis error: {str(e)}"]
            )

    def _calculate_indicators(self, ohlcv_data: List[Dict]) -> Dict[str, Any]:
        """Calculate all technical indicators for regime detection"""

        # Extract price arrays
        closes = [c['close'] for c in ohlcv_data]
        highs = [c['high'] for c in ohlcv_data]
        lows = [c['low'] for c in ohlcv_data]
        volumes = [c.get('volume', 0) for c in ohlcv_data]

        # Calculate indicators
        adx = self._calculate_adx(highs, lows, closes, period=14)
        rsi = self._calculate_rsi(closes, period=14)
        atr = self._calculate_atr(highs, lows, closes, period=14)
        bb_width = self._calculate_bb_width(closes, period=20, std_dev=2)

        # Calculate moving averages
        ema_20 = self._calculate_ema(closes, 20)
        ema_50 = self._calculate_ema(closes, 50)
        sma_200 = self._calculate_sma(closes, 200) if len(closes) >= 200 else ema_50

        # Trend direction and strength
        current_price = closes[-1]
        trend_direction = 1 if current_price > ema_50 else -1
        trend_strength = (adx / 100) * 100 * trend_direction  # Normalized -100 to 100

        # Volatility percentile (compare current ATR to historical)
        atr_history = [self._calculate_atr(highs[i-14:i], lows[i-14:i], closes[i-14:i], 14)
                       for i in range(14, len(closes), 5)]
        volatility_percentile = self._percentile_rank(atr, atr_history) if atr_history else 50

        # Momentum score based on RSI
        if rsi < 30:
            momentum_score = (rsi - 50) * 2  # Negative
        elif rsi > 70:
            momentum_score = (rsi - 50) * 2  # Positive
        else:
            momentum_score = (rsi - 50) * 1.5

        # Volume profile
        avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        if current_volume > avg_volume * self.thresholds['volume_climax_multiplier']:
            volume_profile = "climax"
        elif current_volume > avg_volume * 1.5:
            volume_profile = "high"
        elif current_volume < avg_volume * 0.5:
            volume_profile = "low"
        else:
            volume_profile = "normal"

        # Key levels (support/resistance)
        key_levels = {
            'current_price': current_price,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'recent_high': max(highs[-20:]),
            'recent_low': min(lows[-20:]),
            'atr': atr
        }

        # Bollinger Band squeeze detection
        bb_squeeze = bb_width < self._percentile_value(
            [self._calculate_bb_width(closes[i-20:i], 20, 2)
             for i in range(20, len(closes), 5)],
            self.thresholds['bb_squeeze_percentile']
        ) if len(closes) >= 40 else False

        return {
            'adx': adx,
            'rsi': rsi,
            'atr': atr,
            'bb_width': bb_width,
            'bb_squeeze': bb_squeeze,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'trend_strength': trend_strength,
            'volatility_percentile': volatility_percentile,
            'momentum_score': momentum_score,
            'volume_profile': volume_profile,
            'key_levels': key_levels,
            'price_above_50ema': current_price > ema_50,
            'price_above_20ema': current_price > ema_20,
            'ema_20_above_50': ema_20 > ema_50
        }

    def _classify_regime(
        self,
        indicators: Dict[str, Any]
    ) -> Tuple[MarketRegime, float, List[str]]:
        """
        Classify market regime based on calculated indicators.

        Returns:
            (regime, confidence, reasoning)
        """
        reasoning = []
        confidence_factors = []

        adx = indicators['adx']
        rsi = indicators['rsi']
        vol_percentile = indicators['volatility_percentile']
        trend_strength = indicators['trend_strength']
        volume_profile = indicators['volume_profile']
        bb_squeeze = indicators['bb_squeeze']
        price_above_50ema = indicators['price_above_50ema']
        ema_20_above_50 = indicators['ema_20_above_50']

        # Check for extreme conditions first

        # CAPITULATION: RSI extreme low + high volume + below EMAs
        if rsi < self.thresholds['rsi_extreme_fear'] and volume_profile in ['high', 'climax']:
            reasoning.append(f"RSI at extreme fear ({rsi:.1f})")
            reasoning.append(f"Volume profile: {volume_profile}")
            confidence_factors.append(85)
            return MarketRegime.CAPITULATION, sum(confidence_factors) / len(confidence_factors), reasoning

        # EUPHORIA: RSI extreme high + high volume + above EMAs
        if rsi > self.thresholds['rsi_extreme_greed'] and volume_profile in ['high', 'climax']:
            reasoning.append(f"RSI at extreme greed ({rsi:.1f})")
            reasoning.append(f"Volume profile: {volume_profile}")
            confidence_factors.append(85)
            return MarketRegime.EUPHORIA, sum(confidence_factors) / len(confidence_factors), reasoning

        # BREAKOUT_POTENTIAL: BB squeeze + consolidation
        if bb_squeeze and adx < self.thresholds['adx_trending']:
            reasoning.append("Bollinger Band squeeze detected")
            reasoning.append(f"ADX showing consolidation ({adx:.1f})")
            confidence_factors.append(75)
            return MarketRegime.BREAKOUT_POTENTIAL, sum(confidence_factors) / len(confidence_factors), reasoning

        # TRENDING conditions
        if adx > self.thresholds['adx_trending']:
            confidence_factors.append(min(adx * 2, 95))

            if adx > self.thresholds['adx_strong_trend']:
                reasoning.append(f"Strong trend (ADX: {adx:.1f})")
            else:
                reasoning.append(f"Moderate trend (ADX: {adx:.1f})")

            # Determine direction
            if price_above_50ema and ema_20_above_50:
                reasoning.append("Price and EMAs aligned bullish")
                return MarketRegime.TRENDING_BULLISH, sum(confidence_factors) / len(confidence_factors), reasoning
            elif not price_above_50ema and not ema_20_above_50:
                reasoning.append("Price and EMAs aligned bearish")
                return MarketRegime.TRENDING_BEARISH, sum(confidence_factors) / len(confidence_factors), reasoning

        # CHOPPY conditions (no strong trend)
        reasoning.append(f"No strong trend (ADX: {adx:.1f})")

        if vol_percentile > self.thresholds['volatility_high']:
            reasoning.append(f"High volatility ({vol_percentile:.0f} percentile)")
            confidence_factors.append(70)
            return MarketRegime.CHOPPY_VOLATILE, sum(confidence_factors) / len(confidence_factors), reasoning
        elif vol_percentile < self.thresholds['volatility_low']:
            reasoning.append(f"Low volatility ({vol_percentile:.0f} percentile)")
            confidence_factors.append(70)
            return MarketRegime.CHOPPY_CALM, sum(confidence_factors) / len(confidence_factors), reasoning
        else:
            reasoning.append(f"Normal volatility ({vol_percentile:.0f} percentile)")
            confidence_factors.append(60)
            # Default to volatile if in middle range
            return MarketRegime.CHOPPY_VOLATILE, sum(confidence_factors) / len(confidence_factors), reasoning

    # ==================== Technical Indicator Calculations ====================

    def _calculate_adx(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> float:
        """Calculate Average Directional Index"""
        if len(closes) < period + 1:
            return 0

        # Calculate True Range and Directional Movement
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []

        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)

            plus_dm = max(highs[i] - highs[i-1], 0) if highs[i] - highs[i-1] > lows[i-1] - lows[i] else 0
            minus_dm = max(lows[i-1] - lows[i], 0) if lows[i-1] - lows[i] > highs[i] - highs[i-1] else 0

            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)

        # Smooth with EMA
        atr = self._calculate_ema(tr_list, period)
        smooth_plus_dm = self._calculate_ema(plus_dm_list, period)
        smooth_minus_dm = self._calculate_ema(minus_dm_list, period)

        # Calculate DI
        plus_di = (smooth_plus_dm / atr * 100) if atr > 0 else 0
        minus_di = (smooth_minus_dm / atr * 100) if atr > 0 else 0

        # Calculate DX and ADX
        dx_sum = abs(plus_di - minus_di)
        dx_total = plus_di + minus_di
        dx = (dx_sum / dx_total * 100) if dx_total > 0 else 0

        return dx

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(closes) < period + 1:
            return 50

        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> float:
        """Calculate Average True Range"""
        if len(closes) < 2:
            return 0

        tr_list = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)

        return sum(tr_list[-period:]) / min(len(tr_list), period)

    def _calculate_bb_width(
        self,
        closes: List[float],
        period: int = 20,
        std_dev: float = 2
    ) -> float:
        """Calculate Bollinger Band width"""
        if len(closes) < period:
            return 0

        sma = sum(closes[-period:]) / period
        variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
        std = variance ** 0.5

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        width = ((upper - lower) / sma) * 100 if sma > 0 else 0
        return width

    def _calculate_ema(self, data: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0

        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period  # Start with SMA

        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def _calculate_sma(self, data: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        return sum(data[-period:]) / period

    def _percentile_rank(self, value: float, data: List[float]) -> float:
        """Calculate percentile rank of value in data"""
        if not data:
            return 50
        count_below = sum(1 for d in data if d < value)
        return (count_below / len(data)) * 100

    def _percentile_value(self, data: List[float], percentile: float) -> float:
        """Get value at given percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(idx, len(sorted_data) - 1)]

    def get_regime_distribution(self, hours: int = 24) -> Dict[str, float]:
        """Get distribution of regimes over past N hours"""
        # Calculate how many entries correspond to the time period
        entries_per_hour = 12  # 5-minute intervals
        count = min(hours * entries_per_hour, len(self.regime_history))

        if count == 0:
            return {}

        recent = self.regime_history[-count:]
        distribution = {}

        for analysis in recent:
            regime_name = analysis.regime.value
            distribution[regime_name] = distribution.get(regime_name, 0) + 1

        # Convert to percentages
        for regime in distribution:
            distribution[regime] = (distribution[regime] / count) * 100

        return distribution

    def get_current_regime(self) -> Optional[RegimeAnalysis]:
        """Get the current regime analysis"""
        return self.current_regime


# Singleton instance
_detector_instance: Optional[MarketRegimeDetector] = None


def get_regime_detector() -> MarketRegimeDetector:
    """Get or create the global MarketRegimeDetector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MarketRegimeDetector()
    return _detector_instance


if __name__ == "__main__":
    # Test the regime detector with synthetic data
    import random

    logging.basicConfig(level=logging.INFO)

    detector = MarketRegimeDetector()

    # Generate synthetic trending data
    base_price = 95000
    ohlcv_data = []

    for i in range(100):
        # Simulate uptrend
        trend = i * 50  # Rising trend
        noise = random.uniform(-200, 200)
        close = base_price + trend + noise

        ohlcv_data.append({
            'open': close - random.uniform(-100, 100),
            'high': close + random.uniform(0, 300),
            'low': close - random.uniform(0, 300),
            'close': close,
            'volume': random.uniform(100, 1000),
            'timestamp': datetime.utcnow().isoformat()
        })

    # Analyze regime
    analysis = detector.analyze(ohlcv_data, "BTC/USD")

    print("\n=== REGIME ANALYSIS ===")
    print(f"Regime: {analysis.regime.value}")
    print(f"Confidence: {analysis.confidence:.1f}%")
    print(f"Trend Strength: {analysis.trend_strength:.1f}")
    print(f"Volatility: {analysis.volatility_percentile:.0f} percentile")
    print(f"Momentum: {analysis.momentum_score:.1f}")
    print(f"Volume Profile: {analysis.volume_profile}")
    print("\nReasoning:")
    for reason in analysis.reasoning:
        print(f"  - {reason}")

    print("\nMarketRegimeDetector test complete!")

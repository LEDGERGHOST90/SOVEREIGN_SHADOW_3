#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Market Regime Detector
Classifies market conditions for strategy selection

Market Regimes:
- trending_bull: Strong uptrend, momentum strategies work best
- trending_bear: Strong downtrend, short or wait strategies
- choppy_volatile: Range-bound with high volatility, mean reversion works
- choppy_calm: Range-bound with low volatility, breakout preparation

Detection uses multiple indicators:
- ADX for trend strength
- ATR for volatility
- Price vs moving averages
- RSI for momentum

Author: SovereignShadow Trading System
"""

import numpy as np
import pandas as pd
import logging
from enum import Enum
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class MarketRegime(str, Enum):
    """Market regime classification"""
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    CHOPPY_VOLATILE = "choppy_volatile"
    CHOPPY_CALM = "choppy_calm"
    UNKNOWN = "unknown"


@dataclass
class RegimeAnalysis:
    """Detailed regime analysis result"""
    regime: MarketRegime
    confidence: float  # 0-100
    
    # Underlying indicators
    adx: float  # Average Directional Index
    plus_di: float  # +DI
    minus_di: float  # -DI
    atr_percent: float  # ATR as % of price
    rsi: float
    trend_direction: int  # 1 = up, -1 = down, 0 = neutral
    volatility_percentile: float  # vs historical
    
    # Strategy recommendations
    recommended_strategies: list
    avoid_strategies: list
    
    metadata: Dict[str, Any]


class RegimeDetector:
    """
    Market Regime Detection Engine
    
    Uses multiple technical indicators to classify market conditions
    into one of four regimes, each suited for different strategy types.
    """
    
    # Thresholds for regime classification
    ADX_TREND_THRESHOLD = 25  # ADX > 25 = trending market
    VOLATILITY_HIGH_PERCENTILE = 70  # Top 30% = high volatility
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # Strategy mappings per regime
    REGIME_STRATEGIES = {
        MarketRegime.TRENDING_BULL: [
            "TrendFollowEMA", "MomentumScalp", "BreakoutRetest",
            "ParabolicSAR", "ADXTrendFilter", "IchimokuCloud"
        ],
        MarketRegime.TRENDING_BEAR: [
            "RSIReversion", "BollingerBounce", "FibonacciRetracement",
            "SupportResistanceBounce", "DivergenceScalp"
        ],
        MarketRegime.CHOPPY_VOLATILE: [
            "ElderReversion", "BandedStochastic", "StochasticCrossover",
            "MACDDivergence", "VWAPMeanReversion", "KeltnerChannelBreakout"
        ],
        MarketRegime.CHOPPY_CALM: [
            "VolatilityBreakout", "DonchianChannel", "ATRVolatilityBreakout",
            "OpeningRangeBreakout", "DynamicCrossfire"
        ]
    }
    
    AVOID_STRATEGIES = {
        MarketRegime.TRENDING_BULL: ["ElderReversion", "VWAPMeanReversion"],
        MarketRegime.TRENDING_BEAR: ["TrendFollowEMA", "MomentumScalp"],
        MarketRegime.CHOPPY_VOLATILE: ["TrendFollowEMA", "BreakoutRetest"],
        MarketRegime.CHOPPY_CALM: ["MomentumScalp", "ElderReversion"]
    }
    
    def __init__(self, lookback_period: int = 100):
        """
        Initialize regime detector
        
        Args:
            lookback_period: Number of candles for indicator calculation
        """
        self.lookback_period = lookback_period
        self.volatility_history = []  # For percentile calculation
        
        logger.info(f"🔍 Regime Detector initialized (lookback={lookback_period})")
    
    def detect_regime(self, df: pd.DataFrame) -> RegimeAnalysis:
        """
        Detect current market regime from OHLCV data
        
        Args:
            df: DataFrame with columns: open, high, low, close, volume
                Must have at least `lookback_period` rows
        
        Returns:
            RegimeAnalysis with classification and metrics
        """
        if len(df) < self.lookback_period:
            logger.warning(f"⚠️  Insufficient data: {len(df)} < {self.lookback_period}")
            return self._unknown_regime()
        
        # Calculate indicators
        adx, plus_di, minus_di = self._calculate_adx(df)
        atr_percent = self._calculate_atr_percent(df)
        rsi = self._calculate_rsi(df)
        trend_direction = self._calculate_trend_direction(df)
        volatility_percentile = self._get_volatility_percentile(atr_percent)
        
        # Store volatility for historical comparison
        self._update_volatility_history(atr_percent)
        
        # Classify regime
        regime, confidence = self._classify_regime(
            adx, plus_di, minus_di, atr_percent, rsi, trend_direction, volatility_percentile
        )
        
        # Get recommendations
        recommended = self.REGIME_STRATEGIES.get(regime, [])
        avoid = self.AVOID_STRATEGIES.get(regime, [])
        
        analysis = RegimeAnalysis(
            regime=regime,
            confidence=confidence,
            adx=round(adx, 2),
            plus_di=round(plus_di, 2),
            minus_di=round(minus_di, 2),
            atr_percent=round(atr_percent, 4),
            rsi=round(rsi, 2),
            trend_direction=trend_direction,
            volatility_percentile=round(volatility_percentile, 1),
            recommended_strategies=recommended,
            avoid_strategies=avoid,
            metadata={
                'candles_analyzed': len(df),
                'last_close': float(df['close'].iloc[-1]),
                'timestamp': str(df.index[-1]) if hasattr(df.index[-1], 'isoformat') else str(df.index[-1])
            }
        )
        
        logger.info(f"📊 Regime: {regime.value} (confidence={confidence:.1f}%)")
        
        return analysis
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Tuple[float, float, float]:
        """Calculate ADX, +DI, -DI"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        plus_dm[(plus_dm > minus_dm) == False] = 0
        minus_dm[(minus_dm > plus_dm) == False] = 0
        
        # Smoothed DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return (
            float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0,
            float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 0,
            float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 0
        )
    
    def _calculate_atr_percent(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate ATR as percentage of price"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        current_price = close.iloc[-1]
        
        return (atr / current_price) * 100
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI"""
        delta = df['close'].diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
    
    def _calculate_trend_direction(self, df: pd.DataFrame) -> int:
        """
        Calculate trend direction using multiple MAs
        
        Returns:
            1 = bullish, -1 = bearish, 0 = neutral
        """
        close = df['close']
        
        # Short, medium, long EMAs
        ema_20 = close.ewm(span=20).mean().iloc[-1]
        ema_50 = close.ewm(span=50).mean().iloc[-1]
        ema_100 = close.ewm(span=100).mean().iloc[-1] if len(close) >= 100 else close.mean()
        
        current_price = close.iloc[-1]
        
        # Count bullish signals
        bullish_signals = 0
        if current_price > ema_20:
            bullish_signals += 1
        if ema_20 > ema_50:
            bullish_signals += 1
        if ema_50 > ema_100:
            bullish_signals += 1
        
        if bullish_signals >= 2:
            return 1
        elif bullish_signals <= 0:
            return -1
        else:
            return 0
    
    def _get_volatility_percentile(self, current_atr_pct: float) -> float:
        """Get percentile ranking of current volatility"""
        if not self.volatility_history:
            return 50.0  # Default to median
        
        sorted_history = sorted(self.volatility_history)
        rank = sum(1 for v in sorted_history if v <= current_atr_pct)
        
        return (rank / len(sorted_history)) * 100
    
    def _update_volatility_history(self, atr_percent: float):
        """Update volatility history for percentile calculation"""
        self.volatility_history.append(atr_percent)
        
        # Keep last 500 readings
        if len(self.volatility_history) > 500:
            self.volatility_history = self.volatility_history[-500:]
    
    def _classify_regime(
        self,
        adx: float,
        plus_di: float,
        minus_di: float,
        atr_percent: float,
        rsi: float,
        trend_direction: int,
        volatility_percentile: float
    ) -> Tuple[MarketRegime, float]:
        """
        Classify regime based on indicators
        
        Returns:
            (regime, confidence)
        """
        is_trending = adx > self.ADX_TREND_THRESHOLD
        is_high_volatility = volatility_percentile > self.VOLATILITY_HIGH_PERCENTILE
        
        # Calculate base confidence from ADX strength
        if is_trending:
            # Strong trend = higher confidence
            adx_confidence = min((adx - 20) * 2, 40)  # Max 40 from ADX
        else:
            # Choppy = confidence based on how low ADX is
            adx_confidence = min((30 - adx), 30)  # Max 30 from low ADX
        
        # Determine regime
        if is_trending:
            if trend_direction > 0 or plus_di > minus_di:
                regime = MarketRegime.TRENDING_BULL
                # Add confidence from RSI not being oversold
                rsi_bonus = 20 if rsi > 40 else 10
            else:
                regime = MarketRegime.TRENDING_BEAR
                # Add confidence from RSI not being overbought
                rsi_bonus = 20 if rsi < 60 else 10
        else:
            if is_high_volatility:
                regime = MarketRegime.CHOPPY_VOLATILE
                # Higher volatility = more confidence in this classification
                rsi_bonus = min(volatility_percentile - 50, 30)
            else:
                regime = MarketRegime.CHOPPY_CALM
                # Lower volatility = more confidence
                rsi_bonus = min(70 - volatility_percentile, 30)
        
        # Calculate final confidence (cap at 95%)
        confidence = min(adx_confidence + rsi_bonus + 30, 95)
        
        return regime, confidence
    
    def _unknown_regime(self) -> RegimeAnalysis:
        """Return unknown regime when data is insufficient"""
        return RegimeAnalysis(
            regime=MarketRegime.UNKNOWN,
            confidence=0,
            adx=0,
            plus_di=0,
            minus_di=0,
            atr_percent=0,
            rsi=50,
            trend_direction=0,
            volatility_percentile=50,
            recommended_strategies=[],
            avoid_strategies=[],
            metadata={'error': 'Insufficient data'}
        )
    
    def get_regime_summary(self, analysis: RegimeAnalysis) -> str:
        """Get human-readable summary of regime analysis"""
        return f"""
📊 Market Regime Analysis
========================
Regime: {analysis.regime.value.upper()}
Confidence: {analysis.confidence:.1f}%

Indicators:
  ADX: {analysis.adx} (trend strength)
  +DI: {analysis.plus_di} / -DI: {analysis.minus_di}
  ATR%: {analysis.atr_percent:.2f}%
  RSI: {analysis.rsi}
  Trend: {'↑ Bullish' if analysis.trend_direction > 0 else '↓ Bearish' if analysis.trend_direction < 0 else '→ Neutral'}
  Volatility: {analysis.volatility_percentile:.0f}th percentile

Recommended Strategies:
  {', '.join(analysis.recommended_strategies[:5]) if analysis.recommended_strategies else 'None'}

Avoid:
  {', '.join(analysis.avoid_strategies) if analysis.avoid_strategies else 'None'}
"""


# Example usage and testing
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='1h')
    
    # Simulated trending market
    base_price = 100000
    trend = np.cumsum(np.random.randn(200) * 500 + 50)  # Slight upward bias
    
    df = pd.DataFrame({
        'open': base_price + trend + np.random.randn(200) * 100,
        'high': base_price + trend + abs(np.random.randn(200)) * 200,
        'low': base_price + trend - abs(np.random.randn(200)) * 200,
        'close': base_price + trend + np.random.randn(200) * 100,
        'volume': np.random.randint(100, 1000, 200)
    }, index=dates)
    
    # Make sure high/low are correct
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    # Detect regime
    detector = RegimeDetector()
    analysis = detector.detect_regime(df)
    
    print(detector.get_regime_summary(analysis))

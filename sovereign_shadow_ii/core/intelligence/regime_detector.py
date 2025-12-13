#!/usr/bin/env python3
"""
Market Regime Detector - DIRECTIVE LAYER

Classifies market conditions into regimes:
- trending_bullish: Strong uptrend
- trending_bearish: Strong downtrend  
- choppy_volatile: Range-bound with high volatility
- choppy_calm: Range-bound with low volatility
- breakout: Breaking out of range
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime classifications"""
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    CHOPPY_VOLATILE = "choppy_volatile"
    CHOPPY_CALM = "choppy_calm"
    BREAKOUT = "breakout"
    UNKNOWN = "unknown"


@dataclass
class RegimeAnalysis:
    """Market regime analysis result"""
    regime: MarketRegime
    confidence: float  # 0-100
    indicators: Dict[str, float]
    timestamp: datetime
    reasoning: str


class MarketRegimeDetector:
    """
    Detects market regime using multiple indicators:
    
    1. Trend strength (ADX, EMA alignment)
    2. Volatility (ATR, Bollinger Band width)
    3. Price action (Higher highs/lows, support/resistance)
    """
    
    def __init__(
        self,
        adx_threshold: float = 25.0,
        volatility_threshold: float = 0.02,
        trend_ema_periods: List[int] = [21, 50, 200]
    ):
        """
        Initialize regime detector
        
        Args:
            adx_threshold: ADX above this = trending
            volatility_threshold: ATR % above this = volatile
            trend_ema_periods: EMA periods for trend detection
        """
        self.adx_threshold = adx_threshold
        self.volatility_threshold = volatility_threshold
        self.trend_ema_periods = trend_ema_periods
    
    def detect_regime(self, df: pd.DataFrame) -> RegimeAnalysis:
        """
        Detect current market regime
        
        Args:
            df: OHLCV dataframe with columns: open, high, low, close, volume
        
        Returns:
            RegimeAnalysis: Detected regime with confidence and reasoning
        """
        # Calculate indicators
        indicators = self._calculate_indicators(df)
        
        # Determine regime
        regime, confidence, reasoning = self._classify_regime(indicators)
        
        return RegimeAnalysis(
            regime=regime,
            confidence=confidence,
            indicators=indicators,
            timestamp=datetime.now(),
            reasoning=reasoning
        )
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators for regime detection"""
        indicators = {}
        
        # 1. ADX (Trend Strength)
        adx = self._calculate_adx(df)
        indicators['adx'] = adx
        
        # 2. ATR (Volatility)
        atr = self._calculate_atr(df)
        atr_percent = (atr / df['close'].iloc[-1]) * 100
        indicators['atr'] = atr
        indicators['atr_percent'] = atr_percent
        
        # 3. EMA Alignment (Trend Direction)
        emas = {}
        for period in self.trend_ema_periods:
            emas[period] = df['close'].ewm(span=period).mean().iloc[-1]
        
        current_price = df['close'].iloc[-1]
        
        # Check if price is above/below EMAs
        above_ema_21 = current_price > emas[21]
        above_ema_50 = current_price > emas[50]
        above_ema_200 = current_price > emas[200]
        
        # EMA alignment score: +3 = all bullish, -3 = all bearish
        ema_score = 0
        if above_ema_21:
            ema_score += 1
        else:
            ema_score -= 1
        
        if above_ema_50:
            ema_score += 1
        else:
            ema_score -= 1
        
        if above_ema_200:
            ema_score += 1
        else:
            ema_score -= 1
        
        indicators['ema_alignment'] = ema_score
        indicators['ema_21'] = emas[21]
        indicators['ema_50'] = emas[50]
        indicators['ema_200'] = emas[200]
        
        # 4. RSI (Overbought/Oversold)
        rsi = self._calculate_rsi(df)
        indicators['rsi'] = rsi
        
        # 5. Bollinger Band Width (Volatility measure)
        bb_width = self._calculate_bb_width(df)
        indicators['bb_width'] = bb_width
        
        # 6. Price momentum (ROC - Rate of Change)
        roc = ((df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]) * 100
        indicators['roc_20'] = roc
        
        return indicators
    
    def _classify_regime(self, indicators: Dict[str, float]) -> tuple:
        """
        Classify market regime based on indicators
        
        Returns:
            (regime, confidence, reasoning)
        """
        adx = indicators['adx']
        atr_percent = indicators['atr_percent']
        ema_alignment = indicators['ema_alignment']
        rsi = indicators['rsi']
        roc = indicators['roc_20']
        
        # TRENDING BULLISH
        # - Strong ADX (>25)
        # - Price above EMAs (ema_alignment > 0)
        # - Positive momentum (ROC > 0)
        if adx > self.adx_threshold and ema_alignment >= 2 and roc > 0:
            confidence = min(adx + abs(ema_alignment * 10) + roc, 100)
            return (
                MarketRegime.TRENDING_BULLISH,
                confidence,
                f"Strong uptrend: ADX={adx:.1f}, EMA alignment={ema_alignment}, ROC={roc:.1f}%"
            )
        
        # TRENDING BEARISH
        # - Strong ADX (>25)
        # - Price below EMAs (ema_alignment < 0)
        # - Negative momentum (ROC < 0)
        if adx > self.adx_threshold and ema_alignment <= -2 and roc < 0:
            confidence = min(adx + abs(ema_alignment * 10) + abs(roc), 100)
            return (
                MarketRegime.TRENDING_BEARISH,
                confidence,
                f"Strong downtrend: ADX={adx:.1f}, EMA alignment={ema_alignment}, ROC={roc:.1f}%"
            )
        
        # CHOPPY VOLATILE
        # - Weak ADX (<25)
        # - High ATR (>2%)
        # - Mixed EMA signals
        if adx < self.adx_threshold and atr_percent > self.volatility_threshold:
            confidence = min((1 - adx/50) * 100 + atr_percent * 20, 100)
            return (
                MarketRegime.CHOPPY_VOLATILE,
                confidence,
                f"Range-bound volatile: ADX={adx:.1f}, ATR={atr_percent:.2f}%"
            )
        
        # CHOPPY CALM
        # - Weak ADX (<25)
        # - Low ATR (<2%)
        # - Mixed EMA signals
        if adx < self.adx_threshold and atr_percent <= self.volatility_threshold:
            confidence = min((1 - adx/50) * 100, 100)
            return (
                MarketRegime.CHOPPY_CALM,
                confidence,
                f"Range-bound calm: ADX={adx:.1f}, ATR={atr_percent:.2f}%"
            )
        
        # BREAKOUT
        # - Moderate ADX (20-30)
        # - RSI extreme (>70 or <30)
        # - High momentum
        if 20 < adx < 30 and (rsi > 70 or rsi < 30) and abs(roc) > 5:
            confidence = min(abs(roc) * 5 + (100 - abs(50 - rsi)), 100)
            direction = "bullish" if roc > 0 else "bearish"
            return (
                MarketRegime.BREAKOUT,
                confidence,
                f"Breakout {direction}: ADX={adx:.1f}, RSI={rsi:.1f}, ROC={roc:.1f}%"
            )
        
        # UNKNOWN - couldn't clearly classify
        return (
            MarketRegime.UNKNOWN,
            30.0,
            f"Mixed signals: ADX={adx:.1f}, EMA={ema_alignment}, ATR={atr_percent:.2f}%"
        )
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average Directional Index (trend strength)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Calculate +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate smoothed +DI and -DI
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 20.0
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range (volatility)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.0
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_bb_width(self, df: pd.DataFrame, period: int = 20, std: int = 2) -> float:
        """Calculate Bollinger Band Width (volatility)"""
        sma = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)
        
        bb_width = ((upper_band - lower_band) / sma) * 100
        return bb_width.iloc[-1] if not pd.isna(bb_width.iloc[-1]) else 5.0


def test_regime_detector():
    """Test regime detector with sample data"""
    print("\n" + "="*70)
    print("🧪 TESTING MARKET REGIME DETECTOR")
    print("="*70)
    
    # Create sample trending bullish data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    
    # Trending data
    trend = np.linspace(90000, 100000, 100)
    noise = np.random.normal(0, 500, 100)
    close_prices = trend + noise
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices - 100,
        'high': close_prices + 200,
        'low': close_prices - 200,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # Test detector
    detector = MarketRegimeDetector()
    result = detector.detect_regime(df)
    
    print(f"\n📊 Regime Detected: {result.regime.value}")
    print(f"   Confidence: {result.confidence:.1f}%")
    print(f"   Reasoning: {result.reasoning}")
    print(f"\n🔍 Indicators:")
    for key, value in result.indicators.items():
        print(f"   {key}: {value:.2f}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_regime_detector()

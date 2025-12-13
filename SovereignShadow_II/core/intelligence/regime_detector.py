"""
Market Regime Detector
Classifies market conditions into regimes for strategy selection
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Market Regime Detector
    Classifies market into regimes: trending_up, trending_down, choppy_volatile, choppy_calm
    """
    
    def __init__(self, performance_tracker=None):
        """
        Initialize regime detector
        
        Args:
            performance_tracker: Optional PerformanceTracker instance for logging
        """
        self.performance_tracker = performance_tracker
        self.current_regime = None
        self.last_detection = None
    
    def detect_regime(
        self,
        price_data: pd.DataFrame,
        timeframe: str = '15m'
    ) -> Dict[str, Any]:
        """
        Detect current market regime from price data
        
        Args:
            price_data: DataFrame with columns: timestamp, open, high, low, close, volume
            timeframe: Timeframe string (e.g., '15m', '1h')
        
        Returns:
            Dictionary with regime, confidence, and indicators
        """
        if len(price_data) < 100:
            logger.warning("Insufficient data for regime detection")
            return {
                'regime': 'choppy_calm',
                'confidence': 0.5,
                'indicators': {}
            }
        
        # Calculate indicators
        indicators = self._calculate_indicators(price_data)
        
        # Classify regime
        regime, confidence = self._classify_regime(indicators)
        
        result = {
            'regime': regime,
            'confidence': confidence,
            'indicators': indicators,
            'timestamp': datetime.now()
        }
        
        self.current_regime = regime
        self.last_detection = result
        
        # Log regime detection
        if self.performance_tracker:
            self.performance_tracker.log_regime(
                regime, confidence, indicators
            )
        
        logger.info(f"📊 Market regime detected: {regime} (confidence: {confidence:.2%})")
        
        return result
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators for regime detection"""
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # Trend indicators
        ema_20 = close.ewm(span=20).mean()
        ema_50 = close.ewm(span=50).mean()
        ema_200 = close.ewm(span=200).mean() if len(df) >= 200 else ema_50
        
        # Price position relative to EMAs
        price_above_ema20 = (close.iloc[-1] > ema_20.iloc[-1])
        price_above_ema50 = (close.iloc[-1] > ema_50.iloc[-1])
        ema20_above_ema50 = (ema_20.iloc[-1] > ema_50.iloc[-1])
        
        # Volatility (ATR)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        atr_percent = (atr / close.iloc[-1]) * 100
        
        # Volatility regime
        avg_atr = tr.rolling(window=50).mean().iloc[-1]
        avg_atr_percent = (avg_atr / close.iloc[-1]) * 100
        is_volatile = atr_percent > avg_atr_percent * 1.2
        
        # RSI for momentum
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # ADX for trend strength
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr_smooth = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / tr_smooth)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / tr_smooth)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=14).mean().iloc[-1]
        
        # Volume trend
        volume_ma = volume.rolling(window=20).mean().iloc[-1]
        volume_ratio = volume.iloc[-1] / volume_ma if volume_ma > 0 else 1.0
        
        # Price range (choppiness)
        price_range = (high.rolling(window=20).max() - low.rolling(window=20).min()).iloc[-1]
        price_range_percent = (price_range / close.iloc[-1]) * 100
        
        return {
            'price_above_ema20': price_above_ema20,
            'price_above_ema50': price_above_ema50,
            'ema20_above_ema50': ema20_above_ema50,
            'atr_percent': atr_percent,
            'is_volatile': is_volatile,
            'rsi': current_rsi,
            'adx': adx,
            'volume_ratio': volume_ratio,
            'price_range_percent': price_range_percent
        }
    
    def _classify_regime(self, indicators: Dict[str, Any]) -> tuple:
        """
        Classify regime based on indicators
        
        Returns:
            Tuple of (regime_name, confidence)
        """
        # Trend strength threshold
        strong_trend_threshold = 25.0  # ADX > 25 = strong trend
        
        # Determine trend direction
        is_uptrend = (
            indicators['price_above_ema20'] and
            indicators['price_above_ema50'] and
            indicators['ema20_above_ema50']
        )
        
        is_downtrend = (
            not indicators['price_above_ema20'] and
            not indicators['price_above_ema50'] and
            not indicators['ema20_above_ema50']
        )
        
        # Strong trend
        if indicators['adx'] > strong_trend_threshold:
            if is_uptrend:
                confidence = min(0.7 + (indicators['adx'] / 100), 0.95)
                return ('trending_up', confidence)
            elif is_downtrend:
                confidence = min(0.7 + (indicators['adx'] / 100), 0.95)
                return ('trending_down', confidence)
        
        # Choppy market (low ADX)
        if indicators['adx'] < 20:
            if indicators['is_volatile']:
                confidence = 0.6 + (indicators['atr_percent'] / 10) * 0.1
                confidence = min(confidence, 0.85)
                return ('choppy_volatile', confidence)
            else:
                confidence = 0.5 + (1 - indicators['atr_percent'] / 5) * 0.2
                confidence = min(confidence, 0.75)
                return ('choppy_calm', confidence)
        
        # Weak trend (transitional)
        if is_uptrend:
            return ('trending_up', 0.55)
        elif is_downtrend:
            return ('trending_down', 0.55)
        else:
            # Sideways
            if indicators['is_volatile']:
                return ('choppy_volatile', 0.6)
            else:
                return ('choppy_calm', 0.6)
    
    def get_current_regime(self) -> Optional[str]:
        """Get current detected regime"""
        return self.current_regime

"""
Market Filters Module
=====================
Implements research-backed market sentiment and macro filters (2024-2025).

Filters:
1. Fear & Greed Index (FGI) - Sentiment gauge from alternative.me
2. DXY Correlation - Dollar strength as macro trend filter

Author: SOVEREIGN_SHADOW_3
Created: 2025-12-14
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Signal(Enum):
    """Trading signal types"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class MarketFilters:
    """
    Market sentiment and macro filters for trading decisions.

    Features:
    - Fear & Greed Index monitoring (alternative.me API)
    - DXY correlation analysis
    - Combined multi-factor signals
    - Smart caching to minimize API calls

    Research basis:
    - FGI > 80 sell signal = 50% more profit over 90 days (backtested)
    - BTC/DXY correlation: -0.4 to -0.8 over 5-year periods
    """

    # API endpoints
    FGI_API = "https://api.alternative.me/fng/"
    FGI_HISTORY_API = "https://api.alternative.me/fng/?limit={}"

    # FGI thresholds (0-100 scale)
    FGI_EXTREME_FEAR = 25
    FGI_FEAR = 45
    FGI_NEUTRAL_LOW = 45
    FGI_NEUTRAL_HIGH = 55
    FGI_GREED = 75
    FGI_EXTREME_GREED = 80  # Backtested sell signal

    # Cache settings
    CACHE_DURATION_SECONDS = 3600  # 1 hour for FGI (updates daily)
    DXY_CACHE_DURATION = 1800  # 30 minutes for DXY

    def __init__(self):
        """Initialize market filters with caching"""
        self._fgi_cache: Optional[Dict] = None
        self._fgi_cache_time: Optional[float] = None
        self._dxy_cache: Optional[Dict] = None
        self._dxy_cache_time: Optional[float] = None

        logger.info("MarketFilters initialized")

    def get_fear_greed(self, use_cache: bool = True) -> Dict:
        """
        Get Fear & Greed Index from alternative.me API.

        Args:
            use_cache: Use cached data if available and fresh

        Returns:
            Dict with:
                - value: FGI value (0-100)
                - classification: Text classification
                - signal: BULLISH/BEARISH/NEUTRAL
                - confidence: Signal confidence (0-100)
                - timestamp: Data timestamp
                - source: API source

        Example:
            {
                'value': 82,
                'classification': 'Extreme Greed',
                'signal': 'BEARISH',
                'confidence': 85,
                'timestamp': '2025-12-14 10:00:00',
                'source': 'alternative.me'
            }
        """
        # Check cache
        if use_cache and self._is_fgi_cache_valid():
            logger.info("Using cached Fear & Greed data")
            return self._fgi_cache

        try:
            # Fetch from API
            response = requests.get(self.FGI_API, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'data' not in data or len(data['data']) == 0:
                raise ValueError("Invalid API response structure")

            fgi_data = data['data'][0]
            fgi_value = int(fgi_data['value'])
            fgi_classification = fgi_data['value_classification']

            # Generate signal based on research thresholds
            signal, confidence = self._interpret_fgi(fgi_value)

            result = {
                'value': fgi_value,
                'classification': fgi_classification,
                'signal': signal.value,
                'confidence': confidence,
                'timestamp': datetime.fromtimestamp(int(fgi_data['timestamp'])).strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'alternative.me',
                'note': 'CFGI.io offers 15-min updates for 52+ tokens'
            }

            # Update cache
            self._fgi_cache = result
            self._fgi_cache_time = time.time()

            logger.info(f"FGI: {fgi_value} ({fgi_classification}) -> {signal.value} (confidence: {confidence}%)")

            return result

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Fear & Greed Index: {e}")
            return self._get_fallback_fgi()
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse Fear & Greed data: {e}")
            return self._get_fallback_fgi()

    def _interpret_fgi(self, value: int) -> Tuple[Signal, int]:
        """
        Interpret FGI value into trading signal.

        Research-based thresholds:
        - < 25: Extreme Fear (BUY opportunity)
        - 25-45: Fear (slight BULLISH)
        - 45-55: Neutral
        - 55-75: Greed (slight BEARISH)
        - > 75: Extreme Greed (SELL signal)
        - > 80: Strong SELL (backtested: 50% more profit)

        Args:
            value: FGI value (0-100)

        Returns:
            Tuple of (Signal, confidence_percentage)
        """
        if value < self.FGI_EXTREME_FEAR:
            # Extreme Fear - Strong buy signal
            confidence = min(100, int((self.FGI_EXTREME_FEAR - value) * 3 + 70))
            return Signal.BULLISH, confidence

        elif value < self.FGI_FEAR:
            # Fear - Moderate buy signal
            confidence = min(70, int((self.FGI_FEAR - value) * 2 + 50))
            return Signal.BULLISH, confidence

        elif value < self.FGI_NEUTRAL_HIGH:
            # Neutral zone
            return Signal.NEUTRAL, 50

        elif value < self.FGI_GREED:
            # Greed - Moderate sell signal
            confidence = min(70, int((value - self.FGI_NEUTRAL_HIGH) * 2 + 50))
            return Signal.BEARISH, confidence

        elif value < self.FGI_EXTREME_GREED:
            # High Greed - Strong sell signal
            confidence = min(85, int((value - self.FGI_GREED) * 3 + 60))
            return Signal.BEARISH, confidence

        else:
            # Extreme Greed (> 80) - Research-backed sell signal
            confidence = min(100, int((value - self.FGI_EXTREME_GREED) * 2 + 85))
            return Signal.BEARISH, confidence

    def get_dxy_signal(self, use_cache: bool = True) -> Dict:
        """
        Get DXY (Dollar Index) correlation signal.

        Research: BTC shows -0.4 to -0.8 correlation with DXY
        - Rising DXY (strong dollar) = BTC weakness = BEARISH
        - Falling DXY (weak dollar) = BTC strength = BULLISH

        Args:
            use_cache: Use cached data if available

        Returns:
            Dict with:
                - current_value: Current DXY value
                - change_7d: 7-day percent change
                - signal: BULLISH/BEARISH/NEUTRAL
                - confidence: Signal confidence
                - correlation: Expected BTC correlation
                - source: Data source

        Note:
            Uses yfinance for DXY data. Requires 'yfinance' package.
            Install: pip install yfinance
        """
        # Check cache
        if use_cache and self._is_dxy_cache_valid():
            logger.info("Using cached DXY data")
            return self._dxy_cache

        try:
            import yfinance as yf

            # Fetch DXY data (7 days for trend)
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="7d")

            if hist.empty or len(hist) < 2:
                raise ValueError("Insufficient DXY data")

            current_value = float(hist['Close'].iloc[-1])
            start_value = float(hist['Close'].iloc[0])
            change_7d = ((current_value - start_value) / start_value) * 100

            # Generate signal (inverse correlation with BTC)
            signal, confidence = self._interpret_dxy(change_7d)

            result = {
                'current_value': round(current_value, 2),
                'change_7d': round(change_7d, 2),
                'signal': signal.value,
                'confidence': confidence,
                'correlation': -0.6,  # Average BTC/DXY correlation
                'source': 'yfinance (DX-Y.NYB)',
                'interpretation': self._get_dxy_interpretation(change_7d)
            }

            # Update cache
            self._dxy_cache = result
            self._dxy_cache_time = time.time()

            logger.info(f"DXY: {current_value} ({change_7d:+.2f}% 7d) -> {signal.value} (confidence: {confidence}%)")

            return result

        except ImportError:
            logger.error("yfinance not installed. Install with: pip install yfinance")
            return self._get_fallback_dxy()
        except Exception as e:
            logger.error(f"Failed to fetch DXY data: {e}")
            return self._get_fallback_dxy()

    def _interpret_dxy(self, change_7d: float) -> Tuple[Signal, int]:
        """
        Interpret DXY trend into BTC signal.

        Inverse correlation logic:
        - DXY rising > 2% = Strong dollar = BEARISH for BTC
        - DXY rising 0.5-2% = Moderate BEARISH
        - DXY flat (-0.5 to 0.5%) = NEUTRAL
        - DXY falling -0.5 to -2% = Moderate BULLISH
        - DXY falling < -2% = Strong BULLISH for BTC

        Args:
            change_7d: 7-day percent change in DXY

        Returns:
            Tuple of (Signal, confidence)
        """
        if change_7d > 2.0:
            # Strong dollar = Bearish for BTC
            confidence = min(100, int(change_7d * 20 + 60))
            return Signal.BEARISH, confidence

        elif change_7d > 0.5:
            # Moderate dollar strength
            confidence = min(70, int(change_7d * 25 + 45))
            return Signal.BEARISH, confidence

        elif change_7d > -0.5:
            # Flat/neutral
            return Signal.NEUTRAL, 50

        elif change_7d > -2.0:
            # Moderate dollar weakness = Bullish for BTC
            confidence = min(70, int(abs(change_7d) * 25 + 45))
            return Signal.BULLISH, confidence

        else:
            # Strong dollar weakness = Bullish for BTC
            confidence = min(100, int(abs(change_7d) * 20 + 60))
            return Signal.BULLISH, confidence

    def _get_dxy_interpretation(self, change_7d: float) -> str:
        """Get human-readable DXY interpretation"""
        if change_7d > 2.0:
            return "Strong dollar (bearish for BTC)"
        elif change_7d > 0.5:
            return "Rising dollar (slight bearish for BTC)"
        elif change_7d > -0.5:
            return "Stable dollar (neutral)"
        elif change_7d > -2.0:
            return "Falling dollar (slight bullish for BTC)"
        else:
            return "Weak dollar (bullish for BTC)"

    def get_combined_filter(self, weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Get combined market filter signal from multiple sources.

        Combines Fear & Greed Index and DXY signals with weighted scoring.

        Args:
            weights: Optional custom weights. Default: {'fgi': 0.6, 'dxy': 0.4}

        Returns:
            Dict with:
                - signal: Overall BULLISH/BEARISH/NEUTRAL
                - confidence: Overall confidence (0-100)
                - score: Composite score (-100 to +100)
                - components: Individual filter results
                - recommendation: Trading recommendation

        Example:
            {
                'signal': 'BEARISH',
                'confidence': 78,
                'score': -65,
                'components': {
                    'fgi': {...},
                    'dxy': {...}
                },
                'recommendation': 'Avoid new long positions'
            }
        """
        # Default weights (FGI slightly more important based on research)
        if weights is None:
            weights = {'fgi': 0.6, 'dxy': 0.4}

        # Get individual signals
        fgi_data = self.get_fear_greed()
        dxy_data = self.get_dxy_signal()

        # Convert signals to scores (-100 to +100)
        fgi_score = self._signal_to_score(fgi_data['signal'], fgi_data['confidence'])
        dxy_score = self._signal_to_score(dxy_data['signal'], dxy_data['confidence'])

        # Calculate weighted composite score
        composite_score = (fgi_score * weights['fgi']) + (dxy_score * weights['dxy'])

        # Determine overall signal
        if composite_score > 25:
            overall_signal = Signal.BULLISH
            overall_confidence = min(100, int(composite_score))
        elif composite_score < -25:
            overall_signal = Signal.BEARISH
            overall_confidence = min(100, int(abs(composite_score)))
        else:
            overall_signal = Signal.NEUTRAL
            overall_confidence = 50

        # Generate recommendation
        recommendation = self._get_recommendation(overall_signal, overall_confidence)

        result = {
            'signal': overall_signal.value,
            'confidence': overall_confidence,
            'score': round(composite_score, 2),
            'components': {
                'fgi': fgi_data,
                'dxy': dxy_data
            },
            'weights': weights,
            'recommendation': recommendation,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.info(f"Combined Filter: {overall_signal.value} (confidence: {overall_confidence}%, score: {composite_score:.2f})")

        return result

    def _signal_to_score(self, signal: str, confidence: int) -> float:
        """
        Convert signal and confidence to numeric score.

        Args:
            signal: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            confidence: Confidence percentage (0-100)

        Returns:
            Score from -100 (strong bearish) to +100 (strong bullish)
        """
        if signal == 'BULLISH':
            return confidence
        elif signal == 'BEARISH':
            return -confidence
        else:  # NEUTRAL
            return 0

    def _get_recommendation(self, signal: Signal, confidence: int) -> str:
        """Get trading recommendation based on signal and confidence"""
        if signal == Signal.BULLISH:
            if confidence >= 80:
                return "Strong buying opportunity - Consider accumulating"
            elif confidence >= 60:
                return "Moderate buy signal - Look for entries"
            else:
                return "Slight bullish bias - Wait for confirmation"

        elif signal == Signal.BEARISH:
            if confidence >= 80:
                return "Strong sell signal - Avoid new longs, consider exits"
            elif confidence >= 60:
                return "Moderate bearish - Reduce exposure, raise stops"
            else:
                return "Slight bearish bias - Be cautious with new positions"

        else:  # NEUTRAL
            return "Neutral market - Trade with tight risk management"

    def _is_fgi_cache_valid(self) -> bool:
        """Check if FGI cache is still valid"""
        if self._fgi_cache is None or self._fgi_cache_time is None:
            return False
        return (time.time() - self._fgi_cache_time) < self.CACHE_DURATION_SECONDS

    def _is_dxy_cache_valid(self) -> bool:
        """Check if DXY cache is still valid"""
        if self._dxy_cache is None or self._dxy_cache_time is None:
            return False
        return (time.time() - self._dxy_cache_time) < self.DXY_CACHE_DURATION

    def _get_fallback_fgi(self) -> Dict:
        """Return fallback data if FGI API fails"""
        logger.warning("Using fallback FGI data - API unavailable")
        return {
            'value': 50,
            'classification': 'Neutral (API Error)',
            'signal': Signal.NEUTRAL.value,
            'confidence': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'fallback',
            'error': 'API unavailable'
        }

    def _get_fallback_dxy(self) -> Dict:
        """Return fallback data if DXY fetch fails"""
        logger.warning("Using fallback DXY data - API unavailable")
        return {
            'current_value': 0,
            'change_7d': 0,
            'signal': Signal.NEUTRAL.value,
            'confidence': 0,
            'correlation': -0.6,
            'source': 'fallback',
            'interpretation': 'Data unavailable',
            'error': 'API unavailable'
        }

    def get_fgi_history(self, days: int = 30) -> Dict:
        """
        Get historical Fear & Greed Index data.

        Args:
            days: Number of days of history (max 365)

        Returns:
            Dict with historical FGI values and trend analysis
        """
        try:
            url = self.FGI_HISTORY_API.format(days)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'data' not in data:
                raise ValueError("Invalid API response")

            history = []
            for entry in data['data']:
                history.append({
                    'date': datetime.fromtimestamp(int(entry['timestamp'])).strftime('%Y-%m-%d'),
                    'value': int(entry['value']),
                    'classification': entry['value_classification']
                })

            # Calculate trend
            values = [h['value'] for h in history]
            avg_value = sum(values) / len(values) if values else 50
            trend = "rising" if values[0] > values[-1] else "falling" if values[0] < values[-1] else "stable"

            return {
                'history': history,
                'average': round(avg_value, 2),
                'trend': trend,
                'period': f"{days} days",
                'data_points': len(history)
            }

        except Exception as e:
            logger.error(f"Failed to fetch FGI history: {e}")
            return {'error': str(e), 'history': []}


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("SOVEREIGN_SHADOW_3 - Market Filters")
    print("Research-backed sentiment and macro filters")
    print("=" * 80)
    print()

    # Initialize filters
    filters = MarketFilters()

    # Test Fear & Greed Index
    print("1. FEAR & GREED INDEX")
    print("-" * 80)
    fgi = filters.get_fear_greed()
    print(f"Value: {fgi['value']}/100")
    print(f"Classification: {fgi['classification']}")
    print(f"Signal: {fgi['signal']} (Confidence: {fgi['confidence']}%)")
    print(f"Timestamp: {fgi['timestamp']}")
    print(f"Source: {fgi['source']}")
    print(f"Note: {fgi.get('note', 'N/A')}")
    print()

    # Test DXY Signal
    print("2. DXY CORRELATION FILTER")
    print("-" * 80)
    dxy = filters.get_dxy_signal()
    if 'error' not in dxy:
        print(f"Current DXY: {dxy['current_value']}")
        print(f"7-Day Change: {dxy['change_7d']:+.2f}%")
        print(f"Signal: {dxy['signal']} (Confidence: {dxy['confidence']}%)")
        print(f"BTC Correlation: {dxy['correlation']}")
        print(f"Interpretation: {dxy['interpretation']}")
    else:
        print(f"Error: {dxy['error']}")
        print("Note: Install yfinance for DXY data: pip install yfinance")
    print()

    # Test Combined Filter
    print("3. COMBINED MARKET FILTER")
    print("-" * 80)
    combined = filters.get_combined_filter()
    print(f"Overall Signal: {combined['signal']}")
    print(f"Confidence: {combined['confidence']}%")
    print(f"Composite Score: {combined['score']}/100")
    print(f"Recommendation: {combined['recommendation']}")
    print()
    print("Component Weights:")
    print(f"  - Fear & Greed: {combined['weights']['fgi'] * 100:.0f}%")
    print(f"  - DXY Correlation: {combined['weights']['dxy'] * 100:.0f}%")
    print()

    # Test FGI History
    print("4. FEAR & GREED HISTORY (30 days)")
    print("-" * 80)
    history = filters.get_fgi_history(days=30)
    if 'error' not in history:
        print(f"Average FGI: {history['average']}")
        print(f"Trend: {history['trend'].upper()}")
        print(f"Data Points: {history['data_points']}")
        print()
        print("Recent values:")
        for entry in history['history'][:5]:
            print(f"  {entry['date']}: {entry['value']} ({entry['classification']})")
    else:
        print(f"Error: {history['error']}")
    print()

    print("=" * 80)
    print("Integration Example:")
    print("=" * 80)
    print("""
# In your trading agent:
from core.filters.market_filters import MarketFilters, Signal

def should_trade(self):
    filters = MarketFilters()
    market = filters.get_combined_filter()

    # Check if market conditions are favorable
    if market['signal'] == Signal.BEARISH.value and market['confidence'] > 75:
        print(f"Market filter: {market['recommendation']}")
        return False  # Skip trading in extremely bearish conditions

    # Adjust position sizing based on confidence
    if market['confidence'] > 80:
        position_multiplier = 1.5  # Increase size in strong signals
    elif market['confidence'] < 50:
        position_multiplier = 0.5  # Reduce size in weak signals
    else:
        position_multiplier = 1.0

    return True

# Real-time monitoring:
fgi = filters.get_fear_greed()
if fgi['value'] > 80:
    print("ALERT: Extreme Greed detected - Consider taking profits")
elif fgi['value'] < 25:
    print("ALERT: Extreme Fear detected - Look for buying opportunities")
    """)
    print()
    print("=" * 80)
    print("Research References:")
    print("=" * 80)
    print("1. Fear & Greed Index: https://alternative.me/crypto/fear-and-greed-index/")
    print("2. Advanced FGI (15-min updates): https://cfgi.io/")
    print("3. DXY/BTC Correlation: -0.4 to -0.8 (5-year historical analysis)")
    print("4. Backtested Result: FGI > 80 sell = 50% more profit over 90 days")
    print("=" * 80)

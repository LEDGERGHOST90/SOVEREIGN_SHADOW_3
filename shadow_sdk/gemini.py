"""
🧠 ShadowMind - Google Gemini AI Integration

AI-driven market analysis, sentiment analysis, and trading insights using Google's Gemini.

Features:
    - Market sentiment analysis
    - Technical analysis interpretation
    - News and social media sentiment
    - Trading decision support
    - Risk assessment insights
    - Portfolio optimization suggestions

Version: 1.0.0-GENESIS
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("shadow_sdk.gemini")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("🧠 google-generativeai not installed. Run: pip install google-generativeai")


class ShadowMind:
    """
    🧠 ShadowMind - AI-Powered Trading Intelligence

    Integrates Google Gemini for advanced market analysis and trading insights.

    Features:
        - Real-time market sentiment analysis
        - Technical indicator interpretation
        - News & social sentiment analysis
        - Risk assessment & portfolio optimization
        - Natural language trading queries

    Example:
        >>> mind = ShadowMind()
        >>> analysis = mind.analyze_market("BTC", price_data, news)
        >>> recommendation = mind.get_trade_recommendation("BTC", "long", 0.02)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-pro"):
        """
        Initialize ShadowMind with Gemini API.

        Args:
            api_key: Optional Gemini API key (defaults to env var GEMINI_API_KEY)
            model: Gemini model to use. Options:
                   - "gemini-2.5-pro" (default, powerful and free tier compatible)
                   - "gemini-3-pro-preview" (newest, requires paid plan)
                   - "gemini-2.5-flash" (fast, free tier friendly)
                   - "gemini-2.0-flash-exp" (experimental)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.model_name = model
        self.model = genai.GenerativeModel(model)

        # System prompt for trading context
        self.system_context = """
You are ShadowMind, an elite AI trading analyst integrated into the Sovereign Shadow II trading system.

Your role:
- Analyze market data, news, and sentiment
- Provide actionable trading insights
- Assess risk and opportunity
- Support strategic decision-making

Trading Philosophy: "Fearless. Bold. Smiling through chaos."
Risk Management: 1-2% per trade, system over emotion
Portfolio: BTC 40%, ETH 30%, SOL 20%, XRP 10%

Respond with clear, concise, actionable insights.
"""

        self.query_count = 0
        self.last_query_time = None

        logger.info(f"🧠 ShadowMind initialized with {self.model_name}")

    def analyze_market(
        self,
        asset: str,
        price_data: Dict[str, Any],
        news: Optional[List[str]] = None,
        timeframe: str = "4H"
    ) -> Dict[str, Any]:
        """
        Analyze market conditions for a specific asset.

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH")
            price_data: Dict with price, volume, indicators
            news: Optional list of recent news headlines
            timeframe: Trading timeframe

        Returns:
            Dict with sentiment, key_points, recommendation
        """
        # Build prompt
        prompt = f"""
Analyze {asset} market conditions:

PRICE DATA:
- Current: ${price_data.get('price', 'N/A')}
- 24h Change: {price_data.get('change_24h', 'N/A')}%
- Volume: {price_data.get('volume', 'N/A')}
- Timeframe: {timeframe}

TECHNICAL INDICATORS:
{self._format_indicators(price_data.get('indicators', {}))}

RECENT NEWS:
{self._format_news(news) if news else "No news provided"}

Provide:
1. Market Sentiment (bullish/bearish/neutral with confidence %)
2. Key Technical Points (3-5 bullet points)
3. Risk Factors (2-3 key risks)
4. Actionable Recommendation (clear buy/sell/hold with reasoning)
"""

        try:
            response = self.model.generate_content(
                f"{self.system_context}\n\n{prompt}"
            )

            self.query_count += 1
            self.last_query_time = datetime.now()

            return {
                "asset": asset,
                "timestamp": datetime.now().isoformat(),
                "analysis": response.text,
                "raw_response": response,
                "query_count": self.query_count
            }

        except Exception as e:
            logger.error(f"🧠 Gemini analysis failed: {e}")
            return {
                "asset": asset,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "analysis": None
            }

    def get_trade_recommendation(
        self,
        asset: str,
        direction: str,
        position_size: float,
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get AI recommendation for a specific trade.

        Args:
            asset: Asset symbol
            direction: "long" or "short"
            position_size: Position size as % of portfolio
            market_data: Optional current market data

        Returns:
            Dict with recommendation, confidence, risk_assessment
        """
        prompt = f"""
Evaluate this trade setup:

TRADE DETAILS:
- Asset: {asset}
- Direction: {direction.upper()}
- Position Size: {position_size * 100}% of portfolio
- Risk per trade: 1-2% maximum

MARKET CONTEXT:
{self._format_market_data(market_data) if market_data else "Limited market data"}

Based on:
1. Current market conditions
2. Risk/reward profile
3. Portfolio allocation (BTC 40%, ETH 30%, SOL 20%, XRP 10%)

Provide:
- Recommendation: APPROVE / REJECT / MODIFY
- Confidence: 0-100%
- Risk Assessment: LOW / MEDIUM / HIGH
- Key Considerations (3 points)
- Suggested Modifications (if any)
"""

        try:
            response = self.model.generate_content(
                f"{self.system_context}\n\n{prompt}"
            )

            self.query_count += 1
            self.last_query_time = datetime.now()

            return {
                "asset": asset,
                "direction": direction,
                "timestamp": datetime.now().isoformat(),
                "recommendation": response.text,
                "query_count": self.query_count
            }

        except Exception as e:
            logger.error(f"🧠 Trade recommendation failed: {e}")
            return {
                "asset": asset,
                "direction": direction,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "recommendation": None
            }

    def analyze_portfolio(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze portfolio and suggest rebalancing.

        Args:
            current_allocation: Current % allocation by asset
            target_allocation: Target % allocation
            market_conditions: Optional market context

        Returns:
            Dict with analysis, rebalancing_suggestions
        """
        prompt = f"""
Analyze portfolio allocation:

CURRENT ALLOCATION:
{self._format_allocation(current_allocation)}

TARGET ALLOCATION:
{self._format_allocation(target_allocation)}

DEVIATIONS:
{self._calculate_deviations(current_allocation, target_allocation)}

MARKET CONDITIONS:
{self._format_market_data(market_conditions) if market_conditions else "Standard conditions"}

Provide:
1. Allocation Analysis (what's off-target and why it matters)
2. Rebalancing Priority (high/medium/low with rationale)
3. Suggested Actions (specific buy/sell amounts)
4. Timing Considerations (execute now or wait?)
5. Risk Assessment (potential downsides)
"""

        try:
            response = self.model.generate_content(
                f"{self.system_context}\n\n{prompt}"
            )

            self.query_count += 1
            self.last_query_time = datetime.now()

            return {
                "timestamp": datetime.now().isoformat(),
                "analysis": response.text,
                "current": current_allocation,
                "target": target_allocation,
                "query_count": self.query_count
            }

        except Exception as e:
            logger.error(f"🧠 Portfolio analysis failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "analysis": None
            }

    def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Ask ShadowMind any trading-related question.

        Args:
            question: Natural language question
            context: Optional context dict

        Returns:
            AI response as string
        """
        context_str = ""
        if context:
            context_str = f"\n\nCONTEXT:\n{self._format_dict(context)}"

        prompt = f"{question}{context_str}"

        try:
            response = self.model.generate_content(
                f"{self.system_context}\n\n{prompt}"
            )

            self.query_count += 1
            self.last_query_time = datetime.now()

            return response.text

        except Exception as e:
            logger.error(f"🧠 Query failed: {e}")
            return f"Error: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """Get ShadowMind usage statistics."""
        return {
            "queries_total": self.query_count,
            "last_query": self.last_query_time.isoformat() if self.last_query_time else None,
            "model": self.model_name,
            "status": "active"
        }

    # Helper methods

    def _format_indicators(self, indicators: Dict[str, Any]) -> str:
        """Format technical indicators for prompt."""
        if not indicators:
            return "No indicators provided"

        lines = []
        for key, value in indicators.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_news(self, news: List[str]) -> str:
        """Format news headlines for prompt."""
        return "\n".join(f"- {headline}" for headline in news[:5])

    def _format_market_data(self, data: Dict[str, Any]) -> str:
        """Format market data for prompt."""
        if not data:
            return "No market data provided"

        return "\n".join(f"- {k}: {v}" for k, v in data.items())

    def _format_allocation(self, allocation: Dict[str, float]) -> str:
        """Format portfolio allocation."""
        return "\n".join(f"- {asset}: {pct}%" for asset, pct in allocation.items())

    def _calculate_deviations(
        self,
        current: Dict[str, float],
        target: Dict[str, float]
    ) -> str:
        """Calculate allocation deviations."""
        lines = []
        for asset in target:
            curr = current.get(asset, 0)
            tgt = target[asset]
            dev = curr - tgt
            sign = "+" if dev > 0 else ""
            lines.append(f"- {asset}: {sign}{dev:.1f}% ({curr}% vs {tgt}% target)")
        return "\n".join(lines)

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        return "\n".join(f"- {k}: {v}" for k, v in data.items())


def test_connection() -> bool:
    """
    Test Gemini API connection.

    Returns:
        True if connection successful
    """
    try:
        mind = ShadowMind()
        response = mind.ask("What is the capital of France?")

        if "Paris" in response:
            logger.info("🧠 Gemini connection test: SUCCESS")
            return True
        else:
            logger.warning("🧠 Gemini connection test: Unexpected response")
            return False

    except Exception as e:
        logger.error(f"🧠 Gemini connection test: FAILED - {e}")
        return False


if __name__ == "__main__":
    # Test ShadowMind
    logging.basicConfig(level=logging.INFO)

    print("🧠 Testing ShadowMind initialization...")
    test_connection()

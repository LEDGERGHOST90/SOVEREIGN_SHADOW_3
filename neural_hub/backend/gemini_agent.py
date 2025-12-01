#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Gemini Neural Agent
AI-powered trading brain using Google Gemini 2.5 Pro

Features:
- Market analysis with confidence scoring
- Pattern recognition
- Signal generation
- Risk assessment
- Strategy recommendations
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

import google.generativeai as genai

PROJECT_ROOT = Path(__file__).parent.parent.parent

# =============================================================================
# CONFIGURATION
# =============================================================================

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class MarketData:
    symbol: str
    price: float
    rsi: float
    ema_20: float
    ema_50: float
    volume_ratio: float
    change_1h: float
    change_24h: float
    high_24h: float
    low_24h: float
    market_cap: Optional[float] = None
    sentiment: str = "neutral"

@dataclass
class TradingSignal:
    symbol: str
    action: str
    confidence: int
    reasoning: str
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit_1: Optional[float]
    take_profit_2: Optional[float]
    risk_level: str
    timeframe: str
    position_size_pct: float
    timestamp: str

@dataclass
class MarketAnalysis:
    symbol: str
    trend: str
    strength: int
    support_levels: List[float]
    resistance_levels: List[float]
    patterns_detected: List[str]
    key_insights: List[str]
    recommendation: str
    timestamp: str

# =============================================================================
# GEMINI NEURAL AGENT
# =============================================================================

class GeminiNeuralAgent:
    """AI-powered trading brain using Gemini"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._load_api_key()
        genai.configure(api_key=self.api_key)

        # Use Gemini 2.0 Flash (latest, fastest)
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                'temperature': 0.3,  # Lower = more focused
                'top_p': 0.8,
                'max_output_tokens': 2048,
            }
        )

        # Trading rules from your config
        self.trading_rules = {
            'risk_per_trade': 2.0,
            'stop_loss_pct': 15.0,
            'take_profit_1_pct': 30.0,
            'take_profit_2_pct': 75.0,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'volume_spike_threshold': 2.0,
            'max_position_usd': 100.0,
            'max_daily_loss': 150.0
        }

    def _load_api_key(self) -> str:
        """Load Gemini API key from .env"""
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip()
        return os.environ.get("GEMINI_API_KEY", "")

    # =========================================================================
    # SIGNAL GENERATION
    # =========================================================================

    async def generate_signal(self, market_data: MarketData) -> TradingSignal:
        """Generate a trading signal for a symbol"""

        prompt = f"""You are an expert crypto trading analyst for the Sovereign Shadow trading system.

MARKET DATA FOR {market_data.symbol}:
- Current Price: ${market_data.price:,.4f}
- RSI (14): {market_data.rsi:.1f}
- 20 EMA: ${market_data.ema_20:,.4f}
- 50 EMA: ${market_data.ema_50:,.4f}
- Volume vs Average: {market_data.volume_ratio:.1f}x
- 1h Change: {market_data.change_1h:+.2f}%
- 24h Change: {market_data.change_24h:+.2f}%
- 24h High: ${market_data.high_24h:,.4f}
- 24h Low: ${market_data.low_24h:,.4f}
- Market Sentiment: {market_data.sentiment}

TRADING RULES (MUST FOLLOW):
1. BUY SIGNAL requires ALL of these:
   - RSI < {self.trading_rules['rsi_oversold']} (oversold)
   - Volume > {self.trading_rules['volume_spike_threshold']}x average
   - Price above 20 EMA

2. SELL SIGNAL when ANY of these:
   - RSI > {self.trading_rules['rsi_overbought']} (overbought)
   - Stop loss hit ({self.trading_rules['stop_loss_pct']}% below entry)
   - Take profit hit

3. HOLD when conditions not met but position is open

4. WATCH when interesting setup forming but not ready

RISK PARAMETERS:
- Risk per trade: {self.trading_rules['risk_per_trade']}%
- Stop Loss: {self.trading_rules['stop_loss_pct']}% below entry
- Take Profit 1: {self.trading_rules['take_profit_1_pct']}% (sell 50%)
- Take Profit 2: {self.trading_rules['take_profit_2_pct']}% (sell remaining)
- Max Position: ${self.trading_rules['max_position_usd']}

Analyze the data and respond with ONLY valid JSON (no markdown, no backticks):
{{
    "action": "BUY" or "SELL" or "HOLD" or "WATCH",
    "confidence": 0-100,
    "reasoning": "2-3 sentence explanation",
    "entry_price": price or null,
    "stop_loss": price or null,
    "take_profit_1": price or null,
    "take_profit_2": price or null,
    "risk_level": "low" or "medium" or "high" or "extreme",
    "timeframe": "1h" or "4h" or "1d",
    "position_size_pct": percentage of portfolio
}}"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            # Parse JSON response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            data = json.loads(text)

            return TradingSignal(
                symbol=market_data.symbol,
                action=data.get("action", "HOLD"),
                confidence=data.get("confidence", 0),
                reasoning=data.get("reasoning", ""),
                entry_price=data.get("entry_price"),
                stop_loss=data.get("stop_loss"),
                take_profit_1=data.get("take_profit_1"),
                take_profit_2=data.get("take_profit_2"),
                risk_level=data.get("risk_level", "medium"),
                timeframe=data.get("timeframe", "4h"),
                position_size_pct=data.get("position_size_pct", 0),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"Gemini error: {e}")
            return TradingSignal(
                symbol=market_data.symbol,
                action="HOLD",
                confidence=0,
                reasoning=f"Error generating signal: {str(e)}",
                entry_price=None,
                stop_loss=None,
                take_profit_1=None,
                take_profit_2=None,
                risk_level="high",
                timeframe="4h",
                position_size_pct=0,
                timestamp=datetime.now().isoformat()
            )

    # =========================================================================
    # DEEP ANALYSIS
    # =========================================================================

    async def deep_analyze(self, market_data: MarketData, news: List[str] = None) -> MarketAnalysis:
        """Perform deep analysis of a symbol"""

        news_text = "\n".join(f"- {n}" for n in (news or [])) or "No recent news"

        prompt = f"""You are a senior crypto market analyst. Perform deep technical and fundamental analysis.

SYMBOL: {market_data.symbol}

PRICE DATA:
- Current: ${market_data.price:,.4f}
- 24h High: ${market_data.high_24h:,.4f}
- 24h Low: ${market_data.low_24h:,.4f}
- 24h Change: {market_data.change_24h:+.2f}%

TECHNICAL INDICATORS:
- RSI: {market_data.rsi:.1f}
- 20 EMA: ${market_data.ema_20:,.4f}
- 50 EMA: ${market_data.ema_50:,.4f}
- Volume Ratio: {market_data.volume_ratio:.1f}x

RECENT NEWS:
{news_text}

Analyze and respond with ONLY valid JSON:
{{
    "trend": "bullish" or "bearish" or "neutral" or "ranging",
    "strength": 0-100,
    "support_levels": [price1, price2, price3],
    "resistance_levels": [price1, price2, price3],
    "patterns_detected": ["pattern1", "pattern2"],
    "key_insights": ["insight1", "insight2", "insight3"],
    "recommendation": "1-2 sentence actionable recommendation"
}}"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            data = json.loads(text)

            return MarketAnalysis(
                symbol=market_data.symbol,
                trend=data.get("trend", "neutral"),
                strength=data.get("strength", 50),
                support_levels=data.get("support_levels", []),
                resistance_levels=data.get("resistance_levels", []),
                patterns_detected=data.get("patterns_detected", []),
                key_insights=data.get("key_insights", []),
                recommendation=data.get("recommendation", ""),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            return MarketAnalysis(
                symbol=market_data.symbol,
                trend="unknown",
                strength=0,
                support_levels=[],
                resistance_levels=[],
                patterns_detected=[],
                key_insights=[f"Error: {str(e)}"],
                recommendation="Unable to analyze",
                timestamp=datetime.now().isoformat()
            )

    # =========================================================================
    # PORTFOLIO ANALYSIS
    # =========================================================================

    async def analyze_portfolio(self, holdings: Dict[str, float], market_data: Dict[str, MarketData]) -> Dict:
        """Analyze entire portfolio and suggest rebalancing"""

        holdings_text = "\n".join(f"- {sym}: ${val:,.2f}" for sym, val in holdings.items())
        total = sum(holdings.values())

        prompt = f"""You are a portfolio manager for a crypto trading system.

CURRENT HOLDINGS (Total: ${total:,.2f}):
{holdings_text}

TARGET ALLOCATION:
- BTC: 40%
- ETH: 30%
- SOL: 20%
- XRP: 10%

MARKET CONDITIONS:
{json.dumps({sym: {"price": d.price, "rsi": d.rsi, "change_24h": d.change_24h} for sym, d in market_data.items()}, indent=2)}

Analyze and respond with ONLY valid JSON:
{{
    "current_allocation": {{"BTC": 25.5, "ETH": 30.2}},
    "drift_from_target": {{"BTC": -14.5, "ETH": 0.2}},
    "rebalance_needed": true or false,
    "suggested_trades": [
        {{"action": "BUY", "symbol": "BTC", "amount_usd": 100}},
        {{"action": "SELL", "symbol": "XRP", "amount_usd": 50}}
    ],
    "risk_assessment": "1-2 sentences about portfolio risk",
    "recommendation": "1-2 sentences of action"
}}"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            return json.loads(text)

        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # STRATEGY SELECTION
    # =========================================================================

    async def select_strategy(self, market_conditions: Dict) -> Dict:
        """Select best strategy based on market conditions"""

        prompt = f"""You are a trading strategy selector. Based on current market conditions, recommend the best strategy.

MARKET CONDITIONS:
- BTC Trend: {market_conditions.get('btc_trend', 'unknown')}
- Market Volatility: {market_conditions.get('volatility', 'medium')}
- Fear & Greed Index: {market_conditions.get('fear_greed', 50)}
- Funding Rates: {market_conditions.get('funding', 'neutral')}

AVAILABLE STRATEGIES:
1. swing_trade - RSI + Volume breakouts (best in ranging/volatile markets)
2. momentum - Ride strong trends (best in trending markets)
3. mean_reversion - Buy dips, sell rips (best in ranging markets)
4. breakout - Trade support/resistance breaks (best at key levels)
5. dca_accumulate - Dollar cost average (best in fear/uncertain markets)

Respond with ONLY valid JSON:
{{
    "recommended_strategy": "strategy_name",
    "confidence": 0-100,
    "reasoning": "Why this strategy fits current conditions",
    "alternative": "backup strategy if primary fails",
    "avoid": "strategy to avoid in current conditions"
}}"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()

            return json.loads(text)

        except Exception as e:
            return {"error": str(e), "recommended_strategy": "swing_trade"}

    # =========================================================================
    # CHAT INTERFACE
    # =========================================================================

    async def chat(self, message: str, context: Dict = None) -> str:
        """Interactive chat with the neural agent"""

        context_text = ""
        if context:
            context_text = f"""
CURRENT CONTEXT:
- Portfolio Value: ${context.get('portfolio_value', 0):,.2f}
- Open Positions: {context.get('open_positions', 0)}
- Today's P&L: ${context.get('daily_pnl', 0):+,.2f}
- Active Signals: {context.get('active_signals', 0)}
"""

        prompt = f"""You are the Sovereign Shadow Neural Agent - an AI trading assistant.
You speak concisely and directly about crypto trading.
{context_text}

User: {message}

Respond helpfully and concisely (2-4 sentences max unless they ask for detail)."""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            return response.text.strip()

        except Exception as e:
            return f"Neural agent error: {str(e)}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_market_data(raw: Dict) -> MarketData:
    """Create MarketData from raw API response"""
    return MarketData(
        symbol=raw.get("symbol", ""),
        price=raw.get("price", 0),
        rsi=raw.get("rsi", 50),
        ema_20=raw.get("ema_20", raw.get("price", 0)),
        ema_50=raw.get("ema_50", raw.get("price", 0)),
        volume_ratio=raw.get("volume_ratio", 1.0),
        change_1h=raw.get("change_1h", 0),
        change_24h=raw.get("change_24h", 0),
        high_24h=raw.get("high_24h", raw.get("price", 0)),
        low_24h=raw.get("low_24h", raw.get("price", 0)),
        market_cap=raw.get("market_cap"),
        sentiment=raw.get("sentiment", "neutral")
    )


# =============================================================================
# TEST
# =============================================================================

async def test_agent():
    """Test the Gemini Neural Agent"""
    agent = GeminiNeuralAgent()

    # Test market data
    test_data = MarketData(
        symbol="BTC",
        price=90628.22,
        rsi=45.2,
        ema_20=89500.00,
        ema_50=88000.00,
        volume_ratio=1.5,
        change_1h=0.5,
        change_24h=-1.2,
        high_24h=92000.00,
        low_24h=89000.00,
        sentiment="neutral"
    )

    print("Testing Gemini Neural Agent...")
    print("=" * 50)

    # Test signal generation
    print("\n[SIGNAL GENERATION]")
    signal = await agent.generate_signal(test_data)
    print(f"Action: {signal.action}")
    print(f"Confidence: {signal.confidence}%")
    print(f"Reasoning: {signal.reasoning}")

    # Test deep analysis
    print("\n[DEEP ANALYSIS]")
    analysis = await agent.deep_analyze(test_data)
    print(f"Trend: {analysis.trend}")
    print(f"Strength: {analysis.strength}")
    print(f"Patterns: {analysis.patterns_detected}")
    print(f"Recommendation: {analysis.recommendation}")

    # Test chat
    print("\n[CHAT]")
    response = await agent.chat("What's the best entry for BTC right now?")
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(test_agent())

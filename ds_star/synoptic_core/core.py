#!/usr/bin/env python3
"""
SYNOPTIC CORE - The unified asset analysis engine
Produces Smart Asset Scores from technical, on-chain, fundamental, and sentiment data
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Import sub-clients
from .market_data_client import MarketDataClient
from .onchain_client import OnChainClient
from .text_sources_client import TextSourcesClient


@dataclass
class SmartAssetScore:
    """Result of Synoptic Core analysis"""
    asset: str
    smart_asset_score: int  # 0-100
    dominant_driver: str  # technical | on_chain | fundamental | sentiment
    thesis: str
    risks: List[str]
    supporting_signals: Dict[str, List[str]]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class SynopticCore:
    """
    Unified asset analysis engine for Sovereign Shadow 3

    Fuses:
    - Technical market data (OHLCV, RSI, MACD, volatility)
    - On-chain data (whale movements, liquidity, staking)
    - Fundamental data (whitepapers, dev updates)
    - Sentiment data (news, social media)

    Outputs a Smart Asset Score (0-100) with thesis and risk assessment
    """

    # Scoring weights (configurable)
    WEIGHTS = {
        "technical": 0.30,
        "on_chain": 0.30,
        "fundamental": 0.20,
        "sentiment": 0.20
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.market_client = MarketDataClient()
        self.onchain_client = OnChainClient()
        self.text_client = TextSourcesClient()

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Analysis logs directory
        self.log_dir = Path(__file__).parent.parent.parent / "logs" / "synoptic_core"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_system_prompt(self) -> str:
        """Load the Synoptic Core system prompt"""
        import yaml
        prompt_file = Path(__file__).parent.parent / "configs" / "system_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f)
                return prompts.get("synoptic_core", "")
        return ""

    def assess(
        self,
        asset: str,
        timeframe: str = "1d",
        lookback_days: int = 30,
        context: Optional[str] = None
    ) -> SmartAssetScore:
        """
        Perform unified assessment of an asset

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH", "SOL")
            timeframe: Data timeframe (1h, 4h, 1d)
            lookback_days: How many days of data to analyze
            context: Additional context or notes

        Returns:
            SmartAssetScore with thesis and recommendations
        """
        # Gather all data streams
        technical_data = self._get_technical_signals(asset, timeframe, lookback_days)
        onchain_data = self._get_onchain_signals(asset, lookback_days)
        fundamental_data = self._get_fundamental_signals(asset)
        sentiment_data = self._get_sentiment_signals(asset)

        # Calculate component scores
        technical_score = self._score_technical(technical_data)
        onchain_score = self._score_onchain(onchain_data)
        fundamental_score = self._score_fundamental(fundamental_data)
        sentiment_score = self._score_sentiment(sentiment_data)

        # Weighted composite score
        composite_score = int(
            technical_score * self.WEIGHTS["technical"] +
            onchain_score * self.WEIGHTS["on_chain"] +
            fundamental_score * self.WEIGHTS["fundamental"] +
            sentiment_score * self.WEIGHTS["sentiment"]
        )

        # Determine dominant driver
        scores = {
            "technical": technical_score,
            "on_chain": onchain_score,
            "fundamental": fundamental_score,
            "sentiment": sentiment_score
        }
        dominant = max(scores, key=scores.get)

        # Generate thesis based on score and signals
        thesis = self._generate_thesis(asset, composite_score, dominant, scores)

        # Identify risks
        risks = self._identify_risks(technical_data, onchain_data, fundamental_data, sentiment_data)

        # Build supporting signals
        supporting = {
            "technical": technical_data.get("signals", []),
            "on_chain": onchain_data.get("signals", []),
            "fundamental": fundamental_data.get("signals", []),
            "sentiment": sentiment_data.get("signals", [])
        }

        result = SmartAssetScore(
            asset=asset,
            smart_asset_score=composite_score,
            dominant_driver=dominant,
            thesis=thesis,
            risks=risks,
            supporting_signals=supporting
        )

        # Log the analysis
        self._log_analysis(result, {
            "technical_score": technical_score,
            "onchain_score": onchain_score,
            "fundamental_score": fundamental_score,
            "sentiment_score": sentiment_score
        })

        return result

    def _get_technical_signals(self, asset: str, timeframe: str, days: int) -> Dict[str, Any]:
        """Gather technical analysis signals"""
        try:
            ohlcv = self.market_client.get_ohlcv(asset, timeframe, days)
            indicators = self.market_client.get_indicators(ohlcv)

            signals = []

            # RSI signals
            rsi = indicators.get("rsi", 50)
            if rsi < 30:
                signals.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                signals.append(f"RSI overbought ({rsi:.1f})")
            else:
                signals.append(f"RSI neutral ({rsi:.1f})")

            # MACD signals
            macd = indicators.get("macd", {})
            if macd.get("histogram", 0) > 0:
                signals.append("MACD bullish")
            else:
                signals.append("MACD bearish")

            # Trend signals
            ema_20 = indicators.get("ema_20")
            ema_50 = indicators.get("ema_50")
            current_price = indicators.get("close")

            if current_price and ema_20 and ema_50:
                if current_price > ema_20 > ema_50:
                    signals.append("Strong uptrend (price > EMA20 > EMA50)")
                elif current_price < ema_20 < ema_50:
                    signals.append("Strong downtrend (price < EMA20 < EMA50)")
                else:
                    signals.append("Trend consolidating")

            # Volatility
            atr_pct = indicators.get("atr_pct", 0)
            if atr_pct > 5:
                signals.append(f"High volatility ({atr_pct:.1f}% ATR)")
            elif atr_pct < 2:
                signals.append(f"Low volatility ({atr_pct:.1f}% ATR)")

            return {
                "data": indicators,
                "signals": signals,
                "score_factors": {
                    "trend_aligned": current_price > ema_20 if current_price and ema_20 else False,
                    "momentum_positive": macd.get("histogram", 0) > 0,
                    "not_overbought": rsi < 70,
                    "not_oversold": rsi > 30
                }
            }
        except Exception as e:
            return {"data": {}, "signals": [f"Technical data unavailable: {e}"], "score_factors": {}}

    def _get_onchain_signals(self, asset: str, days: int) -> Dict[str, Any]:
        """Gather on-chain analysis signals"""
        try:
            onchain = self.onchain_client.get_metrics(asset, days)
            signals = []

            # Whale activity
            whale_flow = onchain.get("whale_net_flow", 0)
            if whale_flow > 0:
                signals.append(f"Whale accumulation (+${whale_flow:,.0f})")
            elif whale_flow < 0:
                signals.append(f"Whale distribution (-${abs(whale_flow):,.0f})")

            # Exchange flows
            exchange_flow = onchain.get("exchange_net_flow", 0)
            if exchange_flow < 0:
                signals.append("Net outflow from exchanges (bullish)")
            elif exchange_flow > 0:
                signals.append("Net inflow to exchanges (bearish)")

            # Active addresses
            addr_growth = onchain.get("active_address_growth", 0)
            if addr_growth > 5:
                signals.append(f"Strong address growth (+{addr_growth:.1f}%)")
            elif addr_growth < -5:
                signals.append(f"Declining addresses ({addr_growth:.1f}%)")

            # Protocol metrics (for DeFi)
            tvl_change = onchain.get("tvl_change_pct", 0)
            if tvl_change > 10:
                signals.append(f"TVL growing (+{tvl_change:.1f}%)")
            elif tvl_change < -10:
                signals.append(f"TVL declining ({tvl_change:.1f}%)")

            return {
                "data": onchain,
                "signals": signals if signals else ["No significant on-chain signals"],
                "score_factors": {
                    "whale_accumulating": whale_flow > 0,
                    "exchange_outflow": exchange_flow < 0,
                    "address_growth": addr_growth > 0,
                    "tvl_healthy": tvl_change > -10
                }
            }
        except Exception as e:
            return {"data": {}, "signals": [f"On-chain data unavailable: {e}"], "score_factors": {}}

    def _get_fundamental_signals(self, asset: str) -> Dict[str, Any]:
        """Gather fundamental analysis signals"""
        try:
            fundamentals = self.text_client.get_fundamentals(asset)
            signals = []

            # Development activity
            dev_activity = fundamentals.get("github_commits_30d", 0)
            if dev_activity > 100:
                signals.append(f"High dev activity ({dev_activity} commits/30d)")
            elif dev_activity > 30:
                signals.append(f"Moderate dev activity ({dev_activity} commits/30d)")
            elif dev_activity > 0:
                signals.append(f"Low dev activity ({dev_activity} commits/30d)")

            # Team updates
            last_update = fundamentals.get("last_major_update_days", 999)
            if last_update < 30:
                signals.append("Recent major update")
            elif last_update > 90:
                signals.append("No major updates in 90+ days")

            # Tokenomics
            inflation_rate = fundamentals.get("annual_inflation_pct", 0)
            if inflation_rate > 10:
                signals.append(f"High inflation ({inflation_rate:.1f}%/yr)")
            elif inflation_rate < 2:
                signals.append(f"Low inflation ({inflation_rate:.1f}%/yr)")

            return {
                "data": fundamentals,
                "signals": signals if signals else ["Limited fundamental data"],
                "score_factors": {
                    "active_development": dev_activity > 30,
                    "recent_updates": last_update < 60,
                    "healthy_tokenomics": inflation_rate < 10
                }
            }
        except Exception as e:
            return {"data": {}, "signals": [f"Fundamental data unavailable: {e}"], "score_factors": {}}

    def _get_sentiment_signals(self, asset: str) -> Dict[str, Any]:
        """Gather sentiment analysis signals"""
        try:
            sentiment = self.text_client.get_sentiment(asset)
            signals = []

            # Overall sentiment score
            score = sentiment.get("composite_score", 50)
            if score > 70:
                signals.append(f"Very bullish sentiment ({score}/100)")
            elif score > 55:
                signals.append(f"Bullish sentiment ({score}/100)")
            elif score < 30:
                signals.append(f"Very bearish sentiment ({score}/100)")
            elif score < 45:
                signals.append(f"Bearish sentiment ({score}/100)")
            else:
                signals.append(f"Neutral sentiment ({score}/100)")

            # Social volume
            social_change = sentiment.get("social_volume_change_pct", 0)
            if social_change > 50:
                signals.append(f"Social volume spike (+{social_change:.0f}%)")
            elif social_change < -30:
                signals.append(f"Social volume declining ({social_change:.0f}%)")

            # Fear & Greed (if available)
            fear_greed = sentiment.get("fear_greed_index", 50)
            if fear_greed > 75:
                signals.append(f"Extreme greed ({fear_greed}) - caution")
            elif fear_greed < 25:
                signals.append(f"Extreme fear ({fear_greed}) - opportunity?")

            return {
                "data": sentiment,
                "signals": signals if signals else ["Sentiment data limited"],
                "score_factors": {
                    "positive_sentiment": score > 50,
                    "not_extreme_greed": fear_greed < 75,
                    "social_engagement": social_change > -20
                }
            }
        except Exception as e:
            return {"data": {}, "signals": [f"Sentiment data unavailable: {e}"], "score_factors": {}}

    def _score_technical(self, data: Dict[str, Any]) -> int:
        """Calculate technical score (0-100)"""
        factors = data.get("score_factors", {})
        score = 50  # Base score

        if factors.get("trend_aligned"):
            score += 15
        if factors.get("momentum_positive"):
            score += 15
        if factors.get("not_overbought"):
            score += 10
        if factors.get("not_oversold"):
            score += 10

        return min(100, max(0, score))

    def _score_onchain(self, data: Dict[str, Any]) -> int:
        """Calculate on-chain score (0-100)"""
        factors = data.get("score_factors", {})
        score = 50

        if factors.get("whale_accumulating"):
            score += 15
        if factors.get("exchange_outflow"):
            score += 15
        if factors.get("address_growth"):
            score += 10
        if factors.get("tvl_healthy"):
            score += 10

        return min(100, max(0, score))

    def _score_fundamental(self, data: Dict[str, Any]) -> int:
        """Calculate fundamental score (0-100)"""
        factors = data.get("score_factors", {})
        score = 50

        if factors.get("active_development"):
            score += 20
        if factors.get("recent_updates"):
            score += 15
        if factors.get("healthy_tokenomics"):
            score += 15

        return min(100, max(0, score))

    def _score_sentiment(self, data: Dict[str, Any]) -> int:
        """Calculate sentiment score (0-100)"""
        factors = data.get("score_factors", {})
        score = 50

        if factors.get("positive_sentiment"):
            score += 20
        if factors.get("not_extreme_greed"):
            score += 10
        if factors.get("social_engagement"):
            score += 10

        # Use raw sentiment score if available
        raw_score = data.get("data", {}).get("composite_score")
        if raw_score is not None:
            return raw_score

        return min(100, max(0, score))

    def _generate_thesis(
        self,
        asset: str,
        score: int,
        dominant: str,
        component_scores: Dict[str, int]
    ) -> str:
        """Generate a thesis statement based on analysis"""

        if score >= 70:
            outlook = "bullish"
            recommendation = "favorable for accumulation"
        elif score >= 55:
            outlook = "cautiously optimistic"
            recommendation = "suitable for measured positions"
        elif score >= 45:
            outlook = "neutral"
            recommendation = "requires patience; no clear edge"
        elif score >= 30:
            outlook = "cautious"
            recommendation = "reduce exposure or wait for better setup"
        else:
            outlook = "bearish"
            recommendation = "avoid new positions; protect capital"

        driver_map = {
            "technical": "price action and momentum",
            "on_chain": "on-chain activity and whale behavior",
            "fundamental": "project development and tokenomics",
            "sentiment": "market sentiment and social activity"
        }

        thesis = (
            f"{asset} scores {score}/100 with a {outlook} outlook. "
            f"The primary driver is {driver_map.get(dominant, dominant)} "
            f"(score: {component_scores.get(dominant, 0)}). "
            f"Current conditions are {recommendation}."
        )

        return thesis

    def _identify_risks(
        self,
        technical: Dict[str, Any],
        onchain: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> List[str]:
        """Identify key risks from all data streams"""
        risks = []

        # Technical risks
        tech_factors = technical.get("score_factors", {})
        if not tech_factors.get("not_overbought"):
            risks.append("Overbought conditions may lead to pullback")
        if not tech_factors.get("trend_aligned"):
            risks.append("Price below key moving averages")

        # On-chain risks
        onchain_factors = onchain.get("score_factors", {})
        if not onchain_factors.get("whale_accumulating"):
            risks.append("Whale distribution or lack of large buyer interest")
        if not onchain_factors.get("exchange_outflow"):
            risks.append("Exchange inflows suggest potential selling pressure")

        # Fundamental risks
        fund_factors = fundamental.get("score_factors", {})
        if not fund_factors.get("active_development"):
            risks.append("Low development activity may indicate stalled progress")
        if not fund_factors.get("healthy_tokenomics"):
            risks.append("High inflation or unfavorable token economics")

        # Sentiment risks
        sent_factors = sentiment.get("score_factors", {})
        if not sent_factors.get("not_extreme_greed"):
            risks.append("Extreme greed often precedes corrections")

        return risks if risks else ["No major risks identified; maintain standard caution"]

    def _log_analysis(self, result: SmartAssetScore, component_scores: Dict[str, int]):
        """Log analysis for audit trail"""
        log_entry = {
            "timestamp": result.timestamp,
            "asset": result.asset,
            "smart_asset_score": result.smart_asset_score,
            "component_scores": component_scores,
            "dominant_driver": result.dominant_driver,
            "thesis": result.thesis,
            "risks": result.risks
        }

        log_file = self.log_dir / f"{result.asset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)


# CLI interface
if __name__ == "__main__":
    import sys

    core = SynopticCore()

    asset = sys.argv[1] if len(sys.argv) > 1 else "BTC"
    print(f"\n{'='*60}")
    print(f"SYNOPTIC CORE - Analyzing {asset}")
    print('='*60)

    result = core.assess(asset)

    print(f"\nSmart Asset Score: {result.smart_asset_score}/100")
    print(f"Dominant Driver: {result.dominant_driver}")
    print(f"\nThesis:\n{result.thesis}")
    print(f"\nRisks:")
    for risk in result.risks:
        print(f"  - {risk}")
    print(f"\nSupporting Signals:")
    for category, signals in result.supporting_signals.items():
        print(f"  {category.upper()}:")
        for signal in signals:
            print(f"    - {signal}")
    print('='*60)

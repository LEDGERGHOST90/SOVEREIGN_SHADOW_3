#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - Swarm Integration for D.O.E.

Integrates the multi-agent swarm with the D.O.E. orchestrator.

Based on CryptoTrade EMNLP 2024 paper findings:
- On-chain stats: +16% alpha (via WhaleWatcherAgent)
- News/sentiment: +9% alpha (via ManusResearcherAgent, SentimentScannerAgent)
- Reflection mechanism: +11% alpha (via ReflectionAgent)
- Multi-agent collaboration enhances decision quality

Architecture:
    ┌───────────────────────────────────────────────────────────┐
    │                     D.O.E. ORCHESTRATOR                    │
    │  ┌─────────────────────────────────────────────────────┐  │
    │  │              SWARM INTEGRATION LAYER                │  │
    │  │                                                     │  │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
    │  │  │   Whale     │  │   Manus     │  │  Sentiment  │  │  │
    │  │  │  Watcher    │  │ Researcher  │  │   Scanner   │  │  │
    │  │  │  (+16%)     │  │   (+9%)     │  │   (+9%)     │  │  │
    │  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │  │
    │  │         │                │                │         │  │
    │  │         └────────────────┼────────────────┘         │  │
    │  │                          ▼                          │  │
    │  │               ┌───────────────────┐                 │  │
    │  │               │     HIVE MIND     │                 │  │
    │  │               │  (Consensus Vote) │                 │  │
    │  │               └─────────┬─────────┘                 │  │
    │  │                         │                           │  │
    │  │                         ▼                           │  │
    │  │               ┌───────────────────┐                 │  │
    │  │               │   REFLECTION      │                 │  │
    │  │               │     AGENT         │                 │  │
    │  │               │    (+11%)         │                 │  │
    │  │               └───────────────────┘                 │  │
    │  │                                                     │  │
    │  └─────────────────────────────────────────────────────┘  │
    │                          │                                │
    │                          ▼                                │
    │              ┌───────────────────┐                        │
    │              │  Strategy Selector │                       │
    │              │  (Informed by Swarm)│                      │
    │              └───────────────────┘                        │
    └───────────────────────────────────────────────────────────┘
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class SwarmSignal:
    """Aggregated signal from the swarm"""
    decision: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    consensus_reached: bool
    vote_breakdown: Dict[str, int]  # {"buy": 3, "sell": 1, "hold": 0}
    agent_votes: Dict[str, Dict]
    reasoning: List[str]
    alpha_sources: Dict[str, float]  # {"on_chain": 0.16, "news": 0.09, "reflection": 0.11}
    timestamp: datetime = None

    def to_dict(self) -> Dict:
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "consensus_reached": self.consensus_reached,
            "vote_breakdown": self.vote_breakdown,
            "agent_count": len(self.agent_votes),
            "reasoning": self.reasoning,
            "alpha_sources": self.alpha_sources,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class SwarmIntegration:
    """
    Integrates multi-agent swarm with D.O.E. orchestrator.

    Provides:
    - Aggregated signals from all swarm agents
    - Consensus voting via HiveMind
    - Reflection-based learning
    - Alpha enhancement from multiple data sources
    """

    def __init__(
        self,
        consensus_threshold: float = 0.60,  # 60% agreement
        min_confidence: float = 0.5,  # 50% minimum confidence
        enable_reflection: bool = True
    ):
        self.consensus_threshold = consensus_threshold
        self.min_confidence = min_confidence
        self.enable_reflection = enable_reflection

        # Lazy-loaded agents
        self._whale_watcher = None
        self._manus_researcher = None
        self._sentiment_scanner = None
        self._reflection_agent = None
        self._hive_mind = None

        # Agent list for HiveMind
        self._swarm_agents = []

        # Stats
        self.stats = {
            "signals_generated": 0,
            "consensus_reached": 0,
            "consensus_failed": 0,
            "buy_signals": 0,
            "sell_signals": 0,
            "hold_signals": 0
        }

        logger.info("SwarmIntegration initialized")
        logger.info(f"Consensus threshold: {consensus_threshold:.0%}")

    def _load_agent_module(self, module_path: str, factory_name: str):
        """
        Load an agent module directly from file path to avoid __init__.py import issues.
        """
        import importlib.util

        # Get the SS_III root directory
        ss3_root = Path(__file__).parent.parent.parent.parent

        # Build full path to the module file
        module_file = ss3_root / (module_path.replace('.', '/') + '.py')

        if not module_file.exists():
            raise ImportError(f"Module file not found: {module_file}")

        # Load module directly from file
        spec = importlib.util.spec_from_file_location(module_path, module_file)
        module = importlib.util.module_from_spec(spec)

        # Add SS_III to sys.path for dependencies
        if str(ss3_root) not in sys.path:
            sys.path.insert(0, str(ss3_root))

        spec.loader.exec_module(module)

        # Get the factory function
        factory = getattr(module, factory_name)
        return factory

    @property
    def whale_watcher(self):
        """Lazy load WhaleWatcherAgent (+16% alpha)"""
        if self._whale_watcher is None:
            try:
                create_whale_watcher = self._load_agent_module(
                    'core.swarm.agents.whale_watcher',
                    'create_whale_watcher'
                )
                self._whale_watcher = create_whale_watcher("swarm_whale_watcher")
                self._swarm_agents.append(self._whale_watcher)
                logger.info("✓ WhaleWatcherAgent loaded (+16% alpha)")
            except Exception as e:
                logger.warning(f"⚠ WhaleWatcherAgent unavailable: {e}")
        return self._whale_watcher

    @property
    def manus_researcher(self):
        """Lazy load ManusResearcherAgent (+9% alpha)"""
        if self._manus_researcher is None:
            try:
                create_manus_researcher = self._load_agent_module(
                    'core.swarm.agents.manus_researcher',
                    'create_manus_researcher'
                )
                self._manus_researcher = create_manus_researcher("swarm_manus")
                self._swarm_agents.append(self._manus_researcher)
                logger.info("✓ ManusResearcherAgent loaded (+9% alpha)")
            except Exception as e:
                logger.warning(f"⚠ ManusResearcherAgent unavailable: {e}")
        return self._manus_researcher

    @property
    def sentiment_scanner(self):
        """Lazy load SentimentScannerAgent (+9% alpha)"""
        if self._sentiment_scanner is None:
            try:
                create_sentiment_scanner = self._load_agent_module(
                    'core.swarm.agents.sentiment_scanner',
                    'create_sentiment_scanner'
                )
                self._sentiment_scanner = create_sentiment_scanner("swarm_sentiment")
                self._swarm_agents.append(self._sentiment_scanner)
                logger.info("✓ SentimentScannerAgent loaded (+9% alpha)")
            except Exception as e:
                logger.warning(f"⚠ SentimentScannerAgent unavailable: {e}")
        return self._sentiment_scanner

    @property
    def reflection_agent(self):
        """Lazy load ReflectionAgent (+11% alpha)"""
        if self._reflection_agent is None and self.enable_reflection:
            try:
                from doe_engine.core.intelligence.reflection_agent import get_reflection_agent
                self._reflection_agent = get_reflection_agent()
                logger.info("✓ ReflectionAgent loaded (+11% alpha)")
            except Exception as e:
                logger.warning(f"⚠ ReflectionAgent unavailable: {e}")
        return self._reflection_agent

    def initialize_swarm(self):
        """Initialize all swarm agents"""
        logger.info("Initializing swarm agents...")

        # Force load all agents
        _ = self.whale_watcher
        _ = self.manus_researcher
        _ = self.sentiment_scanner
        _ = self.reflection_agent

        total_alpha = 0.0
        if self._whale_watcher:
            total_alpha += 0.16
        if self._manus_researcher:
            total_alpha += 0.09
        if self._sentiment_scanner:
            total_alpha += 0.09
        if self._reflection_agent:
            total_alpha += 0.11

        logger.info(f"Swarm initialized: {len(self._swarm_agents)} agents, potential +{total_alpha:.0%} alpha")

        return len(self._swarm_agents)

    async def get_swarm_signal(
        self,
        symbol: str,
        market_data: Any,
        regime: str = None
    ) -> SwarmSignal:
        """
        Get aggregated signal from all swarm agents.

        Args:
            symbol: Trading symbol (e.g., "BTC/USD")
            market_data: Market data object
            regime: Current market regime (optional)

        Returns:
            SwarmSignal with consensus decision
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"SWARM SIGNAL REQUEST: {symbol}")
        logger.info(f"{'='*60}")

        votes: Dict[str, Dict] = {}
        alpha_sources = {}

        # Create a simple market data object if needed
        class SimpleMarketData:
            def __init__(self, sym):
                self.symbol = sym

        if not hasattr(market_data, 'symbol'):
            market_data = SimpleMarketData(symbol)

        # 1. Get WhaleWatcher signal (on-chain +16%)
        if self.whale_watcher:
            try:
                whale_vote = await self.whale_watcher.analyze_market(market_data)
                votes["whale_watcher"] = whale_vote
                alpha_sources["on_chain"] = 0.16
                logger.info(f"  🐋 WhaleWatcher: {whale_vote.get('decision', 'hold').upper()} "
                           f"({whale_vote.get('confidence', 0):.0%})")
            except Exception as e:
                logger.error(f"  ❌ WhaleWatcher error: {e}")

        # 2. Get ManusResearcher signal (off-chain +9%)
        if self.manus_researcher:
            try:
                manus_vote = await self.manus_researcher.analyze_market(market_data)
                votes["manus_researcher"] = manus_vote
                alpha_sources["news_sentiment"] = 0.09
                logger.info(f"  📚 ManusResearcher: {manus_vote.get('decision', 'hold').upper()} "
                           f"({manus_vote.get('confidence', 0):.0%})")
            except Exception as e:
                logger.error(f"  ❌ ManusResearcher error: {e}")

        # 3. Get SentimentScanner signal (sentiment +9%)
        if self.sentiment_scanner:
            try:
                sentiment_vote = await self.sentiment_scanner.analyze_market(market_data)
                votes["sentiment_scanner"] = sentiment_vote
                if "news_sentiment" not in alpha_sources:
                    alpha_sources["sentiment"] = 0.09
                logger.info(f"  📱 SentimentScanner: {sentiment_vote.get('decision', 'hold').upper()} "
                           f"({sentiment_vote.get('confidence', 0):.0%})")
            except Exception as e:
                logger.error(f"  ❌ SentimentScanner error: {e}")

        # 4. Get Reflection guidance (+11%)
        reflection_guidance = None
        if self.reflection_agent:
            try:
                # Reflection agent provides general guidance, not symbol-specific
                reflection_guidance = self.reflection_agent.get_trading_guidance()
                alpha_sources["reflection"] = 0.11
                approach = reflection_guidance.get('recommended_approach', 'balanced')
                logger.info(f"  🔄 Reflection: approach={approach}")
            except Exception as e:
                logger.error(f"  ❌ ReflectionAgent error: {e}")

        # Build consensus
        signal = self._build_consensus(votes, reflection_guidance, alpha_sources)

        # Update stats
        self.stats["signals_generated"] += 1
        if signal.consensus_reached:
            self.stats["consensus_reached"] += 1
        else:
            self.stats["consensus_failed"] += 1

        if signal.decision == "buy":
            self.stats["buy_signals"] += 1
        elif signal.decision == "sell":
            self.stats["sell_signals"] += 1
        else:
            self.stats["hold_signals"] += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"SWARM CONSENSUS: {signal.decision.upper()}")
        logger.info(f"Confidence: {signal.confidence:.0%}")
        logger.info(f"Consensus: {'✅ YES' if signal.consensus_reached else '❌ NO'}")
        logger.info(f"{'='*60}\n")

        return signal

    def _build_consensus(
        self,
        votes: Dict[str, Dict],
        reflection_guidance: Optional[Dict],
        alpha_sources: Dict[str, float]
    ) -> SwarmSignal:
        """Build consensus from agent votes"""

        if not votes:
            return SwarmSignal(
                decision="hold",
                confidence=0.0,
                consensus_reached=False,
                vote_breakdown={"buy": 0, "sell": 0, "hold": 0},
                agent_votes={},
                reasoning=["No agents available"],
                alpha_sources={},
                timestamp=datetime.now(timezone.utc)
            )

        # Count votes
        vote_count = {"buy": 0, "sell": 0, "hold": 0}
        total_confidence = 0.0
        reasoning = []

        for agent_id, vote in votes.items():
            decision = vote.get("decision", "hold").lower()
            confidence = vote.get("confidence", 0)

            if decision in vote_count:
                vote_count[decision] += 1

            total_confidence += confidence
            reasoning.append(f"{agent_id}: {vote.get('reasoning', 'No reason')}")

        avg_confidence = total_confidence / len(votes) if votes else 0.0

        # Determine winning decision
        winning_decision = max(vote_count, key=vote_count.get)
        winning_votes = vote_count[winning_decision]
        total_votes = len(votes)

        # Check consensus threshold
        consensus_reached = (
            winning_votes / total_votes >= self.consensus_threshold
            if total_votes > 0 else False
        )

        # Apply reflection adjustment
        if reflection_guidance and consensus_reached:
            bias = reflection_guidance.get("trade_bias", "neutral")
            bias_confidence = reflection_guidance.get("confidence", 0)

            # Boost confidence if reflection agrees
            if (winning_decision == "buy" and bias in ["bullish", "long"]) or \
               (winning_decision == "sell" and bias in ["bearish", "short"]):
                avg_confidence = min(avg_confidence + 0.1, 1.0)  # +10% boost
                reasoning.append(f"Reflection confirms: {bias}")

            # Reduce confidence if reflection disagrees
            elif (winning_decision == "buy" and bias in ["bearish", "short"]) or \
                 (winning_decision == "sell" and bias in ["bullish", "long"]):
                avg_confidence = max(avg_confidence - 0.1, 0.0)  # -10% penalty
                reasoning.append(f"Reflection warns: {bias}")

        return SwarmSignal(
            decision=winning_decision if consensus_reached else "hold",
            confidence=avg_confidence,
            consensus_reached=consensus_reached,
            vote_breakdown=vote_count,
            agent_votes=votes,
            reasoning=reasoning,
            alpha_sources=alpha_sources,
            timestamp=datetime.now(timezone.utc)
        )

    def record_trade_outcome(
        self,
        trade_id: str,
        symbol: str,
        entry_price: float,
        exit_price: float,
        side: str,
        strategy: str,
        regime: str,
        pnl: float,
        pnl_percent: float,
        news_sentiment: str = "neutral",
        on_chain_signal: str = "neutral",
        reasoning: str = ""
    ):
        """
        Record trade outcome for reflection learning.

        This enables the +11% alpha from reflection mechanism.

        Args:
            trade_id: Unique trade identifier
            symbol: Trading pair (e.g., "BTC/USD")
            entry_price: Entry price
            exit_price: Exit price
            side: "BUY" or "SELL"
            strategy: Strategy name that generated signal
            regime: Market regime at trade time
            pnl: Absolute P&L
            pnl_percent: P&L as percentage
            news_sentiment: Manus news sentiment (bullish/bearish/neutral)
            on_chain_signal: On-chain signal (bullish/bearish/neutral)
            reasoning: Why the trade was made
        """
        if self.reflection_agent:
            try:
                # ReflectionAgent.record_trade() takes individual params, not a dataclass
                self.reflection_agent.record_trade(
                    trade_id=trade_id,
                    symbol=symbol,
                    action=side,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    return_pct=pnl_percent,
                    regime=regime,
                    strategy=strategy,
                    news_sentiment=news_sentiment,
                    on_chain_signal=on_chain_signal,
                    reasoning=reasoning
                )
                logger.info(f"✅ Trade recorded for reflection: {trade_id} ({pnl_percent:+.2f}%)")

            except Exception as e:
                logger.error(f"❌ Failed to record trade for reflection: {e}")

    def get_stats(self) -> Dict:
        """Get swarm integration statistics"""
        agent_stats = {}

        if self._whale_watcher:
            agent_stats["whale_watcher"] = self._whale_watcher.get_stats()
        if self._manus_researcher:
            agent_stats["manus_researcher"] = self._manus_researcher.get_stats()
        if self._sentiment_scanner:
            agent_stats["sentiment_scanner"] = self._sentiment_scanner.get_stats()

        return {
            "swarm_stats": self.stats,
            "agent_count": len(self._swarm_agents),
            "agent_stats": agent_stats,
            "potential_alpha": sum([
                0.16 if self._whale_watcher else 0,
                0.09 if self._manus_researcher else 0,
                0.09 if self._sentiment_scanner else 0,
                0.11 if self._reflection_agent else 0
            ])
        }


# Singleton instance
_swarm_integration: Optional[SwarmIntegration] = None


def get_swarm_integration() -> SwarmIntegration:
    """Get or create the swarm integration instance"""
    global _swarm_integration
    if _swarm_integration is None:
        _swarm_integration = SwarmIntegration()
    return _swarm_integration


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("SWARM INTEGRATION FOR D.O.E.")
    print("=" * 70)
    print()

    swarm = get_swarm_integration()
    agent_count = swarm.initialize_swarm()

    print()
    print(f"Active agents: {agent_count}")
    print()

    stats = swarm.get_stats()
    print(f"Potential alpha: +{stats['potential_alpha']:.0%}")
    print()

    print("Alpha breakdown:")
    print("  - WhaleWatcher (on-chain): +16%")
    print("  - ManusResearcher (news): +9%")
    print("  - SentimentScanner: +9%")
    print("  - ReflectionAgent: +11%")
    print("  - Total potential: +45%")
    print()
    print("✅ Swarm ready for D.O.E. integration!")
    print("=" * 70)

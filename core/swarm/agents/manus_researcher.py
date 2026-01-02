#!/usr/bin/env python3
"""
MANUS RESEARCH AGENT
Integrates Manus AI research into the swarm for off-chain intelligence
Part of the Autonomous Trading Colony

Sovereign Shadow III - Off-Chain Intelligence Layer

Based on CryptoTrade EMNLP 2024 paper findings:
- News/sentiment provides +9% alpha improvement
- Multi-agent collaboration enhances decision quality
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class ManusResearchSignal:
    """Research signal from Manus AI"""
    query: str
    analysis: str
    sentiment: str  # "bullish", "bearish", "neutral"
    confidence: float  # 0.0 to 1.0
    sources_cited: List[str]
    key_findings: List[str]
    recommendations: List[str]
    timestamp: datetime = None


class ManusResearcherAgent:
    """
    Specialized Agent: Manus Researcher

    Strategy: Off-chain intelligence gathering
    - Deep web research with Manus AI
    - News and sentiment analysis
    - Scholarly source aggregation
    - Market narrative tracking

    Based on CryptoTrade paper: News sentiment adds +9% alpha

    Capital Allocation: 15% (medium-high impact signals)
    Personality: patient_observer (waits for quality research)
    """

    def __init__(self, agent_id: str = "manus_researcher"):
        self.agent_id = agent_id
        self.specialty = "off_chain_research"
        self.personality = "patient_observer"
        self.capital_allocation = 0.15
        self.state = "initializing"

        # Research clients (lazy load to avoid import errors)
        self._manus_client = None
        self._research_swarm = None

        # Cache for research results
        self.research_cache: Dict[str, ManusResearchSignal] = {}
        self.cache_ttl_seconds = 300  # 5 minute cache

        # Performance tracking
        self.stats = {
            "research_completed": 0,
            "bullish_signals": 0,
            "bearish_signals": 0,
            "neutral_signals": 0,
            "avg_confidence": 0.0,
            "sources_total": 0
        }

        logger.info(f"📚 Created ManusResearcher agent '{agent_id}'")

    @property
    def manus_client(self):
        """Lazy load Manus client"""
        if self._manus_client is None:
            try:
                from core.integrations.manus_client import ManusClient
                self._manus_client = ManusClient()
                logger.info("   ✓ Manus client initialized")
            except Exception as e:
                logger.warning(f"   ⚠ Manus client unavailable: {e}")
        return self._manus_client

    @property
    def research_swarm(self):
        """Lazy load Research Swarm"""
        if self._research_swarm is None:
            try:
                from core.integrations.research_swarm import ResearchSwarm
                self._research_swarm = ResearchSwarm()
                logger.info("   ✓ Research swarm initialized")
            except Exception as e:
                logger.warning(f"   ⚠ Research swarm unavailable: {e}")
        return self._research_swarm

    async def initialize(self):
        """Initialize the manus researcher"""
        self.state = "active"
        return True

    async def research_asset(
        self,
        symbol: str,
        focus_areas: List[str] = None
    ) -> Optional[ManusResearchSignal]:
        """
        Perform deep research on an asset using Manus AI

        Args:
            symbol: Asset symbol (e.g., "BTC", "LINK")
            focus_areas: Specific areas to research

        Returns:
            ManusResearchSignal with findings
        """
        if focus_areas is None:
            focus_areas = ["price_drivers", "sentiment", "news", "fundamentals"]

        # Check cache first
        cache_key = f"{symbol}_{'-'.join(focus_areas)}"
        if cache_key in self.research_cache:
            cached = self.research_cache[cache_key]
            age = (datetime.now(timezone.utc) - cached.timestamp).total_seconds()
            if age < self.cache_ttl_seconds:
                logger.info(f"   📚 Using cached research for {symbol}")
                return cached

        # Build research query
        query = f"""
        Research {symbol} for trading decision:

        FOCUS AREAS:
        {chr(10).join(f'- {area}' for area in focus_areas)}

        REQUIREMENTS:
        1. Current market sentiment (bullish/bearish/neutral)
        2. Recent news and developments
        3. Key price drivers
        4. Risk factors
        5. Trading recommendation with confidence level

        Provide evidence-based analysis with source citations.
        """

        try:
            if self.research_swarm:
                # Use full research swarm (Manus + Gemini + DS-Star)
                result = self.research_swarm.research(
                    query=query,
                    asset=symbol,
                    wait_for_manus=False  # Don't block
                )

                # Parse result
                signal = self._parse_swarm_result(symbol, result)

            elif self.manus_client:
                # Fallback to Manus only
                task = self.manus_client.create_task(
                    prompt=query,
                    agent_profile='manus-1.6-max',
                    task_mode='agent'
                )

                # Return pending signal
                signal = ManusResearchSignal(
                    query=query,
                    analysis=f"Research pending: task_id={task.get('task_id')}",
                    sentiment="neutral",
                    confidence=0.5,
                    sources_cited=[],
                    key_findings=["Research in progress"],
                    recommendations=["Wait for Manus completion"],
                    timestamp=datetime.now(timezone.utc)
                )
            else:
                logger.warning("No research clients available")
                return None

            # Cache the result
            self.research_cache[cache_key] = signal

            # Update stats
            self.stats["research_completed"] += 1
            if signal.sentiment == "bullish":
                self.stats["bullish_signals"] += 1
            elif signal.sentiment == "bearish":
                self.stats["bearish_signals"] += 1
            else:
                self.stats["neutral_signals"] += 1

            self.stats["sources_total"] += len(signal.sources_cited)

            # Update running average confidence
            total = self.stats["research_completed"]
            old_avg = self.stats["avg_confidence"]
            self.stats["avg_confidence"] = (old_avg * (total - 1) + signal.confidence) / total

            return signal

        except Exception as e:
            logger.error(f"Research error for {symbol}: {e}")
            return None

    def _parse_swarm_result(self, symbol: str, result: Dict) -> ManusResearchSignal:
        """Parse ResearchSwarm result into ManusResearchSignal"""

        # Extract from synthesis
        synthesis = result.get('synthesis', {})
        raw = result.get('raw_results', {})

        # Determine sentiment from analysis
        sentiment = "neutral"
        gemini = raw.get('gemini', {})
        analysis = gemini.get('analysis', '')

        analysis_lower = analysis.lower()
        bullish_words = ['bullish', 'upward', 'positive', 'buy', 'accumulate', 'growth']
        bearish_words = ['bearish', 'downward', 'negative', 'sell', 'distribute', 'decline']

        bullish_count = sum(1 for w in bullish_words if w in analysis_lower)
        bearish_count = sum(1 for w in bearish_words if w in analysis_lower)

        if bullish_count > bearish_count + 2:
            sentiment = "bullish"
        elif bearish_count > bullish_count + 2:
            sentiment = "bearish"

        # Extract confidence
        confidence = synthesis.get('confidence', 50.0) / 100.0

        # Extract sources
        sources = synthesis.get('scholarly_refs', [])

        # Extract findings
        findings = synthesis.get('key_findings', [])
        if not findings and analysis:
            # Try to extract key findings from analysis
            for line in analysis.split('\n'):
                if line.strip().startswith('- ') or line.strip().startswith('* '):
                    findings.append(line.strip()[2:])
                if len(findings) >= 5:
                    break

        # Extract recommendations
        recommendations = synthesis.get('recommendations', [])

        return ManusResearchSignal(
            query=result.get('query', ''),
            analysis=analysis[:2000] if analysis else "No analysis available",
            sentiment=sentiment,
            confidence=confidence,
            sources_cited=sources[:10],
            key_findings=findings[:5],
            recommendations=recommendations[:3],
            timestamp=datetime.now(timezone.utc)
        )

    async def analyze_market(self, market_data) -> Dict:
        """
        Analyze market using off-chain research

        This is the main entry point for HiveMind voting.
        Returns signal if significant research findings.
        """
        symbol = market_data.symbol.replace('/USD', '').replace('/USDT', '')

        # Perform research
        signal = await self.research_asset(symbol)

        if signal:
            self.stats["research_completed"] += 1

            # Convert sentiment to trading decision
            if signal.sentiment == "bullish" and signal.confidence > 0.6:
                return {
                    "decision": "buy",
                    "confidence": signal.confidence,
                    "reasoning": f"Manus research bullish: {signal.key_findings[0] if signal.key_findings else 'Strong sentiment'}",
                    "source": "manus_research"
                }
            elif signal.sentiment == "bearish" and signal.confidence > 0.6:
                return {
                    "decision": "sell",
                    "confidence": signal.confidence,
                    "reasoning": f"Manus research bearish: {signal.key_findings[0] if signal.key_findings else 'Weak sentiment'}",
                    "source": "manus_research"
                }

        return {
            "decision": "hold",
            "confidence": 0.0,
            "reasoning": "Insufficient off-chain signal"
        }

    async def get_narrative_analysis(self, topic: str) -> Dict[str, Any]:
        """
        Analyze market narrative around a topic

        Useful for understanding macro trends and narratives
        """
        query = f"""
        Analyze the current market narrative around: {topic}

        Cover:
        1. Dominant narrative threads
        2. Sentiment shift over past week
        3. Influencer opinions
        4. Institutional perspective
        5. Retail sentiment

        Rate narrative strength: strong/moderate/weak
        Rate consensus: high/medium/low/divided
        """

        if self.manus_client:
            try:
                task = self.manus_client.create_task(
                    prompt=query,
                    agent_profile='manus-1.6-max',
                    task_mode='agent'
                )
                return {
                    "status": "dispatched",
                    "task_id": task.get('task_id'),
                    "topic": topic
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {"status": "unavailable", "reason": "Manus client not initialized"}

    def get_stats(self) -> Dict:
        """Get manus researcher statistics"""
        return {
            "agent_id": self.agent_id,
            "specialty": self.specialty,
            **self.stats,
            "cache_size": len(self.research_cache)
        }


def create_manus_researcher(agent_id: str = "manus_researcher") -> ManusResearcherAgent:
    """Factory function to create manus researcher agent"""
    return ManusResearcherAgent(agent_id=agent_id)


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("📚 MANUS RESEARCHER AGENT")
    print("=" * 70)
    print()

    agent = create_manus_researcher()
    stats = agent.get_stats()

    print(f"Agent ID: {stats['agent_id']}")
    print(f"Specialty: {stats['specialty']}")
    print()
    print("Strategy: Off-chain intelligence via Manus AI")
    print("Capital Allocation: 15%")
    print()
    print("Capabilities:")
    print("  - Deep web research with Manus AI")
    print("  - Multi-AI synthesis (Manus + Gemini + DS-Star)")
    print("  - News and sentiment aggregation")
    print("  - Narrative analysis")
    print()
    print("✅ Manus Researcher ready for off-chain intelligence!")
    print("=" * 70)

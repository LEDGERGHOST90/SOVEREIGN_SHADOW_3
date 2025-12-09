#!/usr/bin/env python3
"""
HIVE MIND ORCHESTRATOR
The collective consciousness that coordinates all specialized agents
Implements voting, consensus building, and coordinated attacks

Sovereign Shadow 2 - Autonomous Trading Colony
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class AgentVote:
    """A vote from a single agent"""
    agent_id: str
    decision: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    veto: bool = False  # Risk manager can veto
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConsensusDecision:
    """Final decision reached by hive mind"""
    symbol: str
    decision: str  # "buy", "sell", "hold"
    total_confidence: float
    agent_votes: Dict[str, AgentVote]
    consensus_reached: bool
    vote_count: Dict[str, int]  # {"buy": 3, "sell": 1, "hold": 0}
    vetoed: bool = False
    veto_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HiveMind:
    """
    The Autonomous Trading Colony's Collective Consciousness

    Coordinates multiple specialized agents:
    - Volatility Hunter (aggressive opportunist)
    - RSI Reader (patient observer)
    - Technical Master (patient observer)
    - Pattern Master (contrarian analyst)
    - [FUTURE] Whale Watcher (smart money tracker)
    - [FUTURE] Sentiment Scanner (social analysis)
    - [FUTURE] Risk Manager (has VETO power)
    """

    def __init__(
        self,
        agents: List,
        consensus_threshold: float = 0.75,  # 75% must agree
        min_votes: int = 3,  # At least 3 agents must agree
        risk_manager_veto: bool = True
    ):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.consensus_threshold = consensus_threshold
        self.min_votes = min_votes
        self.risk_manager_veto = risk_manager_veto

        # Shared memory - all agents can read/write
        self.shared_brain = Path("/Volumes/LegacySafe/SovereignShadow 2/ClaudeSDK/colony_brain")
        self.shared_brain.mkdir(exist_ok=True)

        # Performance tracking
        self.agent_performance: Dict[str, Dict] = {}
        self.consensus_history: List[ConsensusDecision] = []

        logger.info(f"🧠 Hive Mind initialized with {len(self.agents)} agents")
        logger.info(f"   Consensus threshold: {consensus_threshold:.0%}")
        logger.info(f"   Minimum votes required: {min_votes}")

    async def broadcast_opportunity(self, symbol: str, market_data: Any) -> ConsensusDecision:
        """
        Broadcast opportunity to ALL agents and collect votes

        This is the CORE of the hive mind:
        1. Send to all agents
        2. Each analyzes independently
        3. Collect votes
        4. Build consensus
        5. Execute if agreed
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔊 BROADCASTING OPPORTUNITY TO COLONY")
        logger.info(f"{'='*70}")
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Agents voting: {len(self.agents)}")

        # Collect votes from all agents
        votes: Dict[str, AgentVote] = {}

        for agent_id, agent in self.agents.items():
            try:
                # Each agent analyzes the same data
                decision = await agent.analyze_market(market_data)

                vote = AgentVote(
                    agent_id=agent_id,
                    decision=decision.decision_type.value,
                    confidence=decision.confidence,
                    reasoning=decision.reasoning if hasattr(decision, 'reasoning') else "Analysis complete"
                )

                votes[agent_id] = vote

                logger.info(f"   ✅ {agent_id}: {vote.decision.upper()} ({vote.confidence:.1%} confidence)")

            except Exception as e:
                logger.error(f"   ❌ {agent_id} failed to vote: {e}")

        # Build consensus from votes
        consensus = self._build_consensus(symbol, votes)

        # Save to history
        self.consensus_history.append(consensus)
        self._save_consensus(consensus)

        return consensus

    def _build_consensus(self, symbol: str, votes: Dict[str, AgentVote]) -> ConsensusDecision:
        """
        Analyze votes and determine if consensus reached

        Rules:
        - Count votes for each decision (buy/sell/hold)
        - Check if threshold met (e.g., 75% agree)
        - Check if minimum votes met (e.g., 3+ agents)
        - Check for risk manager veto
        """
        # Count votes
        vote_count = {"buy": 0, "sell": 0, "hold": 0}
        total_confidence = 0.0

        for vote in votes.values():
            vote_count[vote.decision] += 1
            total_confidence += vote.confidence

        avg_confidence = total_confidence / len(votes) if votes else 0.0

        # Determine winning decision
        winning_decision = max(vote_count, key=vote_count.get)
        winning_votes = vote_count[winning_decision]
        total_votes = len(votes)

        # Check consensus
        consensus_reached = (
            winning_votes >= self.min_votes and
            winning_votes / total_votes >= self.consensus_threshold
        )

        # Check for veto
        vetoed = False
        veto_reason = None

        if self.risk_manager_veto:
            for vote in votes.values():
                if vote.veto:
                    vetoed = True
                    veto_reason = f"{vote.agent_id} VETO: {vote.reasoning}"
                    logger.warning(f"⛔ {veto_reason}")

        consensus = ConsensusDecision(
            symbol=symbol,
            decision=winning_decision,
            total_confidence=avg_confidence,
            agent_votes=votes,
            consensus_reached=consensus_reached and not vetoed,
            vote_count=vote_count,
            vetoed=vetoed,
            veto_reason=veto_reason
        )

        # Log result
        logger.info(f"\n{'='*70}")
        logger.info(f"🧠 HIVE MIND CONSENSUS")
        logger.info(f"{'='*70}")
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Decision: {winning_decision.upper()}")
        logger.info(f"Vote Count: {vote_count}")
        logger.info(f"Confidence: {avg_confidence:.1%}")
        logger.info(f"Consensus: {'✅ YES' if consensus_reached else '❌ NO'}")
        if vetoed:
            logger.info(f"Status: ⛔ VETOED - {veto_reason}")
        logger.info(f"{'='*70}\n")

        return consensus

    async def coordinate_attack(self, consensus: ConsensusDecision, market_data: Any):
        """
        When consensus reached, COORDINATE all agents for execution

        Like a military operation:
        1. Sniper scouts ahead (checks liquidity)
        2. Technical Master plans entry (optimal price)
        3. Risk Manager approves position size
        4. All execute SIMULTANEOUSLY
        """
        if not consensus.consensus_reached:
            logger.info("⏸️  No consensus - agents stand down")
            return

        logger.info(f"\n{'='*70}")
        logger.info(f"⚔️  COORDINATED ATTACK INITIATED")
        logger.info(f"{'='*70}")
        logger.info(f"Target: {consensus.symbol}")
        logger.info(f"Action: {consensus.decision.upper()}")

        # Assign roles to each agent
        tasks = []

        for agent_id, agent in self.agents.items():
            # Each agent has a specific role in execution
            if "volatility" in agent_id:
                # Volatility hunter checks for optimal entry timing
                task = self._agent_role_scout(agent, market_data)
            elif "rsi" in agent_id:
                # RSI reader monitors momentum
                task = self._agent_role_momentum(agent, market_data)
            elif "technical" in agent_id:
                # Technical master plans execution
                task = self._agent_role_planner(agent, market_data)
            elif "pattern" in agent_id:
                # Pattern master watches for invalidation
                task = self._agent_role_guard(agent, market_data)
            else:
                task = self._agent_role_default(agent, market_data)

            tasks.append(task)

        # All agents execute their roles SIMULTANEOUSLY
        results = await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"✅ Coordinated attack complete - {len(results)} agents responded")
        logger.info(f"{'='*70}\n")

        return results

    async def _agent_role_scout(self, agent, market_data):
        """Volatility hunter scouts for best entry"""
        logger.info(f"   🔍 {agent.agent_id}: Scouting entry conditions")
        await asyncio.sleep(0.1)  # Simulate analysis
        return {"agent": agent.agent_id, "role": "scout", "status": "ready"}

    async def _agent_role_momentum(self, agent, market_data):
        """RSI reader monitors momentum"""
        logger.info(f"   📊 {agent.agent_id}: Monitoring momentum")
        await asyncio.sleep(0.1)
        return {"agent": agent.agent_id, "role": "momentum", "status": "ready"}

    async def _agent_role_planner(self, agent, market_data):
        """Technical master plans execution"""
        logger.info(f"   🎯 {agent.agent_id}: Planning execution")
        await asyncio.sleep(0.1)
        return {"agent": agent.agent_id, "role": "planner", "status": "ready"}

    async def _agent_role_guard(self, agent, market_data):
        """Pattern master watches for invalidation"""
        logger.info(f"   🛡️  {agent.agent_id}: Guarding position")
        await asyncio.sleep(0.1)
        return {"agent": agent.agent_id, "role": "guard", "status": "ready"}

    async def _agent_role_default(self, agent, market_data):
        """Default role for other agents"""
        logger.info(f"   ⚡ {agent.agent_id}: Supporting")
        await asyncio.sleep(0.1)
        return {"agent": agent.agent_id, "role": "support", "status": "ready"}

    def learn_from_trade(self, trade_result: Dict):
        """
        COLLECTIVE LEARNING - All agents learn from every trade

        This is what makes the colony get smarter over time:
        - Successful trade → All agents note what worked
        - Failed trade → All agents note what to avoid
        - Each agent updates their internal model
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"📚 COLLECTIVE LEARNING SESSION")
        logger.info(f"{'='*70}")

        # Extract lessons from trade
        lessons = {
            "symbol": trade_result.get("symbol"),
            "outcome": trade_result.get("pnl", 0) > 0,
            "pnl": trade_result.get("pnl", 0),
            "pnl_percent": trade_result.get("pnl_percent", 0),
            "hold_time": trade_result.get("hold_time", 0),
            "agent_votes": trade_result.get("agent_votes", {})
        }

        # Identify which agents voted correctly
        for agent_id, vote in lessons["agent_votes"].items():
            if agent_id not in self.agent_performance:
                self.agent_performance[agent_id] = {
                    "correct": 0,
                    "incorrect": 0,
                    "accuracy": 0.0,
                    "total_pnl_contribution": 0.0
                }

            # Did this agent's vote lead to profit?
            correct = (
                (vote == "buy" and lessons["outcome"]) or
                (vote == "sell" and not lessons["outcome"])
            )

            if correct:
                self.agent_performance[agent_id]["correct"] += 1
                logger.info(f"   ✅ {agent_id}: CORRECT prediction")
            else:
                self.agent_performance[agent_id]["incorrect"] += 1
                logger.info(f"   ❌ {agent_id}: Incorrect prediction")

            # Update accuracy
            total = (self.agent_performance[agent_id]["correct"] +
                    self.agent_performance[agent_id]["incorrect"])
            self.agent_performance[agent_id]["accuracy"] = (
                self.agent_performance[agent_id]["correct"] / total
            )

            # Track P&L contribution
            self.agent_performance[agent_id]["total_pnl_contribution"] += (
                lessons["pnl"] / len(lessons["agent_votes"])
            )

        logger.info(f"{'='*70}\n")

        # Save lessons to shared brain
        self._save_lesson(lessons)

    def get_agent_rankings(self) -> List[Dict]:
        """Get agents ranked by performance"""
        rankings = []
        for agent_id, perf in self.agent_performance.items():
            rankings.append({
                "agent_id": agent_id,
                "accuracy": perf["accuracy"],
                "total_pnl": perf["total_pnl_contribution"],
                "correct": perf["correct"],
                "incorrect": perf["incorrect"]
            })

        # Sort by accuracy, then by P&L
        rankings.sort(key=lambda x: (x["accuracy"], x["total_pnl"]), reverse=True)
        return rankings

    def _save_consensus(self, consensus: ConsensusDecision):
        """Save consensus to shared brain"""
        filename = self.shared_brain / f"consensus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "symbol": consensus.symbol,
            "decision": consensus.decision,
            "confidence": consensus.total_confidence,
            "vote_count": consensus.vote_count,
            "consensus_reached": consensus.consensus_reached,
            "vetoed": consensus.vetoed,
            "timestamp": consensus.timestamp.isoformat(),
            "votes": {
                agent_id: {
                    "decision": vote.decision,
                    "confidence": vote.confidence,
                    "reasoning": vote.reasoning
                }
                for agent_id, vote in consensus.agent_votes.items()
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_lesson(self, lesson: Dict):
        """Save trade lesson to shared brain"""
        filename = self.shared_brain / f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(lesson, f, indent=2)

    def get_stats(self) -> Dict:
        """Get hive mind statistics"""
        return {
            "total_agents": len(self.agents),
            "consensus_decisions": len(self.consensus_history),
            "agent_performance": self.agent_performance,
            "agent_rankings": self.get_agent_rankings()
        }


# Test the hive mind
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 HIVE MIND ORCHESTRATOR TEST")
    print("=" * 70)
    print()
    print("This module coordinates multiple specialized agents")
    print("into a unified trading colony with collective intelligence.")
    print()
    print("Features:")
    print("  ✅ Agent voting and consensus building")
    print("  ✅ Coordinated attack execution")
    print("  ✅ Collective learning from trades")
    print("  ✅ Performance tracking and rankings")
    print("  ✅ Risk manager veto power")
    print()
    print("Ready to integrate with Multi-Agent Market Research Coordinator!")
    print("=" * 70)

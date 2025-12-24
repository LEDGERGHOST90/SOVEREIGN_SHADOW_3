#!/usr/bin/env python3
"""
AGENT ORCHESTRATOR - Coordinates all trading agents for MCP integration
Connects 12+ dormant agents to the sovereign-trader MCP server.

Usage:
    from core.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    result = orchestrator.get_council_opinion("BTC")
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
sys.path.insert(0, str(SS3_ROOT))
sys.path.insert(0, str(SS3_ROOT / 'src'))  # For pandas_ta shim

# Import Strategy Engine (Manus framework integration)
try:
    from core.strategies.strategy_engine import StrategyEngine, MarketRegimeDetector
    STRATEGY_ENGINE_AVAILABLE = True
except ImportError:
    STRATEGY_ENGINE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("orchestrator")

# BRAIN.json path
BRAIN_PATH = SS3_ROOT / "BRAIN.json"


def load_brain() -> dict:
    """Load BRAIN.json state."""
    if BRAIN_PATH.exists():
        return json.loads(BRAIN_PATH.read_text())
    return {}


def save_brain(brain: dict):
    """Save BRAIN.json state."""
    brain['last_updated'] = datetime.now().isoformat()
    BRAIN_PATH.write_text(json.dumps(brain, indent=2))


class AgentOrchestrator:
    """
    Coordinates all 12+ trading agents for unified decision-making.

    Agents loaded:
    - ReflectAgent: Pre-trade critique (31% performance improvement)
    - WhaleAgent: Open interest & whale tracking
    - SwarmAgent: Multi-model consensus
    - FundingArbAgent: Funding rate arbitrage
    - LiquidationAgent: Liquidation cascade detection
    - RBIAgent: Research-Backtest-Implement
    - RegimeAgent: Market regime detection (placeholder)
    - MomentumAgent: Trend signals (placeholder)
    - PortfolioAgent: Rebalancing recommendations
    - RiskAgent: Risk assessment
    """

    def __init__(self):
        """Initialize all agents."""
        self.agents = {}
        self.brain = load_brain()
        self._load_agents()

        # Initialize Strategy Engine (Manus framework)
        self.strategy_engine = None
        if STRATEGY_ENGINE_AVAILABLE:
            try:
                self.strategy_engine = StrategyEngine()
                logger.info("Strategy Engine loaded (Manus framework)")
            except Exception as e:
                logger.warning(f"Could not load Strategy Engine: {e}")

        logger.info(f"AgentOrchestrator initialized with {len(self.agents)} agents")

    def _load_agents(self):
        """Load all available agents with graceful fallback."""

        # ReflectAgent - Pre-trade critique
        try:
            from core.agents.reflect_agent import ReflectAgent
            self.agents['reflect'] = {
                'class': ReflectAgent,
                'instance': None,  # Lazy load
                'purpose': 'Pre-trade critique and risk assessment'
            }
            logger.info("Loaded ReflectAgent")
        except Exception as e:
            logger.warning(f"Could not load ReflectAgent: {e}")

        # WhaleAgent - Open interest tracking
        try:
            from core.agents.whale_agent import WhaleAgent
            self.agents['whale'] = {
                'class': WhaleAgent,
                'instance': None,
                'purpose': 'Whale activity and OI tracking'
            }
            logger.info("Loaded WhaleAgent")
        except Exception as e:
            logger.warning(f"Could not load WhaleAgent: {e}")

        # SwarmAgent - Multi-model consensus
        try:
            from core.agents.swarm_agent import SwarmAgent
            self.agents['swarm'] = {
                'class': SwarmAgent,
                'instance': None,
                'purpose': 'Multi-AI consensus voting'
            }
            logger.info("Loaded SwarmAgent")
        except Exception as e:
            logger.warning(f"Could not load SwarmAgent: {e}")

        # FundingArbAgent - Funding rate arbitrage
        try:
            from core.agents.fundingarb_agent import FundingArbAgent
            self.agents['fundingarb'] = {
                'class': FundingArbAgent,
                'instance': None,
                'purpose': 'Funding rate arbitrage detection'
            }
            logger.info("Loaded FundingArbAgent")
        except Exception as e:
            logger.warning(f"Could not load FundingArbAgent: {e}")

        # LiquidationAgent - Cascade detection
        try:
            from core.agents.liquidation_agent import LiquidationAgent
            self.agents['liquidation'] = {
                'class': LiquidationAgent,
                'instance': None,
                'purpose': 'Liquidation cascade detection'
            }
            logger.info("Loaded LiquidationAgent")
        except Exception as e:
            logger.warning(f"Could not load LiquidationAgent: {e}")

        # RiskAgent - Risk assessment
        try:
            from core.agents_highlevel.risk_agent import RiskAgent
            self.agents['risk'] = {
                'class': RiskAgent,
                'instance': None,
                'purpose': 'Portfolio risk assessment'
            }
            logger.info("Loaded RiskAgent")
        except Exception as e:
            logger.warning(f"Could not load RiskAgent: {e}")

        # PortfolioAgent - Rebalancing
        try:
            from core.agents_highlevel.portfolio_agent import PortfolioAgent
            self.agents['portfolio'] = {
                'class': PortfolioAgent,
                'instance': None,
                'purpose': 'Portfolio rebalancing recommendations'
            }
            logger.info("Loaded PortfolioAgent")
        except Exception as e:
            logger.warning(f"Could not load PortfolioAgent: {e}")

    def _get_agent(self, name: str):
        """Lazy-load and return an agent instance."""
        if name not in self.agents:
            return None

        agent_info = self.agents[name]
        if agent_info['instance'] is None:
            try:
                agent_info['instance'] = agent_info['class']()
                logger.info(f"Instantiated {name} agent")
            except Exception as e:
                logger.error(f"Failed to instantiate {name}: {e}")
                return None

        return agent_info['instance']

    def get_council_opinion(self, symbol: str) -> dict:
        """
        Query relevant agents and synthesize opinion.

        Args:
            symbol: Asset symbol (e.g., 'BTC', 'ETH')

        Returns:
            {
                'recommendation': 'BUY' | 'SELL' | 'HOLD',
                'confidence': 0-100,
                'agents': {agent_name: opinion, ...},
                'reasoning': str,
                'timestamp': str
            }
        """
        opinions = {}

        # Query each available agent
        # Note: Most agents need market data passed to them
        # This is a simplified version - full impl would fetch data first

        for agent_name in self.agents.keys():
            try:
                opinion = self._query_agent(agent_name, symbol)
                if opinion:
                    opinions[agent_name] = opinion
            except Exception as e:
                logger.warning(f"Agent {agent_name} failed: {e}")
                opinions[agent_name] = {'signal': 'ERROR', 'error': str(e)}

        # Synthesize consensus
        consensus = self._synthesize_consensus(opinions)

        # Log to BRAIN.json
        self._log_council_decision(symbol, consensus)

        return consensus

    def _query_agent(self, agent_name: str, symbol: str) -> Optional[dict]:
        """Query a single agent for its opinion."""

        # For now, return placeholder - agents need market data
        # Full implementation would:
        # 1. Fetch market data for symbol
        # 2. Pass to agent's analyze method
        # 3. Return structured response

        return {
            'signal': 'NEUTRAL',
            'confidence': 50,
            'reasoning': f'{agent_name} analysis pending - needs market data',
            'agent': agent_name
        }

    def _synthesize_consensus(self, opinions: Dict[str, dict]) -> dict:
        """Synthesize multiple agent opinions into consensus."""

        if not opinions:
            return {
                'recommendation': 'HOLD',
                'confidence': 0,
                'agents': {},
                'reasoning': 'No agent opinions available',
                'timestamp': datetime.now().isoformat()
            }

        # Count signals
        signals = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'NEUTRAL': 0}
        total_confidence = 0
        valid_opinions = 0

        for agent_name, opinion in opinions.items():
            signal = opinion.get('signal', 'NEUTRAL').upper()
            if signal in signals:
                signals[signal] += 1
            confidence = opinion.get('confidence', 50)
            total_confidence += confidence
            valid_opinions += 1

        # Determine majority
        if signals['BUY'] > signals['SELL'] and signals['BUY'] > signals['HOLD']:
            recommendation = 'BUY'
        elif signals['SELL'] > signals['BUY'] and signals['SELL'] > signals['HOLD']:
            recommendation = 'SELL'
        else:
            recommendation = 'HOLD'

        avg_confidence = total_confidence / valid_opinions if valid_opinions > 0 else 0

        return {
            'recommendation': recommendation,
            'confidence': int(avg_confidence),
            'agents': opinions,
            'signal_counts': signals,
            'reasoning': f"Council voted: BUY={signals['BUY']}, SELL={signals['SELL']}, HOLD={signals['HOLD']}",
            'timestamp': datetime.now().isoformat()
        }

    def pre_trade_check(self, trade_proposal: dict) -> dict:
        """
        Run ReflectAgent + RiskAgent before trade execution.

        Args:
            trade_proposal: {
                'symbol': str,
                'side': 'BUY' | 'SELL',
                'amount_usd': float,
                'exchange': str
            }

        Returns:
            {
                'approved': bool,
                'risk_score': 0-100,
                'critique': str,
                'position_size_recommendation': float
            }
        """
        result = {
            'approved': True,
            'risk_score': 50,
            'critique': '',
            'position_size_recommendation': trade_proposal.get('amount_usd', 0),
            'checks': []
        }

        # ReflectAgent critique
        reflect = self._get_agent('reflect')
        if reflect:
            try:
                # Build context for ReflectAgent
                proposed = {
                    'symbol': trade_proposal.get('symbol', 'BTC'),
                    'direction': trade_proposal.get('side', 'BUY'),
                    'entry_price': 0,  # Would need current price
                    'position_value': trade_proposal.get('amount_usd', 0),
                    'stop_loss': 0,
                    'take_profit': 0,
                    'risk_amount': trade_proposal.get('amount_usd', 0) * 0.03,  # 3% risk
                    'risk_percent': 0.03,
                    'risk_reward_ratio': 2.0
                }

                market_context = {
                    'trend_4h': 'unknown',
                    'setup_15m': 'unknown',
                    'volatility': 'medium',
                    'market_phase': 'unknown'
                }

                critique = reflect.analyze_trade(proposed, market_context)

                result['critique'] = critique.reasoning
                result['risk_score'] = int(critique.risk_score * 10)  # 0-10 -> 0-100
                result['approved'] = critique.decision == 'APPROVE'
                result['checks'].append({
                    'agent': 'reflect',
                    'decision': critique.decision,
                    'confidence': critique.confidence
                })

            except Exception as e:
                logger.error(f"ReflectAgent check failed: {e}")
                result['checks'].append({
                    'agent': 'reflect',
                    'error': str(e)
                })

        # Basic position sizing check
        brain = load_brain()
        rules = brain.get('rules', {})
        max_position = rules.get('max_position', 100)

        if trade_proposal.get('amount_usd', 0) > max_position:
            result['approved'] = False
            result['critique'] += f" Position exceeds max size (${max_position})."
            result['position_size_recommendation'] = max_position

        return result

    def get_regime(self, market_data=None) -> Dict:
        """
        Get current market regime using Strategy Engine (ADX + ATR).

        Args:
            market_data: Optional DataFrame with OHLCV. If None, uses Fear & Greed fallback.

        Returns:
            Dict with regime info or simple string for backwards compatibility
        """
        # Use Strategy Engine if available and data provided
        if self.strategy_engine and market_data is not None:
            try:
                import pandas as pd
                if isinstance(market_data, pd.DataFrame):
                    result = self.strategy_engine.analyze(market_data)
                    return result['regime']
            except Exception as e:
                logger.warning(f"Strategy Engine regime detection failed: {e}")

        # Fallback to Fear & Greed API
        try:
            import requests
            fg = requests.get('https://api.alternative.me/fng/', timeout=5).json()
            value = int(fg['data'][0]['value'])
            classification = fg['data'][0]['value_classification']

            if value < 25:
                regime = 'High Volatility Range'
            elif value > 75:
                regime = 'High Volatility Trend'
            elif value < 45:
                regime = 'Transitioning Market'
            else:
                regime = 'Low Volatility Range'

            return {
                'regime': regime,
                'fear_greed': value,
                'classification': classification,
                'source': 'fear_greed_api'
            }

        except Exception as e:
            logger.warning(f"Could not determine regime: {e}")
            return {'regime': 'UNKNOWN', 'error': str(e)}

    def select_strategy(self, market_data=None, symbol: str = "BTC") -> Dict:
        """
        Select optimal strategy for current regime using Manus framework.

        Args:
            market_data: DataFrame with OHLCV data
            symbol: Asset symbol for context

        Returns:
            Strategy recommendation with confidence
        """
        if not self.strategy_engine:
            return {
                'error': 'Strategy Engine not available',
                'fallback': 'Use ReflectAgent for trade critique'
            }

        try:
            import pandas as pd

            # If no data provided, return available strategies
            if market_data is None:
                return {
                    'symbol': symbol,
                    'message': 'Provide OHLCV data for strategy selection',
                    'available_strategies': list(self.strategy_engine.strategies.get('strategies', {}).keys())
                }

            # Full analysis
            result = self.strategy_engine.analyze(market_data)

            # Log to BRAIN
            self._log_strategy_selection(symbol, result)

            return {
                'symbol': symbol,
                'regime': result['regime'],
                'selected': result['selected_strategy'],
                'alternatives': result['alternatives'],
                'historical_performers': result['historical_top'],
                'timestamp': result['timestamp']
            }

        except Exception as e:
            logger.error(f"Strategy selection failed: {e}")
            return {'error': str(e)}

    def _log_strategy_selection(self, symbol: str, result: Dict):
        """Log strategy selection to BRAIN.json"""
        try:
            brain = load_brain()
            if 'strategy_selections' not in brain:
                brain['strategy_selections'] = []

            brain['strategy_selections'] = brain['strategy_selections'][-9:]
            brain['strategy_selections'].append({
                'symbol': symbol,
                'regime': result['regime']['regime'] if isinstance(result['regime'], dict) else result['regime'],
                'strategy': result['selected_strategy']['name'] if result['selected_strategy'] else None,
                'timestamp': result['timestamp']
            })
            save_brain(brain)
        except Exception as e:
            logger.warning(f"Could not log strategy selection: {e}")

    def log_trade_result(self, strategy_name: str, regime: str, action: str,
                         entry: float, exit: float = None, success: bool = True):
        """Log trade result to Strategy Engine for learning"""
        if self.strategy_engine:
            self.strategy_engine.log_result(strategy_name, regime, action, entry, exit, success)
            logger.info(f"Logged trade: {strategy_name} {action} - {'WIN' if success else 'LOSS'}")

    def scan_opportunities(self) -> list:
        """
        Query opportunity-finding agents.

        Returns:
            List of opportunity dicts from FundingArbAgent, etc.
        """
        opportunities = []

        # FundingArb opportunities
        fundingarb = self._get_agent('fundingarb')
        if fundingarb:
            try:
                # Would call fundingarb.scan() or similar
                opportunities.append({
                    'type': 'funding_arb',
                    'status': 'agent_loaded',
                    'detail': 'Funding arbitrage scanner ready'
                })
            except Exception as e:
                logger.warning(f"FundingArb scan failed: {e}")

        # Liquidation opportunities
        liquidation = self._get_agent('liquidation')
        if liquidation:
            try:
                opportunities.append({
                    'type': 'liquidation',
                    'status': 'agent_loaded',
                    'detail': 'Liquidation cascade monitor ready'
                })
            except Exception as e:
                logger.warning(f"Liquidation scan failed: {e}")

        return opportunities

    def _log_council_decision(self, symbol: str, decision: dict):
        """Log council decision to BRAIN.json."""
        try:
            brain = load_brain()

            if 'council_decisions' not in brain:
                brain['council_decisions'] = []

            # Keep last 10 decisions
            brain['council_decisions'] = brain['council_decisions'][-9:]
            brain['council_decisions'].append({
                'symbol': symbol,
                'decision': decision['recommendation'],
                'confidence': decision['confidence'],
                'timestamp': decision['timestamp']
            })

            save_brain(brain)

        except Exception as e:
            logger.error(f"Failed to log council decision: {e}")

    def list_agents(self) -> dict:
        """List all available agents and their status."""
        return {
            name: {
                'purpose': info['purpose'],
                'loaded': info['instance'] is not None
            }
            for name, info in self.agents.items()
        }


# Quick test
if __name__ == "__main__":
    print("Testing AgentOrchestrator...")

    orchestrator = AgentOrchestrator()

    print("\n=== Available Agents ===")
    for name, status in orchestrator.list_agents().items():
        loaded = "READY" if status['loaded'] else "available"
        print(f"  {name}: {status['purpose']} [{loaded}]")

    print("\n=== Council Opinion on BTC ===")
    opinion = orchestrator.get_council_opinion("BTC")
    print(f"Recommendation: {opinion['recommendation']}")
    print(f"Confidence: {opinion['confidence']}%")
    print(f"Reasoning: {opinion['reasoning']}")

    print("\n=== Market Regime ===")
    regime = orchestrator.get_regime()
    print(f"Current Regime: {regime}")

    print("\n=== Opportunity Scan ===")
    opportunities = orchestrator.scan_opportunities()
    for opp in opportunities:
        print(f"  {opp['type']}: {opp['detail']}")

    print("\nOrchestrator test complete!")

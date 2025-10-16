"""
🧠 ShadowSynapse - AI Reasoning & Orchestration Layer

The "brain" of the empire - coordinates all Shadow SDK modules and makes
intelligent trading decisions based on market intelligence, signals, and sentiment.

Philosophy: "Fearless. Bold. Smiling through chaos."
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("shadow_sdk.synapse")


class ShadowSynapse:
    """
    🧠 ShadowSynapse - AI Orchestration Layer
    
    The central intelligence coordinating ShadowScope, ShadowPulse, and ShadowSnaps
    to make optimal trading decisions.
    
    Features:
        - Multi-signal fusion (price + sentiment + momentum)
        - Strategy selection and routing
        - Risk assessment and position sizing
        - Trade execution coordination
        - Performance tracking and learning
    
    Example:
        >>> synapse = ShadowSynapse()
        >>> synapse.connect_scope(shadow_scope)
        >>> synapse.connect_pulse(shadow_pulse)
        >>> synapse.connect_snaps(shadow_snaps)
        >>> decision = await synapse.analyze_opportunity(signal)
    """
    
    def __init__(self):
        """Initialize ShadowSynapse AI orchestration layer."""
        self.scope = None  # ShadowScope instance
        self.pulse = None  # ShadowPulse instance
        self.snaps = None  # ShadowSnaps instance
        
        self.decisions_made = 0
        self.trades_executed = 0
        self.total_profit = 0.0
        self.win_rate = 0.0
        
        self.decision_history: List[Dict[str, Any]] = []
        
        logger.info("🧠 ShadowSynapse initialized")
    
    def connect_scope(self, scope):
        """Connect to ShadowScope intelligence layer."""
        self.scope = scope
        logger.info("🔗 ShadowScope connected to Synapse")
    
    def connect_pulse(self, pulse):
        """Connect to ShadowPulse signal layer."""
        self.pulse = pulse
        logger.info("🔗 ShadowPulse connected to Synapse")
    
    def connect_snaps(self, snaps):
        """Connect to ShadowSnaps sentiment layer."""
        self.snaps = snaps
        logger.info("🔗 ShadowSnaps connected to Synapse")
    
    async def analyze_opportunity(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a trading opportunity using all available intelligence.
        
        Args:
            signal: Trading signal from ShadowPulse
        
        Returns:
            Trading decision with strategy, risk parameters, and execution plan
        """
        self.decisions_made += 1
        
        # Gather intelligence from all layers
        market_intel = await self._gather_market_intelligence(signal)
        sentiment = await self._gather_sentiment(signal)
        risk_assessment = await self._assess_risk(signal, market_intel, sentiment)
        
        # Make trading decision
        decision = await self._make_decision(signal, market_intel, sentiment, risk_assessment)
        
        # Store in history
        self.decision_history.append(decision)
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
        
        logger.info(f"🧠 Decision #{self.decisions_made}: {decision['action']} {signal['pair']} - Confidence: {decision['confidence']:.2%}")
        
        return decision
    
    async def _gather_market_intelligence(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Gather market intelligence from ShadowScope."""
        if not self.scope:
            return {"available": False}
        
        try:
            intel = await self.scope.get_market_intelligence()
            pair = signal.get('pair', 'BTC/USD')
            
            return {
                "available": True,
                "volatility": intel['volatility'],
                "volumes": intel['volumes'],
                "vwap": intel['vwap'].get(pair, 0),
                "correlations": intel['correlations']
            }
        except Exception as e:
            logger.error(f"❌ Failed to gather market intelligence: {e}")
            return {"available": False}
    
    async def _gather_sentiment(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Gather sentiment from ShadowSnaps."""
        if not self.snaps:
            return {"available": False}
        
        try:
            pair = signal.get('pair', 'BTC/USD')
            asset = pair.split('/')[0]  # Extract base asset
            sentiment = await self.snaps.get_sentiment(asset)
            
            return {
                "available": True,
                "score": sentiment['score'],
                "magnitude": sentiment['magnitude'],
                "trending": sentiment['trending']
            }
        except Exception as e:
            logger.error(f"❌ Failed to gather sentiment: {e}")
            return {"available": False}
    
    async def _assess_risk(self, signal: Dict[str, Any], market_intel: Dict[str, Any], sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for the trading opportunity."""
        from . import MAX_POSITION_SIZE, STOP_LOSS_PERCENT
        
        # Base risk score
        risk_score = 0.5  # Neutral
        
        # Adjust for volatility
        if market_intel.get('available'):
            # Higher volatility = higher risk
            risk_score += 0.1  # Simplified
        
        # Adjust for sentiment
        if sentiment.get('available'):
            # Strong sentiment reduces risk for trend-following
            if abs(sentiment['score']) > 0.7:
                risk_score -= 0.1
        
        # Adjust for spread size
        spread = signal.get('spread', 0)
        if spread < 0.001:  # < 0.1%
            risk_score += 0.2  # Higher risk for tiny spreads
        
        # Calculate position size based on risk
        base_position = 100  # Base $100 position
        risk_multiplier = 1.0 - risk_score  # Lower risk = larger position
        position_size = min(base_position * risk_multiplier, MAX_POSITION_SIZE)
        
        return {
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
            "position_size": position_size,
            "stop_loss": STOP_LOSS_PERCENT,
            "max_loss": position_size * STOP_LOSS_PERCENT
        }
    
    async def _make_decision(self, signal: Dict[str, Any], market_intel: Dict[str, Any], 
                            sentiment: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        """Make final trading decision."""
        
        # Calculate confidence score
        confidence = self._calculate_confidence(signal, market_intel, sentiment, risk)
        
        # Determine action
        action = "execute" if confidence > 0.6 and risk['risk_score'] < 0.7 else "pass"
        
        # Select strategy
        strategy = self._select_strategy(signal, risk)
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "signal": signal,
            "strategy": strategy,
            "confidence": confidence,
            "risk_assessment": risk,
            "market_intel": market_intel['available'],
            "sentiment": sentiment['available'],
            "reasoning": self._generate_reasoning(action, confidence, risk)
        }
        
        return decision
    
    def _calculate_confidence(self, signal: Dict[str, Any], market_intel: Dict[str, Any],
                             sentiment: Dict[str, Any], risk: Dict[str, Any]) -> float:
        """Calculate confidence score for the decision."""
        confidence = signal.get('confidence', 0.5)
        
        # Boost confidence if we have complete intel
        if market_intel.get('available'):
            confidence += 0.1
        if sentiment.get('available') and sentiment['trending']:
            confidence += 0.1
        
        # Reduce confidence for high risk
        if risk['risk_score'] > 0.7:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _select_strategy(self, signal: Dict[str, Any], risk: Dict[str, Any]) -> str:
        """Select optimal trading strategy."""
        signal_type = signal.get('type', 'unknown')
        spread = signal.get('spread', 0)
        
        if signal_type == 'micro_movement' and spread < 0.001:
            return "Micro Movement Scalp"
        elif spread >= 0.025:
            return "Cross-Exchange Arbitrage"
        elif spread >= 0.002:
            return "Coinbase-OKX Arbitrage"
        else:
            return "Bid-Ask Spread Scalp"
    
    def _generate_reasoning(self, action: str, confidence: float, risk: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the decision."""
        if action == "execute":
            return f"High confidence ({confidence:.2%}) with {risk['risk_level']} risk. Executing with ${risk['position_size']:.2f} position."
        else:
            return f"Passing on opportunity - confidence {confidence:.2%} below threshold or risk too high ({risk['risk_level']})."
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "decisions_made": self.decisions_made,
            "trades_executed": self.trades_executed,
            "total_profit": self.total_profit,
            "win_rate": self.win_rate,
            "recent_decisions": self.decision_history[-10:] if self.decision_history else []
        }
    
    def update_performance(self, trade_result: Dict[str, Any]):
        """Update performance metrics after trade execution."""
        self.trades_executed += 1
        self.total_profit += trade_result.get('profit', 0)
        
        # Update win rate
        if trade_result.get('success'):
            wins = sum(1 for d in self.decision_history if d.get('result', {}).get('success'))
            self.win_rate = wins / self.trades_executed if self.trades_executed > 0 else 0
        
        logger.info(f"📊 Performance updated: {self.trades_executed} trades, ${self.total_profit:.2f} profit, {self.win_rate:.1%} win rate")


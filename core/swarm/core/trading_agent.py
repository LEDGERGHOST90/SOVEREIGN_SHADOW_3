#!/usr/bin/env python3
"""
Core Trading Agent - The foundation of the AI Agent Trading Ecosystem
Built on your existing modular architecture
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json

# Import from correct path - exchange_interfaces is in core/exchanges/
try:
    from core.exchanges.interfaces import BaseModule, EventBus
except ImportError:
    # Fallback: Define minimal stubs if interfaces not available
    from abc import ABC, abstractmethod
    from typing import Any

    class BaseModule(ABC):
        """Base class for all system modules"""
        @abstractmethod
        async def process(self, input_data: Any) -> Any:
            pass
        @abstractmethod
        async def initialize(self) -> bool:
            pass
        @abstractmethod
        async def shutdown(self) -> None:
            pass

    class EventBus(ABC):
        """Abstract event bus stub"""
        pass

# DIContainer was imported but never used - removed

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Agent operational states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    LEARNING = "learning"
    EVOLVING = "evolving"
    ERROR = "error"

class DecisionType(Enum):
    """Types of trading decisions"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NO_OP = "no_op"

@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    exchange: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None

@dataclass
class TradingDecision:
    """Agent trading decision"""
    agent_id: str
    decision_type: DecisionType
    symbol: str
    amount: float
    price: float
    confidence: float
    reasoning: str
    timestamp: datetime
    expected_profit: Optional[float] = None
    risk_score: Optional[float] = None

@dataclass
class PerformanceMetrics:
    """Agent performance tracking"""
    total_trades: int = 0
    profitable_trades: int = 0
    total_profit: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_profit_per_trade: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class AgentBrain(ABC):
    """Abstract agent brain for decision making"""
    
    @abstractmethod
    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Analyze market data and return insights"""
        pass
    
    @abstractmethod
    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Learn from trading outcomes"""
        pass

class SimpleAgentBrain(AgentBrain):
    """Simple agent brain implementation"""
    
    def __init__(self, personality: str):
        self.personality = personality
        self.learning_rate = 0.01
        self.memory = []
        
    async def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """Simple analysis based on personality"""
        analysis = {
            "price_trend": "neutral",
            "volume_trend": "normal",
            "volatility": "medium",
            "sentiment": "neutral",
            "confidence": 0.5
        }
        
        # Personality-based adjustments
        if self.personality == "aggressive_opportunist":
            analysis["confidence"] = min(analysis["confidence"] * 1.2, 1.0)
        elif self.personality == "patient_observer":
            analysis["confidence"] = max(analysis["confidence"] * 0.8, 0.1)
            
        return analysis
    
    async def learn(self, outcome: Dict[str, Any]) -> None:
        """Simple learning mechanism"""
        self.memory.append(outcome)
        # Keep only last 1000 outcomes
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]

class TradingAgent(BaseModule):
    """
    Core Trading Agent - The foundation of the AI ecosystem
    Extends your existing BaseModule architecture
    """
    
    def __init__(self, agent_id: str, personality: str, specialization: str):
        super().__init__()
        self.agent_id = agent_id
        self.personality = personality
        self.specialization = specialization
        self.state = AgentState.INITIALIZING
        self.capital_allocation = 0.0
        self.is_active = True
        
        # Core components
        self.brain = SimpleAgentBrain(personality)
        self.performance = PerformanceMetrics()
        
        # Agent metadata
        self.created_at = datetime.now(timezone.utc)
        self.last_decision = None
        self.decision_count = 0
        
        logger.info(f"Created agent {agent_id} with personality {personality} and specialization {specialization}")
    
    async def process(self, input_data: Any) -> Any:
        """
        Main processing method - implements BaseModule interface
        This is where the agent makes trading decisions
        """
        if not self.is_active or self.state != AgentState.ACTIVE:
            return None
            
        try:
            # Convert input to MarketData if needed
            if isinstance(input_data, dict):
                market_data = self._dict_to_market_data(input_data)
            elif isinstance(input_data, MarketData):
                market_data = input_data
            else:
                logger.warning(f"Unknown input data type: {type(input_data)}")
                return None
            
            # Make trading decision
            decision = await self._make_decision(market_data)
            
            # Update performance
            await self._update_performance(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in agent {self.agent_id} process: {e}")
            self.state = AgentState.ERROR
            return None
    
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            self.state = AgentState.INITIALIZING
            # Agent initialization logic here
            self.state = AgentState.ACTIVE
            logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            self.state = AgentState.ERROR
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the agent"""
        try:
            self.state = AgentState.PAUSED
            self.is_active = False
            logger.info(f"Agent {self.agent_id} shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down agent {self.agent_id}: {e}")
    
    async def _make_decision(self, market_data: MarketData) -> TradingDecision:
        """Core decision-making logic"""
        
        # 1. Analyze market data
        analysis = await self.brain.analyze(market_data)
        
        # 2. Apply specialization strategy
        signal = await self._apply_strategy(analysis, market_data)
        
        # 3. Apply personality filters
        decision = await self._apply_personality_filters(signal, market_data)
        
        # 4. Store decision
        self.last_decision = decision
        self.decision_count += 1
        
        return decision
    
    async def _apply_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Apply specialization-specific strategy"""
        
        if self.specialization == "arbitrage":
            return await self._arbitrage_strategy(analysis, market_data)
        elif self.specialization == "momentum":
            return await self._momentum_strategy(analysis, market_data)
        elif self.specialization == "mean_reversion":
            return await self._mean_reversion_strategy(analysis, market_data)
        else:
            return {"action": "hold", "confidence": 0.5, "reasoning": "Unknown specialization"}
    
    async def _arbitrage_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Arbitrage trading strategy"""
        # Simple arbitrage logic - look for price discrepancies
        if market_data.bid and market_data.ask:
            spread = market_data.ask - market_data.bid
            spread_percent = (spread / market_data.price) * 100
            
            if spread_percent > 0.1:  # 0.1% spread threshold
                return {
                    "action": "buy",
                    "confidence": min(analysis["confidence"] * 1.5, 1.0),
                    "reasoning": f"Arbitrage opportunity: {spread_percent:.3f}% spread",
                    "expected_profit": spread_percent
                }
        
        return {"action": "hold", "confidence": 0.3, "reasoning": "No arbitrage opportunity"}
    
    async def _momentum_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Momentum trading strategy"""
        # Simple momentum logic
        if analysis["price_trend"] == "up" and analysis["volume_trend"] == "high":
            return {
                "action": "buy",
                "confidence": analysis["confidence"],
                "reasoning": "Momentum signal: price up, volume high"
            }
        elif analysis["price_trend"] == "down" and analysis["volume_trend"] == "high":
            return {
                "action": "sell",
                "confidence": analysis["confidence"],
                "reasoning": "Momentum signal: price down, volume high"
            }
        
        return {"action": "hold", "confidence": 0.4, "reasoning": "No clear momentum signal"}
    
    async def _mean_reversion_strategy(self, analysis: Dict[str, Any], market_data: MarketData) -> Dict[str, Any]:
        """Mean reversion trading strategy"""
        # Simple mean reversion logic
        if analysis["volatility"] == "high":
            return {
                "action": "buy",
                "confidence": analysis["confidence"] * 0.8,
                "reasoning": "Mean reversion: high volatility, expect bounce"
            }
        
        return {"action": "hold", "confidence": 0.3, "reasoning": "No mean reversion signal"}
    
    async def _apply_personality_filters(self, signal: Dict[str, Any], market_data: MarketData) -> TradingDecision:
        """Apply personality-based filters to trading signal"""
        
        # Convert signal to decision
        decision_type = DecisionType.BUY if signal["action"] == "buy" else DecisionType.SELL if signal["action"] == "sell" else DecisionType.HOLD
        
        # Apply personality adjustments
        confidence = signal["confidence"]
        amount = 0.0
        
        if decision_type != DecisionType.HOLD:
            # Personality-based position sizing
            if self.personality == "aggressive_opportunist":
                amount = min(self.capital_allocation * 0.1, 1000)  # 10% of capital, max $1000
                confidence = min(confidence * 1.2, 1.0)
            elif self.personality == "patient_observer":
                amount = min(self.capital_allocation * 0.05, 500)  # 5% of capital, max $500
                confidence = max(confidence * 0.8, 0.1)
            elif self.personality == "contrarian_analyst":
                amount = min(self.capital_allocation * 0.07, 750)  # 7% of capital, max $750
                confidence = confidence
            else:
                amount = min(self.capital_allocation * 0.05, 500)  # Default conservative
        
        return TradingDecision(
            agent_id=self.agent_id,
            decision_type=decision_type,
            symbol=market_data.symbol,
            amount=amount,
            price=market_data.price,
            confidence=confidence,
            reasoning=signal["reasoning"],
            timestamp=datetime.now(timezone.utc),
            expected_profit=signal.get("expected_profit"),
            risk_score=self._calculate_risk_score(signal, market_data)
        )
    
    def _calculate_risk_score(self, signal: Dict[str, Any], market_data: MarketData) -> float:
        """Calculate risk score for the decision"""
        base_risk = 0.5
        
        # Adjust based on confidence
        if signal["confidence"] > 0.8:
            base_risk *= 0.7
        elif signal["confidence"] < 0.3:
            base_risk *= 1.3
        
        # Adjust based on personality
        if self.personality == "aggressive_opportunist":
            base_risk *= 1.2
        elif self.personality == "patient_observer":
            base_risk *= 0.8
        
        return min(max(base_risk, 0.1), 1.0)
    
    async def _update_performance(self, decision: TradingDecision) -> None:
        """Update agent performance metrics"""
        self.performance.total_trades += 1
        
        # Simple performance tracking
        if decision.expected_profit and decision.expected_profit > 0:
            self.performance.profitable_trades += 1
            self.performance.total_profit += decision.expected_profit
        
        # Calculate win rate
        if self.performance.total_trades > 0:
            self.performance.win_rate = self.performance.profitable_trades / self.performance.total_trades
        
        # Calculate average profit per trade
        if self.performance.total_trades > 0:
            self.performance.avg_profit_per_trade = self.performance.total_profit / self.performance.total_trades
        
        self.performance.last_updated = datetime.now(timezone.utc)
    
    def _dict_to_market_data(self, data: Dict[str, Any]) -> MarketData:
        """Convert dictionary to MarketData object"""
        return MarketData(
            symbol=data.get("symbol", "BTC/USDT"),
            price=float(data.get("price", 0)),
            volume=float(data.get("volume", 0)),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            exchange=data.get("exchange", "unknown"),
            bid=data.get("bid"),
            ask=data.get("ask"),
            spread=data.get("spread")
        )
    
    async def analyze_market(self, market_data: MarketData) -> TradingDecision:
        """
        Analyze market data and make a trading decision
        This is the main entry point for hive mind consensus voting
        Wraps the process() method to provide a consistent API
        """
        return await self.process(market_data)

    async def learn_from_outcome(self, outcome: Dict[str, Any]) -> None:
        """Learn from trading outcome"""
        await self.brain.learn(outcome)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get agent performance summary"""
        return {
            "agent_id": self.agent_id,
            "personality": self.personality,
            "specialization": self.specialization,
            "state": self.state.value,
            "capital_allocation": self.capital_allocation,
            "performance": {
                "total_trades": self.performance.total_trades,
                "profitable_trades": self.performance.profitable_trades,
                "win_rate": self.performance.win_rate,
                "total_profit": self.performance.total_profit,
                "avg_profit_per_trade": self.performance.avg_profit_per_trade
            },
            "created_at": self.created_at.isoformat(),
            "last_decision": self.last_decision.timestamp.isoformat() if self.last_decision else None,
            "decision_count": self.decision_count
        }
    
    def activate(self) -> None:
        """Activate the agent"""
        self.is_active = True
        self.state = AgentState.ACTIVE
        logger.info(f"Agent {self.agent_id} activated")
    
    def deactivate(self) -> None:
        """Deactivate the agent"""
        self.is_active = False
        self.state = AgentState.PAUSED
        logger.info(f"Agent {self.agent_id} deactivated")
    
    def set_capital_allocation(self, amount: float) -> None:
        """Set capital allocation for the agent"""
        self.capital_allocation = amount
        logger.info(f"Agent {self.agent_id} capital allocation set to ${amount:,.2f}")

# Factory function for creating agents
def create_agent(agent_type: str, personality: str, agent_id: Optional[str] = None) -> TradingAgent:
    """Factory function to create agents"""
    if agent_id is None:
        agent_id = f"{agent_type}_{personality}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return TradingAgent(
        agent_id=agent_id,
        personality=personality,
        specialization=agent_type
    )

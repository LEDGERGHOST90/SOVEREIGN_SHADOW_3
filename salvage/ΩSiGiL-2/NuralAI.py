#!/usr/bin/env python3
import sys
"""
Neural AGI Trading Ecosystem
Modular AI system inspired by neural networks and reinforcement learning
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from flask import Flask, request, jsonify
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Signal:
    """Raw market signal from external sources"""
    id: str
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    source: str  # 'tradingview', 'dexscreener', 'metamask'
    signal_type: str  # 'bullish', 'bearish', 'neutral'
    metadata: Dict[str, Any]

@dataclass
class ModuleDecision:
    """Decision output from a module"""
    module_name: str
    decision: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    risk_score: float  # 0.0 to 1.0
    timestamp: datetime

@dataclass
class TradeOutcome:
    """Final trade result for reinforcement learning"""
    trade_id: str
    signal_id: str
    final_decision: str
    entry_price: float
    exit_price: Optional[float]
    profit_score: float  # -5 to +5
    timing_score: float  # 0.0 to 1.0
    confidence_match: float  # 0.0 to 1.0
    module_accuracy: Dict[str, float]
    timestamp: datetime
    completed: bool

# ============================================================================
# BASE MODULE CLASS
# ============================================================================

class BaseModule(ABC):
    """Base class for all neural modules"""
    
    def __init__(self, name: str, initial_weight: float = 1.0):
        self.name = name
        self.weight = initial_weight
        self.accuracy_history = []
        self.confidence_history = []
        
    @abstractmethod
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Process incoming signal and return decision"""
        pass
    
    def update_weight(self, accuracy_score: float):
        """Update module weight based on performance"""
        self.accuracy_history.append(accuracy_score)
        
        # Keep only last 50 outcomes for adaptive learning
        if len(self.accuracy_history) > 50:
            self.accuracy_history = self.accuracy_history[-50:]
        
        # Calculate new weight based on recent performance
        recent_avg = np.mean(self.accuracy_history[-10:]) if len(self.accuracy_history) >= 10 else accuracy_score
        
        # Adaptive weight adjustment (0.5 to 2.0 range)
        self.weight = max(0.5, min(2.0, 0.5 + (recent_avg * 1.5)))
        
        logger.info(f"{self.name} weight updated to {self.weight:.3f} (accuracy: {recent_avg:.3f})")

# ============================================================================
# MODULE IMPLEMENTATIONS
# ============================================================================

class SignalScanner(BaseModule):
    """L1: Signal detection and preprocessing"""
    
    def __init__(self):
        super().__init__("SignalScanner", 1.0)
        self.signal_filters = {
            'min_volume': 10000,
            'price_range': (0.01, 1000),
            'valid_sources': ['tradingview', 'dexscreener', 'metamask']
        }
    
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Validate and preprocess incoming signals"""
        
        # Signal validation
        if signal.source not in self.signal_filters['valid_sources']:
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.0,
                reasoning="Invalid signal source",
                risk_score=1.0,
                timestamp=datetime.now()
            )
        
        if signal.volume < self.signal_filters['min_volume']:
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.2,
                reasoning="Volume too low for reliable signal",
                risk_score=0.8,
                timestamp=datetime.now()
            )
        
        # Calculate confidence based on signal strength
        volume_score = min(1.0, signal.volume / 100000)  # Normalize volume
        price_stability = 0.8 if signal.price > 0.1 else 0.5  # Prefer higher prices
        
        confidence = (volume_score + price_stability) / 2
        
        # Determine initial decision based on signal type
        decision_map = {
            'bullish': 'buy',
            'bearish': 'sell',
            'neutral': 'hold'
        }
        
        decision = decision_map.get(signal.signal_type, 'hold')
        
        return ModuleDecision(
            module_name=self.name,
            decision=decision,
            confidence=confidence,
            reasoning=f"Signal validated: {signal.signal_type} with volume {signal.volume}",
            risk_score=1.0 - confidence,
            timestamp=datetime.now()
        )

class R1Reasoner(BaseModule):
    """L2: Rule-based logic and risk assessment"""
    
    def __init__(self):
        super().__init__("R1", 1.2)
        self.risk_thresholds = {
            'max_position_size': 0.2,  # 20% of portfolio
            'stop_loss': 0.02,  # 2% stop loss
            'daily_loss_limit': 0.05,  # 5% daily loss limit
            'min_confidence': 0.3
        }
        self.daily_losses = 0.0
        self.last_reset = datetime.now().date()
    
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Apply rule-based filters and risk management"""
        
        # Reset daily losses if new day
        if datetime.now().date() > self.last_reset:
            self.daily_losses = 0.0
            self.last_reset = datetime.now().date()
        
        # Check daily loss limit
        if self.daily_losses >= self.risk_thresholds['daily_loss_limit']:
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.0,
                reasoning="Daily loss limit reached",
                risk_score=1.0,
                timestamp=datetime.now()
            )
        
        # Analyze signal strength
        l1_decision = context.get('l1_decision')
        if not l1_decision or l1_decision.confidence < self.risk_thresholds['min_confidence']:
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.1,
                reasoning="L1 confidence too low for entry",
                risk_score=0.9,
                timestamp=datetime.now()
            )
        
        # Risk-adjusted confidence
        risk_factor = 1.0 - (self.daily_losses / self.risk_thresholds['daily_loss_limit'])
        confidence = l1_decision.confidence * risk_factor * 0.8  # Conservative adjustment
        
        # Volume-based decision refinement
        volume_strength = min(1.0, signal.volume / 50000)
        if volume_strength < 0.3:
            confidence *= 0.7
        
        return ModuleDecision(
            module_name=self.name,
            decision=l1_decision.decision if confidence > 0.4 else 'hold',
            confidence=confidence,
            reasoning=f"Risk-adjusted decision: risk_factor={risk_factor:.2f}, volume_strength={volume_strength:.2f}",
            risk_score=1.0 - confidence,
            timestamp=datetime.now()
        )

class OmegaShadow(BaseModule):
    """L3: Pattern matching and intuition engine"""
    
    def __init__(self):
        super().__init__("OmegaShadow", 0.9)
        self.pattern_memory = []
        self.market_sentiment = 0.5  # Neutral starting point
        
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Deep pattern analysis and market intuition"""
        
        # Simulate pattern matching against historical data
        pattern_score = self._analyze_patterns(signal)
        sentiment_score = self._assess_market_sentiment(signal)
        timing_score = self._evaluate_timing(signal)
        
        # Combine scores with weighted importance
        intuition_score = (
            pattern_score * 0.4 +
            sentiment_score * 0.3 +
            timing_score * 0.3
        )
        
        # Check for contrarian opportunities
        l1_decision = context.get('l1_decision')
        r1_decision = context.get('r1_decision')
        
        contrarian_boost = 0.0
        if l1_decision and r1_decision:
            if l1_decision.confidence > 0.7 and r1_decision.confidence < 0.3:
                contrarian_boost = 0.2  # Omega sees opportunity others miss
                
        confidence = min(1.0, intuition_score + contrarian_boost)
        
        # Determine decision based on pattern analysis
        if confidence > 0.6:
            decision = signal.signal_type.replace('ish', '') if 'ish' in signal.signal_type else 'buy'
        elif confidence < 0.3:
            decision = 'hold'
        else:
            decision = l1_decision.decision if l1_decision else 'hold'
        
        reasoning = f"Pattern analysis: {pattern_score:.2f}, Sentiment: {sentiment_score:.2f}, Timing: {timing_score:.2f}"
        if contrarian_boost > 0:
            reasoning += f", Contrarian opportunity detected (+{contrarian_boost:.2f})"
        
        return ModuleDecision(
            module_name=self.name,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            risk_score=1.0 - confidence,
            timestamp=datetime.now()
        )
    
    def _analyze_patterns(self, signal: Signal) -> float:
        """Simulate pattern matching analysis"""
        # Simulate finding similar historical patterns
        similar_patterns = len([p for p in self.pattern_memory 
                              if abs(p.get('price', 0) - signal.price) < signal.price * 0.1])
        
        if similar_patterns == 0:
            return 0.5  # Neutral if no patterns found
        
        # Simulate pattern success rate
        pattern_strength = min(1.0, similar_patterns / 10)
        return 0.3 + (pattern_strength * 0.4)  # Range: 0.3 to 0.7
    
    def _assess_market_sentiment(self, signal: Signal) -> float:
        """Analyze overall market sentiment"""
        # Simulate sentiment analysis based on volume and price action
        volume_sentiment = min(1.0, signal.volume / 100000)
        
        # Update running sentiment
        if signal.signal_type == 'bullish':
            self.market_sentiment = min(1.0, self.market_sentiment + 0.1)
        elif signal.signal_type == 'bearish':
            self.market_sentiment = max(0.0, self.market_sentiment - 0.1)
        
        return (volume_sentiment + self.market_sentiment) / 2
    
    def _evaluate_timing(self, signal: Signal) -> float:
        """Evaluate market timing factors"""
        current_hour = datetime.now().hour
        
        # Simulate time-based factors
        # Higher activity during US market hours
        if 9 <= current_hour <= 16:
            time_score = 0.8
        elif 16 < current_hour <= 20:  # After hours but still active
            time_score = 0.6
        else:
            time_score = 0.4
        
        return time_score

class SniperEngine(BaseModule):
    """L4: Trade execution with laddered orders"""
    
    def __init__(self):
        super().__init__("SniperEngine", 1.1)
        self.active_orders = {}
        self.execution_history = []
        
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Determine execution strategy and order placement"""
        
        # Get consensus from previous modules
        decisions = [context.get(f'l{i}_decision') for i in range(1, 4)]
        valid_decisions = [d for d in decisions if d is not None]
        
        if not valid_decisions:
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.0,
                reasoning="No valid upstream decisions",
                risk_score=1.0,
                timestamp=datetime.now()
            )
        
        # Calculate weighted consensus
        total_weight = sum(d.confidence for d in valid_decisions)
        if total_weight == 0:
            weighted_confidence = 0.0
        else:
            weighted_confidence = sum(d.confidence * d.confidence for d in valid_decisions) / total_weight
        
        # Execution strategy based on confidence
        if weighted_confidence > 0.7:
            strategy = "aggressive_ladder"  # 3-tier ladder
            execution_confidence = weighted_confidence * 0.9
        elif weighted_confidence > 0.4:
            strategy = "conservative_ladder"  # 2-tier ladder
            execution_confidence = weighted_confidence * 0.8
        else:
            strategy = "hold"
            execution_confidence = 0.0
        
        # Determine final decision
        buy_votes = sum(1 for d in valid_decisions if d.decision == 'buy')
        sell_votes = sum(1 for d in valid_decisions if d.decision == 'sell')
        
        if strategy == "hold":
            final_decision = 'hold'
        elif buy_votes > sell_votes:
            final_decision = 'buy'
        elif sell_votes > buy_votes:
            final_decision = 'sell'
        else:
            final_decision = 'hold'
        
        reasoning = f"Execution strategy: {strategy}, Consensus: {weighted_confidence:.2f}, Votes: B{buy_votes}/S{sell_votes}"
        
        return ModuleDecision(
            module_name=self.name,
            decision=final_decision,
            confidence=execution_confidence,
            reasoning=reasoning,
            risk_score=1.0 - execution_confidence,
            timestamp=datetime.now()
        )

class VaultGovernor(BaseModule):
    """L5: Long-term wealth management"""
    
    def __init__(self):
        super().__init__("VaultGovernor", 1.3)
        self.vault_allocation = {'BTC': 0.4, 'ETH': 0.4, 'IOTA': 0.2}
        self.rebalance_threshold = 0.1  # 10% deviation triggers rebalance
        
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Determine vault actions and profit conversion"""
        
        # Get execution decision
        execution_decision = context.get('l4_decision')
        if not execution_decision or execution_decision.decision == 'hold':
            return ModuleDecision(
                module_name=self.name,
                decision='hold',
                confidence=0.0,
                reasoning="No execution planned, vault maintaining position",
                risk_score=0.0,
                timestamp=datetime.now()
            )
        
        # Simulate profit potential assessment
        profit_potential = execution_decision.confidence * 0.8
        
        # Vault action determination
        if profit_potential > 0.6:
            vault_action = "prepare_conversion"
            confidence = profit_potential
            reasoning = f"High profit potential ({profit_potential:.2f}), preparing vault conversion"
        elif profit_potential > 0.3:
            vault_action = "monitor"
            confidence = profit_potential * 0.7
            reasoning = f"Moderate potential ({profit_potential:.2f}), monitoring for conversion"
        else:
            vault_action = "hold"
            confidence = 0.2
            reasoning = f"Low potential ({profit_potential:.2f}), maintaining current vault"
        
        return ModuleDecision(
            module_name=self.name,
            decision=vault_action,
            confidence=confidence,
            reasoning=reasoning,
            risk_score=0.3,  # Vault is conservative
            timestamp=datetime.now()
        )

# ============================================================================
# FEEDBACK AND LEARNING SYSTEM
# ============================================================================

class FeedbackTracker(BaseModule):
    """L6: Outcome tracking and reinforcement learning"""
    
    def __init__(self, db_path: str = "trading_ecosystem.db"):
        super().__init__("FeedbackTracker", 1.0)
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for outcome storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_outcomes (
                trade_id TEXT PRIMARY KEY,
                signal_id TEXT,
                final_decision TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_score REAL,
                timing_score REAL,
                confidence_match REAL,
                module_accuracy TEXT,
                timestamp TEXT,
                completed BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_weights (
                module_name TEXT PRIMARY KEY,
                weight REAL,
                accuracy_history TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def process_signal(self, signal: Signal, context: Dict) -> ModuleDecision:
        """Track and analyze decision outcomes"""
        
        # This module doesn't make trading decisions, it analyzes them
        return ModuleDecision(
            module_name=self.name,
            decision='track',
            confidence=1.0,
            reasoning="Tracking decision for learning",
            risk_score=0.0,
            timestamp=datetime.now()
        )
    
    def record_outcome(self, outcome: TradeOutcome):
        """Store trade outcome for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trade_outcomes 
            (trade_id, signal_id, final_decision, entry_price, exit_price, profit_score, 
             timing_score, confidence_match, module_accuracy, timestamp, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            outcome.trade_id, outcome.signal_id, outcome.final_decision,
            outcome.entry_price, outcome.exit_price, outcome.profit_score,
            outcome.timing_score, outcome.confidence_match,
            json.dumps(outcome.module_accuracy), outcome.timestamp.isoformat(),
            outcome.completed
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded outcome for trade {outcome.trade_id}: profit_score={outcome.profit_score}")
    
    def get_performance_stats(self) -> Dict:
        """Get system performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_trades,
                   AVG(profit_score) as avg_profit,
                   AVG(timing_score) as avg_timing,
                   AVG(confidence_match) as avg_confidence_match
            FROM trade_outcomes WHERE completed = 1
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'total_trades': stats[0] if stats[0] else 0,
            'avg_profit': stats[1] if stats[1] else 0.0,
            'avg_timing': stats[2] if stats[2] else 0.0,
            'avg_confidence_match': stats[3] if stats[3] else 0.0
        }

# ============================================================================
# MAIN ECOSYSTEM ORCHESTRATOR
# ============================================================================

class NeuralTradingEcosystem:
    """Main orchestrator for the neural trading system"""
    
    def __init__(self):
        self.modules = {
            'l1': SignalScanner(),
            'l2': R1Reasoner(),
            'l3': OmegaShadow(),
            'l4': SniperEngine(),
            'l5': VaultGovernor(),
            'l6': FeedbackTracker()
        }
        self.decision_history = []
        
    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """Process signal through all neural layers"""
        
        logger.info(f"Processing signal {signal.id} for {signal.symbol}")
        
        context = {}
        decisions = {}
        
        # Process through each layer sequentially
        for layer_id, module in self.modules.items():
            if layer_id == 'l6':  # Feedback tracker doesn't need processing here
                continue
                
            decision = module.process_signal(signal, context)
            decisions[layer_id] = decision
            context[f'{layer_id}_decision'] = decision
            
            logger.info(f"{module.name}: {decision.decision} (confidence: {decision.confidence:.3f})")
        
        # Get final system decision
        final_decision = self._synthesize_decision(decisions)
        
        # Store in history
        decision_record = {
            'signal_id': signal.id,
            'timestamp': datetime.now().isoformat(),
            'layer_decisions': {k: asdict(v) for k, v in decisions.items()},
            'final_decision': asdict(final_decision),
            'signal_data': asdict(signal)
        }
        
        self.decision_history.append(decision_record)
        
        return {
            'final_decision': final_decision,
            'layer_decisions': decisions,
            'reasoning_trace': self._generate_reasoning_trace(decisions, final_decision)
        }
    
    def _synthesize_decision(self, decisions: Dict[str, ModuleDecision]) -> ModuleDecision:
        """Synthesize final decision from all modules"""
        
        # Weight decisions by module weight and confidence
        weighted_scores = {}
        total_weight = 0
        
        for layer_id, decision in decisions.items():
            if layer_id == 'l6':  # Skip feedback tracker
                continue
                
            module = self.modules[layer_id]
            weight = module.weight * decision.confidence
            
            if decision.decision not in weighted_scores:
                weighted_scores[decision.decision] = 0
            
            weighted_scores[decision.decision] += weight
            total_weight += weight
        
        # Find highest weighted decision
        if total_weight == 0:
            final_decision = 'hold'
            final_confidence = 0.0
        else:
            final_decision = max(weighted_scores.keys(), key=lambda k: weighted_scores[k])
            final_confidence = min(1.0, weighted_scores[final_decision] / total_weight)
        
        # Generate combined reasoning
        reasoning_parts = []
        for layer_id, decision in decisions.items():
            if layer_id != 'l6':
                module = self.modules[layer_id]
                reasoning_parts.append(f"{module.name}({decision.confidence:.2f}): {decision.reasoning}")
        
        combined_reasoning = " | ".join(reasoning_parts)
        
        return ModuleDecision(
            module_name="SystemConsensus",
            decision=final_decision,
            confidence=final_confidence,
            reasoning=combined_reasoning,
            risk_score=1.0 - final_confidence,
            timestamp=datetime.now()
        )
    
    def _generate_reasoning_trace(self, decisions: Dict[str, ModuleDecision], 
                                final_decision: ModuleDecision) -> List[str]:
        """Generate human-readable reasoning trace"""
        
        trace = []
        trace.append(f"=== NEURAL DECISION TRACE ===")
        
        for layer_id in sorted(decisions.keys()):
            if layer_id == 'l6':
                continue
            decision = decisions[layer_id]
            module = self.modules[layer_id]
            
            trace.append(f"{module.name} (weight: {module.weight:.2f}):")
            trace.append(f"  Decision: {decision.decision}")
            trace.append(f"  Confidence: {decision.confidence:.3f}")
            trace.append(f"  Risk: {decision.risk_score:.3f}")
            trace.append(f"  Reasoning: {decision.reasoning}")
            trace.append("")
        
        trace.append(f"FINAL SYSTEM DECISION: {final_decision.decision}")
        trace.append(f"SYSTEM CONFIDENCE: {final_decision.confidence:.3f}")
        trace.append(f"SYSTEM REASONING: {final_decision.reasoning}")
        
        return trace
    
    def update_from_outcome(self, outcome: TradeOutcome):
        """Update system based on trade outcome"""
        
        # Record outcome
        self.modules['l6'].record_outcome(outcome)
        
        # Update module weights based on accuracy
        for module_name, accuracy in outcome.module_accuracy.items():
            layer_map = {
                'SignalScanner': 'l1',
                'R1': 'l2', 
                'OmegaShadow': 'l3',
                'SniperEngine': 'l4',
                'VaultGovernor': 'l5'
            }
            
            layer_id = layer_map.get(module_name)
            if layer_id and layer_id in self.modules:
                self.modules[layer_id].update_weight(accuracy)
        
        logger.info(f"System updated from outcome: {outcome.trade_id}")
    
    def get_system_status(self) -> Dict:
        """Get current system status and performance"""
        
        status = {
            'module_weights': {name: module.weight for name, module in self.modules.items()},
            'total_decisions': len(self.decision_history),
            'performance_stats': self.modules['l6'].get_performance_stats()
        }
        
        return status

# ============================================================================
# FLASK API FOR WEBHOOK INTEGRATION
# ============================================================================

# Initialize ecosystem
ecosystem = NeuralTradingEcosystem()
app = Flask(__name__)

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """Receive TradingView webhook alerts"""

    try:
        data = request.get_json()
        logger.info(f"Received webhook signal: {data}")

        # Parse TradingView alert format
        signal = Signal(
            id=str(uuid.uuid4()),
            symbol=data.get('symbol', 'UNKNOWN'),
            price=float(data.get('price', 0)),
            volume=float(data.get('volume', 0)),
            timestamp=datetime.now(),
            source='tradingview',
            signal_type=data.get('signal_type', 'neutral'),
            metadata=data
        )

        # Process through ecosystem
        result = ecosystem.process_signal(signal)

        # Safety check in case something failed silently
        if not result or 'final_decision' not in result or result['final_decision'] is None:
            logger.warning("Signal processed but returned incomplete result.")
            return jsonify({
                'status': 'partial',
                'message': 'Signal processed but final decision missing.',
                'signal_id': signal.id
            })

        return jsonify({
            'status': 'success',
            'signal_id': signal.id,
            'final_decision': result['final_decision'].decision,
            'confidence': result['final_decision'].confidence,
            'reasoning_trace': result['reasoning_trace']
        })

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/webhook/outcome', methods=['POST'])
def record_outcome():
    """Record trade outcome for learning"""
    
    try:
        data = request.get_json()
        
        outcome = TradeOutcome(
            trade_id=data.get('trade_id'),
            signal_id=data.get('signal_id'),
            final_decision=data.get('final_decision'),
            entry_price=float(data.get('entry_price', 0)),
            exit_price=float(data.get('exit_price', 0)) if data.get('exit_price') else None,
            profit_score=float(data.get('profit_score', 0)),
            timing_score=float(data.get('timing_score', 0)),
            confidence_match=float(data.get('confidence_match', 0)),
            module_accuracy=data.get('module_accuracy', {}),
            timestamp=datetime.now(),
            completed=data.get('completed', False)
        )
        
        ecosystem.update_from_outcome(outcome)
        
        return jsonify({'status': 'success', 'message': 'Outcome recorded'})
        
    except Exception as e:
        logger.error(f"Outcome recording error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/signal', methods=['POST'])
def process_manual_signal():
    """Process manual signal input"""
    
    try:
        data = request.get_json()
        
        signal = Signal(
            id=str(uuid.uuid4()),
            symbol=data.get('symbol', 'MANUAL'),
            price=float(data.get('price', 0)),
            volume=float(data.get('volume', 0)),
            timestamp=datetime.now(),
            source=data.get('source', 'manual'),
            signal_type=data.get('signal_type', 'neutral'),
            metadata=data
        )
        
        result = ecosystem.process_signal(signal)
        
        return jsonify({
            'signal_id': signal.id,
            'final_decision': asdict(result['final_decision']),
            'layer_decisions': {k: asdict(v) for k, v in result['layer_decisions'].items()},
            'reasoning_trace': result['reasoning_trace']
        })
        
    except Exception as e:
        logger.error(f"Manual signal error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify(ecosystem.get_system_status())

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get decision history"""
    limit = int(request.args.get('limit', 10))
    return jsonify(ecosystem.decision_history[-limit:])

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================



# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
        logger.info(f"Attempting to start Nural AGI Trading Server on port {port}...")
        app.run(debug=False, port=port, use_reloader=False)
    except OSError as e:
        logger.error(f"Startup failed: {e}")
        raise
    except KeyError as e:
        if str(e) == "'WERKZEUG_SERVER_FD'":
            logger.warning("WERKZEUG_SERVER_FD not set. Flask may not run as expected in this environment.")
        else:
            logger.error(f"Unexpected KeyError: {e}")
            raise
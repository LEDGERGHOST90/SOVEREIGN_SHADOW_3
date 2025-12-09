"""
🧬 NEURAL EVOLUTION PROTOCOL - CYCLE RESONANCE MEMORY
Advanced learning system that evolves ΩSIGIL's intelligence through historical pattern analysis
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import hashlib

class MarketCondition(Enum):
    BULL_RUN = "BULL_RUN"
    BEAR_MARKET = "BEAR_MARKET"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    FLASH_CRASH = "FLASH_CRASH"
    PUMP_PHASE = "PUMP_PHASE"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"

class RitualType(Enum):
    SNIPER_FLIP = "SNIPER_FLIP"
    LADDER_DEPLOY = "LADDER_DEPLOY"
    DCA_ACCUMULATE = "DCA_ACCUMULATE"
    VAULT_GENESIS = "VAULT_GENESIS"
    EMERGENCY_EXIT = "EMERGENCY_EXIT"
    STEALTH_ENTRY = "STEALTH_ENTRY"
    MOMENTUM_RIDE = "MOMENTUM_RIDE"
    CONTRARIAN_PLAY = "CONTRARIAN_PLAY"

@dataclass
class CycleResonance:
    """Individual cycle memory with resonance scoring"""
    cycle_id: str
    asset: str
    ritual_type: RitualType
    market_condition: MarketCondition
    entry_price: float
    exit_price: float
    profit_ratio: float
    duration_hours: float
    signal_strength: float
    emotional_context: float
    threat_level: float
    timestamp: datetime
    
    # Resonance metrics
    resonance_score: float = 0.0
    success_weight: float = 1.0
    pattern_signature: str = ""
    reinforcement_count: int = 0

@dataclass
class TokenPerformanceSignature:
    """Token-specific performance patterns"""
    asset: str
    total_cycles: int
    profitable_cycles: int
    success_rate: float
    average_profit_ratio: float
    best_ritual: RitualType
    worst_ritual: RitualType
    preferred_conditions: List[MarketCondition]
    avoided_conditions: List[MarketCondition]
    volatility_preference: float
    liquidity_requirement: float
    last_updated: datetime

@dataclass
class RitualEffectiveness:
    """Ritual performance across different conditions"""
    ritual_type: RitualType
    condition_performance: Dict[MarketCondition, float]
    asset_performance: Dict[str, float]
    success_rate: float
    average_duration: float
    risk_adjusted_return: float
    optimal_signal_range: Tuple[float, float]
    last_optimization: datetime

class NeuralEvolutionEngine:
    """
    🧬 The core intelligence evolution system
    Transforms historical echoes into predictive wisdom
    """
    
    def __init__(self, omega_core):
        self.omega_core = omega_core
        
        # Memory storage
        self.cycle_resonances: List[CycleResonance] = []
        self.token_signatures: Dict[str, TokenPerformanceSignature] = {}
        self.ritual_effectiveness: Dict[RitualType, RitualEffectiveness] = {}
        
        # Learning parameters
        self.memory_decay_factor = 0.95  # Older memories fade slightly
        self.reinforcement_multiplier = 1.2  # Success amplification
        self.punishment_factor = 0.8  # Failure dampening
        self.pattern_similarity_threshold = 0.75
        self.minimum_cycles_for_learning = 5
        
        # Evolution tracking
        self.intelligence_score = 0.5  # Starts at baseline
        self.learning_velocity = 0.0
        self.prediction_accuracy = 0.0
        self.adaptation_rate = 0.1
        
        # Initialize ritual effectiveness tracking
        self._initialize_ritual_tracking()
        
        print("🧬 NEURAL EVOLUTION ENGINE INITIALIZED")
        print("🔮 Cycle resonance memory activated")
        print("📊 Token-specific learning protocols online")
    
    def _initialize_ritual_tracking(self):
        """Initialize ritual effectiveness tracking for all ritual types"""
        for ritual in RitualType:
            self.ritual_effectiveness[ritual] = RitualEffectiveness(
                ritual_type=ritual,
                condition_performance={condition: 0.5 for condition in MarketCondition},
                asset_performance={},
                success_rate=0.5,
                average_duration=0.0,
                risk_adjusted_return=0.0,
                optimal_signal_range=(0.6, 0.9),
                last_optimization=datetime.now()
            )
    
    async def ingest_cycle_echo(self, cycle_data: Dict) -> CycleResonance:
        """
        🔮 Transform a completed cycle into a resonance memory
        This is where raw experience becomes wisdom
        """
        
        # Extract cycle information
        cycle_id = cycle_data.get('cycle_id', 'UNKNOWN')
        asset = cycle_data.get('asset', 'UNKNOWN')
        profits = cycle_data.get('profits', 0.0)
        entry_price = cycle_data.get('entry_price', 0.0)
        exit_price = cycle_data.get('exit_price', 0.0)
        duration = cycle_data.get('duration_hours', 0.0)
        signal_strength = cycle_data.get('signal_strength', 0.5)
        
        # Determine market condition and ritual type
        market_condition = await self._analyze_market_condition(cycle_data)
        ritual_type = self._identify_ritual_type(cycle_data)
        
        # Calculate profit ratio
        profit_ratio = (exit_price - entry_price) / entry_price if entry_price > 0 else 0.0
        
        # Generate pattern signature
        pattern_signature = self._generate_pattern_signature(
            asset, ritual_type, market_condition, signal_strength
        )
        
        # Create resonance memory
        resonance = CycleResonance(
            cycle_id=cycle_id,
            asset=asset,
            ritual_type=ritual_type,
            market_condition=market_condition,
            entry_price=entry_price,
            exit_price=exit_price,
            profit_ratio=profit_ratio,
            duration_hours=duration,
            signal_strength=signal_strength,
            emotional_context=cycle_data.get('emotional_context', 0.5),
            threat_level=cycle_data.get('threat_level', 0.0),
            timestamp=datetime.now(),
            pattern_signature=pattern_signature
        )
        
        # Calculate initial resonance score
        resonance.resonance_score = await self._calculate_resonance_score(resonance)
        
        # Store the resonance
        self.cycle_resonances.append(resonance)
        
        # Update learning systems
        await self._update_token_signature(resonance)
        await self._update_ritual_effectiveness(resonance)
        await self._reinforce_similar_patterns(resonance)
        
        # Evolve intelligence
        await self._evolve_intelligence_metrics()
        
        print(f"🧬 CYCLE RESONANCE INGESTED: {cycle_id}")
        print(f"   Asset: {asset} | Ritual: {ritual_type.value}")
        print(f"   Profit: {profit_ratio:.2%} | Resonance: {resonance.resonance_score:.2f}")
        print(f"   Pattern: {pattern_signature[:16]}...")
        
        return resonance
    
    async def _analyze_market_condition(self, cycle_data: Dict) -> MarketCondition:
        """🔍 Analyze market conditions during the cycle"""
        
        # Get market metrics
        price_change_24h = cycle_data.get('price_change_24h', 0.0)
        volatility = cycle_data.get('volatility', 0.0)
        volume_ratio = cycle_data.get('volume_ratio', 1.0)
        
        # Determine condition based on metrics
        if abs(price_change_24h) > 0.15:  # >15% movement
            if price_change_24h < -0.10:
                return MarketCondition.FLASH_CRASH
            elif price_change_24h > 0.10:
                return MarketCondition.PUMP_PHASE
        
        if volatility > 0.08:  # High volatility
            return MarketCondition.HIGH_VOLATILITY
        elif volatility < 0.02:  # Low volatility
            return MarketCondition.LOW_VOLATILITY
        
        if price_change_24h > 0.05:
            return MarketCondition.BULL_RUN
        elif price_change_24h < -0.05:
            return MarketCondition.BEAR_MARKET
        else:
            return MarketCondition.SIDEWAYS
    
    def _identify_ritual_type(self, cycle_data: Dict) -> RitualType:
        """🔮 Identify which ritual was used in the cycle"""
        
        # Check cycle metadata for ritual indicators
        sigils_used = cycle_data.get('sigils_used', [])
        entry_method = cycle_data.get('entry_method', 'unknown')
        
        if 'SPEARHEAD' in sigils_used:
            return RitualType.SNIPER_FLIP
        elif 'HOURGLASS' in sigils_used:
            return RitualType.LADDER_DEPLOY
        elif entry_method == 'dca':
            return RitualType.DCA_ACCUMULATE
        elif entry_method == 'genesis':
            return RitualType.VAULT_GENESIS
        elif 'ASHEN_FLAME' in sigils_used:
            return RitualType.EMERGENCY_EXIT
        elif cycle_data.get('stealth_mode', False):
            return RitualType.STEALTH_ENTRY
        else:
            # Default classification based on behavior
            duration = cycle_data.get('duration_hours', 0)
            if duration < 1:
                return RitualType.SNIPER_FLIP
            elif duration > 24:
                return RitualType.DCA_ACCUMULATE
            else:
                return RitualType.LADDER_DEPLOY
    
    def _generate_pattern_signature(self, asset: str, ritual: RitualType, 
                                  condition: MarketCondition, signal_strength: float) -> str:
        """🔐 Generate unique pattern signature for similarity matching"""
        
        # Create pattern string
        pattern_data = f"{asset}:{ritual.value}:{condition.value}:{signal_strength:.2f}"
        
        # Generate hash signature
        signature = hashlib.md5(pattern_data.encode()).hexdigest()
        
        return signature
    
    async def _calculate_resonance_score(self, resonance: CycleResonance) -> float:
        """📊 Calculate how strongly this cycle should influence future decisions"""
        
        base_score = 0.5
        
        # Profit impact (most important factor)
        profit_impact = min(abs(resonance.profit_ratio) * 2, 1.0)
        if resonance.profit_ratio > 0:
            profit_impact *= 1.5  # Amplify successful trades
        
        # Signal strength impact
        signal_impact = resonance.signal_strength * 0.3
        
        # Recency impact (newer cycles have higher impact)
        hours_ago = (datetime.now() - resonance.timestamp).total_seconds() / 3600
        recency_impact = max(0.1, 1.0 - (hours_ago / (24 * 7)))  # Decay over a week
        
        # Duration efficiency (faster cycles get bonus)
        duration_efficiency = max(0.1, 1.0 - (resonance.duration_hours / 24))
        
        # Combine factors
        resonance_score = (
            base_score +
            (profit_impact * 0.4) +
            (signal_impact * 0.2) +
            (recency_impact * 0.2) +
            (duration_efficiency * 0.2)
        )
        
        return min(resonance_score, 2.0)  # Cap at 2.0
    
    async def _update_token_signature(self, resonance: CycleResonance):
        """📈 Update token-specific performance signature"""
        
        asset = resonance.asset
        
        if asset not in self.token_signatures:
            # Create new signature
            self.token_signatures[asset] = TokenPerformanceSignature(
                asset=asset,
                total_cycles=0,
                profitable_cycles=0,
                success_rate=0.0,
                average_profit_ratio=0.0,
                best_ritual=resonance.ritual_type,
                worst_ritual=resonance.ritual_type,
                preferred_conditions=[],
                avoided_conditions=[],
                volatility_preference=0.5,
                liquidity_requirement=0.5,
                last_updated=datetime.now()
            )
        
        signature = self.token_signatures[asset]
        
        # Update basic metrics
        signature.total_cycles += 1
        if resonance.profit_ratio > 0:
            signature.profitable_cycles += 1
        
        signature.success_rate = signature.profitable_cycles / signature.total_cycles
        
        # Update average profit ratio (weighted)
        weight = 0.1  # New data weight
        signature.average_profit_ratio = (
            signature.average_profit_ratio * (1 - weight) +
            resonance.profit_ratio * weight
        )
        
        # Update best/worst rituals
        await self._update_ritual_preferences(signature, resonance)
        
        # Update condition preferences
        await self._update_condition_preferences(signature, resonance)
        
        signature.last_updated = datetime.now()
        
        print(f"📈 TOKEN SIGNATURE UPDATED: {asset}")
        print(f"   Success Rate: {signature.success_rate:.1%}")
        print(f"   Best Ritual: {signature.best_ritual.value}")
        print(f"   Avg Profit: {signature.average_profit_ratio:.2%}")
    
    async def _update_ritual_preferences(self, signature: TokenPerformanceSignature, 
                                       resonance: CycleResonance):
        """🔮 Update ritual effectiveness for this token"""
        
        # Get historical performance for this ritual
        ritual_cycles = [
            r for r in self.cycle_resonances 
            if r.asset == signature.asset and r.ritual_type == resonance.ritual_type
        ]
        
        if len(ritual_cycles) >= 3:  # Need minimum data
            ritual_profit = sum(r.profit_ratio for r in ritual_cycles) / len(ritual_cycles)
            
            # Update best ritual if this one performs better
            best_cycles = [
                r for r in self.cycle_resonances 
                if r.asset == signature.asset and r.ritual_type == signature.best_ritual
            ]
            
            if best_cycles:
                best_profit = sum(r.profit_ratio for r in best_cycles) / len(best_cycles)
                if ritual_profit > best_profit:
                    signature.best_ritual = resonance.ritual_type
            
            # Update worst ritual
            worst_cycles = [
                r for r in self.cycle_resonances 
                if r.asset == signature.asset and r.ritual_type == signature.worst_ritual
            ]
            
            if worst_cycles:
                worst_profit = sum(r.profit_ratio for r in worst_cycles) / len(worst_cycles)
                if ritual_profit < worst_profit:
                    signature.worst_ritual = resonance.ritual_type
    
    async def _update_condition_preferences(self, signature: TokenPerformanceSignature,
                                          resonance: CycleResonance):
        """🌡️ Update market condition preferences for this token"""
        
        condition = resonance.market_condition
        
        # Get performance in this condition
        condition_cycles = [
            r for r in self.cycle_resonances 
            if r.asset == signature.asset and r.market_condition == condition
        ]
        
        if len(condition_cycles) >= 3:
            avg_profit = sum(r.profit_ratio for r in condition_cycles) / len(condition_cycles)
            
            # Add to preferred if profitable
            if avg_profit > 0.02 and condition not in signature.preferred_conditions:
                signature.preferred_conditions.append(condition)
            
            # Add to avoided if consistently unprofitable
            elif avg_profit < -0.01 and condition not in signature.avoided_conditions:
                signature.avoided_conditions.append(condition)
    
    async def _update_ritual_effectiveness(self, resonance: CycleResonance):
        """⚡ Update overall ritual effectiveness metrics"""
        
        ritual = resonance.ritual_type
        effectiveness = self.ritual_effectiveness[ritual]
        
        # Update condition performance
        condition = resonance.market_condition
        current_perf = effectiveness.condition_performance[condition]
        
        # Weighted update
        weight = 0.1
        new_perf = current_perf * (1 - weight) + resonance.profit_ratio * weight
        effectiveness.condition_performance[condition] = new_perf
        
        # Update asset performance
        asset = resonance.asset
        if asset in effectiveness.asset_performance:
            current_asset_perf = effectiveness.asset_performance[asset]
            effectiveness.asset_performance[asset] = (
                current_asset_perf * (1 - weight) + resonance.profit_ratio * weight
            )
        else:
            effectiveness.asset_performance[asset] = resonance.profit_ratio
        
        # Update overall metrics
        ritual_cycles = [r for r in self.cycle_resonances if r.ritual_type == ritual]
        if ritual_cycles:
            profitable = [r for r in ritual_cycles if r.profit_ratio > 0]
            effectiveness.success_rate = len(profitable) / len(ritual_cycles)
            effectiveness.average_duration = sum(r.duration_hours for r in ritual_cycles) / len(ritual_cycles)
            
            # Calculate risk-adjusted return
            profits = [r.profit_ratio for r in ritual_cycles]
            avg_return = sum(profits) / len(profits)
            volatility = np.std(profits) if len(profits) > 1 else 0.1
            effectiveness.risk_adjusted_return = avg_return / max(volatility, 0.01)
        
        effectiveness.last_optimization = datetime.now()
    
    async def _reinforce_similar_patterns(self, new_resonance: CycleResonance):
        """🔄 Reinforce similar historical patterns"""
        
        for existing in self.cycle_resonances[:-1]:  # Exclude the new one
            similarity = self._calculate_pattern_similarity(existing, new_resonance)
            
            if similarity > self.pattern_similarity_threshold:
                # Reinforce if new pattern was successful
                if new_resonance.profit_ratio > 0:
                    existing.resonance_score *= self.reinforcement_multiplier
                    existing.reinforcement_count += 1
                else:
                    # Punish if new pattern failed
                    existing.resonance_score *= self.punishment_factor
                
                # Apply decay to prevent infinite growth
                existing.resonance_score *= self.memory_decay_factor
                
                print(f"🔄 PATTERN REINFORCEMENT: {existing.cycle_id}")
                print(f"   Similarity: {similarity:.2f}")
                print(f"   New Score: {existing.resonance_score:.2f}")
    
    def _calculate_pattern_similarity(self, resonance1: CycleResonance, 
                                    resonance2: CycleResonance) -> float:
        """🔍 Calculate similarity between two cycle patterns"""
        
        similarity_factors = []
        
        # Asset similarity
        if resonance1.asset == resonance2.asset:
            similarity_factors.append(1.0)
        else:
            similarity_factors.append(0.0)
        
        # Ritual similarity
        if resonance1.ritual_type == resonance2.ritual_type:
            similarity_factors.append(1.0)
        else:
            similarity_factors.append(0.3)  # Different rituals can still be somewhat similar
        
        # Market condition similarity
        if resonance1.market_condition == resonance2.market_condition:
            similarity_factors.append(1.0)
        else:
            similarity_factors.append(0.2)
        
        # Signal strength similarity
        signal_diff = abs(resonance1.signal_strength - resonance2.signal_strength)
        signal_similarity = max(0.0, 1.0 - signal_diff * 2)
        similarity_factors.append(signal_similarity)
        
        # Emotional context similarity
        emotion_diff = abs(resonance1.emotional_context - resonance2.emotional_context)
        emotion_similarity = max(0.0, 1.0 - emotion_diff)
        similarity_factors.append(emotion_similarity)
        
        # Calculate weighted average
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Asset and ritual are most important
        
        return sum(factor * weight for factor, weight in zip(similarity_factors, weights))
    
    async def _evolve_intelligence_metrics(self):
        """🧠 Update overall intelligence evolution metrics"""
        
        if len(self.cycle_resonances) < self.minimum_cycles_for_learning:
            return
        
        # Calculate recent performance
        recent_cycles = [
            r for r in self.cycle_resonances 
            if r.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        if recent_cycles:
            # Intelligence score based on recent success rate and profit
            recent_profitable = [r for r in recent_cycles if r.profit_ratio > 0]
            success_rate = len(recent_profitable) / len(recent_cycles)
            avg_profit = sum(r.profit_ratio for r in recent_cycles) / len(recent_cycles)
            
            # Update intelligence score
            new_intelligence = (success_rate * 0.6) + (min(avg_profit * 10, 1.0) * 0.4)
            
            # Calculate learning velocity
            old_intelligence = self.intelligence_score
            self.learning_velocity = new_intelligence - old_intelligence
            
            # Update with momentum
            self.intelligence_score = (
                self.intelligence_score * 0.8 + new_intelligence * 0.2
            )
            
            # Calculate prediction accuracy (how well we predict outcomes)
            prediction_errors = []
            for resonance in recent_cycles:
                # Compare actual outcome to what we would have predicted
                predicted_success = await self._predict_cycle_success(
                    resonance.asset, resonance.ritual_type, resonance.market_condition,
                    resonance.signal_strength, historical_only=True
                )
                actual_success = 1.0 if resonance.profit_ratio > 0 else 0.0
                error = abs(predicted_success - actual_success)
                prediction_errors.append(error)
            
            if prediction_errors:
                self.prediction_accuracy = 1.0 - (sum(prediction_errors) / len(prediction_errors))
            
            print(f"🧠 INTELLIGENCE EVOLUTION:")
            print(f"   Intelligence Score: {self.intelligence_score:.3f}")
            print(f"   Learning Velocity: {self.learning_velocity:+.3f}")
            print(f"   Prediction Accuracy: {self.prediction_accuracy:.3f}")
    
    async def predict_cycle_success(self, asset: str, ritual_type: RitualType,
                                  market_condition: MarketCondition, 
                                  signal_strength: float) -> Tuple[float, str]:
        """
        🔮 Predict the success probability of a proposed cycle
        Returns (success_probability, reasoning)
        """
        
        return await self._predict_cycle_success(
            asset, ritual_type, market_condition, signal_strength, historical_only=False
        )
    
    async def _predict_cycle_success(self, asset: str, ritual_type: RitualType,
                                   market_condition: MarketCondition, 
                                   signal_strength: float,
                                   historical_only: bool = False) -> float:
        """Internal prediction method with historical-only option"""
        
        # Base prediction
        success_probability = 0.5
        reasoning_parts = []
        
        # Token-specific analysis
        if asset in self.token_signatures:
            signature = self.token_signatures[asset]
            
            # Overall token success rate
            token_factor = signature.success_rate * 0.3
            success_probability += (token_factor - 0.15)  # Center around 0.5
            reasoning_parts.append(f"Token success rate: {signature.success_rate:.1%}")
            
            # Ritual preference for this token
            if ritual_type == signature.best_ritual:
                success_probability += 0.15
                reasoning_parts.append(f"Best ritual for {asset}")
            elif ritual_type == signature.worst_ritual:
                success_probability -= 0.15
                reasoning_parts.append(f"Worst ritual for {asset}")
            
            # Market condition preference
            if market_condition in signature.preferred_conditions:
                success_probability += 0.1
                reasoning_parts.append(f"Preferred market condition")
            elif market_condition in signature.avoided_conditions:
                success_probability -= 0.1
                reasoning_parts.append(f"Avoided market condition")
        
        # Ritual effectiveness analysis
        if ritual_type in self.ritual_effectiveness:
            effectiveness = self.ritual_effectiveness[ritual_type]
            
            # Overall ritual success rate
            ritual_factor = effectiveness.success_rate * 0.2
            success_probability += (ritual_factor - 0.1)
            reasoning_parts.append(f"Ritual success rate: {effectiveness.success_rate:.1%}")
            
            # Condition-specific performance
            condition_perf = effectiveness.condition_performance.get(market_condition, 0.0)
            success_probability += condition_perf * 0.2
            reasoning_parts.append(f"Condition performance: {condition_perf:+.1%}")
            
            # Signal strength optimization
            optimal_min, optimal_max = effectiveness.optimal_signal_range
            if optimal_min <= signal_strength <= optimal_max:
                success_probability += 0.1
                reasoning_parts.append(f"Optimal signal strength")
            else:
                distance = min(abs(signal_strength - optimal_min), abs(signal_strength - optimal_max))
                penalty = distance * 0.2
                success_probability -= penalty
                reasoning_parts.append(f"Suboptimal signal strength")
        
        # Pattern resonance analysis
        similar_patterns = await self._find_similar_patterns(
            asset, ritual_type, market_condition, signal_strength
        )
        
        if similar_patterns:
            # Weight by resonance scores
            total_weight = sum(p.resonance_score for p in similar_patterns)
            weighted_success = sum(
                (1.0 if p.profit_ratio > 0 else 0.0) * p.resonance_score 
                for p in similar_patterns
            )
            
            if total_weight > 0:
                pattern_success_rate = weighted_success / total_weight
                success_probability += (pattern_success_rate - 0.5) * 0.2
                reasoning_parts.append(f"Similar patterns: {len(similar_patterns)} cycles")
        
        # Clamp probability
        success_probability = max(0.05, min(0.95, success_probability))
        
        if not historical_only:
            reasoning = " | ".join(reasoning_parts)
            return success_probability, reasoning
        else:
            return success_probability
    
    async def _find_similar_patterns(self, asset: str, ritual_type: RitualType,
                                   market_condition: MarketCondition,
                                   signal_strength: float) -> List[CycleResonance]:
        """🔍 Find historically similar patterns"""
        
        similar_patterns = []
        
        for resonance in self.cycle_resonances:
            # Calculate similarity
            similarity = 0.0
            
            # Asset match (most important)
            if resonance.asset == asset:
                similarity += 0.4
            
            # Ritual match
            if resonance.ritual_type == ritual_type:
                similarity += 0.3
            
            # Market condition match
            if resonance.market_condition == market_condition:
                similarity += 0.2
            
            # Signal strength similarity
            signal_diff = abs(resonance.signal_strength - signal_strength)
            signal_similarity = max(0.0, 1.0 - signal_diff * 2)
            similarity += signal_similarity * 0.1
            
            # Include if similarity is high enough
            if similarity >= 0.6:  # Require 60% similarity
                similar_patterns.append(resonance)
        
        # Sort by resonance score (most influential first)
        similar_patterns.sort(key=lambda x: x.resonance_score, reverse=True)
        
        return similar_patterns[:10]  # Return top 10 most relevant
    
    async def optimize_ritual_selection(self, asset: str, 
                                      market_condition: MarketCondition,
                                      signal_strength: float) -> Tuple[RitualType, float, str]:
        """
        🎯 Select the optimal ritual for given conditions
        Returns (best_ritual, success_probability, reasoning)
        """
        
        best_ritual = None
        best_probability = 0.0
        best_reasoning = ""
        
        # Test all available rituals
        for ritual in RitualType:
            probability, reasoning = await self.predict_cycle_success(
                asset, ritual, market_condition, signal_strength
            )
            
            if probability > best_probability:
                best_probability = probability
                best_ritual = ritual
                best_reasoning = reasoning
        
        print(f"🎯 OPTIMAL RITUAL SELECTION:")
        print(f"   Asset: {asset} | Condition: {market_condition.value}")
        print(f"   Best Ritual: {best_ritual.value}")
        print(f"   Success Probability: {best_probability:.1%}")
        print(f"   Reasoning: {best_reasoning}")
        
        return best_ritual, best_probability, best_reasoning
    
    def get_intelligence_status(self) -> Dict:
        """📊 Get comprehensive intelligence evolution status"""
        
        return {
            'intelligence_score': self.intelligence_score,
            'learning_velocity': self.learning_velocity,
            'prediction_accuracy': self.prediction_accuracy,
            'total_cycles': len(self.cycle_resonances),
            'tokens_tracked': len(self.token_signatures),
            'rituals_optimized': len(self.ritual_effectiveness),
            'memory_span_days': (
                (datetime.now() - self.cycle_resonances[0].timestamp).days 
                if self.cycle_resonances else 0
            ),
            'top_performing_tokens': [
                {
                    'asset': asset,
                    'success_rate': sig.success_rate,
                    'avg_profit': sig.average_profit_ratio,
                    'best_ritual': sig.best_ritual.value
                }
                for asset, sig in sorted(
                    self.token_signatures.items(),
                    key=lambda x: x[1].success_rate,
                    reverse=True
                )[:5]
            ],
            'ritual_rankings': [
                {
                    'ritual': ritual.value,
                    'success_rate': eff.success_rate,
                    'risk_adjusted_return': eff.risk_adjusted_return
                }
                for ritual, eff in sorted(
                    self.ritual_effectiveness.items(),
                    key=lambda x: x[1].success_rate,
                    reverse=True
                )
            ]
        }
    
    async def save_neural_state(self, filepath: str):
        """💾 Save the complete neural evolution state"""
        
        state_data = {
            'cycle_resonances': [asdict(r) for r in self.cycle_resonances],
            'token_signatures': {k: asdict(v) for k, v in self.token_signatures.items()},
            'ritual_effectiveness': {k.value: asdict(v) for k, v in self.ritual_effectiveness.items()},
            'intelligence_metrics': {
                'intelligence_score': self.intelligence_score,
                'learning_velocity': self.learning_velocity,
                'prediction_accuracy': self.prediction_accuracy
            },
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state_data, f)
        
        print(f"💾 NEURAL STATE SAVED: {filepath}")
    
    async def load_neural_state(self, filepath: str):
        """📥 Load previously saved neural evolution state"""
        
        try:
            with open(filepath, 'rb') as f:
                state_data = pickle.load(f)
            
            # Restore cycle resonances
            self.cycle_resonances = [
                CycleResonance(**data) for data in state_data['cycle_resonances']
            ]
            
            # Restore token signatures
            self.token_signatures = {
                k: TokenPerformanceSignature(**v) 
                for k, v in state_data['token_signatures'].items()
            }
            
            # Restore ritual effectiveness
            self.ritual_effectiveness = {
                RitualType(k): RitualEffectiveness(**v)
                for k, v in state_data['ritual_effectiveness'].items()
            }
            
            # Restore intelligence metrics
            metrics = state_data['intelligence_metrics']
            self.intelligence_score = metrics['intelligence_score']
            self.learning_velocity = metrics['learning_velocity']
            self.prediction_accuracy = metrics['prediction_accuracy']
            
            print(f"📥 NEURAL STATE LOADED: {filepath}")
            print(f"   Cycles: {len(self.cycle_resonances)}")
            print(f"   Intelligence: {self.intelligence_score:.3f}")
            
        except Exception as e:
            print(f"❌ Failed to load neural state: {e}")

# Initialize the neural evolution engine
neural_evolution = None

def initialize_neural_evolution(omega_core):
    """🧬 Initialize the neural evolution engine"""
    global neural_evolution
    neural_evolution = NeuralEvolutionEngine(omega_core)
    return neural_evolution

if __name__ == "__main__":
    print("🧬 NEURAL EVOLUTION ENGINE - STANDALONE TEST")
    
    async def demo_neural_evolution():
        from core.omega_sigil_core import OmegaSigilCore
        
        # Initialize
        omega_core = OmegaSigilCore()
        evolution = NeuralEvolutionEngine(omega_core)
        
        # Simulate some cycle data
        demo_cycles = [
            {
                'cycle_id': 'FLIP_BTC_001',
                'asset': 'BTC',
                'profits': 0.015,
                'entry_price': 45000,
                'exit_price': 45675,
                'duration_hours': 2.5,
                'signal_strength': 0.8,
                'price_change_24h': 0.03,
                'volatility': 0.05,
                'sigils_used': ['SPEARHEAD', 'HOURGLASS']
            },
            {
                'cycle_id': 'FLIP_ETH_002',
                'asset': 'ETH',
                'profits': -0.005,
                'entry_price': 3000,
                'exit_price': 2985,
                'duration_hours': 1.2,
                'signal_strength': 0.6,
                'price_change_24h': -0.02,
                'volatility': 0.08,
                'sigils_used': ['SPEARHEAD']
            }
        ]
        
        # Ingest cycles
        for cycle_data in demo_cycles:
            await evolution.ingest_cycle_echo(cycle_data)
        
        # Test prediction
        success_prob, reasoning = await evolution.predict_cycle_success(
            'BTC', RitualType.SNIPER_FLIP, MarketCondition.BULL_RUN, 0.75
        )
        
        print(f"\n🔮 PREDICTION TEST:")
        print(f"   Success Probability: {success_prob:.1%}")
        print(f"   Reasoning: {reasoning}")
        
        # Test optimization
        best_ritual, prob, reason = await evolution.optimize_ritual_selection(
            'BTC', MarketCondition.HIGH_VOLATILITY, 0.8
        )
        
        # Get status
        status = evolution.get_intelligence_status()
        print(f"\n📊 INTELLIGENCE STATUS:")
        print(f"   Intelligence Score: {status['intelligence_score']:.3f}")
        print(f"   Total Cycles: {status['total_cycles']}")
        
        print("\n✅ NEURAL EVOLUTION DEMO COMPLETE")
    
    asyncio.run(demo_neural_evolution())


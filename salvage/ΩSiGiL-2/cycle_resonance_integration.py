"""
🔗 CYCLE RESONANCE INTEGRATION
Seamlessly integrates Neural Evolution with existing ΩSIGIL systems
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core.neural_evolution import (
    NeuralEvolutionEngine, RitualType, MarketCondition,
    initialize_neural_evolution
)

class CycleResonanceIntegrator:
    """
    🔗 Bridges the gap between ΩSIGIL's existing systems and Neural Evolution
    Automatically captures cycle data and feeds it to the learning engine
    """
    
    def __init__(self, omega_core):
        self.omega_core = omega_core
        self.neural_evolution = initialize_neural_evolution(omega_core)
        
        # Integration hooks
        self.auto_learning_enabled = True
        self.prediction_threshold = 0.6  # Minimum confidence for predictions
        self.optimization_mode = True
        
        print("🔗 CYCLE RESONANCE INTEGRATION ACTIVATED")
        print("🧬 Neural Evolution linked to ΩSIGIL core systems")
    
    async def enhance_signal_evaluation(self, signal_data: Dict) -> Dict:
        """
        🔮 Enhance incoming signals with neural predictions
        Called by the main signal processing system
        """
        
        asset = signal_data.get('asset', 'UNKNOWN')
        signal_strength = signal_data.get('strength', 0.5)
        
        # Analyze current market conditions
        market_condition = await self._detect_current_market_condition(signal_data)
        
        # Get optimal ritual recommendation
        if self.optimization_mode:
            optimal_ritual, success_prob, reasoning = await self.neural_evolution.optimize_ritual_selection(
                asset, market_condition, signal_strength
            )
            
            # Enhance signal with neural insights
            signal_data['neural_enhancement'] = {
                'recommended_ritual': optimal_ritual.value,
                'success_probability': success_prob,
                'reasoning': reasoning,
                'market_condition': market_condition.value,
                'confidence_level': 'HIGH' if success_prob > 0.7 else 'MEDIUM' if success_prob > 0.5 else 'LOW'
            }
            
            # Adjust signal strength based on prediction
            if success_prob > self.prediction_threshold:
                signal_data['strength'] = min(signal_data['strength'] * (1 + success_prob * 0.3), 1.0)
                signal_data['neural_boost'] = True
            else:
                signal_data['strength'] = signal_data['strength'] * success_prob
                signal_data['neural_caution'] = True
            
            print(f"🔮 SIGNAL ENHANCED: {asset}")
            print(f"   Original Strength: {signal_strength:.2f}")
            print(f"   Enhanced Strength: {signal_data['strength']:.2f}")
            print(f"   Recommended Ritual: {optimal_ritual.value}")
            print(f"   Success Probability: {success_prob:.1%}")
        
        return signal_data
    
    async def capture_cycle_completion(self, cycle_data: Dict):
        """
        📊 Automatically capture completed cycles for learning
        Called when any trading cycle completes
        """
        
        if not self.auto_learning_enabled:
            return
        
        # Enrich cycle data with market context
        enriched_data = await self._enrich_cycle_data(cycle_data)
        
        # Feed to neural evolution
        resonance = await self.neural_evolution.ingest_cycle_echo(enriched_data)
        
        # Update ΩSIGIL's memory systems
        await self._update_omega_memory(resonance)
        
        print(f"📊 CYCLE CAPTURED FOR LEARNING: {cycle_data.get('cycle_id', 'UNKNOWN')}")
    
    async def _detect_current_market_condition(self, signal_data: Dict) -> MarketCondition:
        """🌡️ Detect current market conditions from signal data"""
        
        # Extract market metrics
        price_change = signal_data.get('price_change_24h', 0.0)
        volatility = signal_data.get('volatility', 0.0)
        volume_ratio = signal_data.get('volume_ratio', 1.0)
        emotional_wave = signal_data.get('emotional_wave', 0.5)
        
        # Determine condition
        if abs(price_change) > 0.15:
            if price_change < -0.10:
                return MarketCondition.FLASH_CRASH
            elif price_change > 0.10:
                return MarketCondition.PUMP_PHASE
        
        if volatility > 0.08:
            return MarketCondition.HIGH_VOLATILITY
        elif volatility < 0.02:
            return MarketCondition.LOW_VOLATILITY
        
        if emotional_wave > 0.7:
            return MarketCondition.BULL_RUN
        elif emotional_wave < 0.3:
            return MarketCondition.BEAR_MARKET
        else:
            return MarketCondition.SIDEWAYS
    
    async def _enrich_cycle_data(self, cycle_data: Dict) -> Dict:
        """📈 Enrich cycle data with additional context for learning"""
        
        # Add market condition analysis
        market_condition = await self._detect_current_market_condition(cycle_data)
        cycle_data['market_condition'] = market_condition.value
        
        # Add emotional context
        if 'emotional_wave' not in cycle_data:
            cycle_data['emotional_wave'] = 0.5  # Default neutral
        
        # Add threat level
        if 'threat_level' not in cycle_data:
            cycle_data['threat_level'] = 0.0  # Default safe
        
        # Add timing context
        cycle_data['hour_of_day'] = datetime.now().hour
        cycle_data['day_of_week'] = datetime.now().weekday()
        
        return cycle_data
    
    async def _update_omega_memory(self, resonance):
        """🧠 Update ΩSIGIL's core memory with neural insights"""
        
        # Update MANUS memory with resonance data
        if hasattr(self.omega_core, 'manus'):
            memory_entry = {
                'type': 'neural_resonance',
                'cycle_id': resonance.cycle_id,
                'asset': resonance.asset,
                'profit_ratio': resonance.profit_ratio,
                'resonance_score': resonance.resonance_score,
                'pattern_signature': resonance.pattern_signature,
                'timestamp': resonance.timestamp
            }
            
            # Store in MANUS memory
            await self.omega_core.manus.store_memory(memory_entry)
    
    async def get_neural_guidance(self, asset: str, proposed_ritual: str) -> Dict:
        """
        🎯 Get neural guidance for a proposed trading action
        Used by Trinity consensus system
        """
        
        # Convert string to enum
        try:
            ritual_type = RitualType(proposed_ritual.upper())
        except ValueError:
            ritual_type = RitualType.SNIPER_FLIP  # Default
        
        # Get current market condition (simplified)
        market_condition = MarketCondition.SIDEWAYS  # Would be detected from real data
        signal_strength = 0.7  # Would come from actual signal
        
        # Get prediction
        success_prob, reasoning = await self.neural_evolution.predict_cycle_success(
            asset, ritual_type, market_condition, signal_strength
        )
        
        # Get alternative recommendations
        optimal_ritual, optimal_prob, optimal_reasoning = await self.neural_evolution.optimize_ritual_selection(
            asset, market_condition, signal_strength
        )
        
        return {
            'proposed_ritual': {
                'ritual': proposed_ritual,
                'success_probability': success_prob,
                'reasoning': reasoning,
                'recommendation': 'APPROVE' if success_prob > 0.6 else 'CAUTION' if success_prob > 0.4 else 'REJECT'
            },
            'optimal_alternative': {
                'ritual': optimal_ritual.value,
                'success_probability': optimal_prob,
                'reasoning': optimal_reasoning
            },
            'neural_confidence': self.neural_evolution.intelligence_score,
            'learning_status': {
                'total_cycles': len(self.neural_evolution.cycle_resonances),
                'intelligence_score': self.neural_evolution.intelligence_score,
                'prediction_accuracy': self.neural_evolution.prediction_accuracy
            }
        }
    
    async def enhance_trinity_consensus(self, consensus_data: Dict) -> Dict:
        """
        ⚖️ Enhance Trinity consensus with neural insights
        Called during Trinity voting process
        """
        
        asset = consensus_data.get('asset', 'UNKNOWN')
        proposed_action = consensus_data.get('action', 'UNKNOWN')
        
        # Get neural guidance
        guidance = await self.get_neural_guidance(asset, proposed_action)
        
        # Add neural vote to consensus
        neural_vote = {
            'agent': 'NEURAL_EVOLUTION',
            'vote': guidance['proposed_ritual']['recommendation'],
            'confidence': guidance['neural_confidence'],
            'reasoning': guidance['proposed_ritual']['reasoning'],
            'alternative_suggestion': guidance['optimal_alternative']['ritual']
        }
        
        consensus_data['neural_input'] = neural_vote
        
        # Influence Trinity votes based on neural confidence
        if guidance['neural_confidence'] > 0.8:
            consensus_data['neural_influence'] = 'HIGH'
            # High confidence neural input can influence Trinity decisions
        elif guidance['neural_confidence'] > 0.6:
            consensus_data['neural_influence'] = 'MEDIUM'
        else:
            consensus_data['neural_influence'] = 'LOW'
        
        return consensus_data
    
    def get_learning_dashboard_data(self) -> Dict:
        """📊 Get comprehensive learning status for dashboard display"""
        
        status = self.neural_evolution.get_intelligence_status()
        
        # Add integration-specific metrics
        status['integration_status'] = {
            'auto_learning_enabled': self.auto_learning_enabled,
            'optimization_mode': self.optimization_mode,
            'prediction_threshold': self.prediction_threshold,
            'cycles_processed_today': len([
                r for r in self.neural_evolution.cycle_resonances
                if r.timestamp.date() == datetime.now().date()
            ])
        }
        
        # Add recent performance summary
        recent_cycles = [
            r for r in self.neural_evolution.cycle_resonances
            if (datetime.now() - r.timestamp).days <= 7
        ]
        
        if recent_cycles:
            profitable_recent = [r for r in recent_cycles if r.profit_ratio > 0]
            status['recent_performance'] = {
                'total_cycles': len(recent_cycles),
                'profitable_cycles': len(profitable_recent),
                'success_rate': len(profitable_recent) / len(recent_cycles),
                'average_profit': sum(r.profit_ratio for r in recent_cycles) / len(recent_cycles),
                'best_performing_asset': max(
                    set(r.asset for r in recent_cycles),
                    key=lambda asset: sum(
                        r.profit_ratio for r in recent_cycles if r.asset == asset
                    )
                ) if recent_cycles else 'NONE'
            }
        else:
            status['recent_performance'] = {
                'total_cycles': 0,
                'profitable_cycles': 0,
                'success_rate': 0.0,
                'average_profit': 0.0,
                'best_performing_asset': 'NONE'
            }
        
        return status

# Global integrator instance
cycle_integrator = None

def initialize_cycle_integration(omega_core):
    """🔗 Initialize the cycle resonance integrator"""
    global cycle_integrator
    cycle_integrator = CycleResonanceIntegrator(omega_core)
    return cycle_integrator

async def enhance_signal_with_neural_evolution(signal_data: Dict) -> Dict:
    """🔮 Global function to enhance signals with neural evolution"""
    if cycle_integrator:
        return await cycle_integrator.enhance_signal_evaluation(signal_data)
    return signal_data

async def capture_cycle_for_learning(cycle_data: Dict):
    """📊 Global function to capture cycles for learning"""
    if cycle_integrator:
        await cycle_integrator.capture_cycle_completion(cycle_data)

async def get_neural_consensus_input(consensus_data: Dict) -> Dict:
    """⚖️ Global function to get neural input for Trinity consensus"""
    if cycle_integrator:
        return await cycle_integrator.enhance_trinity_consensus(consensus_data)
    return consensus_data

if __name__ == "__main__":
    print("🔗 CYCLE RESONANCE INTEGRATION - STANDALONE TEST")
    
    async def demo_integration():
        from core.omega_sigil_core import OmegaSigilCore
        
        # Initialize
        omega_core = OmegaSigilCore()
        integrator = CycleResonanceIntegrator(omega_core)
        
        # Test signal enhancement
        test_signal = {
            'asset': 'BTC',
            'strength': 0.7,
            'price_change_24h': 0.05,
            'volatility': 0.06,
            'emotional_wave': 0.8
        }
        
        enhanced_signal = await integrator.enhance_signal_evaluation(test_signal)
        print(f"🔮 ENHANCED SIGNAL: {enhanced_signal}")
        
        # Test cycle capture
        test_cycle = {
            'cycle_id': 'TEST_001',
            'asset': 'BTC',
            'profits': 0.02,
            'entry_price': 45000,
            'exit_price': 45900,
            'duration_hours': 3.0,
            'signal_strength': 0.7
        }
        
        await integrator.capture_cycle_completion(test_cycle)
        
        # Test neural guidance
        guidance = await integrator.get_neural_guidance('BTC', 'SNIPER_FLIP')
        print(f"🎯 NEURAL GUIDANCE: {guidance}")
        
        # Get dashboard data
        dashboard = integrator.get_learning_dashboard_data()
        print(f"📊 DASHBOARD DATA: Intelligence Score = {dashboard['intelligence_score']:.3f}")
        
        print("\n✅ INTEGRATION DEMO COMPLETE")
    
    asyncio.run(demo_integration())


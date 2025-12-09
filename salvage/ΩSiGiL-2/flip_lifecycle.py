"""
ΩSIGIL FLIP LIFECYCLE - 9-Phase Execution Cycle
The sacred sequence that governs every trading action
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from core.omega_sigil_core import OmegaSigilCore, FlipPhase, Signal, MemoryEcho, SigilType

@dataclass
class FlipCycle:
    cycle_id: str
    asset: str
    signal: Signal
    phase: FlipPhase
    start_time: datetime
    ladder_config: Dict
    profits: float = 0.0
    status: str = "ACTIVE"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class FlipLifecycleManager:
    """
    Manages the complete 9-phase flip lifecycle for ΩSIGIL
    Each flip follows the sacred sequence from signal to echo imprint
    """
    
    def __init__(self, omega_core: OmegaSigilCore):
        self.omega_core = omega_core
        self.active_cycles: Dict[str, FlipCycle] = {}
        self.completed_cycles: List[FlipCycle] = []
        self.signal_decay_minutes = 15
        
    async def initiate_flip_cycle(self, signal: Signal) -> Optional[str]:
        """
        Phase 1: SIGNAL RECEIVED 🔮
        Shadow detects emotional wave, whale activity, or momentum pattern
        """
        print(f"🔮 PHASE 1: SIGNAL RECEIVED - {signal.asset}")
        print(f"   Score: {signal.score:.2f} | Pattern: {signal.pattern_type}")
        print(f"   Emotional Wave: {signal.emotional_wave:.2f} | Whale Activity: {signal.whale_activity}")
        
        # Require signal score > 0.7
        if signal.score <= 0.7:
            print(f"❌ Signal score too low: {signal.score:.2f} (required > 0.7)")
            return None
        
        # Create new flip cycle
        cycle_id = f"FLIP_{signal.asset}_{int(signal.timestamp.timestamp())}"
        flip_cycle = FlipCycle(
            cycle_id=cycle_id,
            asset=signal.asset,
            signal=signal,
            phase=FlipPhase.SIGNAL_RECEIVED,
            start_time=signal.timestamp,
            ladder_config={}
        )
        
        self.active_cycles[cycle_id] = flip_cycle
        
        # Move to Phase 2
        return await self._phase_2_memory_weighting(cycle_id)
    
    async def _phase_2_memory_weighting(self, cycle_id: str) -> str:
        """
        Phase 2: MEMORY WEIGHTING 🧠
        Manus compares against last 7 cycles for this asset or pattern class
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.MEMORY_WEIGHTING
        
        print(f"🧠 PHASE 2: MEMORY WEIGHTING - {flip_cycle.asset}")
        
        # Get historical echoes for this asset/pattern
        historical_echoes = self._get_historical_echoes(
            flip_cycle.asset, 
            flip_cycle.signal.pattern_type, 
            days_back=7
        )
        
        # Calculate temporal context and cycle weight
        temporal_context = self._calculate_temporal_context(historical_echoes)
        cycle_weight = self._calculate_cycle_weight(flip_cycle.signal, historical_echoes)
        
        print(f"   Historical Cycles: {len(historical_echoes)}")
        print(f"   Temporal Context: {temporal_context:.2f}")
        print(f"   Cycle Weight: {cycle_weight:.2f}")
        
        # Store in metadata
        flip_cycle.metadata.update({
            'temporal_context': temporal_context,
            'cycle_weight': cycle_weight,
            'historical_count': len(historical_echoes)
        })
        
        # Move to Phase 3
        return await self._phase_3_spearhead_invoked(cycle_id)
    
    async def _phase_3_spearhead_invoked(self, cycle_id: str) -> str:
        """
        Phase 3: SPEARHEAD INVOKED 🔺
        Omega calls for Sniper Flip with Shadow + Omega consensus
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.SPEARHEAD_INVOKED
        
        print(f"🔺 PHASE 3: SPEARHEAD INVOKED - {flip_cycle.asset}")
        
        # Prepare context for sigil invocation
        context = {
            'cycle_id': cycle_id,
            'asset': flip_cycle.asset,
            'signal': asdict(flip_cycle.signal),
            'temporal_context': flip_cycle.metadata.get('temporal_context', 0.5),
            'cycle_weight': flip_cycle.metadata.get('cycle_weight', 0.5)
        }
        
        # Invoke SPEARHEAD sigil (requires Shadow + Omega consensus)
        spearhead_approved = await self.omega_core.invoke_sigil(SigilType.SPEARHEAD, context)
        
        if not spearhead_approved:
            print(f"❌ SPEARHEAD BLOCKED - Terminating cycle {cycle_id}")
            flip_cycle.status = "BLOCKED_SPEARHEAD"
            return cycle_id
        
        # Move to Phase 4
        return await self._phase_4_ladder_deployed(cycle_id)
    
    async def _phase_4_ladder_deployed(self, cycle_id: str) -> str:
        """
        Phase 4: LADDER LOGIC DEPLOYED ⏳
        3-5 rung configuration with signal decay timer
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.LADDER_DEPLOYED
        
        print(f"⏳ PHASE 4: LADDER LOGIC DEPLOYED - {flip_cycle.asset}")
        
        # Generate ladder configuration
        ladder_config = self._generate_ladder_config(flip_cycle)
        flip_cycle.ladder_config = ladder_config
        
        print(f"   Ladder Rungs: {ladder_config['rung_count']}")
        print(f"   Entry Range: {ladder_config['entry_min']:.4f} - {ladder_config['entry_max']:.4f}")
        print(f"   Decay Timer: {self.signal_decay_minutes} minutes")
        
        # Start signal decay timer
        decay_time = flip_cycle.start_time + timedelta(minutes=self.signal_decay_minutes)
        flip_cycle.metadata['decay_time'] = decay_time.isoformat()
        
        # Invoke HOURGLASS sigil for ladder deployment
        context = {
            'cycle_id': cycle_id,
            'ladder_config': ladder_config,
            'decay_time': decay_time.isoformat()
        }
        
        hourglass_approved = await self.omega_core.invoke_sigil(SigilType.HOURGLASS, context)
        
        if not hourglass_approved:
            print(f"❌ HOURGLASS BLOCKED - Ladder deployment failed")
            flip_cycle.status = "BLOCKED_LADDER"
            return cycle_id
        
        # Move to Phase 5
        return await self._phase_5_crystal_scan(cycle_id)
    
    async def _phase_5_crystal_scan(self, cycle_id: str) -> str:
        """
        Phase 5: CRYSTAL NODE SCAN 💠
        Mid-flip review by Manus for overexposure and memory re-evaluation
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.CRYSTAL_SCAN
        
        print(f"💠 PHASE 5: CRYSTAL NODE SCAN - {flip_cycle.asset}")
        
        # Check system overexposure
        overexposure_risk = self._check_system_overexposure()
        
        # Check vault endangerment
        vault_risk = self._check_vault_endangerment()
        
        # Re-evaluate memory signal
        memory_reevaluation = self._reevaluate_memory_signal(flip_cycle)
        
        print(f"   Overexposure Risk: {overexposure_risk:.2f}")
        print(f"   Vault Risk: {vault_risk:.2f}")
        print(f"   Memory Re-eval: {memory_reevaluation:.2f}")
        
        # Store scan results
        flip_cycle.metadata.update({
            'overexposure_risk': overexposure_risk,
            'vault_risk': vault_risk,
            'memory_reevaluation': memory_reevaluation
        })
        
        # Invoke CRYSTAL_NODE sigil
        context = {
            'cycle_id': cycle_id,
            'overexposure_risk': overexposure_risk,
            'vault_risk': vault_risk,
            'memory_reevaluation': memory_reevaluation
        }
        
        crystal_approved = await self.omega_core.invoke_sigil(SigilType.CRYSTAL_NODE, context)
        
        if not crystal_approved:
            print(f"❌ CRYSTAL NODE BLOCKED - Scan failed")
            flip_cycle.status = "BLOCKED_CRYSTAL"
            return cycle_id
        
        # Check if emergency exit needed (Phase 6) or continue to Phase 7
        if overexposure_risk > 0.8 or vault_risk > 0.7:
            return await self._phase_6_ashen_flame(cycle_id)
        else:
            return await self._phase_7_windmark(cycle_id)
    
    async def _phase_6_ashen_flame(self, cycle_id: str) -> str:
        """
        Phase 6: ASHEN FLAME 🜂 (Emergency Exit)
        Shadow triggers emergency exit if emotional volatility detected
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.ASHEN_FLAME
        
        print(f"🜂 PHASE 6: ASHEN FLAME - EMERGENCY EXIT - {flip_cycle.asset}")
        
        # Prepare emergency exit context
        context = {
            'cycle_id': cycle_id,
            'emergency_reason': 'HIGH_RISK_DETECTED',
            'overexposure_risk': flip_cycle.metadata.get('overexposure_risk', 0.0),
            'vault_risk': flip_cycle.metadata.get('vault_risk', 0.0)
        }
        
        # Invoke ASHEN_FLAME sigil (Shadow has override authority)
        emergency_exit = await self.omega_core.invoke_sigil(SigilType.ASHEN_FLAME, context)
        
        if emergency_exit:
            print(f"🔥 EMERGENCY EXIT EXECUTED - Trailing sell logic activated")
            flip_cycle.status = "EMERGENCY_EXIT"
            
            # Execute trailing sell and vault injection/reserve
            profits = await self._execute_trailing_sell(flip_cycle)
            flip_cycle.profits = profits
            
            # Move to Phase 8 (Vault Injection)
            return await self._phase_8_glyph_lock(cycle_id)
        
        # If emergency exit not approved, continue to Phase 7
        return await self._phase_7_windmark(cycle_id)
    
    async def _phase_7_windmark(self, cycle_id: str) -> str:
        """
        Phase 7: WINDMARK 🜁 (Reentry Ritual)
        If ladder exits filled cleanly and new signal within 2 hours with high memory match
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.WINDMARK
        
        print(f"🜁 PHASE 7: WINDMARK - REENTRY RITUAL - {flip_cycle.asset}")
        
        # Check if ladder exits filled cleanly
        clean_exit = self._check_clean_ladder_exit(flip_cycle)
        
        # Check for new signal within 2 hours with high memory match
        reentry_signal = self._check_reentry_signal(flip_cycle)
        
        print(f"   Clean Exit: {clean_exit}")
        print(f"   Reentry Signal: {reentry_signal}")
        
        if clean_exit and reentry_signal:
            # Invoke WINDMARK sigil (requires all 3 trinity votes)
            context = {
                'cycle_id': cycle_id,
                'clean_exit': clean_exit,
                'reentry_signal': reentry_signal,
                'emotional_sync': self.omega_core.emotional_sync
            }
            
            windmark_approved = await self.omega_core.invoke_sigil(SigilType.WINDMARK, context)
            
            if windmark_approved:
                print(f"🌪️ WINDMARK ACTIVATED - New flip cycle initiated")
                flip_cycle.metadata['windmark_activated'] = True
                # Could initiate new cycle here
        
        # Move to Phase 8
        return await self._phase_8_glyph_lock(cycle_id)
    
    async def _phase_8_glyph_lock(self, cycle_id: str) -> str:
        """
        Phase 8: GLYPH LOCK 🔒 (Vault Injection)
        Laddered profits must meet vault minimum with trinity consensus
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.GLYPH_LOCK
        
        print(f"🔒 PHASE 8: GLYPH LOCK - VAULT INJECTION - {flip_cycle.asset}")
        
        # Calculate final profits
        if flip_cycle.profits == 0.0:
            flip_cycle.profits = await self._calculate_final_profits(flip_cycle)
        
        print(f"   Cycle Profits: {flip_cycle.profits:.4f}")
        
        # Check vault minimum threshold
        vault_minimum = 0.001  # Configurable
        meets_minimum = flip_cycle.profits >= vault_minimum
        
        print(f"   Vault Minimum: {vault_minimum:.4f} | Meets Threshold: {meets_minimum}")
        
        if meets_minimum:
            # Invoke GLYPH_LOCK sigil (requires Manus consent)
            context = {
                'cycle_id': cycle_id,
                'profits': flip_cycle.profits,
                'vault_minimum': vault_minimum
            }
            
            glyph_approved = await self.omega_core.invoke_sigil(SigilType.GLYPH_LOCK, context)
            
            if glyph_approved:
                print(f"🏛️ VAULT INJECTION AUTHORIZED - Profits secured")
                flip_cycle.metadata['vault_injected'] = True
                self.omega_core.vault_balance += flip_cycle.profits
        
        # Move to Phase 9
        return await self._phase_9_echo_imprint(cycle_id)
    
    async def _phase_9_echo_imprint(self, cycle_id: str) -> str:
        """
        Phase 9: ECHO IMPRINT 🕸️ (Final Phase)
        Manus stores all flip metadata in neural memory for future pattern recognition
        """
        flip_cycle = self.active_cycles[cycle_id]
        flip_cycle.phase = FlipPhase.ECHO_IMPRINT
        flip_cycle.status = "COMPLETED"
        
        print(f"🕸️ PHASE 9: ECHO IMPRINT - {flip_cycle.asset}")
        
        # Generate echo score for future pattern recognition
        echo_score = self._generate_echo_score(flip_cycle)
        
        # Create memory echo
        memory_echo = MemoryEcho(
            asset=flip_cycle.asset,
            pattern_class=flip_cycle.signal.pattern_type,
            success_rate=1.0 if flip_cycle.profits > 0 else 0.0,
            profit_ratio=flip_cycle.profits,
            emotional_context=flip_cycle.signal.emotional_wave,
            cycle_count=1,
            last_seen=datetime.now()
        )
        
        # Store in MANUS neural memory
        self.omega_core.echo_memories.append(memory_echo)
        
        print(f"   Echo Score: {echo_score:.2f}")
        print(f"   Success Rate: {memory_echo.success_rate:.2f}")
        print(f"   Profit Ratio: {memory_echo.profit_ratio:.4f}")
        
        # Store final metadata
        flip_cycle.metadata.update({
            'echo_score': echo_score,
            'completion_time': datetime.now().isoformat(),
            'total_phases': 9
        })
        
        # Move to completed cycles
        self.completed_cycles.append(flip_cycle)
        del self.active_cycles[cycle_id]
        
        print(f"✅ FLIP CYCLE COMPLETE - {cycle_id}")
        print(f"🧠 Neural memory updated with echo imprint")
        
        return cycle_id
    
    # Helper methods for lifecycle phases
    def _get_historical_echoes(self, asset: str, pattern_type: str, days_back: int = 7) -> List[MemoryEcho]:
        """Get historical echoes for pattern analysis"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return [
            echo for echo in self.omega_core.echo_memories
            if (echo.asset == asset or echo.pattern_class == pattern_type)
            and echo.last_seen >= cutoff_date
        ]
    
    def _calculate_temporal_context(self, historical_echoes: List[MemoryEcho]) -> float:
        """Calculate temporal context from historical data"""
        if not historical_echoes:
            return 0.5
        
        avg_success = sum(echo.success_rate for echo in historical_echoes) / len(historical_echoes)
        return min(max(avg_success, 0.0), 1.0)
    
    def _calculate_cycle_weight(self, signal: Signal, historical_echoes: List[MemoryEcho]) -> float:
        """Calculate cycle weight based on signal and history"""
        base_weight = signal.score
        
        if historical_echoes:
            history_factor = sum(echo.success_rate for echo in historical_echoes) / len(historical_echoes)
            return (base_weight + history_factor) / 2
        
        return base_weight
    
    def _generate_ladder_config(self, flip_cycle: FlipCycle) -> Dict:
        """Generate ladder configuration for the flip"""
        signal = flip_cycle.signal
        
        # 3-5 rung configuration based on signal strength
        rung_count = 3 if signal.score < 0.8 else 5
        
        # Calculate entry range (placeholder logic)
        base_price = 1.0  # Would get from market data
        spread = 0.02 * signal.score  # 2% max spread based on signal
        
        return {
            'rung_count': rung_count,
            'entry_min': base_price * (1 - spread/2),
            'entry_max': base_price * (1 + spread/2),
            'position_size': 0.1,  # 10% of available capital
            'stop_loss': base_price * 0.95,  # 5% stop loss
            'take_profit': base_price * 1.1   # 10% take profit
        }
    
    def _check_system_overexposure(self) -> float:
        """Check if system is overexposed"""
        active_count = len(self.active_cycles)
        max_concurrent = 5  # Maximum concurrent flips
        return min(active_count / max_concurrent, 1.0)
    
    def _check_vault_endangerment(self) -> float:
        """Check if vaults are endangered"""
        # Placeholder logic for vault risk assessment
        return 0.1
    
    def _reevaluate_memory_signal(self, flip_cycle: FlipCycle) -> float:
        """Re-evaluate memory signal strength"""
        original_score = flip_cycle.signal.score
        time_decay = (datetime.now() - flip_cycle.start_time).total_seconds() / 3600  # Hours
        decay_factor = max(0.5, 1.0 - (time_decay * 0.1))  # 10% decay per hour
        return original_score * decay_factor
    
    def _check_clean_ladder_exit(self, flip_cycle: FlipCycle) -> bool:
        """Check if ladder exits were filled cleanly"""
        # Placeholder logic
        return True
    
    def _check_reentry_signal(self, flip_cycle: FlipCycle) -> bool:
        """Check for reentry signal within 2 hours"""
        # Placeholder logic
        return False
    
    async def _execute_trailing_sell(self, flip_cycle: FlipCycle) -> float:
        """Execute trailing sell logic for emergency exit"""
        # Placeholder implementation
        return 0.005  # 0.5% profit
    
    async def _calculate_final_profits(self, flip_cycle: FlipCycle) -> float:
        """Calculate final profits from the flip"""
        # Placeholder implementation
        return 0.01  # 1% profit
    
    def _generate_echo_score(self, flip_cycle: FlipCycle) -> float:
        """Generate echo score for pattern recognition"""
        base_score = flip_cycle.signal.score
        profit_factor = max(0.0, flip_cycle.profits * 10)  # Scale profits
        phase_completion = 1.0  # All 9 phases completed
        
        return min((base_score + profit_factor + phase_completion) / 3, 1.0)


"""
💎 PHASE IV - ΩSIGIL VAULT FEEDBACK LOOP
Recursive capital self-injection and genesis engine
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from core.omega_sigil_core import OmegaSigilCore, SigilType, Signal, TrinityAgent
from lifecycle.flip_lifecycle import FlipLifecycleManager

class VaultState(Enum):
    DORMANT = "DORMANT"
    ACCUMULATING = "ACCUMULATING"
    GENESIS_READY = "GENESIS_READY"
    GENESIS_ACTIVE = "GENESIS_ACTIVE"
    OVERFLOW = "OVERFLOW"

class GenesisMode(Enum):
    CONSERVATIVE = "CONSERVATIVE"  # 10% vault growth triggers
    AGGRESSIVE = "AGGRESSIVE"      # 5% vault growth triggers
    EXPONENTIAL = "EXPONENTIAL"    # 3% vault growth triggers

@dataclass
class VaultMetrics:
    total_balance: float
    growth_rate_24h: float
    injection_count: int
    genesis_cycles: int
    last_injection: datetime
    stability_score: float

@dataclass
class GenesisEvent:
    event_id: str
    trigger_balance: float
    new_signal_generated: bool
    cycle_id: Optional[str]
    timestamp: datetime
    success: bool
    profits_generated: float

class VaultFeedbackLoop:
    """
    💎 Capital Genesis Engine - Self-feeding recursive profit system
    Automatically reinvests profits to generate new trading opportunities
    """
    
    def __init__(self, omega_core: OmegaSigilCore, lifecycle_manager: FlipLifecycleManager):
        self.omega_core = omega_core
        self.lifecycle_manager = lifecycle_manager
        
        # Vault configuration
        self.vault_state = VaultState.DORMANT
        self.genesis_mode = GenesisMode.CONSERVATIVE
        self.growth_threshold = 0.10  # 10% growth triggers genesis
        self.minimum_vault_balance = 0.01  # Minimum balance to activate
        self.maximum_genesis_cycles = 3  # Max concurrent genesis cycles
        
        # Tracking
        self.vault_metrics = VaultMetrics(
            total_balance=0.0,
            growth_rate_24h=0.0,
            injection_count=0,
            genesis_cycles=0,
            last_injection=datetime.now(),
            stability_score=1.0
        )
        
        self.genesis_history: List[GenesisEvent] = []
        self.baseline_balance = 0.0
        self.last_genesis_check = datetime.now()
        
        print("💎 VAULT FEEDBACK LOOP INITIALIZED")
        print("🔁 Capital Genesis Engine ready for activation")
    
    async def process_profit_injection(self, cycle_id: str, profits: float, 
                                     asset: str) -> bool:
        """
        🏛️ Process profits from completed flip cycle
        Automatically injects into vault and checks for genesis triggers
        """
        print(f"💰 PROFIT INJECTION: {profits:.4f} from {cycle_id}")
        
        # Update vault balance
        previous_balance = self.omega_core.vault_balance
        self.omega_core.vault_balance += profits
        
        # Update metrics
        self.vault_metrics.total_balance = self.omega_core.vault_balance
        self.vault_metrics.injection_count += 1
        self.vault_metrics.last_injection = datetime.now()
        
        # Calculate growth rate
        growth = (self.omega_core.vault_balance - previous_balance) / previous_balance if previous_balance > 0 else 0
        self.vault_metrics.growth_rate_24h = growth  # Simplified - would track 24h in real implementation
        
        print(f"🏛️ Vault Balance: {self.omega_core.vault_balance:.4f} (+{profits:.4f})")
        print(f"📈 Growth Rate: {growth:.2%}")
        
        # Check if vault state should change
        await self._update_vault_state()
        
        # Check for genesis trigger
        genesis_triggered = await self._check_genesis_trigger()
        
        if genesis_triggered:
            await self._execute_genesis_cycle(asset)
        
        return True
    
    async def _update_vault_state(self):
        """🔄 Update vault state based on current metrics"""
        current_balance = self.omega_core.vault_balance
        
        if current_balance < self.minimum_vault_balance:
            self.vault_state = VaultState.DORMANT
            
        elif current_balance >= self.minimum_vault_balance and self.vault_state == VaultState.DORMANT:
            self.vault_state = VaultState.ACCUMULATING
            self.baseline_balance = current_balance
            print(f"🔄 VAULT STATE: ACCUMULATING (baseline: {self.baseline_balance:.4f})")
            
        elif self._check_growth_threshold():
            if self.vault_metrics.genesis_cycles < self.maximum_genesis_cycles:
                self.vault_state = VaultState.GENESIS_READY
                print("🔄 VAULT STATE: GENESIS_READY")
            else:
                self.vault_state = VaultState.OVERFLOW
                print("🔄 VAULT STATE: OVERFLOW (max genesis cycles reached)")
    
    def _check_growth_threshold(self) -> bool:
        """📊 Check if vault growth exceeds threshold for genesis"""
        if self.baseline_balance <= 0:
            return False
        
        current_growth = (self.omega_core.vault_balance - self.baseline_balance) / self.baseline_balance
        return current_growth >= self.growth_threshold
    
    async def _check_genesis_trigger(self) -> bool:
        """🔮 Check if conditions are met for genesis cycle"""
        
        # Must be in GENESIS_READY state
        if self.vault_state != VaultState.GENESIS_READY:
            return False
        
        # Must have MANUS + OMEGA approval
        genesis_context = {
            'vault_balance': self.omega_core.vault_balance,
            'growth_rate': self.vault_metrics.growth_rate_24h,
            'stability_score': self.vault_metrics.stability_score,
            'genesis_cycles': self.vault_metrics.genesis_cycles
        }
        
        # Get trinity votes for genesis authorization
        manus_approval = await self._get_manus_genesis_vote(genesis_context)
        omega_approval = await self._get_omega_genesis_vote(genesis_context)
        
        if manus_approval and omega_approval:
            print("✅ TRINITY CONSENSUS: Genesis cycle authorized")
            return True
        else:
            print("❌ TRINITY CONSENSUS: Genesis cycle blocked")
            return False
    
    async def _get_manus_genesis_vote(self, context: Dict) -> bool:
        """🧠 MANUS vote on genesis cycle authorization"""
        
        # Check vault memory integrity
        if self.vault_metrics.stability_score < 0.8:
            print("🧠 MANUS: Vault stability too low for genesis")
            return False
        
        # Check if too many recent genesis cycles
        recent_genesis = [g for g in self.genesis_history 
                         if g.timestamp > datetime.now() - timedelta(hours=1)]
        if len(recent_genesis) > 2:
            print("🧠 MANUS: Too many recent genesis cycles")
            return False
        
        # Check overall success rate
        if self.genesis_history:
            success_rate = sum(1 for g in self.genesis_history if g.success) / len(self.genesis_history)
            if success_rate < 0.6:
                print(f"🧠 MANUS: Genesis success rate too low: {success_rate:.2%}")
                return False
        
        print("🧠 MANUS: Genesis cycle approved")
        return True
    
    async def _get_omega_genesis_vote(self, context: Dict) -> bool:
        """⚡ OMEGA vote on genesis cycle authorization"""
        
        # Check if system is ready for execution
        if self.vault_metrics.genesis_cycles >= self.maximum_genesis_cycles:
            print("⚡ OMEGA: Maximum genesis cycles reached")
            return False
        
        # Check vault balance is sufficient
        if context['vault_balance'] < self.minimum_vault_balance * 2:
            print("⚡ OMEGA: Insufficient vault balance for genesis")
            return False
        
        # Check market conditions (simplified)
        if self.omega_core.threat_level > 0.5:
            print("⚡ OMEGA: Threat level too high for genesis")
            return False
        
        print("⚡ OMEGA: Genesis cycle approved")
        return True
    
    async def _execute_genesis_cycle(self, asset: str) -> bool:
        """
        🌟 Execute capital genesis cycle
        Creates new trading signal from vault growth energy
        """
        print("🌟 EXECUTING CAPITAL GENESIS CYCLE")
        
        # Update state
        self.vault_state = VaultState.GENESIS_ACTIVE
        self.vault_metrics.genesis_cycles += 1
        
        # Calculate genesis signal strength based on vault growth
        growth_rate = self.vault_metrics.growth_rate_24h
        signal_strength = min(0.7 + (growth_rate * 2), 0.95)  # Scale growth to signal strength
        
        # Generate genesis signal
        genesis_signal = Signal(
            score=signal_strength,
            asset=asset,
            pattern_type="vault_genesis",
            emotional_wave=0.3,  # Genesis signals are emotionally neutral
            whale_activity=False,
            timestamp=datetime.now()
        )
        
        print(f"🔮 GENESIS SIGNAL GENERATED:")
        print(f"   Asset: {genesis_signal.asset}")
        print(f"   Strength: {genesis_signal.score:.2f}")
        print(f"   Pattern: {genesis_signal.pattern_type}")
        
        # Initiate new flip cycle with genesis signal
        cycle_id = await self.lifecycle_manager.initiate_flip_cycle(genesis_signal)
        
        # Record genesis event
        genesis_event = GenesisEvent(
            event_id=f"GENESIS_{int(datetime.now().timestamp())}",
            trigger_balance=self.omega_core.vault_balance,
            new_signal_generated=cycle_id is not None,
            cycle_id=cycle_id,
            timestamp=datetime.now(),
            success=cycle_id is not None,
            profits_generated=0.0  # Will be updated when cycle completes
        )
        
        self.genesis_history.append(genesis_event)
        
        if cycle_id:
            print(f"✅ GENESIS CYCLE INITIATED: {cycle_id}")
            
            # Reset baseline for next genesis calculation
            self.baseline_balance = self.omega_core.vault_balance
            
            # Return to accumulating state
            self.vault_state = VaultState.ACCUMULATING
            
            return True
        else:
            print("❌ GENESIS CYCLE FAILED: Signal rejected")
            self.vault_state = VaultState.ACCUMULATING
            self.vault_metrics.genesis_cycles -= 1
            return False
    
    async def monitor_genesis_cycles(self):
        """🔍 Monitor active genesis cycles and update metrics"""
        
        # Check for completed genesis cycles
        for genesis_event in self.genesis_history:
            if genesis_event.cycle_id and genesis_event.profits_generated == 0.0:
                # Check if cycle is completed
                if genesis_event.cycle_id in self.lifecycle_manager.completed_cycles:
                    completed_cycle = None
                    for cycle in self.lifecycle_manager.completed_cycles:
                        if cycle.cycle_id == genesis_event.cycle_id:
                            completed_cycle = cycle
                            break
                    
                    if completed_cycle:
                        genesis_event.profits_generated = completed_cycle.profits
                        genesis_event.success = completed_cycle.profits > 0
                        
                        print(f"🌟 GENESIS CYCLE COMPLETED: {genesis_event.cycle_id}")
                        print(f"   Profits: {genesis_event.profits_generated:.4f}")
                        print(f"   Success: {genesis_event.success}")
        
        # Update stability score based on recent performance
        self._update_stability_score()
    
    def _update_stability_score(self):
        """📊 Update vault stability score based on performance"""
        if not self.genesis_history:
            self.vault_metrics.stability_score = 1.0
            return
        
        # Calculate success rate of recent genesis cycles
        recent_genesis = [g for g in self.genesis_history 
                         if g.timestamp > datetime.now() - timedelta(hours=24)]
        
        if recent_genesis:
            success_rate = sum(1 for g in recent_genesis if g.success) / len(recent_genesis)
            
            # Calculate average profit ratio
            profitable_genesis = [g for g in recent_genesis if g.profits_generated > 0]
            avg_profit_ratio = 0.0
            if profitable_genesis:
                avg_profit_ratio = sum(g.profits_generated for g in profitable_genesis) / len(profitable_genesis)
            
            # Combine success rate and profit performance
            self.vault_metrics.stability_score = (success_rate * 0.7) + (min(avg_profit_ratio * 10, 1.0) * 0.3)
        
        print(f"📊 Vault Stability Score: {self.vault_metrics.stability_score:.2f}")
    
    def get_vault_status(self) -> Dict:
        """📈 Get comprehensive vault status"""
        return {
            'state': self.vault_state.value,
            'balance': self.omega_core.vault_balance,
            'baseline_balance': self.baseline_balance,
            'growth_threshold': self.growth_threshold,
            'growth_rate_24h': self.vault_metrics.growth_rate_24h,
            'stability_score': self.vault_metrics.stability_score,
            'genesis_cycles_active': self.vault_metrics.genesis_cycles,
            'genesis_cycles_max': self.maximum_genesis_cycles,
            'injection_count': self.vault_metrics.injection_count,
            'last_injection': self.vault_metrics.last_injection.isoformat(),
            'genesis_history_count': len(self.genesis_history),
            'genesis_mode': self.genesis_mode.value
        }
    
    def configure_genesis_mode(self, mode: GenesisMode):
        """⚙️ Configure genesis trigger sensitivity"""
        self.genesis_mode = mode
        
        if mode == GenesisMode.CONSERVATIVE:
            self.growth_threshold = 0.10  # 10%
        elif mode == GenesisMode.AGGRESSIVE:
            self.growth_threshold = 0.05  # 5%
        elif mode == GenesisMode.EXPONENTIAL:
            self.growth_threshold = 0.03  # 3%
        
        print(f"⚙️ GENESIS MODE: {mode.value} (threshold: {self.growth_threshold:.1%})")
    
    async def emergency_vault_pause(self) -> bool:
        """🚨 Emergency pause of all vault operations"""
        print("🚨 EMERGENCY VAULT PAUSE ACTIVATED")
        
        self.vault_state = VaultState.DORMANT
        self.vault_metrics.genesis_cycles = 0
        
        # Invoke VOID_SIGIL for system pause if needed
        context = {'emergency': True, 'reason': 'vault_emergency_pause'}
        await self.omega_core.invoke_sigil(SigilType.VOID_SIGIL, context)
        
        return True

# Example usage and testing
if __name__ == "__main__":
    print("💎 VAULT FEEDBACK LOOP - STANDALONE TEST")
    
    async def demo_vault_feedback():
        # Initialize components
        omega_core = OmegaSigilCore()
        lifecycle_manager = FlipLifecycleManager(omega_core)
        vault_loop = VaultFeedbackLoop(omega_core, lifecycle_manager)
        
        print("\n🏛️ SIMULATING VAULT FEEDBACK LOOP")
        
        # Simulate profit injections
        await vault_loop.process_profit_injection("FLIP_BTC_001", 0.005, "BTC")
        await vault_loop.process_profit_injection("FLIP_ETH_002", 0.008, "ETH")
        await vault_loop.process_profit_injection("FLIP_BTC_003", 0.012, "BTC")
        
        # Check vault status
        status = vault_loop.get_vault_status()
        print(f"\n📊 VAULT STATUS:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Test genesis mode changes
        vault_loop.configure_genesis_mode(GenesisMode.AGGRESSIVE)
        
        # Simulate more profits to trigger genesis
        await vault_loop.process_profit_injection("FLIP_SOL_004", 0.015, "SOL")
        
        print("\n✅ VAULT FEEDBACK LOOP DEMO COMPLETE")
    
    asyncio.run(demo_vault_feedback())


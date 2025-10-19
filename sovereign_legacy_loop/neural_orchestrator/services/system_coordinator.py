"""
🎯 System Coordinator Service
=============================

Coordinates all 7 trading systems to prevent conflicts and manage execution.
This is the core intelligence that prevents systems from fighting each other.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from models import (
    SystemHealth, SystemHealthInfo, TradeSignal, ExecutionResult,
    SystemStatus
)
from services.system_connectors import (
    SovereignShadowConnector, OmegaAIConnector, NexusConnector,
    ScoutWatchConnector, Ghost90Connector, ToshiConnector, LedgerConnector
)

logger = logging.getLogger(__name__)


class SystemCoordinator:
    """Coordinates all trading systems to prevent conflicts and manage execution."""
    
    def __init__(self):
        """Initialize the system coordinator."""
        self.connectors = {
            'sovereign_shadow': SovereignShadowConnector(),
            'omega_ai': OmegaAIConnector(),
            'nexus': NexusConnector(),
            'scout_watch': ScoutWatchConnector(),
            'ghost90': Ghost90Connector(),
            'toshi': ToshiConnector(),
            'ledger': LedgerConnector()
        }
        
        # System priorities (higher number = higher priority)
        self.system_priorities = {
            'ledger': 100,      # Highest - emergency vault operations
            'omega_ai': 90,     # High - orchestration layer
            'nexus': 80,        # High - autonomous AI trader
            'sovereign_shadow': 70,  # Medium - primary trading platform
            'scout_watch': 60,  # Medium - surveillance
            'ghost90': 50,      # Medium - execution engine
            'toshi': 40         # Low - dashboard interface
        }
        
        # Capital allocation limits
        self.capital_limits = {
            'sovereign_shadow': 3000.0,  # 30% of $10K hot wallet
            'nexus': 2500.0,             # 25%
            'ghost90': 2000.0,           # 20%
            'scout_watch': 1500.0,       # 15%
            'omega_ai': 1000.0,          # 10%
            'toshi': 0.0,                # No trading
            'ledger': 0.0                # Cold storage only
        }
        
        # Track system states
        self.system_states = {}
        self.execution_history = []
        
        logger.info("🎯 System Coordinator initialized with conflict resolution")
    
    async def execute_signal(self, signal: TradeSignal) -> ExecutionResult:
        """Execute a trade signal with conflict resolution."""
        logger.info(f"Processing signal from {signal.system}: {signal.action} {signal.symbol}")
        
        try:
            # Step 1: Check for conflicts with other systems
            conflicts = await self._detect_conflicts(signal)
            
            if conflicts:
                logger.warning(f"Conflicts detected: {conflicts}")
                return self._resolve_conflicts(signal, conflicts)
            
            # Step 2: Check capital allocation
            if not await self._check_capital_allocation(signal):
                logger.warning(f"Insufficient capital for {signal.system}")
                return ExecutionResult(
                    signal=signal,
                    executed=False,
                    result="INSUFFICIENT_CAPITAL",
                    conflicts=[],
                    system_used=signal.system
                )
            
            # Step 3: Execute through appropriate system
            result = await self._execute_via_system(signal)
            
            # Step 4: Record execution
            self.execution_history.append({
                'signal': signal,
                'result': result,
                'timestamp': datetime.utcnow()
            })
            
            # Keep only last 100 executions
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
            
            logger.info(f"Signal executed successfully via {result.system_used}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return ExecutionResult(
                signal=signal,
                executed=False,
                result=f"ERROR: {str(e)}",
                conflicts=[],
                system_used=signal.system
            )
    
    async def get_system_health(self) -> SystemHealth:
        """Get health status of all systems."""
        logger.info("Checking system health...")
        
        systems = []
        healthy_count = 0
        
        for name, connector in self.connectors.items():
            try:
                health_info = await self._get_system_health_info(name, connector)
                systems.append(health_info)
                
                if health_info.status in [SystemStatus.ACTIVE, SystemStatus.STANDBY]:
                    healthy_count += 1
                    
            except Exception as e:
                logger.error(f"Error checking health for {name}: {e}")
                systems.append(SystemHealthInfo(
                    name=name,
                    status=SystemStatus.ERROR,
                    error_count=1
                ))
        
        # Determine overall status
        if healthy_count == len(systems):
            overall_status = SystemStatus.ACTIVE
        elif healthy_count >= len(systems) * 0.8:  # 80% healthy
            overall_status = SystemStatus.STANDBY
        else:
            overall_status = SystemStatus.ALERT
        
        return SystemHealth(
            overall_status=overall_status,
            systems=systems,
            total_systems=len(systems),
            healthy_systems=healthy_count
        )
    
    async def emergency_stop_all(self) -> Dict:
        """Emergency stop all trading systems."""
        logger.critical("🚨 EMERGENCY STOP INITIATED 🚨")
        
        results = {}
        
        for name, connector in self.connectors.items():
            try:
                # Skip ledger (cold storage) and toshi (dashboard)
                if name in ['ledger', 'toshi']:
                    results[name] = "SKIPPED (Non-trading system)"
                    continue
                
                result = await connector.emergency_stop()
                results[name] = result
                logger.info(f"Emergency stop for {name}: {result}")
                
            except Exception as e:
                logger.error(f"Emergency stop failed for {name}: {e}")
                results[name] = f"FAILED: {str(e)}"
        
        logger.critical("Emergency stop completed")
        return results
    
    async def check_all_systems(self) -> SystemHealth:
        """Check all systems (called by background monitor)."""
        return await self.get_system_health()
    
    async def _detect_conflicts(self, signal: TradeSignal) -> List[str]:
        """Detect conflicts with other systems."""
        conflicts = []
        
        try:
            # Get current positions from all systems
            all_positions = await self._get_all_positions()
            
            # Check for opposing signals on the same symbol
            for system_name, connector in self.connectors.items():
                if system_name == signal.system:
                    continue  # Skip the originating system
                
                try:
                    # Check if system has opposing position
                    system_positions = await connector.get_positions()
                    for pos in system_positions:
                        if pos.symbol == signal.symbol:
                            # Check if this would create a conflict
                            if self._is_opposing_action(signal.action, pos):
                                conflicts.append(f"{system_name} has opposing position in {signal.symbol}")
                                
                except Exception as e:
                    logger.error(f"Error checking conflicts with {system_name}: {e}")
            
            # Check for recent executions on same symbol
            recent_executions = [
                exec for exec in self.execution_history[-10:]  # Last 10 executions
                if exec['signal'].symbol == signal.symbol
                and (datetime.utcnow() - exec['timestamp']).seconds < 300  # Last 5 minutes
            ]
            
            if recent_executions:
                conflicts.append(f"Recent execution on {signal.symbol} within last 5 minutes")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return [f"CONFLICT_CHECK_ERROR: {str(e)}"]
    
    async def _resolve_conflicts(self, signal: TradeSignal, conflicts: List[str]) -> ExecutionResult:
        """Resolve conflicts using priority and confidence weighting."""
        logger.info(f"Resolving conflicts for {signal.signal}: {conflicts}")
        
        # Get system priority
        signal_priority = self.system_priorities.get(signal.system, 50)
        
        # Check if this is an emergency signal (high priority)
        if signal_priority >= 90 or signal.confidence >= 0.95:
            logger.info(f"High priority signal ({signal_priority}), executing despite conflicts")
            return await self._execute_via_system(signal)
        
        # Check if conflicts are from lower priority systems
        conflicting_systems = []
        for conflict in conflicts:
            if "has opposing position" in conflict:
                system_name = conflict.split()[0]
                conflicting_priority = self.system_priorities.get(system_name, 50)
                if conflicting_priority < signal_priority:
                    conflicting_systems.append(system_name)
        
        if conflicting_systems:
            logger.info(f"Conflicts from lower priority systems: {conflicting_systems}")
            return await self._execute_via_system(signal)
        
        # Default: Cancel execution due to conflicts
        return ExecutionResult(
            signal=signal,
            executed=False,
            result="CANCELLED_DUE_TO_CONFLICTS",
            conflicts=conflicts,
            system_used=signal.system
        )
    
    async def _check_capital_allocation(self, signal: TradeSignal) -> bool:
        """Check if system has sufficient capital allocation."""
        system_limit = self.capital_limits.get(signal.system, 0.0)
        
        if system_limit <= 0:
            return False  # System not allowed to trade
        
        # Get current usage for this system
        try:
            current_usage = await self._get_system_capital_usage(signal.system)
            return (current_usage + signal.amount) <= system_limit
            
        except Exception as e:
            logger.error(f"Error checking capital allocation: {e}")
            return False
    
    async def _execute_via_system(self, signal: TradeSignal) -> ExecutionResult:
        """Execute the signal via the appropriate system."""
        try:
            connector = self.connectors.get(signal.system)
            if not connector:
                return ExecutionResult(
                    signal=signal,
                    executed=False,
                    result="SYSTEM_NOT_FOUND",
                    conflicts=[],
                    system_used=signal.system
                )
            
            # Execute the signal
            execution_result = await connector.execute_signal(signal)
            
            return ExecutionResult(
                signal=signal,
                executed=execution_result.get('success', False),
                result=execution_result.get('message', 'Executed'),
                conflicts=[],
                system_used=signal.system
            )
            
        except Exception as e:
            logger.error(f"Error executing via system {signal.system}: {e}")
            return ExecutionResult(
                signal=signal,
                executed=False,
                result=f"EXECUTION_ERROR: {str(e)}",
                conflicts=[],
                system_used=signal.system
            )
    
    async def _get_system_health_info(self, name: str, connector) -> SystemHealthInfo:
        """Get health information for a specific system."""
        try:
            health_data = await connector.health_check()
            
            return SystemHealthInfo(
                name=name,
                status=health_data.get('status', SystemStatus.OFFLINE),
                last_heartbeat=health_data.get('last_heartbeat'),
                error_count=health_data.get('error_count', 0),
                uptime_seconds=health_data.get('uptime_seconds', 0),
                memory_usage_mb=health_data.get('memory_usage_mb', 0.0),
                cpu_usage_percent=health_data.get('cpu_usage_percent', 0.0)
            )
            
        except Exception as e:
            logger.error(f"Error getting health info for {name}: {e}")
            return SystemHealthInfo(
                name=name,
                status=SystemStatus.ERROR,
                error_count=1
            )
    
    async def _get_all_positions(self) -> List:
        """Get all positions from all systems."""
        all_positions = []
        
        for connector in self.connectors.values():
            try:
                positions = await connector.get_positions()
                all_positions.extend(positions)
            except Exception as e:
                logger.error(f"Error getting positions: {e}")
        
        return all_positions
    
    async def _get_system_capital_usage(self, system_name: str) -> float:
        """Get current capital usage for a system."""
        try:
            connector = self.connectors.get(system_name)
            if not connector:
                return 0.0
            
            positions = await connector.get_positions()
            total_value = sum(pos.value_usd for pos in positions)
            
            return total_value
            
        except Exception as e:
            logger.error(f"Error getting capital usage for {system_name}: {e}")
            return 0.0
    
    def _is_opposing_action(self, signal_action: str, position) -> bool:
        """Check if signal action opposes existing position."""
        # This is simplified - in production you'd have more sophisticated logic
        if signal_action == "BUY" and position.amount < 0:
            return True
        elif signal_action == "SELL" and position.amount > 0:
            return True
        
        return False

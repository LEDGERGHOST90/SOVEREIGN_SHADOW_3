"""
SOVEREIGN SHADOW II - Orchestration Module

Master Orchestrator implementing D.O.E. Pattern:
- Directive Layer: Market Regime Detection
- Orchestration Layer: AI Strategy Selection
- Execution Layer: Trade Execution
- Learning Layer: Performance Tracking
"""

from .orchestrator import (
    SovereignShadowOrchestrator,
    OrchestratorConfig,
    Position,
    create_orchestrator
)

from .builtin_strategies import (
    ElderReversionEntry, ElderReversionExit, ElderReversionRisk,
    RSIReversionEntry, RSIReversionExit, RSIReversionRisk,
    TrendFollowEMAEntry, TrendFollowEMAExit, TrendFollowEMARisk,
    get_strategy,
    list_strategies,
    STRATEGY_REGISTRY
)

__all__ = [
    # Orchestrator
    'SovereignShadowOrchestrator',
    'OrchestratorConfig',
    'Position',
    'create_orchestrator',

    # Built-in strategies
    'ElderReversionEntry', 'ElderReversionExit', 'ElderReversionRisk',
    'RSIReversionEntry', 'RSIReversionExit', 'RSIReversionRisk',
    'TrendFollowEMAEntry', 'TrendFollowEMAExit', 'TrendFollowEMARisk',
    'get_strategy',
    'list_strategies',
    'STRATEGY_REGISTRY'
]

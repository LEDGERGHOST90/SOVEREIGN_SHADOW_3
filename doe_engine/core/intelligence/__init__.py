"""
SOVEREIGN SHADOW III - Intelligence Module

D.O.E. Pattern Implementation:
- Directive Layer: MarketRegimeDetector
- Orchestration Layer: AIStrategySelector
- Execution Layer: (Handled by orchestrator)
- Learning Layer: PerformanceTracker
"""

from .performance_tracker import (
    PerformanceTracker,
    get_performance_tracker
)

from .regime_detector import (
    MarketRegime,
    RegimeAnalysis,
    MarketRegimeDetector,
    get_regime_detector
)

from .strategy_selector import (
    StrategyRecommendation,
    AIStrategySelector,
    get_strategy_selector,
    DEFAULT_STRATEGIES
)

__all__ = [
    # Performance Tracker
    'PerformanceTracker',
    'get_performance_tracker',

    # Regime Detector
    'MarketRegime',
    'RegimeAnalysis',
    'MarketRegimeDetector',
    'get_regime_detector',

    # Strategy Selector
    'StrategyRecommendation',
    'AIStrategySelector',
    'get_strategy_selector',
    'DEFAULT_STRATEGIES'
]

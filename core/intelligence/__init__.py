#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Intelligence Layer
D.O.E. Pattern: Directive → Orchestration → Execution

Components:
- performance_tracker: Tracks strategy performance and enables self-annealing
- regime_detector: Classifies market conditions
- strategy_selector: Picks best strategy for current regime
"""

from .performance_tracker import PerformanceTracker
from .regime_detector import RegimeDetector, MarketRegime
from .strategy_selector import StrategySelector

__all__ = [
    'PerformanceTracker',
    'RegimeDetector',
    'MarketRegime',
    'StrategySelector'
]

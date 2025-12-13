"""
Core Module
Main components of Sovereign Shadow II system
"""

from .orchestrator import SovereignShadowOrchestrator
from .exchange_connectors import BaseExchangeConnector, CoinbaseAdvancedConnector
from .intelligence import PerformanceTracker, MarketRegimeDetector, AIStrategySelector

__all__ = [
    'SovereignShadowOrchestrator',
    'BaseExchangeConnector',
    'CoinbaseAdvancedConnector',
    'PerformanceTracker',
    'MarketRegimeDetector',
    'AIStrategySelector'
]

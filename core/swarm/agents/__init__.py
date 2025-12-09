"""
Swarm Colony Agents
6 specialized trading agents with unique strategies
"""

from .volatility_hunter import VolatilityHunter, create_volatility_hunter
from .rsi_reader import RSIReader, create_rsi_reader
from .technical_master import TechnicalMaster, create_technical_master
from .pattern_master import AdvancedPatternMaster, create_advanced_pattern_master
from .whale_watcher import WhaleWatcherAgent, create_whale_watcher
from .sentiment_scanner import SentimentScannerAgent, create_sentiment_scanner

__all__ = [
    'VolatilityHunter', 'create_volatility_hunter',
    'RSIReader', 'create_rsi_reader',
    'TechnicalMaster', 'create_technical_master',
    'AdvancedPatternMaster', 'create_advanced_pattern_master',
    'WhaleWatcherAgent', 'create_whale_watcher',
    'SentimentScannerAgent', 'create_sentiment_scanner'
]

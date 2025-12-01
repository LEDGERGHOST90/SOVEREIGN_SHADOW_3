"""
SYNOPTIC CORE - Unified Fundamental & Technical Analysis
Smart Asset Score from mixed data (price, on-chain, docs, sentiment)
"""

from .core import SynopticCore
from .market_data_client import MarketDataClient
from .onchain_client import OnChainClient
from .text_sources_client import TextSourcesClient

__all__ = ["SynopticCore", "MarketDataClient", "OnChainClient", "TextSourcesClient"]

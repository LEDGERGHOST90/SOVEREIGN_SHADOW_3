"""
Exchange Connectors Module
Provides unified interface for multiple cryptocurrency exchanges
"""

from .base_connector import BaseExchangeConnector
from .coinbase_connector import CoinbaseAdvancedConnector

__all__ = ['BaseExchangeConnector', 'CoinbaseAdvancedConnector']

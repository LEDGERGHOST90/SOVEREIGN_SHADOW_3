"""
🚀 Execution Module

Trading execution bridges:
- Shadow Sniper (Coinbase)
- Swarm Intelligence (multi-agent)
- Universal Exchange Manager (CCXT-based)
- Portfolio Connector (Real capital bridge)
"""

from .universal_exchange_manager import UniversalExchangeManager
from .portfolio_connector import RealPortfolioConnector

__all__ = ['UniversalExchangeManager', 'RealPortfolioConnector']

"""
Market Filters Package
======================
Research-backed market sentiment and macro filters for SOVEREIGN_SHADOW_3.

Modules:
- market_filters: Fear & Greed Index and DXY correlation filters
"""

from .market_filters import OracleMarketFilters

# Alias for backwards compatibility
MarketFilters = OracleMarketFilters

__all__ = ['OracleMarketFilters', 'MarketFilters']

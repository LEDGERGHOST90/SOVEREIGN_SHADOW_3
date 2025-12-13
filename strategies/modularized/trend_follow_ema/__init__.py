#!/usr/bin/env python3
"""
🏴 Trend Follow EMA Strategy
Trend following using EMA crossovers

Type: Trend Following
Suitable Regimes: trending_bull, trending_bear
"""

from .entry import TrendFollowEMAEntry
from .exit import TrendFollowEMAExit
from .risk import TrendFollowEMARisk
from strategies.modularized.base import ModularStrategy


def get_strategy() -> ModularStrategy:
    return ModularStrategy(
        name="TrendFollowEMA",
        entry_module=TrendFollowEMAEntry(),
        exit_module=TrendFollowEMAExit(),
        risk_module=TrendFollowEMARisk(),
        suitable_regimes=["trending_bull"],
        timeframes=["1h", "4h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )


__all__ = ['get_strategy', 'TrendFollowEMAEntry', 'TrendFollowEMAExit', 'TrendFollowEMARisk']

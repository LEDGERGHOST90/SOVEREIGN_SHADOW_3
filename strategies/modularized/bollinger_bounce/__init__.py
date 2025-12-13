#!/usr/bin/env python3
"""
🏴 Bollinger Bounce Strategy
Mean reversion from Bollinger Band extremes
"""

from .entry import BollingerBounceEntry
from .exit import BollingerBounceExit
from .risk import BollingerBounceRisk
from strategies.modularized.base import ModularStrategy


def get_strategy() -> ModularStrategy:
    return ModularStrategy(
        name="BollingerBounce",
        entry_module=BollingerBounceEntry(),
        exit_module=BollingerBounceExit(),
        risk_module=BollingerBounceRisk(),
        suitable_regimes=["choppy_volatile", "trending_bear"],
        timeframes=["15m", "1h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )


__all__ = ['get_strategy']

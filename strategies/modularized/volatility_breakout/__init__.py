#!/usr/bin/env python3
"""
🏴 Volatility Breakout Strategy
ATR-based breakout detection for calm markets
"""

from .entry import VolatilityBreakoutEntry
from .exit import VolatilityBreakoutExit
from .risk import VolatilityBreakoutRisk
from strategies.modularized.base import ModularStrategy


def get_strategy() -> ModularStrategy:
    return ModularStrategy(
        name="VolatilityBreakout",
        entry_module=VolatilityBreakoutEntry(),
        exit_module=VolatilityBreakoutExit(),
        risk_module=VolatilityBreakoutRisk(),
        suitable_regimes=["choppy_calm"],
        timeframes=["1h", "4h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )


__all__ = ['get_strategy']

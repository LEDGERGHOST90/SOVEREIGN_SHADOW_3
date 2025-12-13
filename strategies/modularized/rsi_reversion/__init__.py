#!/usr/bin/env python3
"""
🏴 RSI Reversion Strategy
Mean reversion using RSI oversold/overbought conditions
"""

from .entry import RSIReversionEntry
from .exit import RSIReversionExit
from .risk import RSIReversionRisk
from strategies.modularized.base import ModularStrategy


def get_strategy() -> ModularStrategy:
    return ModularStrategy(
        name="RSIReversion",
        entry_module=RSIReversionEntry(),
        exit_module=RSIReversionExit(),
        risk_module=RSIReversionRisk(),
        suitable_regimes=["choppy_volatile", "trending_bear"],
        timeframes=["15m", "1h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )


__all__ = ['get_strategy', 'RSIReversionEntry', 'RSIReversionExit', 'RSIReversionRisk']

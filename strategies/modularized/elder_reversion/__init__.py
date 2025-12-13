#!/usr/bin/env python3
"""
🏴 Elder Reversion Strategy
Mean reversion using Elder Ray Bull/Bear Power

Type: Mean Reversion
Suitable Regimes: choppy_volatile, choppy_calm
"""

from .entry import ElderReversionEntry
from .exit import ElderReversionExit
from .risk import ElderReversionRisk
from strategies.modularized.base import ModularStrategy


def get_strategy() -> ModularStrategy:
    """Factory function to create strategy instance"""
    return ModularStrategy(
        name="ElderReversion",
        entry_module=ElderReversionEntry(),
        exit_module=ElderReversionExit(),
        risk_module=ElderReversionRisk(),
        suitable_regimes=["choppy_volatile", "choppy_calm"],
        timeframes=["15m", "1h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )


__all__ = ['get_strategy', 'ElderReversionEntry', 'ElderReversionExit', 'ElderReversionRisk']

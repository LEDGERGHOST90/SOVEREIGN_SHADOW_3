#!/usr/bin/env python3
"""🏴 Banded Stochastic Strategy - Stochastic with Bollinger Bands confirmation"""
from .entry import BandedStochasticEntry
from .exit import BandedStochasticExit
from .risk import BandedStochasticRisk
from strategies.modularized.base import ModularStrategy

def get_strategy() -> ModularStrategy:
    return ModularStrategy(
        name="BandedStochastic",
        entry_module=BandedStochasticEntry(),
        exit_module=BandedStochasticExit(),
        risk_module=BandedStochasticRisk(),
        suitable_regimes=["choppy_volatile", "choppy_calm"],
        timeframes=["15m", "1h"],
        assets=["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    )

__all__ = ['get_strategy']

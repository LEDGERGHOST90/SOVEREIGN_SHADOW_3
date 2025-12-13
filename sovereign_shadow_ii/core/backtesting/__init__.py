"""
SOVEREIGN SHADOW II - Backtesting Module

Comprehensive backtesting framework for modularized strategies.
"""

from .backtest_engine import (
    BacktestEngine,
    BacktestResult,
    TradeResult
)

__all__ = [
    'BacktestEngine',
    'BacktestResult',
    'TradeResult'
]

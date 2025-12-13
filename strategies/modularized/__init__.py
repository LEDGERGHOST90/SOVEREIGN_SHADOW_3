#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Modularized Strategies
Skills-Based AI Architecture

Each strategy is broken into three components:
- Entry Module: Signal generation for entries
- Exit Module: Exit logic (take profit, stop loss, signal exit)
- Risk Module: Position sizing and risk management

Directory Structure:
    strategies/modularized/
        base.py                 # Base classes
        registry.py             # Strategy registry
        elder_reversion/        # Individual strategy
            __init__.py
            entry.py
            exit.py
            risk.py
            metadata.json
"""

from .base import (
    BaseEntryModule,
    BaseExitModule,
    BaseRiskModule,
    ModularStrategy,
    Signal,
    ExitSignal,
    PositionSizing
)
from .registry import StrategyRegistry

__all__ = [
    'BaseEntryModule',
    'BaseExitModule',
    'BaseRiskModule',
    'ModularStrategy',
    'Signal',
    'ExitSignal',
    'PositionSizing',
    'StrategyRegistry'
]

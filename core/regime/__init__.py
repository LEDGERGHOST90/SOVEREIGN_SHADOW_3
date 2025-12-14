"""
Regime Detection Module

Contains HMM-based regime detection for adaptive trading strategies.
"""

from .hmm_regime_detector import (
    HMMRegimeDetector,
    RegimeType,
    TradingRules
)

__all__ = [
    'HMMRegimeDetector',
    'RegimeType',
    'TradingRules'
]

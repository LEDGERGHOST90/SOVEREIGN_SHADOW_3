"""
Regime Detection Module

Contains HMM-based regime detection for adaptive trading strategies.
"""

from .hmm_regime_detector import RegimeHMMDetector

# Alias for backwards compatibility
HMMRegimeDetector = RegimeHMMDetector

__all__ = [
    'RegimeHMMDetector',
    'HMMRegimeDetector',
]

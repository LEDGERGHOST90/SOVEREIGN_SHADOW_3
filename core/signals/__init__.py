"""
Sovereign Shadow III - Signals Package

On-chain and market signal modules for enhanced trading intelligence.
"""

from .onchain_signals import FlowOnChainSignals

# Alias for backwards compatibility
OnChainSignals = FlowOnChainSignals

__all__ = ['FlowOnChainSignals', 'OnChainSignals']

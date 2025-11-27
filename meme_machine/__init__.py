"""
MemeMachine - Solana Meme Coin Scanner & Analyzer

A tool for scanning, analyzing, and monitoring meme coins on Solana.
Uses multiple data sources for comprehensive token analysis.

Data Sources:
- DexScreener: Free, no rate limits - best for scanning
- Birdeye: Rate limited but deeper analytics
- Helius: RPC + DAS API for holder analysis and rug detection

Usage:
    python -m meme_machine --help

    # Or import directly:
    from meme_machine import MemeMachine
    machine = MemeMachine()
    machine.dex_scan()
"""

from .scanner import MemeMachine
from .analyzer import BreakoutAnalyzer, TokenScore
from .clients import BirdeyeClient, DexScreenerClient, HeliusClient

__version__ = "1.1.0"
__author__ = "LedgerGhost90"

__all__ = [
    'MemeMachine',
    'BreakoutAnalyzer',
    'TokenScore',
    'BirdeyeClient',
    'DexScreenerClient',
    'HeliusClient'
]

"""
GATEKEEPER - Automated On-Chain Data Wrangling
Standardizes messy CEX/DEX/blockchain API responses into Sovereign Standard Schema

Methods:
- clean(): Row-by-row processing (safe for any size)
- clean_vectorized(): Pandas-based processing (10-100x faster for large datasets)
"""

from .core import Gatekeeper, SovereignStandardRecord, HAS_PANDAS

__all__ = ["Gatekeeper", "SovereignStandardRecord", "HAS_PANDAS"]

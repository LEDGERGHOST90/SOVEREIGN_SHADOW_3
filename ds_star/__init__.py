"""
DS-STAR: Decision Support - Strategic Trading Analysis & Research
Sovereign Shadow 3's Multi-Agent Intelligence Layer

Modules:
1. Synoptic Core - Unified asset analysis (technical + on-chain + fundamental)
2. Architect Forge - Self-correcting strategy builder
3. Oracle Interface - Natural language market insights
4. Gatekeeper - On-chain data normalization
5. Transparent Analyst - Step-by-step execution visibility
"""

__version__ = "1.0.0"
__author__ = "Sovereign Shadow Council"

from .synoptic_core import SynopticCore
from .architect_forge import ArchitectForge
from .oracle_interface import OracleInterface
from .gatekeeper import Gatekeeper
from .transparent_analyst import TransparentAnalyst

__all__ = [
    "SynopticCore",
    "ArchitectForge",
    "OracleInterface",
    "Gatekeeper",
    "TransparentAnalyst"
]

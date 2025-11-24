"""
🏴 SHADOW SDK - Sovereign Shadow Internal Toolbox

The unified Python SDK powering the Sovereign Shadow Trading Empire.

Core Modules:
    - ShadowScope: Market scanner core (real-time intelligence)
    - ShadowPulse: Live signal streaming & heartbeat monitoring
    - ShadowSnaps: Snapshot & historical analytics
    - ShadowSynapse: AI reasoning & orchestration layer

Utilities:
    - logger: System-wide logging & monitoring
    - notion: Automated journaling to Notion
    - exchanges: Unified exchange API wrapper
    - risk: Risk management & safety rules

Version: 0.1.0-GENESIS
Philosophy: "Fearless. Bold. Smiling through chaos."
"""

from .scope import ShadowScope
from .pulse import ShadowPulse
from .snaps import ShadowSnaps
from .synapse import ShadowSynapse
from .gemini import ShadowMind

__version__ = "0.1.0"
__all__ = ["ShadowScope", "ShadowPulse", "ShadowSnaps", "ShadowSynapse", "ShadowMind"]

# Empire Constants
CAPITAL_TOTAL = 8260
CAPITAL_LEDGER = 6600  # Cold storage (read-only)
CAPITAL_COINBASE = 1660  # Hot wallet (active trading)
TARGET_CAPITAL = 50000
TARGET_DATE = "Q4 2025"

# Safety Limits
MAX_DAILY_LOSS = 100
MAX_POSITION_SIZE = 415  # 25% of Coinbase balance
STOP_LOSS_PERCENT = 0.05
CONSECUTIVE_LOSS_LIMIT = 3

# Monitored Assets
EXCHANGES = ["coinbase", "okx", "kraken"]
PAIRS = ["BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "ADA/USD", "DOGE/USD", "LTC/USD"]

# System Philosophy
PHILOSOPHY = "Fearless. Bold. Smiling through chaos."


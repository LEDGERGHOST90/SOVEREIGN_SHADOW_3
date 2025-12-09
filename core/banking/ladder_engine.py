"""
TRX Protocol - Advanced Ladder & TP/SL Engine
Sniper laddered entries with fixed TP1/TP2 logic and trail_after_tp1
Commander: LedgerGhost90
Tag: TRX_PROTOCOL_071425
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd

logger = logging.getLogger('LadderEngine')

class MarketCondition(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

class LadderStrategy(Enum):
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    SNIPER = "sniper"

@dataclass
class MarketAnalysis:
    trend_direction: str
    volatility: float
    volume_ratio: float
    support_level: float
    resistance_level: float
    rsi: float
    macd_signal: str
    condition: MarketCondition
    confidence: float

@dataclass
class LadderLevel:
    level: int
    price: float
    quantity: float
    percentage: float
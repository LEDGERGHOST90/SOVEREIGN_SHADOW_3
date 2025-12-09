"""
KeyBladeAI Trading Engine - Local Sovereignty Edition
Complete local control with surgical API precision
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import aiohttp
import websockets
import sqlite3
from cryptography.fernet import Fernet
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/keyblade_logs/engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('KeyBladeEngine')

class TradingPlatform(Enum):
    KRAKEN = "kraken"
    COINBASE = "coinbase"
    KUCOIN = "kucoin"
    LOCAL_TEST = "local_test"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    OCO = "oco"  # One-Cancels-Other
    TRAILING_STOP = "trailing_stop"

class FlipStatus(Enum):
    PENDING = "pending"
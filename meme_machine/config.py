"""
MemeMachine Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/Volumes/LegacySafe/SovereignShadow_II/.env')

# Base paths
BASE_DIR = Path('/Volumes/LegacySafe/SovereignShadow_II/meme_machine')
LOG_DIR = BASE_DIR / 'logs'

# API Keys
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY', '')
HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '')

# Chain
CHAIN = "solana"

# Snipe Criteria
MIN_LIQUIDITY = 10000       # $10k minimum liquidity
MAX_MARKET_CAP = 1000000    # $1M max market cap for early entry
MIN_VOLUME_24H = 5000       # $5k minimum 24h volume
MAX_AGE_HOURS = 24          # Only tokens < 24h old

# Risk Thresholds
MAX_HOLDER_CONCENTRATION = 50  # Max % held by top 5 wallets
MIN_HOLDERS = 100              # Minimum unique holders

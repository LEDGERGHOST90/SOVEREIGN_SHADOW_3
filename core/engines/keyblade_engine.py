"""
KeyBladeAI Trading Engine - Local Sovereignty Edition
Complete local control with surgical API precision
Integrated from OneDrive/KeyBlade Fortess - Dec 9, 2025
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
import sqlite3
from cryptography.fernet import Fernet
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    OCO = "oco"
    TRAILING_STOP = "trailing_stop"

class FlipStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class FlipConfig:
    asset: str
    entry_price: float
    target_price: float
    stop_loss: float
    position_size: float
    platform: TradingPlatform
    ray_rules_clarity: float
    ai_confidence: float
    max_hold_time: int
    vault_siphon_rate: float = 0.30
    ladder: Optional[List[Tuple[float, float]]] = None

@dataclass
class MarketData:
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    timestamp: datetime
    bid: float
    ask: float
    spread: float

class LocalEncryption:
    """Local encryption for sensitive data"""

    def __init__(self):
        self.key_file = Path.home() / ".keyblade" / "encryption.key"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)

        with open(self.key_file, 'rb') as f:
            self.cipher = Fernet(f.read())

    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        return self.cipher.decrypt(encrypted_data).decode()

class LocalDatabase:
    """Local SQLite database for complete data sovereignty"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path.home() / ".keyblade" / "keyblade.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS flips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flip_id TEXT UNIQUE NOT NULL,
                    asset TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    target_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    position_size REAL NOT NULL,
                    status TEXT NOT NULL,
                    ray_rules_clarity REAL NOT NULL,
                    ai_confidence REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    profit_loss REAL DEFAULT 0,
                    vault_siphon REAL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume_24h REAL NOT NULL,
                    change_24h REAL NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    spread REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS vault_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flip_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    wallet_address TEXT,
                    transaction_hash TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS api_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    response_time_ms INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_flips_status ON flips(status);
                CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
                CREATE INDEX IF NOT EXISTS idx_vault_flip_id ON vault_transactions(flip_id);
            ''')

class APIManager:
    """Manages all external API connections with precision monitoring"""

    def __init__(self, encryption: LocalEncryption):
        self.encryption = encryption
        self.session = None
        self.api_keys = self.load_api_keys()
        self.performance_tracker = {}

    def load_api_keys(self) -> Dict[str, str]:
        """Load encrypted API keys from local storage"""
        keys_file = Path.home() / ".keyblade" / "api_keys.enc"
        if not keys_file.exists():
            api_key = os.getenv("KRAKEN_API_KEY")
            api_secret = os.getenv("KRAKEN_API_SECRET")
            if api_key and api_secret:
                return {"kraken": {"api_key": api_key, "api_secret": api_secret}}
            return {}
        try:
            with open(keys_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self.encryption.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return {}

    async def get_market_data(self, symbol: str, source: str = "kraken") -> Optional[MarketData]:
        """Get real-time market data with precision timing"""
        start_time = time.time()
        try:
            if source == "coingecko":
                data = await self._fetch_coingecko_data(symbol)
            elif source == "kraken":
                data = await self._fetch_kraken_data(symbol)
            else:
                raise ValueError(f"Unsupported data source: {source}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch market data for {symbol}: {e}")
            return None

    async def _fetch_kraken_data(self, symbol: str) -> MarketData:
        """Fetch data from Kraken Public API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        pair = symbol.replace('/', '')
        url = f"https://api.kraken.com/0/public/Ticker?pair={pair}"
        async with self.session.get(url) as response:
            data = await response.json()
        result = data.get('result')
        if not result:
            raise ValueError(f"No data from Kraken for {symbol}")
        ticker = next(iter(result.values()))
        price = float(ticker['c'][0])
        bid = float(ticker['b'][0])
        ask = float(ticker['a'][0])
        volume_24h = float(ticker['v'][1])
        change_24h = float(ticker['p'][1]) - float(ticker['p'][0]) if 'p' in ticker else 0.0
        spread = ask - bid
        return MarketData(
            symbol=symbol,
            price=price,
            volume_24h=volume_24h,
            change_24h=change_24h,
            timestamp=datetime.now(),
            bid=bid,
            ask=ask,
            spread=spread
        )

class RiskManager:
    """Local risk management with Ray Rules integration"""

    def __init__(self, max_position_size: float = 1200, max_daily_loss: float = 500):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0
        self.active_positions = {}

    def validate_flip(self, config: FlipConfig) -> Tuple[bool, str]:
        """Validate flip against risk parameters and Ray Rules"""
        if config.position_size > self.max_position_size:
            return False, f"Position size {config.position_size} exceeds maximum {self.max_position_size}"
        if config.ray_rules_clarity < 0.80:
            return False, f"Ray Rules clarity {config.ray_rules_clarity} below minimum 0.80"
        if config.ai_confidence < 0.80:
            return False, f"AI confidence {config.ai_confidence} below minimum 0.80"
        potential_loss = config.position_size * 0.05
        if self.daily_pnl - potential_loss < -self.max_daily_loss:
            return False, f"Potential daily loss exceeds maximum {self.max_daily_loss}"
        risk = config.entry_price - config.stop_loss
        reward = config.target_price - config.entry_price
        if reward / risk < 2.0:
            return False, f"Risk/reward ratio {reward/risk:.2f} below minimum 2.0"
        return True, "Risk validation passed"

class VaultManager:
    """Local vault management with 30% mandatory siphoning"""

    def __init__(self, db: LocalDatabase):
        self.db = db
        self.siphon_rate = 0.30
        self.vault_balance = 0

    def process_flip_completion(self, flip_id: str, profit: float) -> float:
        """Process completed flip and siphon to vault"""
        if profit <= 0:
            return 0
        siphon_amount = profit * self.siphon_rate
        self.vault_balance += siphon_amount
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute('''
                INSERT INTO vault_transactions (flip_id, amount, transaction_type)
                VALUES (?, ?, ?)
            ''', (flip_id, siphon_amount, 'SIPHON'))
        logger.info(f"Siphoned ${siphon_amount:.2f} to vault from flip {flip_id}")
        return siphon_amount

    def get_vault_status(self) -> Dict:
        """Get current vault status"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                SELECT SUM(amount) FROM vault_transactions
                WHERE transaction_type = 'SIPHON'
            ''')
            total_siphoned = cursor.fetchone()[0] or 0
        return {
            'current_balance': self.vault_balance,
            'total_siphoned': total_siphoned,
            'target_balance': 10000,
            'progress_percentage': (total_siphoned / 10000) * 100
        }

class KeyBladeEngine:
    """Main KeyBladeAI trading engine with complete local sovereignty"""

    def __init__(self):
        self.encryption = LocalEncryption()
        self.db = LocalDatabase()
        self.api_manager = APIManager(self.encryption)
        self.risk_manager = RiskManager()
        self.vault_manager = VaultManager(self.db)
        self.active_flips = {}
        self.is_running = False
        logger.info("KeyBladeAI Engine initialized with local sovereignty")

    async def start_engine(self):
        """Start the KeyBladeAI engine"""
        self.is_running = True
        logger.info("🗝️ KeyBladeAI Engine ACTIVATED - Local Sovereignty Mode")
        await asyncio.gather(
            self.monitor_active_flips(),
            self.update_market_data(),
            self.vault_protection_routine()
        )

    async def execute_flip(self, config: FlipConfig) -> str:
        """Execute a Commander-Class flip with full local control"""
        is_valid, message = self.risk_manager.validate_flip(config)
        if not is_valid:
            logger.error(f"Flip validation failed: {message}")
            return None

        flip_id = f"KB_{config.asset}_{int(time.time())}"
        market_data = await self.api_manager.get_market_data(config.asset)
        if not market_data:
            return None

        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute('''
                INSERT INTO flips (
                    flip_id, asset, platform, entry_price, target_price,
                    stop_loss, position_size, status, ray_rules_clarity, ai_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flip_id, config.asset, config.platform.value, config.entry_price,
                config.target_price, config.stop_loss, config.position_size,
                FlipStatus.ACTIVE.value, config.ray_rules_clarity, config.ai_confidence
            ))

        self.active_flips[flip_id] = config
        if config.ladder:
            for price, size in config.ladder:
                logger.info(f"🔖 Ladder Tier | Schedule sell {size} @ {price}")

        logger.info(f"🎯 Flip {flip_id} executed: {config.asset} @ ${config.entry_price}")
        return flip_id

    async def monitor_active_flips(self):
        """Monitor all active flips for completion conditions"""
        while self.is_running:
            for flip_id, config in list(self.active_flips.items()):
                try:
                    await self.check_flip_status(flip_id, config)
                except Exception as e:
                    logger.error(f"Error monitoring flip {flip_id}: {e}")
            await asyncio.sleep(10)

    async def check_flip_status(self, flip_id: str, config: FlipConfig):
        """Check individual flip status and execute exit conditions"""
        market_data = await self.api_manager.get_market_data(config.asset)
        if not market_data:
            return
        current_price = market_data.price
        if current_price >= config.target_price:
            await self.complete_flip(flip_id, current_price, "TARGET_REACHED")
        elif current_price <= config.stop_loss:
            await self.complete_flip(flip_id, current_price, "STOP_LOSS")
        elif config.ray_rules_clarity < 0.60:
            await self.complete_flip(flip_id, current_price, "RAY_RULES_EXIT")

    async def complete_flip(self, flip_id: str, exit_price: float, reason: str):
        """Complete a flip and process vault siphoning"""
        if flip_id not in self.active_flips:
            return
        config = self.active_flips[flip_id]
        profit = (exit_price - config.entry_price) * (config.position_size / config.entry_price)
        siphon_amount = 0
        if profit > 0:
            siphon_amount = self.vault_manager.process_flip_completion(flip_id, profit)
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute('''
                UPDATE flips SET
                    status = ?, completed_at = CURRENT_TIMESTAMP,
                    profit_loss = ?, vault_siphon = ?
                WHERE flip_id = ?
            ''', (FlipStatus.COMPLETED.value, profit, siphon_amount, flip_id))
        del self.active_flips[flip_id]
        logger.info(f"✅ Flip {flip_id} completed: ${profit:.2f} profit, ${siphon_amount:.2f} siphoned")

    async def update_market_data(self):
        """Continuously update market data for all tracked assets"""
        while self.is_running:
            for config in self.active_flips.values():
                market_data = await self.api_manager.get_market_data(config.asset)
                if market_data:
                    with sqlite3.connect(self.db.db_path) as conn:
                        conn.execute('''
                            INSERT INTO market_data (
                                symbol, price, volume_24h, change_24h,
                                bid, ask, spread, source
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            market_data.symbol, market_data.price, market_data.volume_24h,
                            market_data.change_24h, market_data.bid, market_data.ask,
                            market_data.spread, "kraken"
                        ))
            await asyncio.sleep(30)

    async def vault_protection_routine(self):
        """Continuous vault protection and monitoring"""
        while self.is_running:
            vault_status = self.vault_manager.get_vault_status()
            logger.info(f"🛡️ Vault Status: ${vault_status['current_balance']:.2f} "
                       f"({vault_status['progress_percentage']:.1f}% to target)")
            await asyncio.sleep(300)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        vault_status = self.vault_manager.get_vault_status()
        return {
            'engine_status': 'ACTIVE' if self.is_running else 'INACTIVE',
            'active_flips': len(self.active_flips),
            'vault_balance': vault_status['current_balance'],
            'vault_progress': vault_status['progress_percentage'],
            'total_siphoned': vault_status['total_siphoned'],
            'sovereignty_level': 'MAXIMUM',
            'api_precision': 'SURGICAL',
            'security_grade': 'FORTRESS'
        }

if __name__ == "__main__":
    engine = KeyBladeEngine()
    print("🗝️ KeyBladeAI Engine Ready")

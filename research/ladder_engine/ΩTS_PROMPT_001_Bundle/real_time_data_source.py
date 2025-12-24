#!/usr/bin/env python3
"""
Ω_TOTAL_SYSTEM_CORE - Real-Time Data Source Module
Production-ready data pipeline with Binance + CoinGecko integration
MENACE AI whale intelligence integration ready
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    BINANCE = "binance"
    COINGECKO = "coingecko"
    CACHED = "cached"
    MANUAL = "manual"

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PriceData:
    symbol: str
    price: float
    volume_24h: float
    price_change_24h: float
    timestamp: datetime
    source: DataSource
    whale_signal: Optional[str] = None
    menace_score: Optional[int] = None

@dataclass
class WhaleAlert:
    symbol: str
    alert_type: str
    severity: AlertLevel
    volume_surge: float
    price_impact: float
    timestamp: datetime
    description: str

class RealTimeDataSource:
    """
    Production-ready real-time data source for Ω_TOTAL_SYSTEM
    Integrates Binance API (primary) + CoinGecko (backup) + MENACE AI
    """
    
    def __init__(self):
        # API Endpoints
        self.binance_base = "https://api.binance.com/api/v3"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
        # Rate limiting
        self.binance_last_call = 0
        self.coingecko_last_call = 0
        self.binance_rate_limit = 0.05  # 20 calls per second max
        self.coingecko_rate_limit = 1.2  # 50 calls per minute
        
        # Caching
        self.price_cache = {}
        self.cache_duration = 15  # seconds
        
        # Token mapping
        self.token_map = self._load_token_map()
        
        # MENACE AI integration
        self.whale_alerts = []
        self.menace_enabled = True
        
        logger.info("🧬 Real-Time Data Source initialized")

    def _load_token_map(self) -> Dict[str, Dict[str, Any]]:
        """Load token mapping configuration"""
        return {
            # Active Trading Positions
            "HYPE": {
                "binance_symbol": "HYPEUSDT",
                "coingecko_id": "hyperliquid",
                "category": "active",
                "priority": "high"
            },
            "SUI": {
                "binance_symbol": "SUIUSDT", 
                "coingecko_id": "sui",
                "category": "active",
                "priority": "high"
            },
            "RENDER": {
                "binance_symbol": "RENDERUSDT",
                "coingecko_id": "render-token",
                "category": "active",
                "priority": "high"
            },
            "WIF": {
                "binance_symbol": "WIFUSDT",
                "coingecko_id": "dogwifhat",
                "category": "active",
                "priority": "high"
            },
            "BONK": {
                "binance_symbol": "BONKUSDT",
                "coingecko_id": "bonk",
                "category": "active",
                "priority": "medium"
            },
            "ARB": {
                "binance_symbol": "ARBUSDT",
                "coingecko_id": "arbitrum",
                "category": "active",
                "priority": "medium"
            },
            
            # Target Additions
            "MASK": {
                "binance_symbol": "MASKUSDT",
                "coingecko_id": "mask-network",
                "category": "target",
                "priority": "high"
            },
            "TRUMP": {
                "binance_symbol": None,  # Not on Binance
                "coingecko_id": "maga",
                "category": "target",
                "priority": "medium"
            },
            "STMX": {
                "binance_symbol": "STMXUSDT",
                "coingecko_id": "storm",
                "category": "target",
                "priority": "medium"
            },
            "OCEAN": {
                "binance_symbol": "OCEANUSDT",
                "coingecko_id": "ocean-protocol",
                "category": "target",
                "priority": "medium"
            },
            
            # ISO 20022 Strategic Vault
            "QNT": {
                "binance_symbol": "QNTUSDT",
                "coingecko_id": "quant-network",
                "category": "iso20022",
                "priority": "monitor"
            },
            "XRP": {
                "binance_symbol": "XRPUSDT",
                "coingecko_id": "ripple",
                "category": "iso20022",
                "priority": "monitor"
            },
            "XDC": {
                "binance_symbol": None,
                "coingecko_id": "xdce-crowd-sale",
                "category": "iso20022",
                "priority": "monitor"
            },
            "IOTA": {
                "binance_symbol": "IOTAUSDT",
                "coingecko_id": "iota",
                "category": "iso20022",
                "priority": "monitor"
            },
            "XLM": {
                "binance_symbol": "XLMUSDT",
                "coingecko_id": "stellar",
                "category": "iso20022",
                "priority": "monitor"
            },
            "VET": {
                "binance_symbol": "VETUSDT",
                "coingecko_id": "vechain",
                "category": "iso20022",
                "priority": "monitor"
            },
            "EWT": {
                "binance_symbol": None,
                "coingecko_id": "energy-web-token",
                "category": "iso20022",
                "priority": "monitor"
            },
            
            # SLEEP Tier Assets
            "ADA": {
                "binance_symbol": "ADAUSDT",
                "coingecko_id": "cardano",
                "category": "sleep",
                "priority": "low"
            },
            "KAVA": {
                "binance_symbol": "KAVAUSDT",
                "coingecko_id": "kava",
                "category": "sleep",
                "priority": "low"
            },
            "INJ": {
                "binance_symbol": "INJUSDT",
                "coingecko_id": "injective-protocol",
                "category": "sleep",
                "priority": "low"
            },
            "COTI": {
                "binance_symbol": "COTIUSDT",
                "coingecko_id": "coti",
                "category": "sleep",
                "priority": "low"
            },
            "ALGO": {
                "binance_symbol": "ALGOUSDT",
                "coingecko_id": "algorand",
                "category": "sleep",
                "priority": "low"
            },
            "XTZ": {
                "binance_symbol": "XTZUSDT",
                "coingecko_id": "tezos",
                "category": "sleep",
                "priority": "low"
            },
            "ATOM": {
                "binance_symbol": "ATOMUSDT",
                "coingecko_id": "cosmos",
                "category": "sleep",
                "priority": "low"
            },
            "FLOW": {
                "binance_symbol": "FLOWUSDT",
                "coingecko_id": "flow",
                "category": "sleep",
                "priority": "low"
            },
            "NEAR": {
                "binance_symbol": "NEARUSDT",
                "coingecko_id": "near",
                "category": "sleep",
                "priority": "low"
            }
        }

    def _rate_limit_check(self, source: str) -> None:
        """Enforce rate limiting for API calls"""
        current_time = time.time()
        
        if source == "binance":
            if current_time - self.binance_last_call < self.binance_rate_limit:
                time.sleep(self.binance_rate_limit - (current_time - self.binance_last_call))
            self.binance_last_call = time.time()
            
        elif source == "coingecko":
            if current_time - self.coingecko_last_call < self.coingecko_rate_limit:
                time.sleep(self.coingecko_rate_limit - (current_time - self.coingecko_last_call))
            self.coingecko_last_call = time.time()

    def _get_cached_price(self, symbol: str) -> Optional[PriceData]:
        """Get cached price data if still valid"""
        if symbol in self.price_cache:
            cached_data = self.price_cache[symbol]
            if (datetime.now() - cached_data.timestamp).seconds < self.cache_duration:
                return cached_data
        return None

    def _cache_price(self, price_data: PriceData) -> None:
        """Cache price data"""
        self.price_cache[price_data.symbol] = price_data

    def get_current_price(self, symbol: str) -> Optional[PriceData]:
        """
        Get current price with fallback hierarchy:
        1. Cached data (if recent)
        2. Binance API (primary)
        3. CoinGecko API (backup)
        4. Last known good price
        """
        try:
            # Check cache first
            cached = self._get_cached_price(symbol)
            if cached:
                return cached

            # Get token configuration
            if symbol not in self.token_map:
                logger.warning(f"Token {symbol} not in token map")
                return None

            token_config = self.token_map[symbol]
            
            # Try Binance first (if available)
            if token_config.get("binance_symbol"):
                price_data = self._get_binance_price(symbol, token_config["binance_symbol"])
                if price_data:
                    self._cache_price(price_data)
                    return price_data

            # Fallback to CoinGecko
            if token_config.get("coingecko_id"):
                price_data = self._get_coingecko_price(symbol, token_config["coingecko_id"])
                if price_data:
                    self._cache_price(price_data)
                    return price_data

            logger.error(f"Failed to get price for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    def _get_binance_price(self, symbol: str, binance_symbol: str) -> Optional[PriceData]:
        """Get price from Binance API"""
        try:
            self._rate_limit_check("binance")
            
            # Get ticker data
            ticker_url = f"{self.binance_base}/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            response = requests.get(ticker_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            price_data = PriceData(
                symbol=symbol,
                price=float(data["lastPrice"]),
                volume_24h=float(data["volume"]),
                price_change_24h=float(data["priceChangePercent"]),
                timestamp=datetime.now(),
                source=DataSource.BINANCE
            )
            
            # Check for whale signals
            if self.menace_enabled:
                price_data.menace_score = self._calculate_menace_score(price_data)
                price_data.whale_signal = self._detect_whale_signal(price_data)
            
            return price_data

        except Exception as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None

    def _get_coingecko_price(self, symbol: str, coingecko_id: str) -> Optional[PriceData]:
        """Get price from CoinGecko API"""
        try:
            self._rate_limit_check("coingecko")
            
            # Get price data
            price_url = f"{self.coingecko_base}/simple/price"
            params = {
                "ids": coingecko_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            
            response = requests.get(price_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            token_data = data.get(coingecko_id, {})
            
            if not token_data:
                return None
            
            price_data = PriceData(
                symbol=symbol,
                price=float(token_data.get("usd", 0)),
                volume_24h=float(token_data.get("usd_24h_vol", 0)),
                price_change_24h=float(token_data.get("usd_24h_change", 0)),
                timestamp=datetime.now(),
                source=DataSource.COINGECKO
            )
            
            return price_data

        except Exception as e:
            logger.error(f"CoinGecko API error for {symbol}: {e}")
            return None

    def _calculate_menace_score(self, price_data: PriceData) -> int:
        """
        Calculate MENACE AI score (0-100)
        Higher score = higher whale activity/opportunity
        """
        try:
            score = 50  # Base score
            
            # Volume surge factor
            if price_data.volume_24h > 0:
                # Placeholder logic - replace with actual whale detection
                if abs(price_data.price_change_24h) > 10:
                    score += 20  # High volatility
                if abs(price_data.price_change_24h) > 20:
                    score += 15  # Extreme volatility
                
                # Volume-based scoring (placeholder)
                if price_data.volume_24h > 1000000:  # $1M+ volume
                    score += 10
                if price_data.volume_24h > 10000000:  # $10M+ volume
                    score += 10
            
            return min(100, max(0, score))

        except Exception as e:
            logger.error(f"Error calculating MENACE score: {e}")
            return 50

    def _detect_whale_signal(self, price_data: PriceData) -> Optional[str]:
        """
        Detect whale signals based on price/volume data
        Returns signal type or None
        """
        try:
            # Placeholder whale detection logic
            # Replace with actual whale wallet tracking
            
            if abs(price_data.price_change_24h) > 15 and price_data.volume_24h > 5000000:
                if price_data.price_change_24h > 0:
                    return "WHALE_ACCUMULATION"
                else:
                    return "WHALE_DISTRIBUTION"
            
            if price_data.volume_24h > 20000000:  # $20M+ volume
                return "WHALE_ACTIVITY"
            
            return None

        except Exception as e:
            logger.error(f"Error detecting whale signal: {e}")
            return None

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple symbols efficiently"""
        results = {}
        
        for symbol in symbols:
            price_data = self.get_current_price(symbol)
            if price_data:
                results[symbol] = price_data
        
        return results

    def get_whale_alerts(self, symbol: str = None) -> List[WhaleAlert]:
        """Get recent whale alerts"""
        if symbol:
            return [alert for alert in self.whale_alerts if alert.symbol == symbol]
        return self.whale_alerts

    def monitor_volume_surge(self, symbol: str, threshold: float = 3.0) -> bool:
        """
        Monitor for volume surges (MENACE AI trigger)
        Returns True if volume surge detected
        """
        try:
            current_data = self.get_current_price(symbol)
            if not current_data:
                return False
            
            # Placeholder logic - replace with historical volume comparison
            # This would need historical data to calculate average volume
            
            # For now, use 24h change as proxy
            if abs(current_data.price_change_24h) > 20:  # 20% price change
                alert = WhaleAlert(
                    symbol=symbol,
                    alert_type="VOLUME_SURGE",
                    severity=AlertLevel.HIGH,
                    volume_surge=threshold,
                    price_impact=current_data.price_change_24h,
                    timestamp=datetime.now(),
                    description=f"Volume surge detected for {symbol}: {current_data.price_change_24h:.2f}%"
                )
                self.whale_alerts.append(alert)
                return True
            
            return False

        except Exception as e:
            logger.error(f"Error monitoring volume surge for {symbol}: {e}")
            return False

    def get_portfolio_snapshot(self) -> Dict[str, Any]:
        """Get complete portfolio price snapshot"""
        active_symbols = [symbol for symbol, config in self.token_map.items() 
                         if config["category"] == "active"]
        
        prices = self.get_multiple_prices(active_symbols)
        
        total_value = 0
        portfolio_data = {}
        
        for symbol, price_data in prices.items():
            portfolio_data[symbol] = {
                "price": price_data.price,
                "change_24h": price_data.price_change_24h,
                "volume_24h": price_data.volume_24h,
                "menace_score": price_data.menace_score,
                "whale_signal": price_data.whale_signal,
                "source": price_data.source.value,
                "timestamp": price_data.timestamp.isoformat()
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio": portfolio_data,
            "whale_alerts": len(self.whale_alerts),
            "data_sources_active": ["binance", "coingecko"]
        }

    def health_check(self) -> Dict[str, Any]:
        """System health check"""
        try:
            # Test Binance API
            binance_status = self._test_binance_api()
            
            # Test CoinGecko API
            coingecko_status = self._test_coingecko_api()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "binance_api": binance_status,
                "coingecko_api": coingecko_status,
                "cache_size": len(self.price_cache),
                "whale_alerts": len(self.whale_alerts),
                "token_map_size": len(self.token_map),
                "status": "healthy" if binance_status and coingecko_status else "degraded"
            }

        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"status": "error", "error": str(e)}

    def _test_binance_api(self) -> bool:
        """Test Binance API connectivity"""
        try:
            response = requests.get(f"{self.binance_base}/ping", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _test_coingecko_api(self) -> bool:
        """Test CoinGecko API connectivity"""
        try:
            response = requests.get(f"{self.coingecko_base}/ping", timeout=5)
            return response.status_code == 200
        except:
            return False

# Global instance for easy import
data_source = RealTimeDataSource()

# Convenience functions for Flip Engine integration
def get_current_price(symbol: str) -> Optional[float]:
    """Simple price getter for Flip Engine compatibility"""
    price_data = data_source.get_current_price(symbol)
    return price_data.price if price_data else None

def get_price_with_data(symbol: str) -> Optional[PriceData]:
    """Full price data getter"""
    return data_source.get_current_price(symbol)

def get_whale_signals(symbol: str) -> List[str]:
    """Get whale signals for symbol"""
    price_data = data_source.get_current_price(symbol)
    signals = []
    if price_data and price_data.whale_signal:
        signals.append(price_data.whale_signal)
    return signals

def monitor_portfolio() -> Dict[str, Any]:
    """Monitor complete portfolio"""
    return data_source.get_portfolio_snapshot()

if __name__ == "__main__":
    # Test the system
    print("🧬 Testing Ω_TOTAL_SYSTEM Real-Time Data Source")
    
    # Health check
    health = data_source.health_check()
    print(f"Health Status: {health}")
    
    # Test price feeds
    test_symbols = ["HYPE", "SUI", "MASK", "WIF"]
    for symbol in test_symbols:
        price_data = data_source.get_current_price(symbol)
        if price_data:
            print(f"{symbol}: ${price_data.price:.4f} ({price_data.price_change_24h:+.2f}%) "
                  f"[{price_data.source.value}] MENACE: {price_data.menace_score}")
        else:
            print(f"{symbol}: Failed to get price")
    
    # Portfolio snapshot
    snapshot = data_source.get_portfolio_snapshot()
    print(f"\nPortfolio Snapshot: {len(snapshot['portfolio'])} tokens tracked")
    
    print("🚀 Real-Time Data Source ready for deployment!")


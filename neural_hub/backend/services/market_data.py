#!/usr/bin/env python3
"""
Market Data Service - Fetches real-time market data
"""

import os
import asyncio
import aiohttp
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class MarketDataService:
    """Service for fetching market data"""

    def __init__(self):
        self.api_key = self._load_api_key()
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.cache = {}
        self.cache_ttl = 30  # seconds

    def _load_api_key(self) -> str:
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("CRYPTOCOMPARE_API_KEY="):
                    return line.split("=", 1)[1].strip()
        return os.environ.get("CRYPTOCOMPARE_API_KEY", "")

    async def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/price"
                params = {"fsym": symbol, "tsyms": "USD", "api_key": self.api_key}

                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    return data.get("USD", 0)
        except:
            return 0

    async def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get prices for multiple symbols"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/pricemulti"
                params = {
                    "fsyms": ",".join(symbols),
                    "tsyms": "USD",
                    "api_key": self.api_key
                }

                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    return {sym: data.get(sym, {}).get("USD", 0) for sym in symbols}
        except:
            return {sym: 0 for sym in symbols}

    async def get_ohlcv(self, symbol: str, limit: int = 100) -> Dict:
        """Get OHLCV data"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v2/histohour"
                params = {
                    "fsym": symbol,
                    "tsym": "USD",
                    "limit": limit,
                    "api_key": self.api_key
                }

                async with session.get(url, params=params) as resp:
                    data = await resp.json()

                    if data.get("Response") == "Success":
                        ohlcv = data["Data"]["Data"]
                        return {
                            "open": [x["open"] for x in ohlcv],
                            "high": [x["high"] for x in ohlcv],
                            "low": [x["low"] for x in ohlcv],
                            "close": [x["close"] for x in ohlcv],
                            "volume": [x["volumeto"] for x in ohlcv],
                        }
                    return {}
        except:
            return {}

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return round(ema, 6)

    async def get_market_data(self, symbol: str):
        """Get comprehensive market data for a symbol"""
        from neural_hub.backend.gemini_agent import MarketData

        # Get OHLCV data
        ohlcv = await self.get_ohlcv(symbol, limit=100)

        if not ohlcv or not ohlcv.get("close"):
            # Fallback to just price
            price = await self.get_price(symbol)
            return MarketData(
                symbol=symbol,
                price=price,
                rsi=50,
                ema_20=price,
                ema_50=price,
                volume_ratio=1.0,
                change_1h=0,
                change_24h=0,
                high_24h=price,
                low_24h=price
            )

        closes = ohlcv["close"]
        volumes = ohlcv["volume"]

        current_price = closes[-1]
        price_1h_ago = closes[-2] if len(closes) > 1 else current_price
        price_24h_ago = closes[-24] if len(closes) >= 24 else closes[0]

        change_1h = ((current_price - price_1h_ago) / price_1h_ago * 100) if price_1h_ago else 0
        change_24h = ((current_price - price_24h_ago) / price_24h_ago * 100) if price_24h_ago else 0

        avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
        volume_ratio = volumes[-1] / avg_volume if avg_volume else 1.0

        return MarketData(
            symbol=symbol,
            price=current_price,
            rsi=self._calculate_rsi(closes),
            ema_20=self._calculate_ema(closes, 20),
            ema_50=self._calculate_ema(closes, 50),
            volume_ratio=round(volume_ratio, 2),
            change_1h=round(change_1h, 2),
            change_24h=round(change_24h, 2),
            high_24h=max(ohlcv["high"][-24:]) if len(ohlcv["high"]) >= 24 else max(ohlcv["high"]),
            low_24h=min(ohlcv["low"][-24:]) if len(ohlcv["low"]) >= 24 else min(ohlcv["low"])
        )

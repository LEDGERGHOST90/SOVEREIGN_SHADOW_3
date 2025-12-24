"""
Birdeye API Client
Solana token analytics - requires API key
Free tier: 30k CUs/month, 1 RPS
"""
import time
import requests
from typing import Dict, List

from ..config import BIRDEYE_API_KEY, CHAIN


class BirdeyeClient:
    """Birdeye API client for Solana token data"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or BIRDEYE_API_KEY
        self.base_url = "https://public-api.birdeye.so"
        self.headers = {
            "X-API-KEY": self.api_key,
            "x-chain": CHAIN
        }
        self.last_request_time = 0
        self.rate_limit_delay = 1.1  # 1.1 seconds between requests

        if not self.api_key:
            print("⚠️  No BIRDEYE_API_KEY configured")

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting"""
        self._rate_limit()
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("  [Rate limited - waiting 2s]")
                time.sleep(2)
                return self._request(endpoint, params)
            else:
                return {"error": f"HTTP {response.status_code}: {response.text[:100]}"}

        except Exception as e:
            return {"error": str(e)}

    def get_price(self, token_address: str) -> Dict:
        """Get current price for a token"""
        result = self._request("/defi/price", {"address": token_address})
        if "data" in result:
            return result["data"]
        return result

    def get_multi_price(self, addresses: List[str]) -> Dict:
        """Get prices for multiple tokens"""
        result = self._request("/defi/multi_price", {
            "list_address": ",".join(addresses)
        })
        if "data" in result:
            return result["data"]
        return result

    def get_price_history(self, token_address: str, timeframe: str = "15m", limit: int = 100) -> List:
        """Get OHLCV price history"""
        result = self._request("/defi/ohlcv", {
            "address": token_address,
            "type": timeframe,
            "limit": limit
        })
        if "data" in result and "items" in result["data"]:
            return result["data"]["items"]
        return []

    def get_token_list(self, sort_by: str = "v24hUSD", limit: int = 50) -> List[Dict]:
        """Get token list sorted by criteria"""
        result = self._request("/defi/tokenlist", {
            "sort_by": sort_by,
            "sort_type": "desc",
            "limit": min(limit, 50)  # Max 50 on free tier
        })
        if "data" in result and "tokens" in result["data"]:
            return result["data"]["tokens"]
        return []

    def get_trending(self, limit: int = 20) -> List[Dict]:
        """Get trending tokens by volume"""
        return self.get_token_list("v24hUSD", limit)

    def get_token_overview(self, token_address: str) -> Dict:
        """Get full token overview"""
        result = self._request("/defi/token_overview", {"address": token_address})
        if "data" in result:
            return result["data"]
        return result

    def get_token_security(self, token_address: str) -> Dict:
        """Get token security info"""
        result = self._request("/defi/token_security", {"address": token_address})
        if "data" in result:
            return result["data"]
        return result

    def get_trades(self, token_address: str, limit: int = 50) -> List[Dict]:
        """Get recent trades for a token"""
        result = self._request("/defi/txs/token", {
            "address": token_address,
            "limit": limit
        })
        if "data" in result and "items" in result["data"]:
            return result["data"]["items"]
        return []

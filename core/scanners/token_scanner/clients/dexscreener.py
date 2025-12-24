"""
DexScreener API Client
FREE - No authentication, no rate limits
"""
import requests
from typing import Dict, List


class DexScreenerClient:
    """DexScreener API - free, no auth, no rate limits"""

    def __init__(self):
        self.base_url = "https://api.dexscreener.com"

    def _request(self, endpoint: str) -> Dict:
        """Make API request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def search_tokens(self, query: str) -> List[Dict]:
        """Search for tokens by name/symbol"""
        result = self._request(f"/latest/dex/search?q={query}")
        return result.get("pairs", [])

    def get_token(self, address: str) -> Dict:
        """Get token info by address"""
        result = self._request(f"/latest/dex/tokens/{address}")
        pairs = result.get("pairs", [])
        return pairs[0] if pairs else {}

    def get_new_pairs(self, chain: str = "solana") -> List[Dict]:
        """Get latest token profiles/new pairs"""
        result = self._request("/token-profiles/latest/v1")
        if isinstance(result, list):
            return [p for p in result if p.get("chainId") == chain][:50]
        return []

    def get_trending(self) -> List[Dict]:
        """Get boosted/trending tokens"""
        result = self._request("/token-boosts/latest/v1")
        if isinstance(result, list):
            return result[:30]
        return []

    def get_pair_info(self, chain: str, pair_address: str) -> Dict:
        """Get detailed pair info"""
        result = self._request(f"/latest/dex/pairs/{chain}/{pair_address}")
        return result.get("pair", {})

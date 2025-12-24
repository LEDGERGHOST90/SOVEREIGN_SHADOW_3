"""
Helius API Client
Solana RPC, DAS API, and transaction parsing
Free tier: 1M credits
"""
import requests
from typing import Dict, List

from ..config import HELIUS_API_KEY


class HeliusClient:
    """Helius API for Solana RPC, DAS, and deep analysis"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or HELIUS_API_KEY
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={self.api_key}"
        self.api_url = "https://api.helius.xyz/v0"

        if not self.api_key:
            print("⚠️  No HELIUS_API_KEY configured")

    def _rpc_request(self, method: str, params: List = None) -> Dict:
        """Make RPC request"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or []
            }
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("result", {})
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request"""
        try:
            url = f"{self.api_url}{endpoint}?api-key={self.api_key}"
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_token_metadata(self, mint_address: str) -> Dict:
        """Get token metadata using DAS API"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAsset",
                "params": {"id": mint_address}
            }
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("result", {})
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_token_holders(self, mint_address: str, limit: int = 20) -> List[Dict]:
        """Get top token holders"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenLargestAccounts",
                "params": [mint_address]
            }
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("result", {})
                return result.get("value", [])[:limit]
            return []
        except Exception as e:
            return []

    def get_signatures(self, address: str, limit: int = 10) -> List[Dict]:
        """Get recent transaction signatures"""
        result = self._rpc_request("getSignaturesForAddress", [address, {"limit": limit}])
        return result if isinstance(result, list) else []

    def get_balance(self, address: str) -> float:
        """Get SOL balance"""
        result = self._rpc_request("getBalance", [address])
        if isinstance(result, dict) and "value" in result:
            return result["value"] / 1e9
        return 0.0

    def parse_transaction(self, signature: str) -> Dict:
        """Parse transaction using Helius enhanced API"""
        try:
            url = f"https://api.helius.xyz/v0/transactions/?api-key={self.api_key}"
            payload = {"transactions": [signature]}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result[0] if result else {}
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_holder_concentration(self, mint_address: str) -> Dict:
        """Analyze holder concentration for rug risk"""
        holders = self.get_token_holders(mint_address, limit=20)

        if not holders:
            return {"error": "No holder data"}

        total_supply = sum(float(h.get("amount", 0)) for h in holders)

        if total_supply == 0:
            return {"error": "Zero supply"}

        # Calculate top holder percentages
        top1 = float(holders[0].get("amount", 0)) / total_supply * 100 if holders else 0
        top5 = sum(float(h.get("amount", 0)) for h in holders[:5]) / total_supply * 100
        top10 = sum(float(h.get("amount", 0)) for h in holders[:10]) / total_supply * 100
        top20 = sum(float(h.get("amount", 0)) for h in holders[:20]) / total_supply * 100

        # Risk assessment
        if top1 > 30:
            risk = "CRITICAL"
            message = "Single wallet holds >30% - likely rug"
        elif top5 > 50:
            risk = "HIGH"
            message = "Top 5 wallets hold >50% - concentrated"
        elif top10 > 70:
            risk = "MEDIUM"
            message = "Top 10 hold >70% - somewhat concentrated"
        else:
            risk = "LOW"
            message = "Well distributed"

        return {
            "top1_percent": round(top1, 2),
            "top5_percent": round(top5, 2),
            "top10_percent": round(top10, 2),
            "top20_percent": round(top20, 2),
            "risk_level": risk,
            "message": message,
            "holders_analyzed": len(holders)
        }

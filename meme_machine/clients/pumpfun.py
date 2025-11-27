"""
Pump.fun Token Scanner
Finds pump.fun tokens via DexScreener (pump.fun API restricted)
FREE - Uses DexScreener which has no rate limits
"""
from typing import Dict, List
from .dexscreener import DexScreenerClient


class PumpFunClient:
    """
    Pump.fun token scanner using DexScreener

    Note: Direct pump.fun API is restricted, so we use DexScreener
    to find tokens with 'pump' suffix in their address (pump.fun tokens)
    """

    def __init__(self):
        self.dex = DexScreenerClient()

    def get_new_coins(self, limit: int = 50) -> List[Dict]:
        """
        Get newest pump.fun token launches
        Filters DexScreener for tokens with 'pump' in address
        """
        # Get new pairs and filter for pump.fun tokens
        new_pairs = self.dex.get_new_pairs("solana")

        pumpfun_tokens = []
        for pair in new_pairs:
            address = pair.get("tokenAddress") or pair.get("address", "")
            # Pump.fun tokens end with "pump"
            if address.lower().endswith("pump"):
                pumpfun_tokens.append(self._convert_pair(pair))

        return pumpfun_tokens[:limit]

    def get_graduating(self, limit: int = 20) -> List[Dict]:
        """
        Get pump.fun tokens near graduation (~$69k MC)
        These are about to get real liquidity on Raydium
        """
        # Get trending and filter for pump.fun tokens near graduation
        trending = self.dex.get_trending()

        graduating = []
        for token in trending:
            address = token.get("tokenAddress") or token.get("address", "")
            if not address.lower().endswith("pump"):
                continue

            # Get full pair info
            pair = self.dex.get_token(address)
            if not pair:
                continue

            mc = float(pair.get("marketCap") or pair.get("fdv") or 0)
            # Graduation is around $69k
            if 50000 <= mc <= 100000:
                graduating.append(self._convert_dex_pair(pair))

        return graduating[:limit]

    def get_king_of_hill(self) -> List[Dict]:
        """
        Get hottest pump.fun tokens by volume
        """
        trending = self.dex.get_trending()

        kings = []
        for token in trending:
            address = token.get("tokenAddress") or token.get("address", "")
            if address.lower().endswith("pump"):
                pair = self.dex.get_token(address)
                if pair:
                    kings.append(self._convert_dex_pair(pair))

        # Sort by volume
        kings.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)
        return kings[:10]

    def get_coin(self, mint_address: str) -> Dict:
        """Get specific token info"""
        pair = self.dex.get_token(mint_address)
        if pair:
            return self._convert_dex_pair(pair)
        return {}

    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for pump.fun tokens by name/symbol"""
        pairs = self.dex.search_tokens(query)

        pumpfun_tokens = []
        for pair in pairs:
            if pair.get("chainId") != "solana":
                continue
            address = pair.get("baseToken", {}).get("address", "")
            if address.lower().endswith("pump"):
                pumpfun_tokens.append(self._convert_dex_pair(pair))

        return pumpfun_tokens[:limit]

    def _convert_pair(self, token: Dict) -> Dict:
        """Convert DexScreener new pair format to our format"""
        address = token.get("tokenAddress") or token.get("address", "")

        # Get full info from DexScreener
        pair = self.dex.get_token(address)
        if pair:
            return self._convert_dex_pair(pair)

        return {
            "mint": address,
            "symbol": "???",
            "name": "Unknown",
            "usd_market_cap": 0,
            "reply_count": 0,
        }

    def _convert_dex_pair(self, pair: Dict) -> Dict:
        """Convert DexScreener pair data to our format"""
        base = pair.get("baseToken", {})
        mc = float(pair.get("marketCap") or pair.get("fdv") or 0)
        vol = float(pair.get("volume", {}).get("h24", 0) or 0)
        liq = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        change = float(pair.get("priceChange", {}).get("h24", 0) or 0)

        txns = pair.get("txns", {}).get("h24", {})
        buys = int(txns.get("buys", 0) or 0)
        sells = int(txns.get("sells", 0) or 0)

        return {
            "mint": base.get("address", ""),
            "symbol": base.get("symbol", "???"),
            "name": base.get("name", "Unknown"),
            "usd_market_cap": mc,
            "volume_24h": vol,
            "liquidity": liq,
            "price_change_24h": change,
            "buys_24h": buys,
            "sells_24h": sells,
            "dex": pair.get("dexId", ""),
            "reply_count": buys + sells,  # Use txn count as proxy for activity
        }

    def get_bonding_curve_progress(self, token: Dict) -> float:
        """
        Estimate bonding curve progress (0-100%)
        Tokens graduate at ~$69k market cap
        """
        mc = token.get("usd_market_cap", 0) or 0
        progress = min(100, (mc / 69000) * 100)
        return progress

    def format_token(self, token: Dict) -> Dict:
        """Format token data for display"""
        return {
            "address": token.get("mint", ""),
            "symbol": token.get("symbol", "???"),
            "name": token.get("name", "Unknown"),
            "market_cap": token.get("usd_market_cap", 0) or 0,
            "bonding_progress": self.get_bonding_curve_progress(token),
            "reply_count": token.get("reply_count", 0),
            "volume_24h": token.get("volume_24h", 0),
            "liquidity": token.get("liquidity", 0),
        }

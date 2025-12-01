#!/usr/bin/env python3
"""
On-Chain Data Client for Synoptic Core
Provides whale movements, exchange flows, TVL, and address metrics
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class OnChainClient:
    """
    Fetches on-chain metrics from various blockchain APIs

    Data sources:
    - DeFiLlama (TVL)
    - Glassnode (on-chain metrics)
    - Etherscan/Solscan (transaction data)
    """

    def __init__(self):
        # API keys (optional - some endpoints are public)
        self.etherscan_key = os.getenv("ETHERSCAN_API_KEY", "")
        self.glassnode_key = os.getenv("GLASSNODE_API_KEY", "")

        # Contract addresses for common tokens
        self.token_contracts = {
            "ETH": "native",
            "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "AAVE": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"
        }

    def get_metrics(self, asset: str, days: int = 30) -> Dict[str, Any]:
        """
        Get on-chain metrics for an asset

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH", "SOL")
            days: Lookback period

        Returns:
            Dict with on-chain metrics
        """
        metrics = {}

        # Get TVL data from DeFiLlama (for DeFi protocols)
        tvl_data = self._get_tvl(asset)
        metrics.update(tvl_data)

        # Get whale/exchange flows (mocked for now, integrate real API later)
        flow_data = self._get_flow_metrics(asset, days)
        metrics.update(flow_data)

        # Get address metrics
        addr_data = self._get_address_metrics(asset, days)
        metrics.update(addr_data)

        return metrics

    def _get_tvl(self, asset: str) -> Dict[str, Any]:
        """Get Total Value Locked from DeFiLlama"""
        try:
            # DeFiLlama protocol endpoint
            url = f"https://api.llama.fi/protocol/{asset.lower()}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                current_tvl = data.get("tvl", [])[-1].get("totalLiquidityUSD", 0) if data.get("tvl") else 0

                # Calculate TVL change
                tvl_list = data.get("tvl", [])
                if len(tvl_list) >= 2:
                    recent_tvl = tvl_list[-1].get("totalLiquidityUSD", 0)
                    prev_tvl = tvl_list[-8].get("totalLiquidityUSD", 0) if len(tvl_list) > 7 else tvl_list[0].get("totalLiquidityUSD", 0)
                    tvl_change = ((recent_tvl - prev_tvl) / prev_tvl * 100) if prev_tvl > 0 else 0
                else:
                    tvl_change = 0

                return {
                    "tvl_usd": current_tvl,
                    "tvl_change_pct": tvl_change,
                    "tvl_source": "defillama"
                }
        except Exception as e:
            pass

        # Return mock/neutral data if API fails
        return {
            "tvl_usd": 0,
            "tvl_change_pct": 0,
            "tvl_source": "unavailable"
        }

    def _get_flow_metrics(self, asset: str, days: int) -> Dict[str, Any]:
        """
        Get exchange and whale flow metrics

        For production: Integrate Glassnode, CryptoQuant, or similar
        """
        # Mock data - replace with real API calls
        # Positive = inflow to exchanges (bearish)
        # Negative = outflow from exchanges (bullish)

        import random
        random.seed(hash(asset) % 2**32)

        # Simulate realistic flow patterns
        whale_net_flow = random.uniform(-1e7, 1e7)  # ±$10M
        exchange_net_flow = random.uniform(-5e6, 5e6)  # ±$5M

        return {
            "whale_net_flow": whale_net_flow,
            "exchange_net_flow": exchange_net_flow,
            "large_txns_24h": random.randint(50, 500),
            "flow_source": "mock"  # Change to real source name when integrated
        }

    def _get_address_metrics(self, asset: str, days: int) -> Dict[str, Any]:
        """
        Get active address and holder metrics

        For production: Use blockchain explorers or analytics APIs
        """
        import random
        random.seed(hash(asset + "addr") % 2**32)

        return {
            "active_addresses_24h": random.randint(10000, 500000),
            "active_address_growth": random.uniform(-10, 15),  # % change
            "holder_count": random.randint(100000, 10000000),
            "holder_growth_30d": random.uniform(-5, 10),
            "address_source": "mock"
        }

    def get_whale_transactions(
        self,
        asset: str,
        min_value_usd: float = 100000,
        hours: int = 24
    ) -> list:
        """
        Get recent large transactions (whale movements)

        Args:
            asset: Asset symbol
            min_value_usd: Minimum transaction value
            hours: Lookback period

        Returns:
            List of large transactions
        """
        # Mock implementation
        # For production: Use Whale Alert API, Etherscan, etc.

        import random
        random.seed(int(datetime.now().timestamp()) % 2**32)

        transactions = []
        num_txns = random.randint(5, 20)

        for i in range(num_txns):
            value = random.uniform(min_value_usd, min_value_usd * 100)
            transactions.append({
                "hash": f"0x{''.join(random.choices('abcdef0123456789', k=64))}",
                "value_usd": value,
                "from_type": random.choice(["unknown", "exchange", "whale"]),
                "to_type": random.choice(["unknown", "exchange", "whale"]),
                "timestamp": datetime.now() - timedelta(hours=random.uniform(0, hours))
            })

        return sorted(transactions, key=lambda x: x["value_usd"], reverse=True)


# Test
if __name__ == "__main__":
    client = OnChainClient()

    print("Testing On-Chain Client...")

    for asset in ["BTC", "ETH", "AAVE"]:
        print(f"\n=== {asset} ===")
        metrics = client.get_metrics(asset)
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"  {k}: {v:,.2f}")
            else:
                print(f"  {k}: {v}")

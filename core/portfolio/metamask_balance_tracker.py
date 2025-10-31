#!/usr/bin/env python3
"""
🔥 MetaMask Hot Wallet Balance Tracker
Live tracking of MetaMask Ethereum addresses using public blockchain APIs

ADDRESSES TRACKED:
- 0x097dF24DE4fA66877339e6f75e5Af6d618B6489B (Hot wallet)
- 0xC08413B63ecA84E2d9693af9414330dA88dcD81C (Also Ledger)
- 0xcd2057ebbC340A77c0B55Da60dbEa26310071bDc (Hot wallet)

Source: MetaMask state-logs export Oct 30, 2025
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime
import time


class MetaMaskBalanceTracker:
    """Track MetaMask hot wallet balances using Etherscan API"""

    # Known addresses from MetaMask export
    ADDRESSES = {
        "0x097dF24DE4fA66877339e6f75e5Af6d618B6489B": {
            "name": "MetaMask Hot #1",
            "initial_balance_eth": 0.00100343,
            "type": "hot_wallet"
        },
        "0xC08413B63ecA84E2d9693af9414330dA88dcD81C": {
            "name": "Ledger + MetaMask",
            "initial_balance_eth": 0.00553443,
            "type": "ledger_also"
        },
        "0xcd2057ebbC340A77c0B55Da60dbEa26310071bDc": {
            "name": "MetaMask Hot #2",
            "initial_balance_eth": 0.00282416,
            "type": "hot_wallet"
        }
    }

    def __init__(self, etherscan_api_key: str = None):
        """
        Initialize MetaMask tracker

        Args:
            etherscan_api_key: Optional Etherscan API key for higher rate limits
                              Can work without key but with lower rate limits
        """
        self.api_key = etherscan_api_key
        self.base_url = "https://api.etherscan.io/api"
        self.eth_price_cache = None
        self.eth_price_timestamp = 0

    def get_eth_price(self) -> float:
        """
        Get current ETH price in USD
        Uses CoinGecko API (no key required)
        Caches for 60 seconds to avoid rate limits
        """
        now = time.time()
        if self.eth_price_cache and (now - self.eth_price_timestamp) < 60:
            return self.eth_price_cache

        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "ethereum",
                "vs_currencies": "usd"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            price = response.json()["ethereum"]["usd"]
            self.eth_price_cache = price
            self.eth_price_timestamp = now
            return price
        except Exception as e:
            print(f"⚠️  Error fetching ETH price: {e}")
            return 3900.0  # Fallback price

    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """
        Get ETH balance for a single address using Etherscan API

        Returns:
            {
                "address": "0x...",
                "balance_wei": 1234567890,
                "balance_eth": 0.00123456,
                "balance_usd": 4.82,
                "timestamp": "2025-10-30T12:00:00Z"
            }
        """
        try:
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest"
            }

            if self.api_key:
                params["apikey"] = self.api_key

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data["status"] != "1":
                raise Exception(f"Etherscan API error: {data.get('message', 'Unknown')}")

            balance_wei = int(data["result"])
            balance_eth = balance_wei / 1e18
            eth_price = self.get_eth_price()
            balance_usd = balance_eth * eth_price

            return {
                "address": address,
                "balance_wei": balance_wei,
                "balance_eth": balance_eth,
                "balance_usd": balance_usd,
                "eth_price": eth_price,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        except Exception as e:
            print(f"❌ Error fetching balance for {address}: {e}")
            return {
                "address": address,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def get_all_balances(self) -> Dict[str, Any]:
        """
        Get balances for all MetaMask addresses

        Returns complete snapshot with totals and breakdown
        """
        results = {}
        total_eth = 0
        total_usd = 0

        for address, info in self.ADDRESSES.items():
            print(f"📡 Fetching balance for {info['name']}...")
            balance_data = self.get_address_balance(address)

            if "error" not in balance_data:
                balance_data["name"] = info["name"]
                balance_data["type"] = info["type"]
                balance_data["initial_balance"] = info["initial_balance_eth"]
                balance_data["change_eth"] = balance_data["balance_eth"] - info["initial_balance_eth"]

                total_eth += balance_data["balance_eth"]
                total_usd += balance_data["balance_usd"]

            results[address] = balance_data

            # Rate limiting - Etherscan free tier: 5 calls/sec
            time.sleep(0.25)

        return {
            "addresses": results,
            "totals": {
                "total_eth": total_eth,
                "total_usd": total_usd,
                "eth_price": self.get_eth_price(),
                "address_count": len(self.ADDRESSES)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def print_snapshot(self, snapshot: Dict[str, Any]):
        """Pretty print a balance snapshot"""
        print("\n" + "=" * 70)
        print(f"📸 SNAPSHOT: {snapshot['timestamp']}")
        print("=" * 70)

        totals = snapshot["totals"]
        print(f"\n💰 TOTAL: {totals['total_eth']:.8f} ETH (${totals['total_usd']:.2f})")
        print(f"📈 ETH Price: ${totals['eth_price']:,.2f}\n")

        print("📊 ADDRESS BREAKDOWN:")
        print("-" * 70)

        for address, data in snapshot["addresses"].items():
            if "error" in data:
                print(f"❌ {address[:10]}...{address[-8:]}")
                print(f"   Error: {data['error']}\n")
                continue

            name = data.get("name", "Unknown")
            balance_eth = data["balance_eth"]
            balance_usd = data["balance_usd"]
            change = data.get("change_eth", 0)

            change_indicator = "📈" if change > 0 else "📉" if change < 0 else "━"

            print(f"{change_indicator} {name}")
            print(f"   Address: {address[:10]}...{address[-8:]}")
            print(f"   Balance: {balance_eth:.8f} ETH (${balance_usd:.2f})")

            if abs(change) > 0.00000001:  # More than 1 gwei
                print(f"   Change: {change:+.8f} ETH")

            print()


def main():
    """Run MetaMask balance tracker"""
    import os

    # Try to get Etherscan API key from environment
    api_key = os.getenv("ETHERSCAN_API_KEY")

    if not api_key:
        print("⚠️  No Etherscan API key found in ETHERSCAN_API_KEY env var")
        print("⚠️  Will use free tier with lower rate limits\n")

    tracker = MetaMaskBalanceTracker(etherscan_api_key=api_key)

    # Get one-time snapshot
    print("🔥 MetaMask Hot Wallet - Balance Check\n")
    snapshot = tracker.get_all_balances()
    tracker.print_snapshot(snapshot)

    print("\n" + "=" * 70)
    print("✅ Balance check complete")
    print("=" * 70)


if __name__ == "__main__":
    main()

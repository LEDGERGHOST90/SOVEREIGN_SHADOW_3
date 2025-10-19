#!/usr/bin/env python3
"""
INSTANT MARKET SNAPSHOT - SHOW ALL DATA NOW
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import os
import sys

async def get_coinbase_prices():
    """Get real Coinbase prices"""
    pairs = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD', 'MATIC-USD', 'LINK-USD']
    url = "https://api.coinbase.com/v2/prices"
    
    async with aiohttp.ClientSession() as session:
        results = {}
        for pair in pairs:
            try:
                async with session.get(f"{url}/{pair}/spot") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results[pair] = float(data['data']['amount'])
                        print(f"✅ {pair}: ${results[pair]:,.2f}")
            except Exception as e:
                print(f"❌ {pair}: Error - {e}")
        return results

async def main():
    print("=" * 80)
    print("🎯 INSTANT MARKET SNAPSHOT")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("=" * 80)
    print("\n📊 CURRENT COINBASE PRICES:")
    print("-" * 80)
    
    prices = await get_coinbase_prices()
    
    print("\n" + "=" * 80)
    print(f"✅ Snapshot complete - {len(prices)} pairs fetched")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())



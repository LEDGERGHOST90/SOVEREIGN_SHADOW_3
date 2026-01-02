#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - PORTFOLIO REFRESH
Pull LIVE balances from all exchanges and update BRAIN.json
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add exchanges to path
sys.path.insert(0, str(Path(__file__).parent))

from exchanges.coinbase_connector import CoinbaseConnector
from exchanges.kraken_connector import KrakenConnector
from exchanges.binance_us_connector import BinanceUSConnector

# Load environment variables
env_path = Path(__file__).parent / "ECO_SYSTEM_4" / ".env"
load_dotenv(env_path)

def get_usd_value(balance: dict, symbol: str) -> float:
    """Get USD value of a balance (simplified - using rough estimates)"""
    # Price estimates (would normally call an API for this)
    prices = {
        'BTC': 100000,
        'ETH': 4000,
        'SOL': 200,
        'XRP': 2.5,
        'USDT': 1.0,
        'USD': 1.0,
        'USDC': 1.0,
    }

    total = 0
    for asset, amount in balance.items():
        price = prices.get(asset, 0)
        total += amount * price

    return total

def main():
    print("=" * 70)
    print("🔄 REFRESHING PORTFOLIO - PULLING LIVE DATA")
    print("=" * 70)

    results = {
        "exchanges": {},
        "total": 0
    }

    # ===== COINBASE =====
    print("\n🟦 Connecting to Coinbase...")
    try:
        cb = CoinbaseConnector(
            api_key=os.getenv("COINBASE_API_KEY"),
            api_secret=os.getenv("COINBASE_API_SECRET")
        )

        if cb.connect():
            balance = cb.fetch_balance()
            usd_value = get_usd_value(balance, 'coinbase')
            results["exchanges"]["coinbase"] = {
                "balance": balance,
                "usd_value": usd_value
            }
            print(f"✅ Coinbase: ${usd_value:,.2f}")
            print(f"   Assets: {balance}")
        else:
            print("❌ Coinbase connection failed")
            results["exchanges"]["coinbase"] = {"balance": {}, "usd_value": 0}
    except Exception as e:
        print(f"❌ Coinbase error: {e}")
        results["exchanges"]["coinbase"] = {"balance": {}, "usd_value": 0}

    # ===== KRAKEN =====
    print("\n🟪 Connecting to Kraken...")
    try:
        kraken = KrakenConnector(
            api_key=os.getenv("KRAKEN_API_KEY"),
            api_secret=os.getenv("KRAKEN_PRIVATE_KEY")
        )

        if kraken.connect():
            balance = kraken.fetch_balance()
            usd_value = get_usd_value(balance, 'kraken')
            results["exchanges"]["kraken"] = {
                "balance": balance,
                "usd_value": usd_value
            }
            print(f"✅ Kraken: ${usd_value:,.2f}")
            print(f"   Assets: {balance}")
        else:
            print("❌ Kraken connection failed")
            results["exchanges"]["kraken"] = {"balance": {}, "usd_value": 0}
    except Exception as e:
        print(f"❌ Kraken error: {e}")
        results["exchanges"]["kraken"] = {"balance": {}, "usd_value": 0}

    # ===== BINANCE US =====
    print("\n🟨 Connecting to Binance US...")
    try:
        binance = BinanceUSConnector(
            api_key=os.getenv("BINANCE_US_API_KEY"),
            api_secret=os.getenv("BINANCE_US_SECRET_KEY")
        )

        if binance.connect():
            balance = binance.fetch_balance()
            usd_value = get_usd_value(balance, 'binance_us')
            results["exchanges"]["binance_us"] = {
                "balance": balance,
                "usd_value": usd_value
            }
            print(f"✅ Binance US: ${usd_value:,.2f}")
            print(f"   Assets: {balance}")
        else:
            print("❌ Binance US connection failed")
            results["exchanges"]["binance_us"] = {"balance": {}, "usd_value": 0}
    except Exception as e:
        print(f"❌ Binance US error: {e}")
        results["exchanges"]["binance_us"] = {"balance": {}, "usd_value": 0}

    # ===== CALCULATE TOTALS =====
    total = sum(ex["usd_value"] for ex in results["exchanges"].values())
    results["total"] = total

    print("\n" + "=" * 70)
    print(f"💰 TOTAL EXCHANGE BALANCE: ${total:,.2f}")
    print("=" * 70)

    # ===== UPDATE BRAIN.json =====
    print("\n📝 Updating BRAIN.json...")
    brain_path = Path(__file__).parent / "BRAIN.json"

    try:
        with open(brain_path, 'r') as f:
            brain = json.load(f)

        # Update exchange balances
        brain["portfolio"]["exchanges"]["coinbase"] = round(results["exchanges"]["coinbase"]["usd_value"], 2)
        brain["portfolio"]["exchanges"]["kraken"] = round(results["exchanges"]["kraken"]["usd_value"], 2)
        brain["portfolio"]["exchanges"]["binance_us"] = round(results["exchanges"]["binance_us"]["usd_value"], 2)
        brain["portfolio"]["exchanges"]["total"] = round(total, 2)

        # Update timestamp
        from datetime import datetime
        brain["last_updated"] = datetime.now().isoformat()

        # Save
        with open(brain_path, 'w') as f:
            json.dump(brain, f, indent=2)

        print("✅ BRAIN.json updated successfully")

    except Exception as e:
        print(f"❌ Failed to update BRAIN.json: {e}")

    print("\n✅ REFRESH COMPLETE\n")

    return results

if __name__ == "__main__":
    results = main()

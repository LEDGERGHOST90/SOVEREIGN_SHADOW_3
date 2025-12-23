#!/usr/bin/env python3
"""
Portfolio Sync - Pull live balances from exchanges and update BRAIN.json
"""

import json
import os
from datetime import datetime
from pathlib import Path

BRAIN_PATH = Path("/Volumes/LegacySafe/SS_III/BRAIN.json")

def get_coinbase_balances():
    """Get Coinbase balances via API"""
    try:
        from core.integrations.coinbase_client import CoinbaseClient
        client = CoinbaseClient()
        accounts = client.get_accounts()
        balances = {}
        for acc in accounts:
            if float(acc.get('balance', {}).get('value', 0)) > 0:
                symbol = acc.get('balance', {}).get('currency', 'USD')
                balances[symbol] = float(acc['balance']['value'])
        return balances
    except Exception as e:
        print(f"Coinbase error: {e}")
        return {}

def get_kraken_balances():
    """Get Kraken balances"""
    try:
        from core.integrations.kraken_client import KrakenClient
        client = KrakenClient()
        return client.get_balances()
    except Exception as e:
        print(f"Kraken error: {e}")
        return {}

def get_binance_balances():
    """Get Binance US balances"""
    try:
        from core.integrations.binance_client import BinanceClient
        client = BinanceClient()
        return client.get_balances()
    except Exception as e:
        print(f"Binance error: {e}")
        return {}

def update_brain(portfolio_data: dict):
    """Update BRAIN.json with new portfolio data"""
    try:
        with open(BRAIN_PATH, 'r') as f:
            brain = json.load(f)

        brain['portfolio'].update(portfolio_data)
        brain['portfolio']['snapshot_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        brain['last_updated'] = datetime.now().isoformat()

        with open(BRAIN_PATH, 'w') as f:
            json.dump(brain, f, indent=2)

        print(f"✅ BRAIN.json updated at {brain['portfolio']['snapshot_time']}")
        return True
    except Exception as e:
        print(f"❌ Failed to update BRAIN.json: {e}")
        return False

def main():
    print("=" * 50)
    print("🔄 PORTFOLIO SYNC")
    print("=" * 50)

    # Get exchange balances
    coinbase = get_coinbase_balances()
    kraken = get_kraken_balances()
    binance = get_binance_balances()

    print(f"Coinbase: {coinbase}")
    print(f"Kraken: {kraken}")
    print(f"Binance: {binance}")

    # Calculate totals (simplified - would need price lookups for accurate USD)
    portfolio_data = {
        'exchanges': {
            'coinbase': coinbase,
            'kraken': kraken,
            'binance_us': binance
        }
    }

    update_brain(portfolio_data)
    print("=" * 50)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - BRAIN.json Live Data Refresher

Fetches REAL balances from all connected exchanges.
Updates BRAIN.json with live data for council briefings.

Usage:
    python3 scripts/refresh_brain.py
"""

import json
import os
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import ccxt

# Force IPv4 globally (fixes Binance US)
original_getaddrinfo = socket.getaddrinfo
def forced_ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = forced_ipv4_getaddrinfo

PROJECT_ROOT = Path(__file__).parent.parent
BRAIN_PATH = PROJECT_ROOT / "BRAIN.json"
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


def load_brain():
    with open(BRAIN_PATH) as f:
        return json.load(f)


def save_brain(brain):
    with open(BRAIN_PATH, 'w') as f:
        json.dump(brain, f, indent=2)


def fetch_prices():
    """Fetch live prices from Kraken (public API)"""
    exchange = ccxt.kraken({'enableRateLimit': True})

    prices = {}
    symbols = {
        'btc': 'BTC/USD',
        'eth': 'ETH/USD',
        'sol': 'SOL/USD',
        'xrp': 'XRP/USD',
        'doge': 'DOGE/USD',
        'pepe': 'PEPE/USD',
        'render': 'RENDER/USD',
    }

    for asset, symbol in symbols.items():
        try:
            ticker = exchange.fetch_ticker(symbol)
            prices[asset] = ticker['last']
        except:
            prices[asset] = 0

    prices['updated'] = datetime.utcnow().isoformat() + 'Z'
    return prices


def fetch_kraken():
    """Fetch Kraken balances"""
    try:
        exchange = ccxt.kraken({
            'apiKey': os.getenv('KRAKEN_API_KEY'),
            'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
            'enableRateLimit': True,
        })
        balance = exchange.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v > 0.0001}
    except Exception as e:
        print(f"  Kraken error: {e}")
        return {}


def fetch_binance_us():
    """Fetch Binance US balances"""
    try:
        exchange = ccxt.binanceus({
            'apiKey': os.getenv('BINANCE_US_API_KEY'),
            'secret': os.getenv('BINANCE_US_SECRET_KEY'),
            'enableRateLimit': True,
        })
        balance = exchange.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v > 0.0001}
    except Exception as e:
        print(f"  Binance US error: {e}")
        return {}


def fetch_coinbase():
    """Fetch Coinbase balances"""
    try:
        exchange = ccxt.coinbase({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
            'enableRateLimit': True,
        })
        balance = exchange.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v > 0.0001}
    except Exception as e:
        print(f"  Coinbase error: {e}")
        return {}


def calculate_usd_value(balances, prices):
    """Calculate total USD value of balances"""
    total = 0
    for asset, amount in balances.items():
        asset_lower = asset.lower()
        if asset_lower in ['usdc', 'usd', 'usdt', 'usdg']:
            total += amount
        elif asset_lower in prices and prices[asset_lower]:
            total += amount * prices[asset_lower]
    return round(total, 2)


def main():
    print("=" * 60)
    print("BRAIN.json LIVE REFRESH")
    print("=" * 60)

    brain = load_brain()

    # 1. Fetch live prices
    print("\n[1] Fetching live prices...")
    prices = fetch_prices()
    print(f"  BTC: ${prices.get('btc', 0):,.2f}")
    print(f"  ETH: ${prices.get('eth', 0):,.2f}")
    print(f"  SOL: ${prices.get('sol', 0):,.2f}")
    print(f"  XRP: ${prices.get('xrp', 0):,.2f}")

    # 2. Fetch exchange balances
    print("\n[2] Fetching exchange balances...")

    print("  Kraken...")
    kraken = fetch_kraken()
    kraken_usd = calculate_usd_value(kraken, prices)
    print(f"    Total: ${kraken_usd:,.2f}")

    print("  Binance US...")
    binance = fetch_binance_us()
    binance_usd = calculate_usd_value(binance, prices)
    print(f"    Total: ${binance_usd:,.2f}")

    print("  Coinbase...")
    coinbase = fetch_coinbase()
    coinbase_usd = calculate_usd_value(coinbase, prices)
    print(f"    Total: ${coinbase_usd:,.2f}")

    exchanges_total = kraken_usd + binance_usd + coinbase_usd

    # 3. Update BRAIN.json
    print("\n[3] Updating BRAIN.json...")

    # Update prices
    brain['prices'] = {
        'btc': round(prices.get('btc', 0), 2),
        'eth': round(prices.get('eth', 0), 2),
        'sol': round(prices.get('sol', 0), 2),
        'xrp': round(prices.get('xrp', 0), 2),
        'updated': prices['updated']
    }

    # Update exchange balances
    brain['portfolio']['exchanges'] = {
        'total': round(exchanges_total, 2),
        'kraken': {
            'balances': kraken,
            'total_usd': kraken_usd
        },
        'binance_us': {
            'balances': binance,
            'total_usd': binance_usd
        },
        'coinbase': {
            'balances': coinbase,
            'total_usd': coinbase_usd
        }
    }

    # Update snapshot time
    brain['portfolio']['snapshot_time'] = datetime.utcnow().isoformat() + 'Z'

    # Recalculate net worth (Ledger + Exchanges - AAVE debt)
    ledger_total = brain['portfolio'].get('ledger', {}).get('total', 0)
    aave_debt = abs(brain['portfolio'].get('aave', {}).get('debt', 0))
    net_worth = ledger_total + exchanges_total - aave_debt
    brain['portfolio']['net_worth'] = round(net_worth, 2)

    # Update API status
    brain['config']['apis']['kraken'] = 'ACTIVE'
    brain['config']['apis']['binance_us'] = 'ACTIVE (IPv4)'
    brain['config']['apis']['coinbase'] = 'ACTIVE'

    save_brain(brain)

    # Summary
    print("\n" + "=" * 60)
    print("REFRESH COMPLETE")
    print("=" * 60)
    print(f"\nExchanges Total: ${exchanges_total:,.2f}")
    print(f"  Kraken:     ${kraken_usd:,.2f}")
    print(f"  Binance US: ${binance_usd:,.2f}")
    print(f"  Coinbase:   ${coinbase_usd:,.2f}")
    print(f"\nLedger (unchanged): ${ledger_total:,.2f}")
    print(f"AAVE Debt: -${aave_debt:,.2f}")
    print(f"\nNET WORTH: ${net_worth:,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()

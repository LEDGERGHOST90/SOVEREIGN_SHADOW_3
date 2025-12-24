#!/usr/bin/env python3
"""
Fetch REAL live prices using YOUR UniversalExchangeManager
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.modules.execution.universal_exchange_manager import UniversalExchangeManager

def main():
    print("🔄 Connecting to YOUR exchanges...\n")

    # Initialize YOUR universal exchange manager
    manager = UniversalExchangeManager()

    # Connect to all YOUR configured exchanges
    exchange_results = manager.connect_to_all_exchanges()

    print("\n📊 Connected exchanges:")
    for exchange_name, exchange_obj in exchange_results.items():
        if exchange_obj:
            print(f"   ✅ {exchange_name.upper()}")
        else:
            print(f"   ❌ {exchange_name.upper()} (failed)")

    # Get first working exchange
    working_exchange = None
    exchange_name_used = None
    for name, exch in exchange_results.items():
        if exch:
            working_exchange = exch
            exchange_name_used = name
            break

    if not working_exchange:
        print("\n❌ No exchanges connected! Check your .env credentials")
        return {}

    print(f"\n🔍 Fetching prices from {exchange_name_used.upper()}...\n")

    # Pairs to fetch
    pairs_to_fetch = [
        'SUI/USDT', 'RENDER/USDT', 'AVAX/USDT', 'OP/USDT', 'ARB/USDT',
        'WIF/USDT', 'BRETT/USDT', 'DOGE/USDT', 'PEPE/USDT', 'FLOKI/USDT',
        'BONK/USDT', 'SHIB/USDT', 'POPCAT/USDT', 'XLM/USDT', 'HBAR/USDT',
        'ICP/USDT', 'LTC/USDT', 'BCH/USDT', 'FET/USDT', 'OCEAN/USDT'
    ]

    print("="*80)
    print("💰 REAL MARKET PRICES (LIVE FROM YOUR EXCHANGE)")
    print("="*80)

    real_prices = {}
    for pair in pairs_to_fetch:
        try:
            ticker = working_exchange.fetch_ticker(pair)
            if ticker and 'last' in ticker:
                price = ticker['last']
                real_prices[pair.replace('/', '-')] = price
                print(f"{pair:15} ${price:>15,.8f}")
            else:
                print(f"{pair:15} {'❌ No data':>15}")
        except Exception as e:
            print(f"{pair:15} {'❌ Error':>15} ({str(e)[:20]})")

    print("="*80)
    print(f"\n✅ Fetched {len(real_prices)} real prices from {exchange_name_used.upper()}")
    print(f"📡 Source: Live {exchange_name_used} API")

    return real_prices

if __name__ == '__main__':
    prices = main()

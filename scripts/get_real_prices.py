#!/usr/bin/env python3
"""
Get REAL market prices using YOUR exchange injection system
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.tracking.exchange_injection_protocol import InjectionManager

def main():
    # Initialize YOUR injection manager
    manager = InjectionManager()

    # Inject prices from all YOUR exchanges
    print('🔄 Fetching REAL prices from your exchanges...\n')
    manager.inject_all_exchanges()

    # Get real prices for top plays
    pairs = [
        'SUI-USD', 'RENDER-USD', 'AVAX-USD', 'OP-USD', 'ARB-USD',
        'WIF-USD', 'BRETT-USD', 'DOGE-USD', 'PEPE-USD', 'FLOKI-USD',
        'BONK-USD', 'SHIB-USD', 'POPCAT-USD', 'MEW-USD', 'BOME-USD',
        'XLM-USD', 'HBAR-USD', 'ICP-USD', 'LTC-USD', 'BCH-USD'
    ]

    print('📊 REAL MARKET PRICES FROM YOUR EXCHANGES:\n')
    print('='*70)

    available_prices = {}
    for pair in pairs:
        price = manager.get_price(pair)
        if price:
            print(f'{pair:15} ${price:>12.8f}')
            available_prices[pair] = price
        else:
            print(f'{pair:15} {"❌ Not available":>12}')

    print('='*70)
    print(f'\n✅ Found {len(available_prices)}/{len(pairs)} real prices')

    # Show which exchanges were used
    print('\n🔗 Exchange sources:')
    print(f'   Coinbase, Kraken, OKX, Binance, Gate.io')
    print(f'   (120min cache, real-time market data)')

    return available_prices

if __name__ == '__main__':
    prices = main()

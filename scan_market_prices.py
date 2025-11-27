#!/usr/bin/env python3
"""Live market scanner for opportunities"""

import ccxt
import os
from datetime import datetime

print('🔍 LIVE MARKET SCAN')
print(f'Time: {datetime.now().strftime("%H:%M:%S PST")}')
print('=' * 80)

# Initialize Coinbase
try:
    cb = ccxt.coinbase({
        'apiKey': os.getenv('COINBASE_API_KEY'),
        'secret': os.getenv('COINBASE_API_SECRET'),
    })

    # Top assets to scan
    assets = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD',
        'LINK/USD', 'AVAX/USD', 'MATIC/USD', 'DOT/USD',
        'ADA/USD', 'ATOM/USD', 'UNI/USD', 'LTC/USD'
    ]

    opportunities = []

    print('\n📊 PRICE & MOMENTUM')
    print('-' * 80)
    print(f'{"Asset":<12} {"Price":>12} {"24h Change":>12} {"Volume":>15} {"Signal":>15}')
    print('-' * 80)

    for symbol in assets:
        try:
            ticker = cb.fetch_ticker(symbol)
            price = ticker['last']
            change_24h = ticker['percentage'] if ticker['percentage'] else 0
            volume_24h = ticker['quoteVolume'] if ticker['quoteVolume'] else 0

            # Determine signal
            if change_24h > 5:
                signal = '🚀 STRONG UP'
                if volume_24h > 1e9:  # Over $1B volume
                    opportunities.append((symbol, price, change_24h, 'Strong momentum with high volume'))
            elif change_24h > 3:
                signal = '📈 UP'
            elif change_24h < -5:
                signal = '💥 OVERSOLD'
                if volume_24h > 5e8:  # Over $500M volume
                    opportunities.append((symbol, price, change_24h, 'Potential bounce from oversold'))
            elif change_24h < -3:
                signal = '📉 DOWN'
            else:
                signal = '➡️ FLAT'

            vol_str = f'${volume_24h/1e6:.0f}M'
            print(f'{symbol:<12} ${price:>11,.2f} {change_24h:>11.2f}% {vol_str:>15} {signal:>15}')

        except Exception as e:
            continue

    print('\n' + '=' * 80)
    print('💡 POTENTIAL OPPORTUNITIES')
    print('=' * 80)

    if opportunities:
        for i, (symbol, price, change, reason) in enumerate(opportunities, 1):
            print(f'\n{i}. {symbol.split("/")[0]}')
            print(f'   Price: ${price:,.2f}')
            print(f'   24h: {change:+.2f}%')
            print(f'   Reason: {reason}')
    else:
        print('\nNo clear momentum plays right now.')
        print('Market is ranging - wait for clearer setups.')

    print('\n' + '=' * 80)
    print('⚠️  RISK MANAGEMENT RULES')
    print('=' * 80)
    print('- Max position size: 5% of portfolio ($236)')
    print('- Stop loss: 2% below entry')
    print('- Take profit: 4%+ above entry (2:1 R:R minimum)')
    print('- No revenge trading')
    print('- No FOMO on pumps already up >10%')

except Exception as e:
    print(f'Error: {e}')
    print('\nTrying Kraken...')

    try:
        kraken = ccxt.kraken({
            'apiKey': os.getenv('KRAKEN_API_KEY'),
            'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
        })

        assets = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']

        print('\n📊 KRAKEN PRICES')
        print('-' * 60)

        for symbol in assets:
            try:
                ticker = kraken.fetch_ticker(symbol)
                price = ticker['last']
                change = ticker['percentage'] if ticker['percentage'] else 0
                print(f'{symbol}: ${price:,.2f} ({change:+.2f}%)')
            except:
                continue

    except Exception as e2:
        print(f'Kraken error: {e2}')

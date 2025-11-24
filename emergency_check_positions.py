#!/usr/bin/env python3
"""Emergency position check - READ ONLY"""
import os
import ccxt
from dotenv import load_dotenv

load_dotenv('/Volumes/LegacySafe/SovereignShadow_II/.env')

# Initialize Binance US
api_key = os.getenv('BINANCE_US_API_KEY')
secret = os.getenv('BINANCE_US_SECRET_KEY')

if not api_key or not secret:
    print("❌ API keys not found")
    exit(1)

try:
    exchange = ccxt.binanceus({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True,
    })

    print("🔌 Connecting to Binance US...")
    balance = exchange.fetch_balance()

    print("\n" + "="*60)
    print("📊 CURRENT BINANCE US POSITIONS")
    print("="*60 + "\n")

    # Get all non-zero balances
    positions = []
    total_usd = 0

    for currency, amounts in balance.items():
        if currency in ['free', 'used', 'total', 'info']:
            continue

        total = amounts.get('total', 0)
        if total > 0.0001:  # Filter dust
            # Get current price in USDT
            try:
                if currency == 'USDT' or currency == 'USD':
                    price = 1.0
                    value_usd = total
                else:
                    ticker = exchange.fetch_ticker(f"{currency}/USDT")
                    price = ticker['last']
                    value_usd = total * price

                positions.append({
                    'symbol': currency,
                    'amount': total,
                    'price': price,
                    'value_usd': value_usd
                })
                total_usd += value_usd

            except Exception as e:
                print(f"⚠️ Could not get price for {currency}: {e}")

    # Sort by value
    positions.sort(key=lambda x: x['value_usd'], reverse=True)

    # Print positions
    for pos in positions:
        print(f"{'='*60}")
        print(f"Asset: {pos['symbol']}")
        print(f"Amount: {pos['amount']:.8f}")
        print(f"Price: ${pos['price']:.4f}")
        print(f"Value: ${pos['value_usd']:.2f}")
        print(f"% of Portfolio: {(pos['value_usd']/total_usd*100):.1f}%")

    print(f"\n{'='*60}")
    print(f"💰 TOTAL PORTFOLIO VALUE: ${total_usd:.2f}")
    print(f"{'='*60}\n")

    # Get BTC price for context
    btc_ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"📊 BTC Price: ${btc_ticker['last']:,.2f}")
    print(f"📊 BTC 24h Change: {btc_ticker['percentage']:.2f}%\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

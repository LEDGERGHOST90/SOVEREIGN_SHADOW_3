#!/usr/bin/env python3
"""
🔍 TEST ALL EXCHANGES - Verify API Connectivity
Tests Coinbase, OKX, and Kraken to ensure all are working correctly
"""

import os
import sys
import ccxt
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv()

def test_exchange(exchange_name, exchange_obj):
    """Test a single exchange"""
    print(f"\n{'='*70}")
    print(f"Testing {exchange_name.upper()}")
    print(f"{'='*70}")

    try:
        # Test 1: Check balance
        print(f"✓ Testing balance fetch...")
        balance = exchange_obj.fetch_balance()
        total_usd = balance.get('total', {}).get('USD', 0) or balance.get('total', {}).get('USDT', 0) or 0
        print(f"  Balance: ${total_usd:.2f} (or equivalent)")

        # Test 2: Fetch ticker
        print(f"✓ Testing market data fetch...")
        ticker = exchange_obj.fetch_ticker('BTC/USD' if exchange_name != 'okx' else 'BTC/USDT')
        print(f"  BTC Price: ${ticker['last']:,.2f}")

        print(f"\n✅ {exchange_name.upper()} - ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"\n❌ {exchange_name.upper()} - FAILED: {e}")
        return False

def main():
    """Test all exchanges"""
    print("\n" + "="*70)
    print("🏴 SOVEREIGN SHADOW - EXCHANGE CONNECTIVITY TEST")
    print("="*70)

    results = {}

    # Test Coinbase
    try:
        coinbase = ccxt.coinbaseadvanced({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
            'enableRateLimit': True
        })
        results['coinbase'] = test_exchange('coinbase', coinbase)
    except Exception as e:
        print(f"\n❌ COINBASE - Setup failed: {e}")
        results['coinbase'] = False

    # Test OKX
    try:
        okx = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_SECRET_KEY'),
            'password': os.getenv('OKX_PASSPHRASE'),
            'enableRateLimit': True
        })
        results['okx'] = test_exchange('okx', okx)
    except Exception as e:
        print(f"\n❌ OKX - Setup failed: {e}")
        results['okx'] = False

    # Test Kraken
    try:
        kraken = ccxt.kraken({
            'apiKey': os.getenv('KRAKEN_API_KEY'),
            'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
            'enableRateLimit': True
        })
        results['kraken'] = test_exchange('kraken', kraken)
    except Exception as e:
        print(f"\n❌ KRAKEN - Setup failed: {e}")
        results['kraken'] = False

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    for exchange, passed in results.items():
        status = "✅ WORKING" if passed else "❌ FAILED"
        print(f"  {exchange.upper():<15} {status}")

    all_passed = all(results.values())
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL EXCHANGES WORKING!")
    else:
        print("⚠️  SOME EXCHANGES NEED ATTENTION")
    print("="*70 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

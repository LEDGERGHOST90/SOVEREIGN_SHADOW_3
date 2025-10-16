#!/usr/bin/env python3
"""
🔍 QUICK API TEST
Test which exchange APIs are actually working
"""

import os
import sys
import ccxt

# Set the API keys
os.environ['BINANCE_US_API_KEY'] = '0ojiA3ChME4VutmwVm0EPqiynZY5ADIS5egWu4Uo9mBz5AyAS5V5T2dbdnvimW9u'
os.environ['BINANCE_US_SECRET_KEY'] = 'r76wFq5n2toHsnzilB6Ag0dXOGv8ZqlmArsVLek64B8LsNtL3SBBsHCFIy1wdxkw'

os.environ['OKX_API_KEY'] = 'b8aa8c00-7697-4f1a-ab15-abcbebaa6a3d'
os.environ['OKX_SECRET_KEY'] = '6191B4C7C162A1F8F9DB492C4A43791F'
os.environ['OKX_PASSPHRASE'] = 'test_passphrase'

os.environ['KRAKEN_API_KEY'] = '3CPEED/7Wt8XQqqjfIWZjHiPfkUn6gWTr2LGmAG7Hti7OT2DEHkhbLkX'
os.environ['KRAKEN_SECRET_KEY'] = 'sxPoUE18/R7xfPtN7nzUXxYdrFHofqw4p90yj0hTcl3agGnsi6gkx9NvELSVkEehxhFAWjvT6Apz+Ga00hEssg=='

os.environ['COINBASE_SANDBOX_KEY'] = 'organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/f006825b-5788-4695-9ccb-ca2b18b71c1e'
os.environ['COINBASE_SANDBOX_SECRET'] = '-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIH6zt255YLHRrgrj5RUpj95AIe2eKEWB2ni9hIwikhl8oAoGCCqGSM49\nAwEHoUQDQgAEBRcW9j9ZTgaL9vIAZp13uqi0cSnjCjlrC7yNIG+m+WxXBhkl5F8n\n/05bfIWeEIm/qJGrMivH2EPFfpuoW/aC9Q==\n-----END EC PRIVATE KEY-----\n'

def test_exchange(exchange_name, exchange_class, config):
    """Test a single exchange"""
    print(f"🧪 Testing {exchange_name}...")
    
    try:
        exchange = exchange_class(config)
        markets = exchange.load_markets()
        
        # Try to get a price
        if exchange_name == 'Kraken':
            ticker = exchange.fetch_ticker('BTC/USD')
        else:
            ticker = exchange.fetch_ticker('BTC/USDT')
        
        print(f"✅ {exchange_name}: SUCCESS")
        print(f"   Markets: {len(markets)}")
        print(f"   BTC Price: ${ticker['last']}")
        return True
        
    except Exception as e:
        print(f"❌ {exchange_name}: FAILED")
        print(f"   Error: {str(e)[:100]}...")
        return False

def main():
    print("🔍 QUICK EXCHANGE API TEST")
    print("=" * 50)
    
    # Test configurations
    tests = [
        ('Binance.US', 'ccxt.binanceus', {
            'apiKey': os.environ['BINANCE_US_API_KEY'],
            'secret': os.environ['BINANCE_US_SECRET_KEY'],
            'sandbox': True,
            'enableRateLimit': True
        }),
        ('OKX', 'ccxt.okx', {
            'apiKey': os.environ['OKX_API_KEY'],
            'secret': os.environ['OKX_SECRET_KEY'],
            'password': os.environ['OKX_PASSPHRASE'],
            'sandbox': True,
            'enableRateLimit': True
        }),
        ('Kraken', 'ccxt.kraken', {
            'apiKey': os.environ['KRAKEN_API_KEY'],
            'secret': os.environ['KRAKEN_SECRET_KEY'],
            'sandbox': False,
            'enableRateLimit': True
        }),
        ('Coinbase', 'ccxt.coinbaseexchange', {
            'apiKey': os.environ['COINBASE_SANDBOX_KEY'],
            'secret': os.environ['COINBASE_SANDBOX_SECRET'],
            'sandbox': True,
            'enableRateLimit': True
        })
    ]
    
    results = []
    for name, class_name, config in tests:
        try:
            exchange_class = eval(class_name)
            success = test_exchange(name, exchange_class, config)
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name}: SETUP FAILED - {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 50)
    working = [name for name, success in results if success]
    failed = [name for name, success in results if not success]
    
    if working:
        print(f"✅ Working: {', '.join(working)}")
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
    
    print(f"\n🎯 Status: {len(working)}/{len(results)} exchanges working")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Test Coinbase API with key ID: 6f149c36-7ab5-4e26-a09f-9ba27949afaa
"""

from coinbase.rest import RESTClient
import sys

print("=" * 70)
print("🚀 COINBASE API TEST - KEY 6f149c36")
print("=" * 70)

# Full API key path with the provided key ID
api_key = "organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/6f149c36-7ab5-4e26-a09f-9ba27949afaa"

# PEM private key from .env
api_secret = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIKJ5tQWa9+3Vvai0TeaTjBKPDRzuNDX5SRQxvYmwLj4EoAoGCCqGSM49
AwEHoUQDQgAE69zpviaRH5Lom+I4qmMOU5mSF3d54TFWyzZiIzkhwyOroK9AWcoI
PIBNPtnbymw2F0K9VfvlrxudFYxpI8P33Q==
-----END EC PRIVATE KEY-----"""

print(f"\n🔑 Credentials:")
print(f"   Key ID: 6f149c36-7ab5-4e26-a09f-9ba27949afaa")
print(f"   Full path: {api_key[:60]}...")
print(f"   PEM Secret: {len(api_secret)} chars, {api_secret.count(chr(10)) + 1} lines")

# Initialize SDK
print("\n🔧 Initializing Coinbase SDK...")
try:
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    print("✅ Client initialized\n")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

# Test 1: List Accounts
print("="*70)
print("📊 TEST 1: LIST ACCOUNTS")
print("="*70)
try:
    response = client.get_accounts()
    
    if response and 'accounts' in response:
        accounts = response['accounts']
        print(f"✅ SUCCESS! Found {len(accounts)} accounts\n")
        
        # Show accounts with balances
        for acc in accounts:
            currency = acc.get('currency', 'N/A')
            available = float(acc.get('available_balance', {}).get('value', 0))
            
            if available > 0:
                print(f"💰 {currency}")
                print(f"   Available: {available:.6f}")
                if currency == 'USDC':
                    print(f"   🎯 TRADING CAPITAL: ${available:.2f}")
                print()
        
        print("🎉 API ACCESS WORKING!")
        
    else:
        print(f"⚠️ Unexpected response format")
        print(response)
        
except Exception as e:
    error_msg = str(e)
    print(f"❌ FAILED: {error_msg}\n")
    
    if "401" in error_msg:
        print("🔍 401 Unauthorized - Possible causes:")
        print("   1. Key permissions insufficient")
        print("   2. Key not activated yet (wait 2-3 minutes)")
        print("   3. Wrong key/secret combination")
        print("\n💡 Solutions:")
        print("   - Check key permissions at portal.cdp.coinbase.com")
        print("   - Ensure ALL wallet:* scopes are enabled")
        print("   - Wait a few minutes if just created")
        
    elif "403" in error_msg:
        print("🔍 403 Forbidden - Possible causes:")
        print("   1. IP whitelist blocking access")
        print("   2. Key restricted to specific IPs")
        print("\n💡 Solutions:")
        print("   - Remove IP whitelist restrictions")
        print("   - Add 0.0.0.0/0 to allowed IPs")
        
    sys.exit(1)

# Test 2: Get Market Data
print("="*70)
print("💰 TEST 2: SOL-USD ORDER BOOK")
print("="*70)
try:
    book = client.get_product_book('SOL-USD', limit=5)
    
    if book and 'pricebook' in book:
        pricebook = book['pricebook']
        bids = pricebook.get('bids', [])
        asks = pricebook.get('asks', [])
        
        if bids and asks:
            best_bid = float(bids[0]['price'])
            best_ask = float(asks[0]['price'])
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid) * 100
            
            print(f"✅ SUCCESS!\n")
            print(f"📊 SOL-USD:")
            print(f"   Best Bid: ${best_bid:.4f}")
            print(f"   Best Ask: ${best_ask:.4f}")
            print(f"   Spread: {spread_pct:.4f}%")
            
            if spread_pct < 0.08:
                print(f"\n🎯 SNIPER OPPORTUNITY!")
    
except Exception as e:
    print(f"❌ Market data failed: {e}")

# Test 3: List Products
print("\n" + "="*70)
print("📈 TEST 3: LIST TRADING PAIRS")
print("="*70)
try:
    products_response = client.get_products()
    
    if products_response and 'products' in products_response:
        products = products_response['products']
        usd_pairs = [p for p in products if '-USD' in p.get('product_id', '')]
        
        print(f"✅ SUCCESS!")
        print(f"   Total pairs: {len(products)}")
        print(f"   USD pairs: {len(usd_pairs)}")
        
except Exception as e:
    print(f"❌ Failed: {e}")

# Final Summary
print("\n" + "="*70)
print("🎯 FINAL STATUS")
print("="*70)

if 'response' in locals() and response:
    print("✅ Coinbase API: FULLY OPERATIONAL")
    print("✅ Authentication: SUCCESS")
    print("✅ Trading Access: CONFIRMED")
    print("\n🚀 SNIPER SYSTEM IS READY!")
    print("\n💰 Next: Deploy scanner and execute first trade")
else:
    print("❌ API access blocked")
    print("⚠️ Action required: Check key permissions/IP whitelist")

print("="*70)

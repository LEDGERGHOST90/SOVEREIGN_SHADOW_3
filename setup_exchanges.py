#!/usr/bin/env python3
'''
SOVEREIGN SHADOW - EXCHANGE SETUP & DIAGNOSTIC
Fix API authentication and verify connections
'''

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def print_header():
    print('\n' + '='*80)
    print('🔧 SOVEREIGN SHADOW - EXCHANGE SETUP DIAGNOSTIC 🔧'.center(80))
    print('='*80 + '\n')

def check_env_file():
    print('📋 STEP 1: CHECKING .env FILE')
    print('-'*80)
    
    if not os.path.exists('.env'):
        print('❌ .env file not found!')
        print('\n✅ Creating template .env file...')
        
        with open('.env', 'w') as f:
            f.write('''# SOVEREIGN SHADOW - EXCHANGE API KEYS
# ==========================================

# COINBASE ADVANCED TRADE (CDP)
COINBASE_API_KEY=organizations/YOUR_ORG_ID/apiKeys/YOUR_KEY_ID
COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END EC PRIVATE KEY-----\n

# OKX
OKX_API_KEY=your-okx-api-key
OKX_API_SECRET=your-okx-secret-key
OKX_API_PASSPHRASE=your-okx-passphrase

# KRAKEN
KRAKEN_API_KEY=your-kraken-api-key
KRAKEN_API_SECRET=your-kraken-private-key

# TRADING CONTROLS
ALLOW_LIVE_EXCHANGE=0  # Set to 1 for live trading
MAX_POSITION_SIZE_USD=250
''')
        print('✅ Template .env created at /Volumes/LegacySafe/SovereignShadow/.env')
        print('\n⚠️  YOU MUST EDIT .env AND ADD YOUR ACTUAL API KEYS!')
        print('='*80)
        return False
    else:
        print('✅ .env file found')
        
        # Check for required keys
        required = ['COINBASE_API_KEY', 'OKX_API_KEY', 'KRAKEN_API_KEY']
        missing = []
        
        for key in required:
            value = os.getenv(key, '')
            if not value or 'YOUR_' in value or 'your-' in value:
                missing.append(key)
                print(f'❌ {key}: Not configured')
            else:
                print(f'✅ {key}: Configured')
        
        print('='*80)
        return len(missing) == 0

def test_coinbase():
    print('\n🔵 STEP 2: TESTING COINBASE CDP')
    print('-'*80)
    
    api_key = os.getenv('COINBASE_API_KEY', '')
    api_secret = os.getenv('COINBASE_API_SECRET', '')
    
    if 'YOUR_' in api_key or not api_key:
        print('❌ Coinbase API key not configured in .env')
        print('\n📋 TO FIX:')
        print('1. Go to https://portal.cdp.coinbase.com/')
        print('2. Create new API key with "Trade" permissions')
        print('3. Download the JSON file')
        print('4. Update .env with the values from JSON:')
        print('   COINBASE_API_KEY=organizations/.../apiKeys/...')
        print('   COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----\\n...\\n-----END EC PRIVATE KEY-----\\n')
        print('='*80)
        return False
    
    try:
        from coinbase.rest import RESTClient
        client = RESTClient(api_key=api_key, api_secret=api_secret, timeout=10)
        accounts = client.get_accounts()
        
        print('✅ Coinbase CDP: CONNECTED')
        print(f'📊 Found {len(accounts.get("accounts", []))} accounts')
        
        for acc in accounts.get('accounts', [])[:3]:
            print(f'   - {acc.get("name", "Unknown")}: {acc.get("currency", "N/A")}')
        
        print('='*80)
        return True
        
    except Exception as e:
        print(f'❌ Coinbase Error: {e}')
        print('\n📋 TROUBLESHOOTING:')
        print('1. Check API key format (must include "organizations/" prefix)')
        print('2. Verify private key includes full PEM format')
        print('3. Add your IP to allowlist: https://portal.cdp.coinbase.com/')
        print('4. Ensure API key has "Trade" permissions enabled')
        print('='*80)
        return False

def test_okx():
    print('\n🟠 STEP 3: TESTING OKX')
    print('-'*80)
    
    api_key = os.getenv('OKX_API_KEY', '')
    
    if 'your-' in api_key or not api_key:
        print('❌ OKX API key not configured in .env')
        print('\n📋 TO FIX:')
        print('1. Go to OKX > Account > API Management')
        print('2. Create new API with "Trade" permission')
        print('3. Save the API key, Secret key, and Passphrase')
        print('4. Update .env with these values')
        print('='*80)
        return False
    
    try:
        import ccxt
        exchange = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY'),
            'secret': os.getenv('OKX_API_SECRET'),
            'password': os.getenv('OKX_API_PASSPHRASE'),
        })
        
        balance = exchange.fetch_balance()
        print('✅ OKX: CONNECTED')
        print(f'📊 Total Balance: ${balance.get("total", {}).get("USDT", 0):.2f} USDT')
        print('='*80)
        return True
        
    except Exception as e:
        print(f'❌ OKX Error: {e}')
        print('\n📋 CHECK: API key, secret, and passphrase in .env')
        print('='*80)
        return False

def test_kraken():
    print('\n🟣 STEP 4: TESTING KRAKEN')
    print('-'*80)
    
    api_key = os.getenv('KRAKEN_API_KEY', '')
    
    if 'your-' in api_key or not api_key:
        print('❌ Kraken API key not configured in .env')
        print('\n📋 TO FIX:')
        print('1. Go to Kraken > Settings > API')
        print('2. Create new key with "Query Funds" and "Create & Modify Orders"')
        print('3. Update .env with API key and private key')
        print('='*80)
        return False
    
    try:
        import ccxt
        exchange = ccxt.kraken({
            'apiKey': os.getenv('KRAKEN_API_KEY'),
            'secret': os.getenv('KRAKEN_API_SECRET'),
        })
        
        balance = exchange.fetch_balance()
        print('✅ Kraken: CONNECTED')
        print(f'📊 Total Balance: ${balance.get("total", {}).get("USD", 0):.2f} USD')
        print('='*80)
        return True
        
    except Exception as e:
        print(f'❌ Kraken Error: {e}')
        print('\n📋 CHECK: API key and private key in .env')
        print('='*80)
        return False

def show_next_steps(results):
    print('\n🎯 NEXT STEPS')
    print('='*80)
    
    if all(results.values()):
        print('\n🎉 ALL EXCHANGES CONNECTED! YOU\'RE READY TO TRADE!')
        print('\n📋 RECOMMENDED ACTIONS:')
        print('1. Run meme scanner:     python3 meme_coin_scanner.py 100')
        print('2. Check DeFi profits:   python3 profit_extraction_protocol.py')
        print('3. Launch dashboard:     python3 live_dashboard.py')
        print('4. Start master control: python3 master_control.py')
    else:
        print('\n⚠️  SOME EXCHANGES NEED CONFIGURATION')
        print('\n📋 PRIORITY ACTIONS:')
        
        if not results.get('env'):
            print('1. ✏️  Edit .env file and add your API keys')
            print('   nano .env  # or use your preferred editor')
        
        if not results.get('coinbase'):
            print('2. 🔵 Fix Coinbase CDP authentication')
            print('   - Go to https://portal.cdp.coinbase.com/')
            print('   - Download API key JSON')
            print('   - Update .env with correct format')
        
        if not results.get('okx'):
            print('3. 🟠 Configure OKX API')
            print('   - Log into OKX')
            print('   - Create API with Trade permission')
            print('   - Add credentials to .env')
        
        if not results.get('kraken'):
            print('4. 🟣 Configure Kraken API')
            print('   - Log into Kraken')
            print('   - Create API key')
            print('   - Add credentials to .env')
        
        print('\n5. Re-run this diagnostic: python3 setup_exchanges.py')
    
    print('='*80)

def main():
    print_header()
    
    results = {}
    
    # Run all checks
    results['env'] = check_env_file()
    results['coinbase'] = test_coinbase() if results['env'] else False
    results['okx'] = test_okx() if results['env'] else False
    results['kraken'] = test_kraken() if results['env'] else False
    
    # Show summary
    show_next_steps(results)
    
    print('\n')

if __name__ == '__main__':
    main()

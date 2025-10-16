#!/usr/bin/env python3
"""
🔥 TEST COINBASE WITH OFFICIAL LIBRARY
Using coinbase-advanced-py directly - no ccxt bullshit
"""

from coinbase.rest import RESTClient
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

# Get credentials
api_key = os.getenv('COINBASE_API_KEY')
api_secret = os.getenv('COINBASE_API_SECRET')

print(f"🔑 API Key: {api_key[:30]}...")
print(f"🔐 Secret length: {len(api_secret)}")

try:
    print("\n🚀 Testing Coinbase Advanced Trade API...")
    
    # Create client
    client = RESTClient(api_key=api_key, api_secret=api_secret)
    
    # Test connection
    print("📡 Fetching accounts...")
    accounts = client.get_accounts()
    
    print("✅ SUCCESS! Connected to Coinbase!")
    print(f"📊 Found {len(accounts.accounts)} accounts")
    
    # Show balances
    total_value = 0
    for account in accounts.accounts:
        currency = account.currency
        
        # Handle balance parsing
        if hasattr(account, 'available_balance') and account.available_balance:
            if hasattr(account.available_balance, 'value'):
                balance = account.available_balance.value
            else:
                balance = account.available_balance.get('value', '0')
        else:
            balance = '0'
            
        available = float(balance) if balance else 0
        
        if available > 0:
            print(f"💰 {currency}: ${available}")
            if currency in ['USD', 'USDC']:
                total_value += available
    
    print(f"\n🎯 TOTAL TRADING CAPITAL: ${total_value}")
    
    if total_value > 0:
        print("🔥 READY TO TRADE!")
    else:
        print("⚠️  No trading capital found")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    
    # Try to get more details
    import traceback
    print("\n🔍 Full traceback:")
    traceback.print_exc()

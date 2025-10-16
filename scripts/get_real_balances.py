#!/usr/bin/env python3
"""
REAL PORTFOLIO BALANCE CHECKER
Get actual balances from your connected APIs
"""
import os
import ccxt
import json
from datetime import datetime

def get_real_balances():
    """Fetch real balances from all connected exchanges"""
    
    print("🔍 CHECKING YOUR REAL BALANCES...")
    print("=" * 50)
    
    balances = {}
    total_usd_value = 0
    
    # Coinbase Balance Check
    if os.getenv('COINBASE_SANDBOX_KEY') and os.getenv('COINBASE_SANDBOX_SECRET'):
        try:
            print("📊 Fetching Coinbase balances...")
            coinbase = ccxt.coinbaseexchange({
                'apiKey': os.getenv('COINBASE_SANDBOX_KEY'),
                'secret': os.getenv('COINBASE_SANDBOX_SECRET'),
                'password': 'Nevernest25!',
                'sandbox': True,
                'enableRateLimit': True,
            })
            
            cb_balance = coinbase.fetch_balance()
            balances['coinbase'] = cb_balance
            
            print("💰 COINBASE BALANCES:")
            for currency, amount in cb_balance['total'].items():
                if amount > 0:
                    print(f"   {currency}: {amount}")
                    
        except Exception as e:
            print(f"❌ Coinbase error: {e}")
    
    # Kraken Balance Check  
    if os.getenv('KRAKEN_API_KEY') and os.getenv('KRAKEN_SECRET_KEY'):
        try:
            print("\n📊 Fetching Kraken balances...")
            kraken = ccxt.kraken({
                'apiKey': os.getenv('KRAKEN_API_KEY'),
                'secret': os.getenv('KRAKEN_SECRET_KEY'),
                'enableRateLimit': True,
            })
            
            kr_balance = kraken.fetch_balance()
            balances['kraken'] = kr_balance
            
            print("💰 KRAKEN BALANCES:")
            for currency, amount in kr_balance['total'].items():
                if amount > 0:
                    print(f"   {currency}: {amount}")
                    
        except Exception as e:
            print(f"❌ Kraken error: {e}")
    
    # OKX Balance Check
    if os.getenv('OKX_API_KEY') and os.getenv('OKX_SECRET_KEY'):
        try:
            print("\n📊 Fetching OKX balances...")
            okx = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET_KEY'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'sandbox': True,
                'enableRateLimit': True,
            })
            
            okx_balance = okx.fetch_balance()
            balances['okx'] = okx_balance
            
            print("💰 OKX BALANCES:")
            for currency, amount in okx_balance['total'].items():
                if amount > 0:
                    print(f"   {currency}: {amount}")
                    
        except Exception as e:
            print(f"❌ OKX error: {e}")
    
    # Save to file for monitoring
    timestamp = datetime.now().isoformat()
    balance_report = {
        'timestamp': timestamp,
        'balances': balances,
        'total_exchanges': len(balances)
    }
    
    os.makedirs('logs/ai_enhanced', exist_ok=True)
    with open('logs/ai_enhanced/real_balances.json', 'w') as f:
        json.dump(balance_report, f, indent=2, default=str)
    
    print(f"\n📄 Balance report saved to: logs/ai_enhanced/real_balances.json")
    return balances

if __name__ == "__main__":
    get_real_balances()
#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - UNIVERSAL EXCHANGE CONNECTOR
Automatically connects to ANY exchange with credentials in .env
"""

import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

class UniversalExchangeManager:
    """Dynamically connect to any CCXT exchange based on .env credentials"""
    
    def __init__(self):
        self.exchanges = {}
        self.errors = {}
        
    def detect_configured_exchanges(self):
        """Scan .env for exchange credentials"""
        configured = []
        
        for exchange_id in ccxt.exchanges:
            env_prefix = exchange_id.upper()
            
            has_key = (
                os.getenv(f'{env_prefix}_API_KEY') or
                os.getenv(f'{env_prefix}_KEY')
            )
            
            if has_key:
                configured.append(exchange_id)
        
        return configured
    
    def get_credentials(self, exchange_id):
        """Extract credentials for specific exchange from .env"""
        env_prefix = exchange_id.upper()
        
        api_key = (
            os.getenv(f'{env_prefix}_API_KEY') or
            os.getenv(f'{env_prefix}_KEY')
        )
        
        secret = (
            os.getenv(f'{env_prefix}_API_SECRET') or
            os.getenv(f'{env_prefix}_SECRET')
        )
        
        password = (
            os.getenv(f'{env_prefix}_API_PASSPHRASE') or
            os.getenv(f'{env_prefix}_PASSPHRASE') or
            os.getenv(f'{env_prefix}_PASSWORD')
        )
        
        credentials = {
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        }
        
        if password:
            credentials['password'] = password
            
        return credentials
    
    def connect_exchange(self, exchange_id):
        """Connect to a specific exchange"""
        try:
            exchange_class = getattr(ccxt, exchange_id)
            credentials = self.get_credentials(exchange_id)
            exchange = exchange_class(credentials)
            balance = exchange.fetch_balance()
            
            self.exchanges[exchange_id] = {
                'client': exchange,
                'balance': balance,
                'status': 'connected'
            }
            
            return True, exchange
            
        except Exception as e:
            self.errors[exchange_id] = str(e)
            return False, str(e)
    
    def connect_all(self):
        """Connect to all configured exchanges"""
        configured = self.detect_configured_exchanges()
        
        results = {}
        for exchange_id in configured:
            success, result = self.connect_exchange(exchange_id)
            results[exchange_id] = {
                'success': success,
                'result': result
            }
        
        return results

def main():
    print('\n' + '='*70)
    print('🌐 SOVEREIGN SHADOW - UNIVERSAL EXCHANGE CONNECTOR')
    print('='*70 + '\n')
    
    manager = UniversalExchangeManager()
    
    print('🔍 Detecting configured exchanges...')
    configured = manager.detect_configured_exchanges()
    print(f'Found {len(configured)} configured exchanges: {", ".join(configured)}\n')
    
    print('🔌 Connecting to all exchanges...')
    print('-'*70)
    
    results = manager.connect_all()
    
    for exchange_id, result in results.items():
        if result['success']:
            balance_data = manager.exchanges[exchange_id]['balance']
            total = balance_data.get('total', {})
            
            main_balance = 0
            main_currency = 'USD'
            
            for curr in ['USDT', 'USD', 'USDC', 'BTC']:
                if total.get(curr, 0) > 0:
                    main_balance = total[curr]
                    main_currency = curr
                    break
            
            print(f'✅ {exchange_id.upper()}: Connected')
            print(f'   💰 Balance: {main_balance:.2f} {main_currency}')
            
            for currency, amount in total.items():
                if amount > 0 and currency != main_currency:
                    print(f'   - {currency}: {amount}')
        else:
            print(f'❌ {exchange_id.upper()}: Failed')
            print(f'   Error: {result["result"][:100]}')
        
        print()
    
    summary = {
        'total': len(manager.exchanges) + len(manager.errors),
        'connected': len(manager.exchanges),
        'failed': len(manager.errors)
    }
    
    print('='*70)
    print('📊 CONNECTION SUMMARY')
    print('-'*70)
    print(f'Total Configured: {summary["total"]}')
    print(f'✅ Connected:     {summary["connected"]}')
    print(f'❌ Failed:        {summary["failed"]}')
    print('='*70 + '\n')
    
    return manager

if __name__ == '__main__':
    manager = main()

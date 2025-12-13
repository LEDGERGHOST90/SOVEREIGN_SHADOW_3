import ccxt
import os
from datetime import datetime
from .base_connector import BaseExchangeConnector

class CoinbaseAdvancedConnector(BaseExchangeConnector):
    def __init__(self, use_sandbox=True):
        self.use_sandbox = use_sandbox
        self.exchange = self._init_exchange()
        
    def _init_exchange(self):
        api_key = os.getenv('COINBASE_API_KEY')
        api_secret = os.getenv('COINBASE_API_SECRET')
        
        # Allow running without keys for framework testing, but warn/fail if needed
        if not api_key or not api_secret:
             print("Warning: Missing Coinbase credentials. Connector initialized in limited mode.")
        
        exchange = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'fetchBalance': {'type': 'spot'},
                'defaultType': 'spot'
            }
        })
        
        if self.use_sandbox:
            try:
                exchange.set_sandbox_mode(True)
            except Exception as e:
                print(f"Warning: Sandbox mode not supported for this exchange or configuration: {e}")
        
        return exchange
    
    def test_connection(self):
        try:
            if not self.exchange.apiKey:
                return {'status': 'FAILED', 'error': 'No API Credentials'}
            balance = self.exchange.fetch_balance()
            return {'status': 'SUCCESS', 'balance': balance['total']}
        except Exception as e:
            return {'status': 'FAILED', 'error': str(e)}

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def place_order(self, symbol, side, amount, price=None, params={}):
        return self.exchange.create_order(symbol, 'limit' if price else 'market', side, amount, price, params)

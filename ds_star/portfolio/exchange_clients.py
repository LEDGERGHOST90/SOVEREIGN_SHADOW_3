"""
Authenticated Exchange Clients for Portfolio Balance Fetching
Supports: Coinbase, Kraken, OKX, Binance.US
"""

import os
import time
import hmac
import hashlib
import base64
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import urllib.parse


class CoinbaseClient:
    """Coinbase authenticated client for fetching account balances."""
    
    BASE_URL = "https://api.coinbase.com"
    
    def __init__(self):
        self.api_key = os.environ.get('COINBASE_API_KEY', '')
        self.api_secret = os.environ.get('COINBASE_API_SECRET', '')
    
    def _sign_request(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Create Coinbase API signature headers."""
        timestamp = str(int(time.time()))
        message = timestamp + method.upper() + path + body
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-VERSION': '2023-12-01',
            'Content-Type': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.api_secret)
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Fetch all account balances from Coinbase."""
        if not self.is_configured():
            return []
        
        try:
            path = '/v2/accounts'
            headers = self._sign_request('GET', path)
            response = requests.get(f"{self.BASE_URL}{path}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                holdings = []
                for account in data.get('data', []):
                    balance = float(account.get('balance', {}).get('amount', 0))
                    if balance > 0:
                        holdings.append({
                            'symbol': account.get('currency', {}).get('code', ''),
                            'amount': balance,
                            'source': 'coinbase',
                            'name': account.get('currency', {}).get('name', ''),
                            'account_id': account.get('id', '')
                        })
                return holdings
            else:
                print(f"Coinbase error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Coinbase fetch error: {e}")
        
        return []


class KrakenClient:
    """Kraken authenticated client for fetching account balances."""
    
    BASE_URL = "https://api.kraken.com"
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY', '')
        self.api_secret = os.environ.get('KRAKEN_PRIVATE_KEY', '')
    
    def _sign_request(self, path: str, data: Dict) -> Dict[str, str]:
        """Create Kraken API signature."""
        data['nonce'] = str(int(time.time() * 1000))
        post_data = urllib.parse.urlencode(data)
        
        sha256 = hashlib.sha256((data['nonce'] + post_data).encode()).digest()
        message = path.encode() + sha256
        
        signature = base64.b64encode(
            hmac.new(
                base64.b64decode(self.api_secret),
                message,
                hashlib.sha512
            ).digest()
        ).decode()
        
        return {
            'API-Key': self.api_key,
            'API-Sign': signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.api_secret)
    
    def get_balances(self) -> List[Dict[str, Any]]:
        """Fetch account balances from Kraken."""
        if not self.is_configured():
            return []
        
        try:
            path = '/0/private/Balance'
            data = {'nonce': str(int(time.time() * 1000))}
            headers = self._sign_request(path, data.copy())
            
            response = requests.post(
                f"{self.BASE_URL}{path}",
                headers=headers,
                data=urllib.parse.urlencode(data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    print(f"Kraken API error: {result['error']}")
                    return []
                
                holdings = []
                for asset, amount in result.get('result', {}).items():
                    balance = float(amount)
                    if balance > 0.0001:
                        symbol = self._normalize_symbol(asset)
                        holdings.append({
                            'symbol': symbol,
                            'amount': balance,
                            'source': 'kraken',
                            'raw_asset': asset
                        })
                return holdings
        except Exception as e:
            print(f"Kraken fetch error: {e}")
        
        return []
    
    def _normalize_symbol(self, kraken_asset: str) -> str:
        """Convert Kraken asset codes to standard symbols."""
        mappings = {
            'XXBT': 'BTC', 'XBT': 'BTC',
            'XETH': 'ETH', 'ETH': 'ETH',
            'XXRP': 'XRP', 'XRP': 'XRP',
            'ZUSD': 'USD', 'USD': 'USD',
            'XXLM': 'XLM', 'XLM': 'XLM',
            'XLTC': 'LTC', 'LTC': 'LTC',
            'XXDG': 'DOGE', 'DOGE': 'DOGE',
            'XETC': 'ETC', 'ETC': 'ETC',
            'XZEC': 'ZEC', 'ZEC': 'ZEC',
        }
        return mappings.get(kraken_asset, kraken_asset.lstrip('X').lstrip('Z'))


class OKXClient:
    """OKX authenticated client for fetching account balances."""
    
    BASE_URL = "https://www.okx.com"
    
    def __init__(self):
        self.api_key = os.environ.get('OKX_API_KEY', '')
        self.api_secret = os.environ.get('OKX_SECRET_KEY', '')
        self.passphrase = os.environ.get('OKX_PASSPHRASE', '')
    
    def _sign_request(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Create OKX API signature headers."""
        timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        message = timestamp + method.upper() + path + body
        
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode()
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.api_secret and self.passphrase)
    
    def get_balances(self) -> List[Dict[str, Any]]:
        """Fetch account balances from OKX."""
        if not self.is_configured():
            return []
        
        try:
            path = '/api/v5/account/balance'
            headers = self._sign_request('GET', path)
            
            response = requests.get(f"{self.BASE_URL}{path}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') != '0':
                    print(f"OKX API error: {result.get('msg')}")
                    return []
                
                holdings = []
                for account in result.get('data', []):
                    for detail in account.get('details', []):
                        available = float(detail.get('availBal', 0))
                        frozen = float(detail.get('frozenBal', 0))
                        total = available + frozen
                        
                        if total > 0.0001:
                            holdings.append({
                                'symbol': detail.get('ccy', ''),
                                'amount': total,
                                'available': available,
                                'frozen': frozen,
                                'source': 'okx'
                            })
                return holdings
        except Exception as e:
            print(f"OKX fetch error: {e}")
        
        return []


class BinanceUSClient:
    """Binance.US authenticated client for fetching account balances."""
    
    BASE_URL = "https://api.binance.us"
    
    def __init__(self):
        self.api_key = os.environ.get('BINANCE_US_API_KEY', '')
        self.api_secret = os.environ.get('BINANCE_US_SECRET_KEY', '')
    
    def _sign_request(self, params: Dict) -> str:
        """Create Binance.US HMAC-SHA256 signature."""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.api_secret)
    
    def get_balances(self) -> List[Dict[str, Any]]:
        """Fetch account balances from Binance.US."""
        if not self.is_configured():
            return []
        
        try:
            endpoint = '/api/v3/account'
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp, 'recvWindow': 5000}
            
            signature = self._sign_request(params)
            params['signature'] = signature
            
            headers = {'X-MBX-APIKEY': self.api_key}
            
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                holdings = []
                
                for balance in data.get('balances', []):
                    free = float(balance.get('free', 0))
                    locked = float(balance.get('locked', 0))
                    total = free + locked
                    
                    if total > 0.0001:
                        holdings.append({
                            'symbol': balance.get('asset', ''),
                            'amount': total,
                            'available': free,
                            'locked': locked,
                            'source': 'binance_us'
                        })
                return holdings
            else:
                print(f"Binance.US error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Binance.US fetch error: {e}")
        
        return []

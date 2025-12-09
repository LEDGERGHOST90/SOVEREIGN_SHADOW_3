#!/usr/bin/env python3
"""
Coinbase Advanced Trade API Integration (CORRECT VERSION)
Integrates Coinbase Advanced Trade API using proper JWT/ECDSA authentication
"""

import json
import logging
import jwt
import hashlib
import base64
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import aiohttp
import asyncio
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from interfaces import BaseExchange, Price, Balance, OrderSide, OrderType

logger = logging.getLogger(__name__)


class CoinbaseAdvancedTradeClient:
    """Coinbase Advanced Trade API client with proper JWT authentication"""
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """
        Initialize Coinbase Advanced Trade client
        
        Args:
            api_key: Coinbase Advanced Trade API key (organization/xxx/apiKeys/xxx format)
            api_secret: Coinbase Advanced Trade API secret (PEM format EC private key)
            sandbox: Use sandbox environment
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # API endpoints - Coinbase Advanced Trade API
        if sandbox:
            self.base_url = "https://api-public.sandbox.exchange.coinbase.com"
        else:
            self.base_url = "https://api.exchange.coinbase.com"
        
        self._connected = False
        self._private_key = None
        
        # Load the private key from PEM format
        self._load_private_key()
    
    def _load_private_key(self):
        """Load EC private key from PEM format"""
        try:
            # Parse the PEM format private key
            self._private_key = serialization.load_pem_private_key(
                self.api_secret.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            logger.info("✅ Private key loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load private key: {e}")
            raise
    
    def _generate_jwt_token(self, method: str, path: str, body: str = "") -> str:
        """Generate JWT token for Coinbase Advanced Trade API"""
        # Create JWT payload
        now = int(time.time())
        payload = {
            'sub': self.api_key,
            'iss': 'coinbase-cloud',
            'nbf': now,
            'exp': now + 120,  # 2 minutes expiration
            'aud': ['retail_rest_api_proxy']
        }
        
        # Create JWT header
        header = {
            'alg': 'ES256',
            'kid': self.api_key
        }
        
        # Sign the JWT with the private key
        token = jwt.encode(payload, self._private_key, algorithm='ES256', headers=header)
        return token
    
    async def _make_request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Make authenticated request to Coinbase Advanced Trade API"""
        url = self.base_url + path
        body = json.dumps(data) if data else ""
        
        # Generate JWT token
        token = self._generate_jwt_token(method, path, body)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, data=body if data else None
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_text}")
                    raise Exception(f"API request failed: {response.status}")
    
    async def test_connection(self) -> bool:
        """Test connection to Coinbase Advanced Trade API"""
        try:
            # Test with accounts endpoint
            result = await self._make_request('GET', '/accounts')
            self._connected = True
            logger.info("✅ Connected to Coinbase Advanced Trade API")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Coinbase Advanced Trade API: {e}")
            self._connected = False
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    async def get_accounts(self) -> List[Dict]:
        """Get account balances"""
        result = await self._make_request('GET', '/accounts')
        return result.get('accounts', [])
    
    async def get_products(self) -> List[Dict]:
        """Get available trading products"""
        result = await self._make_request('GET', '/products')
        return result.get('products', [])
    
    async def get_product_ticker(self, product_id: str) -> Dict:
        """Get product ticker (price)"""
        result = await self._make_request('GET', f'/products/{product_id}/ticker')
        return result


class CoinbaseAdvancedTradeExchange(BaseExchange):
    """
    Coinbase Advanced Trade exchange implementation
    Uses proper JWT/ECDSA authentication
    """
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """
        Initialize Coinbase Advanced Trade exchange
        
        Args:
            api_key: Coinbase Advanced Trade API key
            api_secret: Coinbase Advanced Trade API secret (PEM format)
            sandbox: Use sandbox environment
        """
        super().__init__('coinbase_advanced_trade', {
            'api_key': api_key,
            'secret': api_secret,
            'sandbox': sandbox,
            'enabled': True
        })
        
        self.client = CoinbaseAdvancedTradeClient(api_key, api_secret, sandbox)
    
    async def connect(self) -> bool:
        """Connect to Coinbase Advanced Trade"""
        try:
            success = await self.client.test_connection()
            if success:
                self._connected = True
                logger.info("✅ Coinbase Advanced Trade exchange connected")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to connect Coinbase Advanced Trade: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Coinbase Advanced Trade"""
        self._connected = False
        logger.info("Disconnected from Coinbase Advanced Trade")
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol to Coinbase Advanced Trade format
        Example: BTC/USDT -> BTC-USD
        """
        # Coinbase Advanced Trade uses BTC-USD format
        base, quote = symbol.split('/')
        if quote == 'USDT':
            quote = 'USD'  # Coinbase uses USD, not USDT
        return f"{base}-{quote}"
    
    async def get_price(self, symbol: str) -> Optional[Price]:
        """Get current price for symbol"""
        if not self.is_connected:
            return None
        
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            ticker = await self.client.get_product_ticker(coinbase_symbol)
            
            return Price(
                symbol=symbol,
                exchange=self.name,
                price=float(ticker['price']),
                timestamp=datetime.now(),
                volume_24h=float(ticker.get('volume', 0)),
                change_24h=0.0  # Would need additional API call
            )
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        if not self.is_connected:
            return []
        
        try:
            accounts = await self.client.get_accounts()
            balances = []
            
            for account in accounts:
                if float(account['available_balance']['value']) > 0:
                    balances.append(Balance(
                        exchange=self.name,
                        asset=account['currency'],
                        free=float(account['available_balance']['value']),
                        used=float(account['hold']['value']),
                        total=float(account['available_balance']['value']) + float(account['hold']['value']),
                        usd_value=None  # Would need price conversion
                    ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            return []
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> str:
        """Place order on Coinbase Advanced Trade"""
        if not self.is_connected:
            raise RuntimeError("Not connected to Coinbase Advanced Trade")
        
        try:
            # Order placement would require additional API implementation
            logger.warning(f"Order placement not yet implemented - {side.value} {amount} {symbol}")
            raise NotImplementedError("Order placement requires full Advanced Trade API integration")
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def get_order_book(self, symbol: str, depth: int = 10) -> Optional[Any]:
        """Get order book for symbol"""
        if not self.is_connected:
            return None
        
        try:
            # Order book would require additional API implementation
            logger.warning(f"Order book not yet implemented - {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return None


async def test_coinbase_advanced_trade_correct(api_key: str, api_secret: str, sandbox: bool = False) -> bool:
    """
    Test Coinbase Advanced Trade connection with correct authentication
    
    Args:
        api_key: Coinbase Advanced Trade API key (organization/xxx/apiKeys/xxx format)
        api_secret: Coinbase Advanced Trade API secret (PEM format)
        sandbox: Use sandbox environment
    
    Returns:
        True if connection successful
    """
    try:
        logger.info("🧪 Testing Coinbase Advanced Trade connection (CORRECT AUTH)...")
        
        exchange = CoinbaseAdvancedTradeExchange(api_key, api_secret, sandbox)
        success = await exchange.connect()
        
        if success:
            logger.info("✅ Coinbase Advanced Trade connection test PASSED")
            
            # Test getting balances
            balances = await exchange.get_balances()
            logger.info(f"📊 Found {len(balances)} account balances")
            
            # Test getting a price
            price = await exchange.get_price("BTC-USD")
            if price:
                logger.info(f"💰 BTC-USD price: ${price.price}")
            
            await exchange.disconnect()
            return True
        else:
            logger.error("❌ Coinbase Advanced Trade connection test FAILED")
            return False
    
    except Exception as e:
        logger.error(f"❌ Connection test error: {e}")
        return False


async def integrate_coinbase_advanced_trade_correct_into_empire(api_key: str, api_secret: str, sandbox: bool = False):
    """
    Integrate Coinbase Advanced Trade into your trading empire (CORRECT VERSION)
    
    Args:
        api_key: Coinbase Advanced Trade API key
        api_secret: Coinbase Advanced Trade API secret (PEM format)
        sandbox: Use sandbox environment
    """
    logger.info("🚀 Integrating Coinbase Advanced Trade (CORRECT) into Shadow.AI Empire...")
    
    # Step 1: Test connection
    test_result = await test_coinbase_advanced_trade_correct(api_key, api_secret, sandbox)
    
    if not test_result:
        logger.error("❌ Cannot integrate Coinbase Advanced Trade - connection test failed")
        return False
    
    # Step 2: Create exchange instance
    coinbase = CoinbaseAdvancedTradeExchange(api_key, api_secret, sandbox)
    await coinbase.connect()
    
    logger.info("✅ Coinbase Advanced Trade successfully integrated into empire!")
    logger.info("📊 Coinbase Advanced Trade Status:")
    logger.info(f"  - Connected: {coinbase.is_connected}")
    logger.info(f"  - Exchange: {coinbase.name}")
    logger.info(f"  - API Key: {api_key[:20]}...")
    logger.info(f"  - Sandbox: {sandbox}")
    
    return coinbase


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Your credentials (you'll need the actual API key and PEM secret)
        API_KEY = "your_organization_api_key_here"  # organizations/xxx/apiKeys/xxx format
        API_SECRET = """-----BEGIN EC PRIVATE KEY-----
your_pem_private_key_here
-----END EC PRIVATE KEY-----"""
        
        # Test the integration
        coinbase = await integrate_coinbase_advanced_trade_correct_into_empire(
            API_KEY, API_SECRET, sandbox=False
        )
        
        if coinbase:
            logger.info("\n🎉 Coinbase Advanced Trade is ready!")
            logger.info("Next steps:")
            logger.info("1. Add to your exchange service")
            logger.info("2. Configure trading pairs")
            logger.info("3. Set up automated strategies")
            
            await coinbase.disconnect()
    
    asyncio.run(main())

"""
Coinbase Advanced Trade Connector
Implements Coinbase Advanced Trade API using CCXT library
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import ccxt
from .base_connector import (
    BaseExchangeConnector,
    Balance,
    Price,
    OrderSide,
    OrderType
)

logger = logging.getLogger(__name__)


class CoinbaseAdvancedConnector(BaseExchangeConnector):
    """
    Coinbase Advanced Trade connector using CCXT
    Supports both sandbox and production environments
    """
    
    def __init__(self, use_sandbox: bool = True):
        """
        Initialize Coinbase Advanced Trade connector
        
        Args:
            use_sandbox: Use sandbox environment (default: True for safety)
        """
        config = {
            'use_sandbox': use_sandbox,
            'enabled': True
        }
        super().__init__('coinbase', config)
        self.exchange = None
    
    def _init_exchange(self) -> ccxt.coinbase:
        """
        Initialize CCXT Coinbase exchange instance
        
        Returns:
            Configured CCXT exchange instance
        """
        api_key = os.getenv('COINBASE_API_KEY')
        api_secret = os.getenv('COINBASE_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError(
                "Missing Coinbase credentials. Set COINBASE_API_KEY and COINBASE_API_SECRET environment variables."
            )
        
        exchange_config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'fetchBalance': {'type': 'spot'},
                'defaultType': 'spot'
            }
        }
        
        exchange = ccxt.coinbase(exchange_config)
        
        if self._use_sandbox:
            exchange.set_sandbox_mode(True)
            logger.info("🔒 Coinbase connector initialized in SANDBOX mode")
        else:
            logger.info("⚠️  Coinbase connector initialized in PRODUCTION mode")
        
        return exchange
    
    async def connect(self) -> bool:
        """
        Connect to Coinbase Advanced Trade
        
        Returns:
            True if connection successful
        """
        try:
            self.exchange = self._init_exchange()
            
            # Test connection by fetching balance
            await self.test_connection()
            
            if self._connected:
                logger.info(f"✅ Connected to Coinbase Advanced Trade ({'SANDBOX' if self._use_sandbox else 'PRODUCTION'})")
                return True
            else:
                logger.error("❌ Failed to connect to Coinbase Advanced Trade")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Coinbase Advanced Trade"""
        self._connected = False
        self.exchange = None
        logger.info("Disconnected from Coinbase Advanced Trade")
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Coinbase Advanced Trade
        
        Returns:
            Dictionary with 'status' and 'balance' or 'error'
        """
        try:
            if not self.exchange:
                self.exchange = self._init_exchange()
            
            # Fetch balance as connection test
            balance = self.exchange.fetch_balance()
            
            # Calculate total USD value
            total_usd = 0.0
            balances_dict = {}
            
            for asset, amounts in balance['total'].items():
                if amounts > 0:
                    # Try to get USD value
                    usd_value = None
                    if asset == 'USD':
                        usd_value = amounts
                        total_usd += amounts
                    elif asset in balance.get('info', {}).get('accounts', []):
                        # Try to get USD value from account info
                        pass
                    
                    balances_dict[asset] = Balance(
                        asset=asset,
                        free=balance['free'].get(asset, 0.0),
                        used=balance['used'].get(asset, 0.0),
                        total=amounts,
                        usd_value=usd_value
                    )
            
            self._connected = True
            
            return {
                'status': 'SUCCESS',
                'balance': balances_dict,
                'total_usd': total_usd
            }
            
        except Exception as e:
            self._connected = False
            error_msg = str(e)
            logger.error(f"❌ Connection test failed: {error_msg}")
            return {
                'status': 'FAILED',
                'error': error_msg
            }
    
    async def get_balance(self) -> Dict[str, Balance]:
        """
        Get account balances
        
        Returns:
            Dictionary mapping asset symbols to Balance objects
        """
        if not self._connected:
            await self.connect()
        
        try:
            balance = self.exchange.fetch_balance()
            balances_dict = {}
            
            for asset, total_amount in balance['total'].items():
                if total_amount > 0:
                    free = balance['free'].get(asset, 0.0)
                    used = balance['used'].get(asset, 0.0)
                    
                    # Calculate USD value if possible
                    usd_value = None
                    if asset == 'USD':
                        usd_value = total_amount
                    else:
                        # Try to get price and calculate USD value
                        try:
                            symbol = f"{asset}/USD"
                            price_data = await self.get_price(symbol)
                            if price_data:
                                usd_value = total_amount * price_data.price
                        except:
                            pass
                    
                    balances_dict[asset] = Balance(
                        asset=asset,
                        free=free,
                        used=used,
                        total=total_amount,
                        usd_value=usd_value
                    )
            
            return balances_dict
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    async def get_price(self, symbol: str) -> Optional[Price]:
        """
        Get current price for symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
        
        Returns:
            Price object or None if error
        """
        if not self._connected:
            await self.connect()
        
        try:
            # Normalize symbol for Coinbase
            coinbase_symbol = self.normalize_symbol(symbol)
            
            ticker = self.exchange.fetch_ticker(coinbase_symbol)
            
            return Price(
                symbol=symbol,
                price=float(ticker['last']),
                timestamp=datetime.fromtimestamp(ticker['timestamp'] / 1000) if ticker.get('timestamp') else datetime.now(),
                volume_24h=ticker.get('quoteVolume'),
                change_24h=ticker.get('percentage')
            )
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Optional[str]:
        """
        Place order on Coinbase Advanced Trade
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            amount: Order amount
            order_type: Order type
            price: Limit price (required for LIMIT orders)
        
        Returns:
            Order ID if successful, None otherwise
        """
        # Safety guardrails
        env = os.getenv('ENV', 'development')
        allow_live = os.getenv('ALLOW_LIVE_EXCHANGE', '0')
        
        if env != 'production' or allow_live != '1':
            logger.warning(f"🚫 Order placement blocked - ENV={env}, ALLOW_LIVE_EXCHANGE={allow_live}")
            logger.info("Order would have been placed:")
            logger.info(f"  Symbol: {symbol}, Side: {side.value}, Amount: {amount}, Type: {order_type.value}")
            return None
        
        if not self._connected:
            await self.connect()
        
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            
            # Convert OrderSide to CCXT format
            ccxt_side = side.value.lower()
            
            # Convert OrderType to CCXT format
            if order_type == OrderType.MARKET:
                ccxt_type = 'market'
            elif order_type == OrderType.LIMIT:
                ccxt_type = 'limit'
            else:
                logger.error(f"Unsupported order type: {order_type}")
                return None
            
            # Place order
            if ccxt_type == 'limit' and price:
                order = self.exchange.create_limit_order(
                    coinbase_symbol,
                    ccxt_side,
                    amount,
                    price
                )
            else:
                order = self.exchange.create_market_order(
                    coinbase_symbol,
                    ccxt_side,
                    amount
                )
            
            logger.info(f"✅ Order placed: {order['id']} - {ccxt_side} {amount} {coinbase_symbol}")
            return order['id']
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol format to Coinbase format
        
        Args:
            symbol: Standard format (e.g., 'BTC/USDT')
        
        Returns:
            Coinbase format (e.g., 'BTC-USD')
        """
        # Coinbase uses BTC-USD format (not BTC/USDT)
        if '/' in symbol:
            base, quote = symbol.split('/')
            # Coinbase uses USD, not USDT
            if quote == 'USDT':
                quote = 'USD'
            return f"{base}-{quote}"
        return symbol

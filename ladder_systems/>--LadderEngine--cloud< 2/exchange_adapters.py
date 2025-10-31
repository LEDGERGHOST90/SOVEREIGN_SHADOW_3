import asyncio
import time
import hmac
import hashlib
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import ccxt

logger = logging.getLogger(__name__)

class BaseExchangeAdapter(ABC):
    """Base class for all exchange adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.passphrase = config.get('passphrase')
        self.is_testnet = config.get('is_testnet', True)
        self.is_paper_trading = config.get('is_paper_trading', True)
        self.use_vpn = config.get('use_vpn', False)
        self.vpn_endpoint = config.get('vpn_endpoint')
        self.exchange_name = config.get('exchange_name')
        
        # Paper trading simulation
        self.paper_balance = config.get('paper_balance', 10000.0)  # USDT
        self.paper_positions = {}
        self.paper_orders = {}
        self.order_counter = 1000
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the exchange"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        pass
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _simulate_order_fill(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate order fill for paper trading"""
        if not self.is_paper_trading:
            return order
        
        # Simulate partial fill with slippage
        fill_percentage = 0.95 + (0.1 * (time.time() % 1))  # 95-100% fill
        slippage = 0.001 * (1 if order['side'] == 'buy' else -1)  # 0.1% slippage
        
        filled_quantity = order['quantity'] * fill_percentage
        filled_price = order.get('price', order.get('market_price', 0)) * (1 + slippage)
        
        order.update({
            'status': 'filled' if fill_percentage > 0.99 else 'partially_filled',
            'filled_quantity': filled_quantity,
            'filled_price': filled_price,
            'remaining_quantity': order['quantity'] - filled_quantity,
            'fees': filled_quantity * filled_price * 0.001,  # 0.1% fee
            'fill_time': datetime.utcnow().isoformat()
        })
        
        return order


class BinanceUSAdapter(BaseExchangeAdapter):
    """Binance.US exchange adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.binance.us" if not self.is_testnet else "https://testnet.binance.vision"
        self.session = requests.Session()
        self.ccxt_exchange = None
        
    async def connect(self) -> bool:
        """Connect to Binance.US"""
        try:
            if self.is_paper_trading:
                logger.info("Binance.US: Connected in paper trading mode")
                return True
            
            # Initialize CCXT exchange
            self.ccxt_exchange = ccxt.binanceus({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'sandbox': self.is_testnet,
                'enableRateLimit': True,
            })
            
            # Test connection
            await self._test_connection()
            logger.info(f"Binance.US: Connected successfully (testnet: {self.is_testnet})")
            return True
            
        except Exception as e:
            logger.error(f"Binance.US connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Binance.US"""
        if self.ccxt_exchange:
            await self.ccxt_exchange.close()
        self.session.close()
        logger.info("Binance.US: Disconnected")
    
    async def _test_connection(self):
        """Test API connection"""
        if self.is_paper_trading:
            return True
        
        endpoint = "/api/v3/account"
        timestamp = int(time.time() * 1000)
        params = f"timestamp={timestamp}"
        signature = self._generate_signature(params)
        
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        url = f"{self.base_url}{endpoint}?{params}&signature={signature}"
        response = self.session.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Connection test failed: {response.text}")
    
    def _generate_signature(self, params: str) -> str:
        """Generate HMAC SHA256 signature for Binance.US"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if self.is_paper_trading:
            return {
                'USDT': self.paper_balance,
                'BTC': 0.0,
                'ETH': 0.0
            }
        
        try:
            balance = await self.ccxt_exchange.fetch_balance()
            return {asset: info['free'] for asset, info in balance.items() if info['free'] > 0}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on Binance.US"""
        self._rate_limit()
        
        order = {
            'id': f"paper_{self.order_counter}",
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'status': 'new',
            'timestamp': datetime.utcnow().isoformat(),
            'exchange': 'binance_us'
        }
        
        self.order_counter += 1
        
        if self.is_paper_trading:
            # Simulate order placement
            if order_type == 'market':
                ticker = await self.get_ticker(symbol)
                order['market_price'] = ticker.get('price', price or 100.0)
            
            order = self._simulate_order_fill(order)
            self.paper_orders[order['id']] = order
            
            logger.info(f"Paper order placed: {order['id']} - {symbol} {side} {quantity}")
            return order
        
        try:
            # Real order placement using CCXT
            result = await self.ccxt_exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price
            )
            
            order.update({
                'id': result['id'],
                'status': result['status'],
                'filled_quantity': result.get('filled', 0),
                'remaining_quantity': result.get('remaining', quantity)
            })
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            order['status'] = 'failed'
            order['error'] = str(e)
            return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        if self.is_paper_trading:
            if order_id in self.paper_orders:
                self.paper_orders[order_id]['status'] = 'cancelled'
                return True
            return False
        
        try:
            await self.ccxt_exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        if self.is_paper_trading:
            return self.paper_orders.get(order_id, {})
        
        try:
            order = await self.ccxt_exchange.fetch_order(order_id, symbol)
            return {
                'id': order['id'],
                'status': order['status'],
                'filled_quantity': order.get('filled', 0),
                'remaining_quantity': order.get('remaining', 0),
                'price': order.get('price'),
                'average_price': order.get('average')
            }
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return {}
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        if self.is_paper_trading:
            # Simulate ticker data
            base_price = 100.0
            if 'BTC' in symbol:
                base_price = 45000.0
            elif 'ETH' in symbol:
                base_price = 3000.0
            elif 'BONK' in symbol:
                base_price = 0.00003
            
            # Add some random variation
            variation = 0.02 * (time.time() % 1 - 0.5)  # ±1% variation
            price = base_price * (1 + variation)
            
            return {
                'symbol': symbol,
                'price': price,
                'bid': price * 0.999,
                'ask': price * 1.001,
                'volume': 1000000.0
            }
        
        try:
            ticker = await self.ccxt_exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume']
            }
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            return {}


class KuCoinAdapter(BaseExchangeAdapter):
    """KuCoin exchange adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.kucoin.com" if not self.is_testnet else "https://openapi-sandbox.kucoin.com"
        self.ccxt_exchange = None
        
    async def connect(self) -> bool:
        """Connect to KuCoin"""
        try:
            if self.is_paper_trading:
                logger.info("KuCoin: Connected in paper trading mode")
                return True
            
            self.ccxt_exchange = ccxt.kucoin({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.passphrase,
                'sandbox': self.is_testnet,
                'enableRateLimit': True,
            })
            
            # Test connection
            await self.ccxt_exchange.load_markets()
            logger.info(f"KuCoin: Connected successfully (testnet: {self.is_testnet})")
            return True
            
        except Exception as e:
            logger.error(f"KuCoin connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from KuCoin"""
        if self.ccxt_exchange:
            await self.ccxt_exchange.close()
        logger.info("KuCoin: Disconnected")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if self.is_paper_trading:
            return {
                'USDT': self.paper_balance,
                'BTC': 0.0,
                'ETH': 0.0
            }
        
        try:
            balance = await self.ccxt_exchange.fetch_balance()
            return {asset: info['free'] for asset, info in balance.items() if info['free'] > 0}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on KuCoin"""
        self._rate_limit()
        
        order = {
            'id': f"paper_kc_{self.order_counter}",
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'status': 'new',
            'timestamp': datetime.utcnow().isoformat(),
            'exchange': 'kucoin'
        }
        
        self.order_counter += 1
        
        if self.is_paper_trading:
            if order_type == 'market':
                ticker = await self.get_ticker(symbol)
                order['market_price'] = ticker.get('price', price or 100.0)
            
            order = self._simulate_order_fill(order)
            self.paper_orders[order['id']] = order
            
            logger.info(f"KuCoin paper order placed: {order['id']} - {symbol} {side} {quantity}")
            return order
        
        try:
            result = await self.ccxt_exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price
            )
            
            order.update({
                'id': result['id'],
                'status': result['status'],
                'filled_quantity': result.get('filled', 0),
                'remaining_quantity': result.get('remaining', quantity)
            })
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to place KuCoin order: {e}")
            order['status'] = 'failed'
            order['error'] = str(e)
            return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        if self.is_paper_trading:
            if order_id in self.paper_orders:
                self.paper_orders[order_id]['status'] = 'cancelled'
                return True
            return False
        
        try:
            await self.ccxt_exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel KuCoin order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        if self.is_paper_trading:
            return self.paper_orders.get(order_id, {})
        
        try:
            order = await self.ccxt_exchange.fetch_order(order_id, symbol)
            return {
                'id': order['id'],
                'status': order['status'],
                'filled_quantity': order.get('filled', 0),
                'remaining_quantity': order.get('remaining', 0),
                'price': order.get('price'),
                'average_price': order.get('average')
            }
        except Exception as e:
            logger.error(f"Failed to get KuCoin order status: {e}")
            return {}
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        if self.is_paper_trading:
            # Simulate ticker data similar to Binance
            base_price = 100.0
            if 'BTC' in symbol:
                base_price = 45000.0
            elif 'ETH' in symbol:
                base_price = 3000.0
            elif 'BONK' in symbol:
                base_price = 0.00003
            
            variation = 0.02 * (time.time() % 1 - 0.5)
            price = base_price * (1 + variation)
            
            return {
                'symbol': symbol,
                'price': price,
                'bid': price * 0.999,
                'ask': price * 1.001,
                'volume': 1000000.0
            }
        
        try:
            ticker = await self.ccxt_exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume']
            }
        except Exception as e:
            logger.error(f"Failed to get KuCoin ticker for {symbol}: {e}")
            return {}


class BybitAdapter(BaseExchangeAdapter):
    """Bybit exchange adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.bybit.com" if not self.is_testnet else "https://api-testnet.bybit.com"
        self.ccxt_exchange = None
        
    async def connect(self) -> bool:
        """Connect to Bybit"""
        try:
            if self.is_paper_trading:
                logger.info("Bybit: Connected in paper trading mode")
                return True
            
            self.ccxt_exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'testnet': self.is_testnet,
                'enableRateLimit': True,
            })
            
            await self.ccxt_exchange.load_markets()
            logger.info(f"Bybit: Connected successfully (testnet: {self.is_testnet})")
            return True
            
        except Exception as e:
            logger.error(f"Bybit connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Bybit"""
        if self.ccxt_exchange:
            await self.ccxt_exchange.close()
        logger.info("Bybit: Disconnected")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if self.is_paper_trading:
            return {
                'USDT': self.paper_balance,
                'BTC': 0.0,
                'ETH': 0.0
            }
        
        try:
            balance = await self.ccxt_exchange.fetch_balance()
            return {asset: info['free'] for asset, info in balance.items() if info['free'] > 0}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on Bybit"""
        self._rate_limit()
        
        order = {
            'id': f"paper_bb_{self.order_counter}",
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'status': 'new',
            'timestamp': datetime.utcnow().isoformat(),
            'exchange': 'bybit'
        }
        
        self.order_counter += 1
        
        if self.is_paper_trading:
            if order_type == 'market':
                ticker = await self.get_ticker(symbol)
                order['market_price'] = ticker.get('price', price or 100.0)
            
            order = self._simulate_order_fill(order)
            self.paper_orders[order['id']] = order
            
            logger.info(f"Bybit paper order placed: {order['id']} - {symbol} {side} {quantity}")
            return order
        
        try:
            result = await self.ccxt_exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=quantity,
                price=price
            )
            
            order.update({
                'id': result['id'],
                'status': result['status'],
                'filled_quantity': result.get('filled', 0),
                'remaining_quantity': result.get('remaining', quantity)
            })
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to place Bybit order: {e}")
            order['status'] = 'failed'
            order['error'] = str(e)
            return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        if self.is_paper_trading:
            if order_id in self.paper_orders:
                self.paper_orders[order_id]['status'] = 'cancelled'
                return True
            return False
        
        try:
            await self.ccxt_exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel Bybit order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        if self.is_paper_trading:
            return self.paper_orders.get(order_id, {})
        
        try:
            order = await self.ccxt_exchange.fetch_order(order_id, symbol)
            return {
                'id': order['id'],
                'status': order['status'],
                'filled_quantity': order.get('filled', 0),
                'remaining_quantity': order.get('remaining', 0),
                'price': order.get('price'),
                'average_price': order.get('average')
            }
        except Exception as e:
            logger.error(f"Failed to get Bybit order status: {e}")
            return {}
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        if self.is_paper_trading:
            # Simulate ticker data
            base_price = 100.0
            if 'BTC' in symbol:
                base_price = 45000.0
            elif 'ETH' in symbol:
                base_price = 3000.0
            elif 'BONK' in symbol:
                base_price = 0.00003
            
            variation = 0.02 * (time.time() % 1 - 0.5)
            price = base_price * (1 + variation)
            
            return {
                'symbol': symbol,
                'price': price,
                'bid': price * 0.999,
                'ask': price * 1.001,
                'volume': 1000000.0
            }
        
        try:
            ticker = await self.ccxt_exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume']
            }
        except Exception as e:
            logger.error(f"Failed to get Bybit ticker for {symbol}: {e}")
            return {}


class ExchangeAdapterFactory:
    """Factory for creating exchange adapters"""
    
    @staticmethod
    def create_adapter(exchange_name: str, config: Dict[str, Any]) -> BaseExchangeAdapter:
        """Create an exchange adapter based on the exchange name"""
        adapters = {
            'binance_us': BinanceUSAdapter,
            'kucoin': KuCoinAdapter,
            'bybit': BybitAdapter
        }
        
        adapter_class = adapters.get(exchange_name.lower())
        if not adapter_class:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
        
        return adapter_class(config)
    
    @staticmethod
    def get_supported_exchanges() -> List[str]:
        """Get list of supported exchanges"""
        return ['binance_us', 'kucoin', 'bybit']


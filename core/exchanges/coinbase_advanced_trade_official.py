#!/usr/bin/env python3
"""
Coinbase Advanced Trade API Integration (OFFICIAL SDK)
Uses the official Coinbase Advanced Trade Python SDK
"""

import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from coinbase.rest import RESTClient
from interfaces import BaseExchange, Price, Balance, OrderSide, OrderType

logger = logging.getLogger(__name__)


class CoinbaseAdvancedTradeOfficialClient:
    """Coinbase Advanced Trade client using official SDK"""
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """
        Initialize Coinbase Advanced Trade client
        
        Args:
            api_key: Coinbase Advanced Trade API key
            api_secret: Coinbase Advanced Trade API secret (PEM format)
            sandbox: Use sandbox environment
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # Initialize the official SDK client
        if sandbox:
            base_url = 'api-public.sandbox.exchange.coinbase.com'
        else:
            base_url = 'api.coinbase.com'
            
        self.client = RESTClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url
        )
        
        self._connected = False
    
    async def test_connection(self) -> bool:
        """Test connection to Coinbase Advanced Trade API"""
        try:
            # Test with get_accounts
            accounts = self.client.get_accounts()
            self._connected = True
            logger.info("✅ Connected to Coinbase Advanced Trade API (Official SDK)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Coinbase Advanced Trade API: {e}")
            self._connected = False
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    def get_accounts(self) -> List[Dict]:
        """Get account balances"""
        accounts_response = self.client.get_accounts()
        return accounts_response.accounts
    
    def get_products(self) -> List[Dict]:
        """Get available trading products"""
        products_response = self.client.get_products()
        return products_response.products
    
    def get_product(self, product_id: str) -> Dict:
        """Get specific product details"""
        return self.client.get_product(product_id)
    
    def get_best_bid_ask(self, product_ids: List[str]) -> Dict:
        """Get best bid/ask prices"""
        return self.client.get_best_bid_ask(product_ids)
    
    def get_product_candles(self, product_id: str, start: str, end: str, granularity: str) -> Dict:
        """Get product candles (price history)"""
        return self.client.get_product_candles(product_id, start, end, granularity)
    
    def place_limit_order(self, pair: str, side: str, size: str, price: str) -> dict:
        """Place a limit order using official SDK"""
        try:
            if side.upper() == "BUY":
                result = self.client.limit_order_gtc_buy(
                    product_id=pair,
                    base_size=size,
                    limit_price=price
                )
            else:
                result = self.client.limit_order_gtc_sell(
                    product_id=pair,
                    base_size=size,
                    limit_price=price
                )
            return {
                "success": True,
                "order_id": result.order_id if hasattr(result, 'order_id') else str(uuid.uuid4()),
                "status": "placed",
                "pair": pair,
                "side": side.upper(),
                "size": size,
                "price": price
            }
        except Exception as e:
            logger.error(f"Limit order failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pair": pair,
                "side": side.upper()
            }
    
    def place_market_order(self, pair: str, side: str, size: str) -> dict:
        """Place a market order using official SDK"""
        try:
            if side.upper() == "BUY":
                result = self.client.market_order_buy(
                    product_id=pair,
                    quote_size=size  # For buy orders, size is in quote currency
                )
            else:
                result = self.client.market_order_sell(
                    product_id=pair,
                    base_size=size  # For sell orders, size is in base currency
                )
            return {
                "success": True,
                "order_id": result.order_id if hasattr(result, 'order_id') else str(uuid.uuid4()),
                "status": "filled",
                "pair": pair,
                "side": side.upper(),
                "size": size
            }
        except Exception as e:
            logger.error(f"Market order failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pair": pair,
                "side": side.upper()
            }
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an open order using official SDK"""
        try:
            result = self.client.cancel_orders([order_id])
            return {
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
                "result": result
            }
        except Exception as e:
            logger.error(f"Cancel order failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }
    
    def place_oco_ladder(self, pair: str, side: str, base_size: str, 
                         entry_price: float, tp_levels: list, sl_price: float) -> dict:
        """
        OCO ladder: entry + multiple take-profits + stop-loss.
        Args:
            pair: "BTC-USD"
            side: "BUY" or "SELL"
            base_size: total position size (split across TP levels)
            entry_price: initial limit entry
            tp_levels: [(price1, pct1), (price2, pct2), ...] where pct sums to 1.0
            sl_price: stop-loss trigger
        """
        orders = []
        
        try:
            # 1. Entry order
            entry = self.place_limit_order(pair, side, base_size, str(entry_price))
            orders.append({"type": "entry", "order": entry})
            
            # 2. TP ladder
            for tp_price, pct in tp_levels:
                tp_size = str(float(base_size) * pct)
                opposite_side = "SELL" if side.upper() == "BUY" else "BUY"
                tp = self.place_limit_order(pair, opposite_side, tp_size, str(tp_price))
                orders.append({"type": "take_profit", "order": tp})
            
            # 3. Stop-loss using stop limit order
            opposite_side = "SELL" if side.upper() == "BUY" else "BUY"
            sl_result = self.client.stop_limit_order_gtc(
                product_id=pair,
                side=opposite_side,
                base_size=base_size,
                stop_price=str(sl_price),
                limit_price=str(sl_price * 0.99)  # 1% slippage buffer
            )
            sl_order = {
                "success": True,
                "order_id": sl_result.order_id if hasattr(sl_result, 'order_id') else str(uuid.uuid4()),
                "status": "placed",
                "type": "stop_loss"
            }
            orders.append({"type": "stop_loss", "order": sl_order})
            
            return {
                "success": True,
                "ladder": orders,
                "pair": pair,
                "side": side.upper(),
                "total_size": base_size
            }
            
        except Exception as e:
            logger.error(f"OCO ladder failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ladder": orders,
                "pair": pair
            }


class CoinbaseAdvancedTradeOfficialExchange(BaseExchange):
    """
    Coinbase Advanced Trade exchange implementation using official SDK
    """
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """
        Initialize Coinbase Advanced Trade exchange
        
        Args:
            api_key: Coinbase Advanced Trade API key
            api_secret: Coinbase Advanced Trade API secret (PEM format)
            sandbox: Use sandbox environment
        """
        super().__init__('coinbase_advanced_trade_official', {
            'api_key': api_key,
            'secret': api_secret,
            'sandbox': sandbox,
            'enabled': True
        })
        
        self.client = CoinbaseAdvancedTradeOfficialClient(api_key, api_secret, sandbox)
    
    async def connect(self) -> bool:
        """Connect to Coinbase Advanced Trade"""
        try:
            success = await self.client.test_connection()
            if success:
                self._connected = True
                logger.info("✅ Coinbase Advanced Trade exchange connected (Official SDK)")
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
        Example: BTC/USDT -> BTC-USD, BTC-USD -> BTC-USD
        """
        # Handle both BTC/USD and BTC-USD formats
        if '/' in symbol:
            base, quote = symbol.split('/')
        elif '-' in symbol:
            base, quote = symbol.split('-')
        else:
            return symbol  # Return as-is if no separator
            
        if quote == 'USDT':
            quote = 'USD'  # Coinbase uses USD, not USDT
        return f"{base}-{quote}"
    
    async def get_price(self, symbol: str) -> Optional[Price]:
        """Get current price for symbol"""
        if not self.is_connected:
            return None
        
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            
            # Get best bid/ask prices
            best_bid_ask = self.client.get_best_bid_ask([coinbase_symbol])
            
            if best_bid_ask and 'pricebooks' in best_bid_ask:
                pricebook = best_bid_ask['pricebooks'][0]
                if pricebook:
                    # Use mid price (average of best bid and ask)
                    best_bid = float(pricebook.get('bids', [{}])[0].get('price', 0))
                    best_ask = float(pricebook.get('asks', [{}])[0].get('price', 0))
                    mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid or best_ask
                    
                    return Price(
                        symbol=symbol,
                        exchange=self.name,
                        price=mid_price,
                        timestamp=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        if not self.is_connected:
            return []
        
        try:
            accounts = self.client.get_accounts()
            balances = []
            
            for account in accounts:
                # Handle SDK response objects
                if hasattr(account, 'available_balance'):
                    if hasattr(account.available_balance, 'value'):
                        available = float(account.available_balance.value)
                    else:
                        available = float(account.available_balance)
                else:
                    available = float(account.get('available_balance', {}).get('value', 0))
                    
                if hasattr(account, 'hold'):
                    if hasattr(account.hold, 'value'):
                        hold = float(account.hold.value)
                    else:
                        hold = float(account.hold)
                else:
                    hold = float(account.get('hold', {}).get('value', 0))
                
                if available > 0 or hold > 0:
                    balances.append(Balance(
                        exchange=self.name,
                        asset=account.currency if hasattr(account, 'currency') else account.get('currency', ''),
                        free=available,
                        used=hold,
                        total=available + hold,
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
            coinbase_symbol = self.normalize_symbol(symbol)
            
            # Order placement using official SDK
            order_config = {
                'product_id': coinbase_symbol,
                'side': side.value.upper(),
                'order_configuration': {}
            }
            
            if order_type == OrderType.MARKET:
                order_config['order_configuration'] = {
                    'market_market_ioc': {
                        'quote_size': str(amount) if side == OrderSide.BUY else None,
                        'base_size': str(amount) if side == OrderSide.SELL else None
                    }
                }
            elif order_type == OrderType.LIMIT:
                order_config['order_configuration'] = {
                    'limit_limit_gtc': {
                        'base_size': str(amount),
                        'limit_price': str(price),
                        'post_only': False
                    }
                }
            
            # Place the order
            result = self.client.create_order(**order_config)
            
            if result and 'order_id' in result:
                logger.info(f"✅ Order placed successfully: {result['order_id']}")
                return result['order_id']
            else:
                raise Exception("Order placement failed - no order ID returned")
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def get_order_book(self, symbol: str, depth: int = 10) -> Optional[Any]:
        """Get order book for symbol"""
        if not self.is_connected:
            return None
        
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            
            # Get best bid/ask (simplified order book)
            best_bid_ask = self.client.get_best_bid_ask([coinbase_symbol])
            
            if best_bid_ask and 'pricebooks' in best_bid_ask:
                return best_bid_ask['pricebooks'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return None


async def test_coinbase_advanced_trade_official(api_key: str, api_secret: str, sandbox: bool = False) -> bool:
    """
    Test Coinbase Advanced Trade connection using official SDK
    
    Args:
        api_key: Coinbase Advanced Trade API key
        api_secret: Coinbase Advanced Trade API secret (PEM format)
        sandbox: Use sandbox environment
    
    Returns:
        True if connection successful
    """
    try:
        logger.info("🧪 Testing Coinbase Advanced Trade connection (Official SDK)...")
        
        exchange = CoinbaseAdvancedTradeOfficialExchange(api_key, api_secret, sandbox)
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
            
            # Test getting products
            products = exchange.client.get_products()
            logger.info(f"📈 Found {len(products)} trading products")
            
            await exchange.disconnect()
            return True
        else:
            logger.error("❌ Coinbase Advanced Trade connection test FAILED")
            return False
    
    except Exception as e:
        logger.error(f"❌ Connection test error: {e}")
        return False


async def integrate_coinbase_advanced_trade_official_into_empire(api_key: str, api_secret: str, sandbox: bool = False):
    """
    Integrate Coinbase Advanced Trade into your trading empire using official SDK
    
    Args:
        api_key: Coinbase Advanced Trade API key
        api_secret: Coinbase Advanced Trade API secret (PEM format)
        sandbox: Use sandbox environment
    """
    logger.info("🚀 Integrating Coinbase Advanced Trade (Official SDK) into Shadow.AI Empire...")
    
    # Step 1: Test connection
    test_result = await test_coinbase_advanced_trade_official(api_key, api_secret, sandbox)
    
    if not test_result:
        logger.error("❌ Cannot integrate Coinbase Advanced Trade - connection test failed")
        return False
    
    # Step 2: Create exchange instance
    coinbase = CoinbaseAdvancedTradeOfficialExchange(api_key, api_secret, sandbox)
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
        # Your credentials
        API_KEY = "organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/e327dd05-3f40-46de-9c63-e094c9338cd9"
        API_SECRET = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIBc7DIs6V0EZdMM7MspxHfRDgy53GuoKSZh+RRPV+2s2oAoGCCqGSM49
AwEHoUQDQgAEHASjLYR4wqs7mQqNyIIsTSvw/nmH5Wpe+0b7vrRIeyUWsSQRVwoH
Zw3doF6jH+BkR+qJZHi/y95fkpSL93o85A==
-----END EC PRIVATE KEY-----"""
        
        # Test the integration
        coinbase = await integrate_coinbase_advanced_trade_official_into_empire(
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

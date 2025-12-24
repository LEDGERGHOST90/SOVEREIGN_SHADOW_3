"""
🔌 Exchange Wrapper

Unified API wrapper for multiple cryptocurrency exchanges.
Supports: Coinbase, OKX, Kraken, Binance US
"""

import ccxt
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("shadow_sdk.utils.exchanges")


class ExchangeWrapper:
    """
    🔌 Unified Exchange API Wrapper
    
    Provides a consistent interface across multiple exchanges.
    
    Example:
        >>> wrapper = ExchangeWrapper()
        >>> wrapper.add_exchange("coinbase", api_key, api_secret)
        >>> balance = await wrapper.get_balance("coinbase")
    """
    
    def __init__(self):
        """Initialize exchange wrapper."""
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        logger.info("🔌 ExchangeWrapper initialized")
    
    def add_exchange(self, name: str, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        """
        Add an exchange connection.
        
        Args:
            name: Exchange name (coinbase, okx, kraken, binanceus)
            api_key: API key
            api_secret: API secret
            passphrase: Passphrase (required for Coinbase, OKX)
        """
        exchange_config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        }
        
        if passphrase:
            exchange_config['password'] = passphrase
        
        try:
            exchange_class = getattr(ccxt, name.lower())
            self.exchanges[name] = exchange_class(exchange_config)
            logger.info(f"✅ {name} exchange added")
        except Exception as e:
            logger.error(f"❌ Failed to add {name} exchange: {e}")
    
    async def get_balance(self, exchange_name: str) -> Dict[str, Any]:
        """Get balance for an exchange."""
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not configured")
        
        try:
            balance = await self.exchanges[exchange_name].fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"❌ Failed to fetch balance from {exchange_name}: {e}")
            return {}
    
    async def get_ticker(self, exchange_name: str, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not configured")
        
        try:
            ticker = await self.exchanges[exchange_name].fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"❌ Failed to fetch ticker from {exchange_name}: {e}")
            return {}
    
    async def create_order(self, exchange_name: str, symbol: str, order_type: str, 
                          side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Create an order on an exchange.
        
        Args:
            exchange_name: Exchange name
            symbol: Trading pair (e.g., "BTC/USD")
            order_type: Order type (market, limit)
            side: Order side (buy, sell)
            amount: Order amount
            price: Order price (required for limit orders)
        """
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange {exchange_name} not configured")
        
        try:
            order = await self.exchanges[exchange_name].create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            logger.info(f"✅ Order created on {exchange_name}: {side} {amount} {symbol}")
            return order
        except Exception as e:
            logger.error(f"❌ Failed to create order on {exchange_name}: {e}")
            return {}
    
    def get_configured_exchanges(self) -> List[str]:
        """Get list of configured exchanges."""
        return list(self.exchanges.keys())


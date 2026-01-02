#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Binance US Connector
Binance US API integration
"""

import ccxt
import logging
from typing import Dict, Optional, Any
from .base_connector import BaseExchangeConnector, OrderSide, OrderType

logger = logging.getLogger(__name__)


class BinanceUSConnector(BaseExchangeConnector):
    """
    Binance US API connector

    Uses CCXT library for standardized interface
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False
    ):
        """Initialize Binance US connector"""
        super().__init__(api_key, api_secret, None, testnet)

        self.exchange = ccxt.binanceus({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'warnOnFetchOpenOrdersWithoutSymbol': False,
                'defaultType': 'spot',
            },
            'hostname': 'api.binance.us',  # Force IPv4
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)
            logger.info("🧪 Binance US testnet mode enabled")

    def connect(self) -> bool:
        """Connect and verify credentials"""
        try:
            self.exchange.fetch_balance()
            self.connected = True
            logger.info(f"✅ Connected to Binance US")
            return True
        except Exception as e:
            logger.error(f"❌ Binance US connection failed: {e}")
            self.connected = False
            return False

    def fetch_balance(self) -> Dict[str, float]:
        """Fetch account balance"""
        try:
            balance = self.exchange.fetch_balance()
            result = {}
            for currency, amounts in balance['total'].items():
                if amounts > 0:
                    result[currency] = amounts

            logger.info(f"💰 Binance US balance: {len(result)} currencies")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance US balance: {e}")
            return {}

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create an order on Binance US"""
        try:
            valid, error = self.validate_order(symbol, side, amount, price)
            if not valid:
                logger.error(f"❌ Order validation failed: {error}")
                return {"error": error, "success": False}

            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type.value,
                side=side.value,
                amount=amount,
                price=price
            )

            logger.info(f"✅ Binance US order created: {order['id']}")
            return self.format_order_response(order)

        except Exception as e:
            logger.error(f"❌ Failed to create Binance US order: {e}")
            return {"error": str(e), "success": False}

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✅ Binance US order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel Binance US order: {e}")
            return False

    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Fetch order details"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return self.format_order_response(order)
        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance US order: {e}")
            return {"error": str(e)}

    def fetch_ticker(self, symbol: str) -> Dict[str, float]:
        """Fetch current ticker price"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "bid": ticker['bid'],
                "ask": ticker['ask'],
                "last": ticker['last']
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance US ticker: {e}")
            return {"error": str(e)}

    def fetch_open_orders(self, symbol: str = None) -> list:
        """
        Fetch open orders

        Args:
            symbol: Trading pair (e.g., 'BTC/USD'). If None, fetches all.
                   Note: Fetching without symbol has 10x stricter rate limits.
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.info(f"📋 Binance US open orders: {len(orders)}")
            return [self.format_order_response(o) for o in orders]
        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance US open orders: {e}")
            return []

    def fetch_my_trades(self, symbol: str, limit: int = 50) -> list:
        """
        Fetch trade history for a symbol

        Args:
            symbol: Trading pair (e.g., 'BTC/USD') - REQUIRED
            limit: Number of trades to fetch (default 50)
        """
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            logger.info(f"📊 Binance US trades for {symbol}: {len(trades)}")
            return trades
        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance US trades: {e}")
            return []

    def fetch_all_trades(self, symbols: list = None, limit: int = 20) -> Dict[str, list]:
        """
        Fetch trade history across multiple symbols

        Args:
            symbols: List of trading pairs. Defaults to common pairs.
            limit: Trades per symbol
        """
        if symbols is None:
            symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'PEPE/USD']

        all_trades = {}
        for symbol in symbols:
            try:
                trades = self.exchange.fetch_my_trades(symbol, limit=limit)
                if trades:
                    all_trades[symbol] = trades
            except Exception:
                continue  # Symbol may not exist or no trades

        logger.info(f"📊 Binance US total: {sum(len(t) for t in all_trades.values())} trades across {len(all_trades)} pairs")
        return all_trades

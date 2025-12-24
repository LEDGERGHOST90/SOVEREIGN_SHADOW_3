#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Kraken Connector
Kraken REST API integration
"""

import ccxt
import logging
from typing import Dict, Optional, Any
from .base_connector import BaseExchangeConnector, OrderSide, OrderType

logger = logging.getLogger(__name__)


class KrakenConnector(BaseExchangeConnector):
    """
    Kraken REST API connector

    Uses CCXT library for standardized interface
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False
    ):
        """Initialize Kraken connector"""
        super().__init__(api_key, api_secret, None, testnet)

        self.exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        if testnet:
            logger.warning("⚠️  Kraken does not have a public testnet")

    def connect(self) -> bool:
        """Connect and verify credentials"""
        try:
            self.exchange.fetch_balance()
            self.connected = True
            logger.info(f"✅ Connected to Kraken")
            return True
        except Exception as e:
            logger.error(f"❌ Kraken connection failed: {e}")
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

            logger.info(f"💰 Kraken balance: {len(result)} currencies")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to fetch Kraken balance: {e}")
            return {}

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create an order on Kraken"""
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

            logger.info(f"✅ Kraken order created: {order['id']}")
            return self.format_order_response(order)

        except Exception as e:
            logger.error(f"❌ Failed to create Kraken order: {e}")
            return {"error": str(e), "success": False}

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✅ Kraken order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel Kraken order: {e}")
            return False

    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Fetch order details"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return self.format_order_response(order)
        except Exception as e:
            logger.error(f"❌ Failed to fetch Kraken order: {e}")
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
            logger.error(f"❌ Failed to fetch Kraken ticker: {e}")
            return {"error": str(e)}

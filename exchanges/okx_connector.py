#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - OKX Connector
OKX v5 API integration
"""

import ccxt
import logging
from typing import Dict, Optional, Any
from .base_connector import BaseExchangeConnector, OrderSide, OrderType

logger = logging.getLogger(__name__)


class OKXConnector(BaseExchangeConnector):
    """
    OKX v5 API connector

    Uses CCXT library for standardized interface
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        testnet: bool = False
    ):
        """Initialize OKX connector"""
        super().__init__(api_key, api_secret, passphrase, testnet)

        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,  # OKX requires passphrase
            'enableRateLimit': True,
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)
            logger.info("🧪 OKX testnet mode enabled")

    def connect(self) -> bool:
        """Connect and verify credentials"""
        try:
            self.exchange.fetch_balance()
            self.connected = True
            logger.info(f"✅ Connected to OKX{'(testnet)' if self.testnet else ''}")
            return True
        except Exception as e:
            logger.error(f"❌ OKX connection failed: {e}")
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

            logger.info(f"💰 OKX balance: {len(result)} currencies")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to fetch OKX balance: {e}")
            return {}

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create an order on OKX"""
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

            logger.info(f"✅ OKX order created: {order['id']}")
            return self.format_order_response(order)

        except Exception as e:
            logger.error(f"❌ Failed to create OKX order: {e}")
            return {"error": str(e), "success": False}

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✅ OKX order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel OKX order: {e}")
            return False

    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Fetch order details"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return self.format_order_response(order)
        except Exception as e:
            logger.error(f"❌ Failed to fetch OKX order: {e}")
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
            logger.error(f"❌ Failed to fetch OKX ticker: {e}")
            return {"error": str(e)}

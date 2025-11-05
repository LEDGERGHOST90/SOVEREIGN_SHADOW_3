#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Coinbase Connector
Coinbase Advanced Trade API integration
"""

import ccxt
import logging
from typing import Dict, Optional, Any
from .base_connector import BaseExchangeConnector, OrderSide, OrderType

logger = logging.getLogger(__name__)


class CoinbaseConnector(BaseExchangeConnector):
    """
    Coinbase Advanced Trade API connector

    Uses CCXT library for standardized interface
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        testnet: bool = False
    ):
        """Initialize Coinbase connector"""
        super().__init__(api_key, api_secret, passphrase, testnet)

        self.exchange = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,  # Coinbase requires passphrase
            'enableRateLimit': True,
        })

        if testnet:
            logger.warning("⚠️  Coinbase does not have a public testnet")

    def connect(self) -> bool:
        """
        Connect and verify credentials

        Returns:
            bool: True if connection successful
        """
        try:
            # Test connection by fetching balance
            self.exchange.fetch_balance()
            self.connected = True
            logger.info(f"✅ Connected to Coinbase")
            return True
        except Exception as e:
            logger.error(f"❌ Coinbase connection failed: {e}")
            self.connected = False
            return False

    def fetch_balance(self) -> Dict[str, float]:
        """
        Fetch account balance

        Returns:
            Dict[str, float]: {"BTC": 0.5, "USDT": 1000.0, ...}
        """
        try:
            balance = self.exchange.fetch_balance()

            # Extract total balance (available + locked)
            result = {}
            for currency, amounts in balance['total'].items():
                if amounts > 0:
                    result[currency] = amounts

            logger.info(f"💰 Coinbase balance: {len(result)} currencies")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to fetch Coinbase balance: {e}")
            return {}

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create an order on Coinbase

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side (buy/sell)
            order_type: Order type (market/limit)
            amount: Order amount
            price: Order price (required for limit)

        Returns:
            Dict with order details
        """
        try:
            # Validate order first
            valid, error = self.validate_order(symbol, side, amount, price)
            if not valid:
                logger.error(f"❌ Order validation failed: {error}")
                return {"error": error, "success": False}

            # Create order
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type.value,
                side=side.value,
                amount=amount,
                price=price
            )

            logger.info(f"✅ Coinbase order created: {order['id']}")
            return self.format_order_response(order)

        except Exception as e:
            logger.error(f"❌ Failed to create Coinbase order: {e}")
            return {"error": str(e), "success": False}

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair

        Returns:
            bool: True if cancellation successful
        """
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✅ Coinbase order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel Coinbase order: {e}")
            return False

    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch order details

        Args:
            order_id: Order ID
            symbol: Trading pair

        Returns:
            Dict with order details
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return self.format_order_response(order)
        except Exception as e:
            logger.error(f"❌ Failed to fetch Coinbase order: {e}")
            return {"error": str(e)}

    def fetch_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Fetch current ticker price

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Dict: {"bid": 99000, "ask": 99100, "last": 99050}
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                "bid": ticker['bid'],
                "ask": ticker['ask'],
                "last": ticker['last']
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch Coinbase ticker: {e}")
            return {"error": str(e)}

    def set_stop_loss(
        self,
        symbol: str,
        amount: float,
        stop_price: float
    ) -> Dict[str, Any]:
        """
        Set stop loss order

        Args:
            symbol: Trading pair
            amount: Amount to sell
            stop_price: Stop loss trigger price

        Returns:
            Dict with order details
        """
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_loss',
                side='sell',
                amount=amount,
                price=stop_price
            )

            logger.info(f"✅ Stop loss set at ${stop_price:,.2f}")
            return self.format_order_response(order)

        except Exception as e:
            logger.error(f"❌ Failed to set stop loss: {e}")
            return {"error": str(e), "success": False}


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    connector = CoinbaseConnector(
        api_key=os.getenv("COINBASE_API_KEY"),
        api_secret=os.getenv("COINBASE_API_SECRET"),
        passphrase=os.getenv("COINBASE_PASSPHRASE")
    )

    if connector.connect():
        print("\n✅ Connected to Coinbase")

        balance = connector.fetch_balance()
        print(f"\n💰 Balance: {balance}")

        ticker = connector.fetch_ticker("BTC/USD")
        print(f"\n📊 BTC/USD: ${ticker['last']:,.2f}")

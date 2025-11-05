#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Base Exchange Connector
Abstract base class for all exchange integrations
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BaseExchangeConnector(ABC):
    """
    Abstract base class for exchange connectors

    All exchange implementations must inherit from this and implement:
    - connect()
    - fetch_balance()
    - create_order()
    - cancel_order()
    - fetch_order()
    - fetch_ticker()
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        testnet: bool = False
    ):
        """
        Initialize exchange connector

        Args:
            api_key: API key
            api_secret: API secret
            passphrase: Passphrase (required for some exchanges like Coinbase, OKX)
            testnet: Use testnet instead of production
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.testnet = testnet
        self.connected = False
        self.exchange_name = self.__class__.__name__.replace("Connector", "")

        logger.info(f"🔌 {self.exchange_name} connector initialized (testnet={testnet})")

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to exchange and verify credentials

        Returns:
            bool: True if connection successful
        """
        pass

    @abstractmethod
    def fetch_balance(self) -> Dict[str, float]:
        """
        Fetch account balance

        Returns:
            Dict[str, float]: {"BTC": 0.5, "USDT": 1000.0, ...}
        """
        pass

    @abstractmethod
    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create an order

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side (buy/sell)
            order_type: Order type (market/limit)
            amount: Order amount in base currency
            price: Order price (required for limit orders)

        Returns:
            Dict with order details including order_id
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair

        Returns:
            bool: True if cancellation successful
        """
        pass

    @abstractmethod
    def fetch_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch order details

        Args:
            order_id: Order ID
            symbol: Trading pair

        Returns:
            Dict with order details
        """
        pass

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Fetch current ticker price

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Dict: {"bid": 99000, "ask": 99100, "last": 99050}
        """
        pass

    def get_position_value(self, symbol: str, amount: float) -> float:
        """
        Get current USD value of a position

        Args:
            symbol: Trading pair
            amount: Amount in base currency

        Returns:
            float: USD value
        """
        ticker = self.fetch_ticker(symbol)
        return ticker["last"] * amount

    def validate_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        price: Optional[float] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate order parameters before submission

        Returns:
            (valid, error_message)
        """
        if amount <= 0:
            return False, "Amount must be positive"

        if price is not None and price <= 0:
            return False, "Price must be positive"

        # Check balance
        balance = self.fetch_balance()
        base_currency = symbol.split('/')[0]
        quote_currency = symbol.split('/')[1]

        if side == OrderSide.BUY:
            required = amount * (price if price else self.fetch_ticker(symbol)["ask"])
            if balance.get(quote_currency, 0) < required:
                return False, f"Insufficient {quote_currency} balance"
        else:
            if balance.get(base_currency, 0) < amount:
                return False, f"Insufficient {base_currency} balance"

        return True, None

    def format_order_response(self, raw_response: Dict) -> Dict[str, Any]:
        """
        Format exchange-specific response to standard format

        Returns standardized order dict:
        {
            "order_id": str,
            "symbol": str,
            "side": OrderSide,
            "type": OrderType,
            "amount": float,
            "price": float,
            "status": OrderStatus,
            "filled": float,
            "timestamp": str
        }
        """
        return {
            "order_id": raw_response.get("id"),
            "symbol": raw_response.get("symbol"),
            "side": raw_response.get("side"),
            "type": raw_response.get("type"),
            "amount": raw_response.get("amount"),
            "price": raw_response.get("price"),
            "status": raw_response.get("status"),
            "filled": raw_response.get("filled", 0),
            "timestamp": raw_response.get("timestamp", datetime.utcnow().isoformat())
        }

    def __repr__(self) -> str:
        return f"{self.exchange_name}Connector(connected={self.connected}, testnet={self.testnet})"

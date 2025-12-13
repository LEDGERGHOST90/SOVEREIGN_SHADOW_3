#!/usr/bin/env python3
"""
Base Exchange Connector
Defines the interface all exchange connectors must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class Balance:
    """Account balance"""
    asset: str
    free: float
    locked: float
    total: float
    usd_value: Optional[float] = None


@dataclass
class Ticker:
    """Price ticker"""
    symbol: str
    bid: float
    ask: float
    last: float
    timestamp: datetime


@dataclass
class Order:
    """Order details"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    amount: float
    price: Optional[float]
    status: str
    filled: float
    timestamp: datetime


class BaseExchangeConnector(ABC):
    """
    Base class for all exchange connectors
    
    All exchange implementations must inherit from this class
    and implement these methods.
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
            api_key: Exchange API key
            api_secret: Exchange API secret
            passphrase: Optional passphrase (Coinbase, KuCoin)
            testnet: Use testnet/sandbox if available
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.testnet = testnet
        self.connected = False
        self.exchange = None
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect and authenticate with exchange
        
        Returns:
            bool: True if connection successful
        """
        pass
    
    @abstractmethod
    def fetch_balance(self) -> Dict[str, Balance]:
        """
        Fetch account balances
        
        Returns:
            Dict[str, Balance]: {"BTC": Balance(...), "USDT": Balance(...)}
        """
        pass
    
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Ticker:
        """
        Fetch current ticker price
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
        
        Returns:
            Ticker: Price information
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
    ) -> Order:
        """
        Create an order
        
        Args:
            symbol: Trading pair
            side: Buy or sell
            order_type: Market, limit, etc.
            amount: Order amount
            price: Limit price (required for limit orders)
        
        Returns:
            Order: Order details
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
    def fetch_order(self, order_id: str, symbol: str) -> Order:
        """
        Fetch order details
        
        Args:
            order_id: Order ID
            symbol: Trading pair
        
        Returns:
            Order: Order details
        """
        pass
    
    def validate_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        price: Optional[float] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate order parameters
        
        Returns:
            (valid, error_message)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        if price is not None and price <= 0:
            return False, "Price must be positive"
        
        return True, None
    
    def format_order_response(self, raw_order: Dict) -> Order:
        """
        Format exchange-specific order response to standard Order object
        
        Args:
            raw_order: Raw order dict from exchange
        
        Returns:
            Order: Standardized order object
        """
        return Order(
            order_id=raw_order.get('id', ''),
            symbol=raw_order.get('symbol', ''),
            side=OrderSide(raw_order.get('side', 'buy')),
            order_type=OrderType(raw_order.get('type', 'market')),
            amount=float(raw_order.get('amount', 0)),
            price=float(raw_order.get('price')) if raw_order.get('price') else None,
            status=raw_order.get('status', 'unknown'),
            filled=float(raw_order.get('filled', 0)),
            timestamp=datetime.now()
        )

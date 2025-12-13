"""
Base Exchange Connector
Abstract base class for all exchange connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


@dataclass
class Balance:
    """Account balance information"""
    asset: str
    free: float
    used: float
    total: float
    usd_value: Optional[float] = None


@dataclass
class Price:
    """Price information"""
    symbol: str
    price: float
    timestamp: datetime
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None


@dataclass
class Order:
    """Order information"""
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    amount: float
    price: Optional[float]
    status: str
    timestamp: datetime


class BaseExchangeConnector(ABC):
    """
    Abstract base class for exchange connectors
    Implements common functionality and defines interface
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize exchange connector
        
        Args:
            name: Exchange name (e.g., 'coinbase', 'okx')
            config: Configuration dictionary with API keys, etc.
        """
        self.name = name
        self.config = config
        self._connected = False
        self._use_sandbox = config.get('use_sandbox', True)
        self._enabled = config.get('enabled', False)
    
    @property
    def is_connected(self) -> bool:
        """Check if connector is connected to exchange"""
        return self._connected
    
    @property
    def use_sandbox(self) -> bool:
        """Check if using sandbox mode"""
        return self._use_sandbox
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to exchange
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to exchange
        
        Returns:
            Dictionary with 'status' ('SUCCESS' or 'FAILED') and 'error' if failed
        """
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, Balance]:
        """
        Get account balances
        
        Returns:
            Dictionary mapping asset symbols to Balance objects
        """
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[Price]:
        """
        Get current price for symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
        
        Returns:
            Price object or None if error
        """
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Optional[str]:
        """
        Place order on exchange
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            amount: Order amount
            order_type: Order type (MARKET, LIMIT, etc.)
            price: Limit price (required for LIMIT orders)
        
        Returns:
            Order ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def normalize_symbol(self, symbol: str) -> str:
        """
        Convert standard symbol format to exchange-specific format
        
        Args:
            symbol: Standard format (e.g., 'BTC/USDT')
        
        Returns:
            Exchange-specific format (e.g., 'BTC-USD' for Coinbase)
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check
        
        Returns:
            Health status dictionary
        """
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "healthy": False,
                    "exchange": self.name
                }
            
            # Try to fetch a price as health check
            test_price = await self.get_price("BTC/USDT")
            
            return {
                "status": "connected",
                "healthy": test_price is not None,
                "exchange": self.name,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "healthy": False,
                "exchange": self.name,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

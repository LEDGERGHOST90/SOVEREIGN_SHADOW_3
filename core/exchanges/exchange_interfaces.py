"""
Modular Interfaces and Base Classes
Defines contracts and abstractions for all system components
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ============================================================================
# CORE DATA MODELS
# ============================================================================

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

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
class Price:
    """Price information with metadata"""
    symbol: str
    exchange: str
    price: float
    timestamp: datetime
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None

@dataclass
class Balance:
    """Account balance information"""
    exchange: str
    asset: str
    free: float
    used: float
    total: float
    usd_value: Optional[float] = None

@dataclass
class OrderBookEntry:
    """Order book entry (bid or ask)"""
    price: float
    size: float

@dataclass
class OrderBook:
    """Order book data"""
    symbol: str
    exchange: str
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: datetime

@dataclass
class Trade:
    """Trade execution data"""
    id: str
    symbol: str
    exchange: str
    side: OrderSide
    amount: float
    price: float
    fee: float
    timestamp: datetime
    order_id: Optional[str] = None

@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity data"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_percent: float
    estimated_profit_percent: float
    min_order_size: float
    max_order_size: float
    timestamp: datetime
    confidence_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM

@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot at a point in time"""
    timestamp: datetime
    total_value_usd: float
    balances: List[Balance]
    allocation_percentages: Dict[str, float]
    risk_metrics: Dict[str, float]

# ============================================================================
# PROTOCOL INTERFACES (for dependency injection)
# ============================================================================

@runtime_checkable
class PriceProvider(Protocol):
    """Protocol for price data providers"""
    
    async def get_price(self, symbol: str, exchange: str) -> Optional[Price]:
        """Get current price for symbol on exchange"""
        ...
    
    async def get_prices(self, symbol: str) -> Dict[str, Price]:
        """Get prices across all available exchanges"""
        ...
    
    async def get_order_book(self, symbol: str, exchange: str) -> Optional[OrderBook]:
        """Get order book for symbol on exchange"""
        ...

@runtime_checkable
class BalanceProvider(Protocol):
    """Protocol for balance data providers"""
    
    async def get_balance(self, exchange: str, asset: str) -> Optional[Balance]:
        """Get balance for specific asset on exchange"""
        ...
    
    async def get_balances(self, exchange: str) -> List[Balance]:
        """Get all balances for exchange"""
        ...
    
    async def get_portfolio(self) -> List[Balance]:
        """Get complete portfolio across all exchanges"""
        ...

@runtime_checkable
class TradeExecutor(Protocol):
    """Protocol for trade execution"""
    
    async def place_order(
        self,
        exchange: str,
        symbol: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> str:
        """Place order and return order ID"""
        ...
    
    async def cancel_order(self, exchange: str, order_id: str) -> bool:
        """Cancel order by ID"""
        ...
    
    async def get_order_status(self, exchange: str, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        ...

@runtime_checkable
class RiskManager(Protocol):
    """Protocol for risk management"""
    
    async def assess_risk(self, opportunity: ArbitrageOpportunity) -> RiskLevel:
        """Assess risk level for arbitrage opportunity"""
        ...
    
    async def calculate_position_size(
        self,
        opportunity: ArbitrageOpportunity,
        available_capital: float
    ) -> float:
        """Calculate optimal position size"""
        ...
    
    async def check_portfolio_risk(self, portfolio: List[Balance]) -> Dict[str, Any]:
        """Check portfolio-level risk metrics"""
        ...

@runtime_checkable
class DataStore(Protocol):
    """Protocol for data persistence"""
    
    async def save_price(self, price: Price) -> None:
        """Save price data"""
        ...
    
    async def save_trade(self, trade: Trade) -> None:
        """Save trade data"""
        ...
    
    async def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Save portfolio snapshot"""
        ...
    
    async def get_price_history(
        self,
        symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Price]:
        """Get historical price data"""
        ...

# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================

class BaseExchange(ABC):
    """Abstract base class for exchange implementations"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if exchange is connected"""
        return self._connected
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[Price]:
        """Get current price for symbol"""
        pass
    
    @abstractmethod
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        amount: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> str:
        """Place order"""
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, depth: int = 10) -> Optional[OrderBook]:
        """Get order book"""
        pass
    
    @abstractmethod
    def normalize_symbol(self, symbol: str) -> str:
        """Convert standard symbol to exchange-specific format"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "healthy": False}
            
            # Try to fetch a price as health check
            test_price = await self.get_price("BTC/USDT")
            
            return {
                "status": "connected",
                "healthy": test_price is not None,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

class BaseArbitrageEngine(ABC):
    """Abstract base class for arbitrage engines"""
    
    def __init__(self, price_provider: PriceProvider, risk_manager: RiskManager):
        self.price_provider = price_provider
        self.risk_manager = risk_manager
        self._monitoring = False
    
    @property
    def is_monitoring(self) -> bool:
        """Check if engine is actively monitoring"""
        return self._monitoring
    
    @abstractmethod
    async def start_monitoring(self, symbols: List[str]) -> None:
        """Start monitoring for arbitrage opportunities"""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Stop monitoring"""
        pass
    
    @abstractmethod
    async def find_opportunities(
        self,
        symbol: str,
        min_profit_threshold: float = 0.2
    ) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities for symbol"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        pass

class BasePortfolioManager(ABC):
    """Abstract base class for portfolio managers"""
    
    def __init__(self, balance_provider: BalanceProvider, price_provider: PriceProvider):
        self.balance_provider = balance_provider
        self.price_provider = price_provider
    
    @abstractmethod
    async def get_portfolio_value(self) -> float:
        """Get total portfolio value in USD"""
        pass
    
    @abstractmethod
    async def get_asset_allocation(self) -> Dict[str, float]:
        """Get asset allocation percentages"""
        pass
    
    @abstractmethod
    async def get_rebalancing_recommendations(
        self,
        target_allocation: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Get rebalancing recommendations"""
        pass
    
    @abstractmethod
    async def calculate_risk_metrics(self) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        pass
    
    @abstractmethod
    async def create_snapshot(self) -> PortfolioSnapshot:
        """Create portfolio snapshot"""
        pass

class BaseRiskManager(ABC):
    """Abstract base class for risk managers"""
    
    @abstractmethod
    async def assess_arbitrage_risk(self, opportunity: ArbitrageOpportunity) -> RiskLevel:
        """Assess risk for arbitrage opportunity"""
        pass
    
    @abstractmethod
    async def calculate_position_size(
        self,
        opportunity: ArbitrageOpportunity,
        available_capital: float,
        risk_tolerance: float = 0.02
    ) -> float:
        """Calculate position size based on risk"""
        pass
    
    @abstractmethod
    async def check_portfolio_limits(self, portfolio: List[Balance]) -> List[str]:
        """Check portfolio against risk limits, return violations"""
        pass
    
    @abstractmethod
    async def calculate_var(
        self,
        portfolio: List[Balance],
        confidence_level: float = 0.95,
        time_horizon_days: int = 1
    ) -> float:
        """Calculate Value at Risk"""
        pass

class BaseDataStore(ABC):
    """Abstract base class for data storage"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize data store"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close data store connections"""
        pass
    
    @abstractmethod
    async def save_price(self, price: Price) -> None:
        """Save price data"""
        pass
    
    @abstractmethod
    async def save_trade(self, trade: Trade) -> None:
        """Save trade execution data"""
        pass
    
    @abstractmethod
    async def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Save portfolio snapshot"""
        pass
    
    @abstractmethod
    async def get_price_history(
        self,
        symbol: str,
        exchange: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Price]:
        """Get historical price data"""
        pass
    
    @abstractmethod
    async def get_trade_history(
        self,
        start_time: datetime,
        end_time: datetime,
        exchange: Optional[str] = None
    ) -> List[Trade]:
        """Get trade history"""
        pass

# ============================================================================
# SERVICE INTERFACES
# ============================================================================

class ExchangeService(ABC):
    """Service interface for exchange operations"""
    
    @abstractmethod
    async def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges"""
        pass
    
    @abstractmethod
    async def get_exchange(self, name: str) -> Optional[BaseExchange]:
        """Get exchange instance by name"""
        pass
    
    @abstractmethod
    async def initialize_exchanges(self, exchange_names: List[str]) -> Dict[str, bool]:
        """Initialize multiple exchanges"""
        pass
    
    @abstractmethod
    async def get_multi_exchange_prices(self, symbol: str) -> Dict[str, Price]:
        """Get prices across all exchanges"""
        pass

class ArbitrageService(ABC):
    """Service interface for arbitrage operations"""
    
    @abstractmethod
    async def start_monitoring(self, symbols: List[str]) -> None:
        """Start arbitrage monitoring"""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Stop arbitrage monitoring"""
        pass
    
    @abstractmethod
    async def get_opportunities(self, limit: int = 10) -> List[ArbitrageOpportunity]:
        """Get current arbitrage opportunities"""
        pass
    
    @abstractmethod
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> List[Trade]:
        """Execute arbitrage opportunity"""
        pass

class PortfolioService(ABC):
    """Service interface for portfolio operations"""
    
    @abstractmethod
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, float]:
        """Get portfolio performance metrics"""
        pass
    
    @abstractmethod
    async def rebalance_portfolio(
        self,
        target_allocation: Dict[str, float],
        execute: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate or execute rebalancing plan"""
        pass

# ============================================================================
# EVENT SYSTEM
# ============================================================================

@dataclass
class Event:
    """Base event class"""
    type: str
    timestamp: datetime
    data: Dict[str, Any]

class EventHandler(Protocol):
    """Protocol for event handlers"""
    
    async def handle(self, event: Event) -> None:
        """Handle an event"""
        ...

class EventBus(ABC):
    """Abstract event bus for pub/sub messaging"""
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to event type"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe from event type"""
        pass

# ============================================================================
# DEPENDENCY INJECTION CONTAINER
# ============================================================================

class Container(ABC):
    """Abstract dependency injection container"""
    
    @abstractmethod
    def register(self, interface: type, implementation: type, singleton: bool = True) -> None:
        """Register implementation for interface"""
        pass
    
    @abstractmethod
    def register_instance(self, interface: type, instance: Any) -> None:
        """Register specific instance"""
        pass
    
    @abstractmethod
    def resolve(self, interface: type) -> Any:
        """Resolve implementation for interface"""
        pass
    
    @abstractmethod
    def create_scope(self) -> 'Container':
        """Create new scope for scoped dependencies"""
        pass

# ============================================================================
# HEALTH CHECK SYSTEM
# ============================================================================

@dataclass
class HealthStatus:
    """Health check status"""
    component: str
    healthy: bool
    status: str
    details: Dict[str, Any]
    timestamp: datetime

class HealthChecker(Protocol):
    """Protocol for health checkers"""
    
    async def check_health(self) -> HealthStatus:
        """Perform health check"""
        ...

class HealthMonitor(ABC):
    """Abstract health monitoring system"""
    
    @abstractmethod
    async def register_checker(self, name: str, checker: HealthChecker) -> None:
        """Register health checker"""
        pass
    
    @abstractmethod
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all components"""
        pass
    
    @abstractmethod
    async def get_overall_status(self) -> HealthStatus:
        """Get overall system health"""
        pass

# ============================================================================
# BASE MODULE INTERFACE
# ============================================================================

class BaseModule(ABC):
    """Base class for all system modules"""
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return result"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the module"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the module"""
        pass

# ============================================================================
# CONFIGURATION INTERFACE
# ============================================================================

class ConfigProvider(Protocol):
    """Protocol for configuration providers"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        ...
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get configuration section"""
        ...
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        ...
    
    def reload(self) -> None:
        """Reload configuration"""
        ...

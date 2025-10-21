"""
Engine Manager Module
Handles Coinbase trading execution, position management, and risk controls
"""

import logging
import json
import yaml
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
from enum import Enum
import os
from pathlib import Path
import hashlib
import hmac
import time
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order side enum"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enum"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Order status enum"""
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass
class Position:
    """Represents an active trading position"""
    symbol: str
    side: OrderSide
    entry_price: Decimal
    size: Decimal
    value_usd: Decimal
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    opened_at: datetime
    pnl: Decimal = Decimal('0')
    pnl_percent: float = 0.0


@dataclass
class Order:
    """Represents a trading order"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: Decimal
    price: Optional[Decimal]
    status: OrderStatus
    created_at: datetime
    filled_at: Optional[datetime] = None
    filled_price: Optional[Decimal] = None
    fees: Decimal = Decimal('0')


@dataclass
class TradingSignal:
    """Trading signal from strategy analysis"""
    symbol: str
    action: OrderSide
    strength: float  # 0-100
    timeframe: str
    price_target: Optional[Decimal]
    stop_loss: Optional[Decimal]
    confidence: float  # 0-1
    reason: str


class EngineManager:
    """
    Manages active trading on Coinbase
    Executes strategies, manages positions, and enforces risk limits
    """
    
    def __init__(self, config_path: str = "../config/ves_architecture.yaml"):
        """Initialize engine manager with configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.daily_pnl = Decimal('0')
        self.win_rate = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        # API configuration (will be loaded from environment)
        self.api_key = os.getenv('COINBASE_API_KEY', '')
        self.api_secret = os.getenv('COINBASE_API_SECRET', '')
        self.api_url = "https://api.coinbase.com/api/v3/brokerage"
        
        # Create data directory for engine state
        self.data_dir = Path("../data/engine")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize rate limiter
        self.last_request_time = 0
        self.rate_limit = 1.0 / self.config['exchanges']['coinbase']['rate_limit_per_second']
        
        logger.info("Engine Manager initialized")
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            config_path = self.config_path
            if not config_path.is_absolute():
                config_path = Path(__file__).parent / config_path
                
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f)
            
            # Merge engine and exchange configs
            return {
                **full_config['engine'],
                'exchanges': full_config['exchanges']
            }
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
            
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Generate HMAC signature for Coinbase API"""
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[dict] = None
    ) -> Optional[dict]:
        """Make authenticated request to Coinbase API"""
        if not self.api_key or not self.api_secret:
            logger.error("API credentials not configured")
            return None
            
        self._rate_limit()
        
        timestamp = str(int(time.time()))
        path = f"/api/v3/brokerage{endpoint}"
        body = json.dumps(data) if data else ''
        
        signature = self._generate_signature(timestamp, method, path, body)
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        try:
            url = f"{self.api_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
            
    def get_account_balances(self) -> Dict[str, Decimal]:
        """
        Get current account balances from Coinbase
        
        Returns:
            Dictionary of asset balances
        """
        response = self._make_request('GET', '/accounts')
        
        if not response or 'accounts' not in response:
            logger.error("Failed to fetch account balances")
            return {}
            
        balances = {}
        for account in response['accounts']:
            currency = account['currency']
            available = Decimal(account['available_balance']['value'])
            
            if available > 0:
                balances[currency] = available
                
        logger.info(f"Fetched {len(balances)} account balances")
        return balances
        
    def analyze_market(self, symbol: str, timeframe: str) -> Optional[TradingSignal]:
        """
        Analyze market and generate trading signal
        
        Args:
            symbol: Trading pair (e.g., 'SOL-USD')
            timeframe: Timeframe for analysis
            
        Returns:
            TradingSignal if opportunity found, None otherwise
        """
        # This is a simplified signal generator
        # In production, would integrate with technical indicators
        
        # Fetch recent price data
        response = self._make_request('GET', f'/products/{symbol}/ticker')
        
        if not response:
            return None
            
        current_price = Decimal(response.get('price', '0'))
        
        if current_price == 0:
            return None
            
        # Simple momentum-based signal (placeholder logic)
        # In reality, would use proper technical analysis
        import random
        
        signal_strength = random.uniform(40, 80)
        
        if signal_strength > 60:
            # Generate buy signal
            stop_loss = current_price * Decimal('0.95')  # 5% stop loss
            take_profit = current_price * Decimal('1.15')  # 15% take profit
            
            return TradingSignal(
                symbol=symbol,
                action=OrderSide.BUY,
                strength=signal_strength,
                timeframe=timeframe,
                price_target=take_profit,
                stop_loss=stop_loss,
                confidence=signal_strength / 100,
                reason=f"Momentum signal on {timeframe} timeframe"
            )
            
        return None
        
    def validate_position_size(
        self, 
        symbol: str, 
        value_usd: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate position size against risk rules
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check max position size
        max_position = Decimal(str(self.config['trading_rules']['max_position_size_usd']))
        if value_usd > max_position:
            return False, f"Position size ${value_usd} exceeds max ${max_position}"
            
        # Check daily loss limit
        daily_limit = Decimal(str(self.config['trading_rules']['daily_loss_limit_usd']))
        if self.daily_pnl < -daily_limit:
            return False, f"Daily loss limit ${daily_limit} reached"
            
        # Check number of open positions
        max_positions = self.config['trading_rules']['max_positions']
        if len(self.positions) >= max_positions:
            return False, f"Maximum {max_positions} positions already open"
            
        # Check asset-specific limits
        for asset_config in self.config['assets'].values():
            if symbol.startswith(asset_config.get('symbol', '')):
                asset_max = Decimal(str(asset_config.get('position_size_max', 10000)))
                if value_usd > asset_max:
                    return False, f"Asset position limit ${asset_max} for {symbol}"
                    
        return True, None
        
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        size: Decimal,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> Optional[Order]:
        """
        Place an order on Coinbase
        
        Returns:
            Order object if successful, None otherwise
        """
        # Validate position size
        # Need to get current price for validation
        ticker_response = self._make_request('GET', f'/products/{symbol}/ticker')
        if not ticker_response:
            logger.error("Failed to get ticker for position validation")
            return None
            
        current_price = Decimal(ticker_response.get('price', '0'))
        position_value = size * current_price
        
        is_valid, error_msg = self.validate_position_size(symbol, position_value)
        if not is_valid:
            logger.warning(f"Order validation failed: {error_msg}")
            return None
            
        # Build order request
        order_data = {
            'product_id': symbol,
            'side': side.value,
            'order_configuration': {}
        }
        
        if order_type == OrderType.MARKET:
            order_data['order_configuration']['market_market_ioc'] = {
                'quote_size': str(size) if side == OrderSide.BUY else None,
                'base_size': str(size) if side == OrderSide.SELL else None
            }
        elif order_type == OrderType.LIMIT:
            order_data['order_configuration']['limit_limit_gtc'] = {
                'base_size': str(size),
                'limit_price': str(limit_price),
                'post_only': True
            }
            
        # Place the order
        response = self._make_request('POST', '/orders', order_data)
        
        if not response or not response.get('success'):
            logger.error(f"Order placement failed: {response}")
            return None
            
        # Create order object
        order_id = response['order_id']
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            size=size,
            price=limit_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.orders[order_id] = order
        
        # Create position if market order (assumed to fill immediately)
        if order_type == OrderType.MARKET:
            self._create_position(order, current_price, stop_price, take_profit)
            
        logger.info(f"Placed {order_type.value} {side.value} order for {size} {symbol}")
        return order
        
    def _create_position(
        self,
        order: Order,
        entry_price: Decimal,
        stop_loss: Optional[Decimal],
        take_profit: Optional[Decimal]
    ) -> None:
        """Create a new position from filled order"""
        position = Position(
            symbol=order.symbol,
            side=order.side,
            entry_price=entry_price,
            size=order.size,
            value_usd=order.size * entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.now()
        )
        
        self.positions[order.symbol] = position
        logger.info(f"Opened position: {position.symbol} @ {entry_price}")
        
    def update_positions(self, market_prices: Dict[str, Decimal]) -> None:
        """
        Update position P&L based on current market prices
        
        Args:
            market_prices: Dictionary of current prices by symbol
        """
        for symbol, position in self.positions.items():
            if symbol not in market_prices:
                continue
                
            current_price = market_prices[symbol]
            
            # Calculate P&L
            if position.side == OrderSide.BUY:
                price_change = current_price - position.entry_price
            else:
                price_change = position.entry_price - current_price
                
            position.pnl = price_change * position.size
            position.pnl_percent = float((price_change / position.entry_price) * 100)
            
            # Check stop loss
            if position.stop_loss:
                if (position.side == OrderSide.BUY and current_price <= position.stop_loss) or \
                   (position.side == OrderSide.SELL and current_price >= position.stop_loss):
                    logger.warning(f"Stop loss triggered for {symbol}")
                    self.close_position(symbol, "STOP_LOSS")
                    
            # Check take profit
            if position.take_profit:
                if (position.side == OrderSide.BUY and current_price >= position.take_profit) or \
                   (position.side == OrderSide.SELL and current_price <= position.take_profit):
                    logger.info(f"Take profit triggered for {symbol}")
                    self.close_position(symbol, "TAKE_PROFIT")
                    
    def close_position(self, symbol: str, reason: str = "MANUAL") -> Optional[Order]:
        """
        Close an open position
        
        Args:
            symbol: Position symbol to close
            reason: Reason for closing (MANUAL, STOP_LOSS, TAKE_PROFIT)
            
        Returns:
            Close order if successful
        """
        if symbol not in self.positions:
            logger.warning(f"No open position for {symbol}")
            return None
            
        position = self.positions[symbol]
        
        # Place closing order (opposite side)
        close_side = OrderSide.SELL if position.side == OrderSide.BUY else OrderSide.BUY
        
        close_order = self.place_order(
            symbol=symbol,
            side=close_side,
            size=position.size,
            order_type=OrderType.MARKET
        )
        
        if close_order:
            # Update statistics
            self.total_trades += 1
            if position.pnl > 0:
                self.winning_trades += 1
                
            self.daily_pnl += position.pnl
            self.win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
            
            # Log the trade
            self._log_trade(position, reason)
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position {symbol}: P&L ${position.pnl:.2f} ({position.pnl_percent:.1f}%)")
            
        return close_order
        
    def execute_trading_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete trading cycle
        
        Returns:
            Summary of actions taken
        """
        cycle_summary = {
            'timestamp': datetime.now().isoformat(),
            'signals_generated': 0,
            'orders_placed': 0,
            'positions_updated': 0,
            'positions_closed': 0
        }
        
        # Get current market prices
        market_prices = {}
        for asset in self.config['assets'].keys():
            if asset == 'USDC' or asset == 'BUFFER':
                continue
                
            symbol = f"{asset}-USD"
            response = self._make_request('GET', f'/products/{symbol}/ticker')
            if response and 'price' in response:
                market_prices[symbol] = Decimal(response['price'])
                
        # Update existing positions
        self.update_positions(market_prices)
        cycle_summary['positions_updated'] = len(self.positions)
        
        # Check for new signals on configured timeframes
        timeframes = self.config['trading_rules']['timeframes']
        
        for timeframe_name, timeframe_value in timeframes.items():
            for asset in ['SOL', 'XRP']:  # Focus on momentum assets
                symbol = f"{asset}-USD"
                
                # Skip if already have position
                if symbol in self.positions:
                    continue
                    
                signal = self.analyze_market(symbol, timeframe_value)
                
                if signal and signal.confidence > 0.6:
                    cycle_summary['signals_generated'] += 1
                    
                    # Calculate position size
                    balance = self.get_account_balances().get('USDC', Decimal('0'))
                    position_size = balance * Decimal('0.1')  # Use 10% of USDC
                    
                    # Place order based on signal
                    order = self.place_order(
                        symbol=symbol,
                        side=signal.action,
                        size=position_size,
                        order_type=OrderType.MARKET,
                        stop_price=signal.stop_loss,
                        take_profit=signal.price_target
                    )
                    
                    if order:
                        cycle_summary['orders_placed'] += 1
                        
        # Save cycle summary
        self._save_cycle_summary(cycle_summary)
        
        return cycle_summary
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        total_position_value = sum(p.value_usd for p in self.positions.values())
        total_pnl = sum(p.pnl for p in self.positions.values())
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'open_positions': len(self.positions),
            'total_position_value': float(total_position_value),
            'unrealized_pnl': float(total_pnl),
            'daily_pnl': float(self.daily_pnl),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.win_rate,
            'positions': {}
        }
        
        for symbol, position in self.positions.items():
            metrics['positions'][symbol] = {
                'side': position.side.value,
                'entry_price': float(position.entry_price),
                'size': float(position.size),
                'pnl': float(position.pnl),
                'pnl_percent': position.pnl_percent
            }
            
        return metrics
        
    def _log_trade(self, position: Position, reason: str) -> None:
        """Log completed trade to file"""
        trades_file = self.data_dir / "trades.jsonl"
        
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': position.symbol,
            'side': position.side.value,
            'entry_price': str(position.entry_price),
            'size': str(position.size),
            'pnl': str(position.pnl),
            'pnl_percent': position.pnl_percent,
            'close_reason': reason,
            'duration_minutes': (datetime.now() - position.opened_at).total_seconds() / 60
        }
        
        with open(trades_file, 'a') as f:
            f.write(json.dumps(trade_data) + '\n')
            
    def _save_cycle_summary(self, summary: Dict) -> None:
        """Save trading cycle summary"""
        cycles_file = self.data_dir / f"cycle_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(cycles_file, 'a') as f:
            f.write(json.dumps(summary) + '\n')
            
    def reset_daily_metrics(self) -> None:
        """Reset daily metrics (call at start of trading day)"""
        self.daily_pnl = Decimal('0')
        logger.info("Daily metrics reset")


# Example usage and testing
if __name__ == "__main__":
    # Initialize engine manager
    engine = EngineManager()
    
    # Get account balances
    balances = engine.get_account_balances()
    print(f"Account Balances: {balances}")
    
    # Analyze market for signals
    signal = engine.analyze_market("SOL-USD", "15m")
    if signal:
        print(f"Signal Generated: {signal.symbol} {signal.action.value} @ confidence {signal.confidence:.2f}")
        
    # Execute a trading cycle
    cycle_result = engine.execute_trading_cycle()
    print(f"Trading Cycle Result: {cycle_result}")
    
    # Get performance metrics
    metrics = engine.get_performance_metrics()
    print(f"Performance Metrics: {json.dumps(metrics, indent=2)}")
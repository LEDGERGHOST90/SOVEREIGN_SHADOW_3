import asyncio
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import pandas as pd
import numpy as np

from src.models.user import db
from src.models.signal import TradingSignal, ExecutionLog
from src.models.exchange_config import Position, RiskSettings
from src.execution.exchange_adapters import ExchangeAdapterFactory
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Market data point for simulation"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    bid: float
    ask: float
    volatility: float = 0.02  # 2% default volatility

@dataclass
class OrderFill:
    """Order fill simulation result"""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    filled_quantity: float
    filled_price: float
    fees: float
    slippage: float
    fill_time: datetime
    partial_fill: bool = False

@dataclass
class LadderLevel:
    """Ladder trading level"""
    level: int
    price: float
    quantity: float
    order_type: str  # entry, tp1, tp2, sl
    status: str = 'pending'  # pending, filled, cancelled
    order_id: Optional[str] = None
    filled_at: Optional[datetime] = None

class MarketSimulator:
    """Realistic market data simulation"""
    
    def __init__(self):
        self.price_history: Dict[str, List[MarketData]] = {}
        self.current_prices: Dict[str, float] = {}
        self.volatility_profiles = {
            # Core Holdings (Ledger + Coinbase)
            'BTC': 0.03,    # 3% daily volatility
            'ETH': 0.04,    # 4% daily volatility
            'SOL': 0.06,    # 6% daily volatility
            'XRP': 0.05,    # 5% daily volatility
            # AI Basket (Coinbase Active)
            'FET': 0.08,    # 8% daily volatility (AI token)
            'RNDR': 0.06,   # 6% daily volatility (AI/GPU)
            'SUI': 0.07,    # 7% daily volatility (L1)
            # Shadow Stack
            'BONK': 0.08,   # 8% daily volatility
            'WIF': 0.10,    # 10% daily volatility
            'STMX': 0.12,   # 12% daily volatility
            'MASK': 0.07,   # 7% daily volatility (Tier 1)
            'TRUMP': 0.15,  # 15% daily volatility (News Driven)
            'ARB': 0.05,    # 5% daily volatility (Steady)
            'QNT': 0.04,    # 4% daily volatility (Vault)
        }
        
        # Initialize base prices (updated 2025-12-29)
        self.base_prices = {
            # Core Holdings
            'BTCUSDT': 94000.0,
            'ETHUSDT': 3350.0,
            'SOLUSDT': 189.0,
            'XRPUSDT': 2.10,
            # AI Basket (Coinbase Active Positions)
            'FETUSDT': 1.30,
            'RENDERUSDT': 7.10,
            'SUIUSDT': 4.20,
            # Shadow Stack
            'BONKUSDT': 0.00003,
            'WIFUSDT': 1.85,
            'STMXUSDT': 0.006,
            'MASKUSDT': 2.90,
            'TRUMPUSDT': 32.0,
            'ARBUSDT': 0.75,
            'QNTUSDT': 105.00
        }
        
        # Initialize current prices
        for symbol, price in self.base_prices.items():
            self.current_prices[symbol] = price
    
    def get_volatility(self, symbol: str) -> float:
        """Get volatility for symbol"""
        for key, vol in self.volatility_profiles.items():
            if key in symbol:
                return vol
        return 0.05  # Default 5% volatility
    
    def simulate_price_movement(self, symbol: str, time_delta_minutes: int = 1) -> MarketData:
        """Simulate realistic price movement"""
        current_price = self.current_prices.get(symbol, 100.0)
        volatility = self.get_volatility(symbol)
        
        # Geometric Brownian Motion for price simulation
        dt = time_delta_minutes / (24 * 60)  # Convert to fraction of day
        drift = 0.0  # Neutral drift
        
        # Random walk with volatility
        random_factor = np.random.normal(0, 1)
        price_change = current_price * (drift * dt + volatility * np.sqrt(dt) * random_factor)
        
        new_price = max(current_price + price_change, 0.00001)  # Prevent negative prices
        self.current_prices[symbol] = new_price
        
        # Calculate bid/ask spread (0.1% typical)
        spread = new_price * 0.001
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        # Simulate volume (random but realistic)
        base_volume = 1000000
        volume_multiplier = 0.5 + random.random()  # 0.5x to 1.5x base volume
        volume = base_volume * volume_multiplier
        
        market_data = MarketData(
            timestamp=datetime.utcnow(),
            symbol=symbol,
            price=new_price,
            volume=volume,
            bid=bid,
            ask=ask,
            volatility=volatility
        )
        
        # Store in history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(market_data)
        
        # Keep only last 1000 data points
        if len(self.price_history[symbol]) > 1000:
            self.price_history[symbol] = self.price_history[symbol][-1000:]
        
        return market_data
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        return self.current_prices.get(symbol, 100.0)
    
    def get_price_history(self, symbol: str, hours: int = 24) -> List[MarketData]:
        """Get price history for symbol"""
        if symbol not in self.price_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [data for data in self.price_history[symbol] if data.timestamp >= cutoff_time]

class PaperTradingEngine:
    """Advanced paper trading simulation engine"""
    
    def __init__(self):
        self.market_simulator = MarketSimulator()
        self.active_positions: Dict[str, Position] = {}
        self.active_ladders: Dict[str, List[LadderLevel]] = {}
        self.paper_balance = 10000.0  # Starting balance
        self.total_pnl = 0.0
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        
        # Simulation settings
        self.slippage_factor = 0.001  # 0.1% slippage
        self.fee_rate = 0.001  # 0.1% trading fee
        self.partial_fill_probability = 0.15  # 15% chance of partial fill
        self.fill_delay_seconds = (1, 5)  # Random delay between 1-5 seconds
        
        # Risk management
        self.max_position_size = 1000.0
        self.max_concurrent_positions = 5
        
    async def process_signal(self, signal: TradingSignal) -> Dict[str, Any]:
        """Process trading signal with ladder execution"""
        try:
            logger.info(f"Processing signal {signal.signal_id} for {signal.symbol}")
            
            # Validate signal
            if not self._validate_signal(signal):
                return {'success': False, 'error': 'Signal validation failed'}
            
            # Create ladder levels
            ladder_levels = self._create_ladder_levels(signal)
            if not ladder_levels:
                return {'success': False, 'error': 'Failed to create ladder levels'}
            
            # Store ladder
            self.active_ladders[signal.signal_id] = ladder_levels
            
            # Execute entry order
            entry_result = await self._execute_entry_order(signal, ladder_levels[0])
            if not entry_result['success']:
                return entry_result
            
            # Set up TP/SL orders
            await self._setup_exit_orders(signal, ladder_levels)
            
            # Log execution
            self._log_execution(signal.id, 'ladder_created', 
                              f"Created {len(ladder_levels)} ladder levels")
            
            return {
                'success': True,
                'signal_id': signal.signal_id,
                'ladder_levels': len(ladder_levels),
                'entry_price': entry_result.get('fill_price'),
                'message': 'Ladder execution initiated'
            }
            
        except Exception as e:
            logger.error(f"Failed to process signal {signal.signal_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal for paper trading"""
        # Check if we have too many positions
        if len(self.active_positions) >= self.max_concurrent_positions:
            logger.warning(f"Max concurrent positions ({self.max_concurrent_positions}) reached")
            return False
        
        # Check position size
        position_value = signal.quantity * signal.entry_price
        if position_value > self.max_position_size:
            logger.warning(f"Position size ${position_value:.2f} exceeds max ${self.max_position_size}")
            return False
        
        # Check available balance
        if position_value > self.paper_balance * 0.9:  # Use max 90% of balance
            logger.warning(f"Insufficient balance for position ${position_value:.2f}")
            return False
        
        return True
    
    def _create_ladder_levels(self, signal: TradingSignal) -> List[LadderLevel]:
        """Create ladder levels from signal"""
        levels = []
        
        # Entry level
        entry_level = LadderLevel(
            level=0,
            price=signal.entry_price,
            quantity=signal.quantity,
            order_type='entry'
        )
        levels.append(entry_level)
        
        # TP1 level
        if signal.tp1_price:
            tp1_quantity = signal.tp1_quantity or (signal.quantity * 0.5)  # Default 50%
            tp1_level = LadderLevel(
                level=1,
                price=signal.tp1_price,
                quantity=tp1_quantity,
                order_type='tp1'
            )
            levels.append(tp1_level)
        
        # TP2 level
        if signal.tp2_price:
            tp2_quantity = signal.tp2_quantity or (signal.quantity * 0.5)  # Default 50%
            tp2_level = LadderLevel(
                level=2,
                price=signal.tp2_price,
                quantity=tp2_quantity,
                order_type='tp2'
            )
            levels.append(tp2_level)
        
        # Stop Loss level
        if signal.sl_price:
            sl_level = LadderLevel(
                level=-1,
                price=signal.sl_price,
                quantity=signal.quantity,  # Full position
                order_type='sl'
            )
            levels.append(sl_level)
        
        return levels
    
    async def _execute_entry_order(self, signal: TradingSignal, entry_level: LadderLevel) -> Dict[str, Any]:
        """Execute entry order with realistic simulation"""
        try:
            # Simulate market data
            market_data = self.market_simulator.simulate_price_movement(signal.symbol)
            
            # Simulate order fill
            fill_result = await self._simulate_order_fill(
                signal.symbol,
                signal.action,
                entry_level.quantity,
                entry_level.price,
                'market' if not entry_level.price else 'limit'
            )
            
            if fill_result.filled_quantity > 0:
                # Create position
                position = Position(
                    signal_id=signal.id,
                    user_id=1,  # Default user
                    symbol=signal.symbol,
                    side='long' if signal.action == 'buy' else 'short',
                    quantity=fill_result.filled_quantity,
                    entry_price=fill_result.filled_price,
                    current_price=market_data.price,
                    entry_order_id=fill_result.order_id,
                    status='open',
                    filled_quantity=fill_result.filled_quantity,
                    remaining_quantity=entry_level.quantity - fill_result.filled_quantity,
                    fees_paid=fill_result.fees
                )
                
                # Store position
                self.active_positions[signal.signal_id] = position
                
                # Update balance
                self.paper_balance -= (fill_result.filled_quantity * fill_result.filled_price + fill_result.fees)
                
                # Update ladder level
                entry_level.status = 'filled'
                entry_level.order_id = fill_result.order_id
                entry_level.filled_at = fill_result.fill_time
                
                self._log_execution(signal.id, 'entry_filled', 
                                  f"Entry filled: {fill_result.filled_quantity} @ ${fill_result.filled_price:.4f}")
                
                return {
                    'success': True,
                    'fill_price': fill_result.filled_price,
                    'filled_quantity': fill_result.filled_quantity,
                    'fees': fill_result.fees
                }
            else:
                return {'success': False, 'error': 'Order not filled'}
                
        except Exception as e:
            logger.error(f"Entry order execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _simulate_order_fill(self, symbol: str, side: str, quantity: float, 
                                 price: Optional[float], order_type: str) -> OrderFill:
        """Simulate realistic order fill"""
        # Get current market data
        market_data = self.market_simulator.simulate_price_movement(symbol)
        
        # Determine fill price
        if order_type == 'market':
            # Market order - use bid/ask with slippage
            if side == 'buy':
                fill_price = market_data.ask * (1 + self.slippage_factor)
            else:
                fill_price = market_data.bid * (1 - self.slippage_factor)
        else:
            # Limit order - check if price is reachable
            if side == 'buy' and price >= market_data.ask:
                fill_price = min(price, market_data.ask)
            elif side == 'sell' and price <= market_data.bid:
                fill_price = max(price, market_data.bid)
            else:
                # Order not fillable at current price
                fill_price = price
                quantity = 0
        
        # Simulate partial fills
        filled_quantity = quantity
        if random.random() < self.partial_fill_probability and quantity > 0:
            filled_quantity = quantity * (0.7 + 0.3 * random.random())  # 70-100% fill
        
        # Calculate fees
        fees = filled_quantity * fill_price * self.fee_rate
        
        # Calculate slippage
        expected_price = price or market_data.price
        slippage = abs(fill_price - expected_price) / expected_price if expected_price > 0 else 0
        
        # Simulate fill delay
        await asyncio.sleep(random.uniform(*self.fill_delay_seconds))
        
        order_id = f"paper_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return OrderFill(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price or fill_price,
            filled_quantity=filled_quantity,
            filled_price=fill_price,
            fees=fees,
            slippage=slippage,
            fill_time=datetime.utcnow(),
            partial_fill=filled_quantity < quantity
        )
    
    async def _setup_exit_orders(self, signal: TradingSignal, ladder_levels: List[LadderLevel]):
        """Set up TP and SL orders"""
        for level in ladder_levels:
            if level.order_type in ['tp1', 'tp2', 'sl']:
                level.order_id = f"exit_{int(time.time())}_{level.level}"
                level.status = 'pending'
                
                self._log_execution(signal.id, f'{level.order_type}_placed', 
                                  f"{level.order_type.upper()} order placed @ ${level.price:.4f}")
    
    async def monitor_positions(self):
        """Monitor active positions and execute ladder logic"""
        while True:
            try:
                for signal_id, position in list(self.active_positions.items()):
                    await self._monitor_position(signal_id, position)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Position monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_position(self, signal_id: str, position: Position):
        """Monitor individual position for TP/SL triggers"""
        try:
            # Get current market price
            market_data = self.market_simulator.simulate_price_movement(position.symbol)
            position.current_price = market_data.price
            
            # Update unrealized PnL
            position.calculate_pnl(market_data.price)
            
            # Check ladder levels
            if signal_id in self.active_ladders:
                ladder_levels = self.active_ladders[signal_id]
                
                for level in ladder_levels:
                    if level.status == 'pending':
                        await self._check_level_trigger(signal_id, position, level, market_data)
            
        except Exception as e:
            logger.error(f"Position monitoring failed for {signal_id}: {e}")
    
    async def _check_level_trigger(self, signal_id: str, position: Position, 
                                 level: LadderLevel, market_data: MarketData):
        """Check if ladder level should be triggered"""
        triggered = False
        
        if level.order_type == 'tp1' or level.order_type == 'tp2':
            # Take profit trigger
            if position.side == 'long' and market_data.price >= level.price:
                triggered = True
            elif position.side == 'short' and market_data.price <= level.price:
                triggered = True
        
        elif level.order_type == 'sl':
            # Stop loss trigger
            if position.side == 'long' and market_data.price <= level.price:
                triggered = True
            elif position.side == 'short' and market_data.price >= level.price:
                triggered = True
        
        if triggered:
            await self._execute_exit_order(signal_id, position, level, market_data)
    
    async def _execute_exit_order(self, signal_id: str, position: Position, 
                                level: LadderLevel, market_data: MarketData):
        """Execute exit order (TP/SL)"""
        try:
            # Simulate exit order fill
            exit_side = 'sell' if position.side == 'long' else 'buy'
            
            fill_result = await self._simulate_order_fill(
                position.symbol,
                exit_side,
                level.quantity,
                level.price,
                'market'  # Exit orders are typically market orders
            )
            
            if fill_result.filled_quantity > 0:
                # Calculate realized PnL
                if position.side == 'long':
                    pnl = (fill_result.filled_price - position.entry_price) * fill_result.filled_quantity
                else:
                    pnl = (position.entry_price - fill_result.filled_price) * fill_result.filled_quantity
                
                pnl -= fill_result.fees  # Subtract fees
                
                # Update position
                position.filled_quantity -= fill_result.filled_quantity
                position.remaining_quantity = max(0, position.remaining_quantity - fill_result.filled_quantity)
                position.realized_pnl += pnl
                position.fees_paid += fill_result.fees
                
                # Update balance
                self.paper_balance += (fill_result.filled_quantity * fill_result.filled_price - fill_result.fees)
                self.total_pnl += pnl
                
                # Update ladder level
                level.status = 'filled'
                level.filled_at = fill_result.fill_time
                
                # Update trade statistics
                if pnl > 0:
                    self.win_count += 1
                else:
                    self.loss_count += 1
                
                self.trade_count += 1
                
                # Log execution
                self._log_execution(position.signal_id, f'{level.order_type}_filled', 
                                  f"{level.order_type.upper()} filled: {fill_result.filled_quantity} @ ${fill_result.filled_price:.4f}, PnL: ${pnl:.2f}")
                
                # Check if position is fully closed
                if position.remaining_quantity <= 0.001:  # Account for rounding
                    position.status = 'closed'
                    position.closed_at = datetime.utcnow()
                    
                    # Remove from active positions
                    if signal_id in self.active_positions:
                        del self.active_positions[signal_id]
                    
                    # Remove ladder
                    if signal_id in self.active_ladders:
                        del self.active_ladders[signal_id]
                    
                    self._log_execution(position.signal_id, 'position_closed', 
                                      f"Position closed. Total PnL: ${position.realized_pnl:.2f}")
                
                # Vault siphon logic
                if pnl > 0:
                    await self._process_vault_siphon(signal_id, pnl)
                
        except Exception as e:
            logger.error(f"Exit order execution failed: {e}")
    
    async def _process_vault_siphon(self, signal_id: str, profit: float):
        """Process vault siphon for profitable trades"""
        try:
            # Get signal to check vault siphon settings
            signal = TradingSignal.query.filter_by(signal_id=signal_id).first()
            if not signal or not signal.vault_siphon_enabled:
                return
            
            risk_config = config_manager.get_risk_config()
            
            if profit >= risk_config.vault_siphon_threshold:
                siphon_amount = profit * (signal.vault_siphon_percentage / 100.0)
                
                # Simulate vault transfer
                self.paper_balance -= siphon_amount
                
                self._log_execution(signal.id, 'vault_siphon', 
                                  f"Vault siphon: ${siphon_amount:.2f} ({signal.vault_siphon_percentage}% of ${profit:.2f})")
                
                logger.info(f"Vault siphon executed: ${siphon_amount:.2f} from signal {signal_id}")
        
        except Exception as e:
            logger.error(f"Vault siphon processing failed: {e}")
    
    def _log_execution(self, signal_id: int, action: str, message: str):
        """Log execution event"""
        try:
            log_entry = ExecutionLog(
                signal_id=signal_id,
                action=action,
                message=message,
                execution_time_ms=0
            )
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get paper trading performance statistics"""
        win_rate = (self.win_count / self.trade_count * 100) if self.trade_count > 0 else 0
        
        return {
            'paper_balance': self.paper_balance,
            'total_pnl': self.total_pnl,
            'trade_count': self.trade_count,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': round(win_rate, 2),
            'active_positions': len(self.active_positions),
            'active_ladders': len(self.active_ladders),
            'roi_percentage': round((self.total_pnl / 10000.0) * 100, 2)  # Assuming 10k starting balance
        }
    
    def get_position_summary(self) -> List[Dict[str, Any]]:
        """Get summary of active positions"""
        positions = []
        
        for signal_id, position in self.active_positions.items():
            # Get current market price
            current_price = self.market_simulator.get_current_price(position.symbol)
            unrealized_pnl = position.calculate_pnl(current_price)
            
            positions.append({
                'signal_id': signal_id,
                'symbol': position.symbol,
                'side': position.side,
                'quantity': position.quantity,
                'entry_price': position.entry_price,
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl,
                'realized_pnl': position.realized_pnl,
                'status': position.status,
                'opened_at': position.opened_at.isoformat() if position.opened_at else None
            })
        
        return positions

# Global paper trading engine instance
paper_trading_engine = PaperTradingEngine()


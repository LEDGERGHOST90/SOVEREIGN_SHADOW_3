#!/usr/bin/env python3
"""
📝 PAPER EXECUTION ENGINE - SOVEREIGNSHADOW.AI
Realistic paper trading execution with latency and slippage
"""

import time
import random
import json
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("paper_execution")

@dataclass
class PaperOrder:
    order_id: str
    symbol: str
    side: str  # BUY/SELL
    size: float
    price: float
    order_type: str
    timestamp: datetime
    status: str  # PENDING/FILLED/CANCELLED/REJECTED
    fill_price: float = None
    fees: float = 0.0
    latency_ms: float = 0.0
    slippage_pct: float = 0.0
    exchange: str = "paper"

class PaperExecutionEngine:
    """Realistic paper trading execution with latency and slippage"""
    
    def __init__(self, data_feed, config):
        self.data_feed = data_feed
        self.config = config
        self.orders = {}
        self.positions = {}
        self.balance = config['trading_config']['starting_balance']
        self.trade_history = []
        self.order_counter = 0
        
        # Execution parameters
        self.latency_range = config['execution']['latency_range']
        self.slippage_range = config['execution']['slippage_range']
        self.success_rate = config['execution']['success_rate']
        
        # Risk management
        self.max_position_size = config['trading_config']['max_position_size']
        self.daily_trades = 0
        self.daily_trade_limit = config['trading_config']['max_daily_trades']
        
        logger.info(f"📝 Paper Execution Engine initialized with ${self.balance:,.2f} balance")
    
    def place_order(self, symbol: str, side: str, size: float, 
                   order_type: str = "MARKET", exchange: str = "binance") -> str:
        """Place paper trading order with realistic execution"""
        
        # Check daily trade limit
        if self.daily_trades >= self.daily_trade_limit:
            logger.warning(f"⚠️ Daily trade limit reached ({self.daily_trade_limit})")
            return None
        
        # Validate position size
        current_price = self.data_feed.get_current_price(symbol, exchange)
        position_value = size * current_price
        max_position_value = self.balance * self.max_position_size
        
        if position_value > max_position_value:
            logger.warning(f"⚠️ Position size too large: ${position_value:,.2f} > ${max_position_value:,.2f}")
            return None
        
        # Generate order ID
        self.order_counter += 1
        order_id = f"PAPER_{self.order_counter}_{int(time.time() * 1000)}"
        
        # Create order
        order = PaperOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            size=size,
            price=current_price,
            order_type=order_type,
            timestamp=datetime.now(),
            status="PENDING",
            exchange=exchange
        )
        
        self.orders[order_id] = order
        
        # Increment daily trade counter
        self.daily_trades += 1
        
        logger.info(f"📝 Paper order placed: {side} {size} {symbol} @ ${current_price:.2f} (Order: {order_id})")
        
        # Simulate realistic execution delay
        threading.Thread(target=self._execute_order, args=(order_id,), daemon=True).start()
        
        return order_id
    
    def _execute_order(self, order_id: str):
        """Execute order with realistic conditions"""
        order = self.orders[order_id]
        
        try:
            # Simulate network latency (50-200ms)
            latency = random.uniform(self.latency_range[0], self.latency_range[1])
            time.sleep(latency)
            
            # Get current price (may have moved during latency)
            current_price = self.data_feed.get_current_price(order.symbol, order.exchange)
            
            # Simulate execution failure (2% chance based on success_rate)
            if random.random() > self.success_rate:
                order.status = "REJECTED"
                logger.warning(f"❌ Order rejected: {order_id}")
                return
            
            # Simulate slippage
            slippage_pct = random.uniform(self.slippage_range[0], self.slippage_range[1])
            
            if order.side == "BUY":
                fill_price = current_price * (1 + slippage_pct)
                # Check if we have enough balance
                total_cost = order.size * fill_price
                if total_cost > self.balance:
                    order.status = "REJECTED"
                    logger.warning(f"❌ Insufficient balance for order: {order_id}")
                    return
            else:
                fill_price = current_price * (1 - slippage_pct)
                # Check if we have enough position to sell
                current_position = self.positions.get(order.symbol, 0)
                if order.size > current_position:
                    order.status = "REJECTED"
                    logger.warning(f"❌ Insufficient position for sell order: {order_id}")
                    return
            
            # Calculate fees (0.1% for most exchanges)
            fees = order.size * fill_price * 0.001
            
            # Execute the order
            order.fill_price = fill_price
            order.fees = fees
            order.latency_ms = latency * 1000
            order.slippage_pct = slippage_pct * 100
            order.status = "FILLED"
            
            # Update positions and balance
            self._update_position(order)
            
            # Log trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'order_id': order_id,
                'symbol': order.symbol,
                'side': order.side,
                'size': order.size,
                'price': order.price,
                'fill_price': fill_price,
                'fees': fees,
                'latency_ms': latency * 1000,
                'slippage_pct': slippage_pct * 100,
                'exchange': order.exchange,
                'portfolio_value': self.get_portfolio_value()
            }
            
            self.trade_history.append(trade_record)
            
            # Save to staging logs
            self._save_trade_log(trade_record)
            
            logger.info(f"✅ Order filled: {order.side} {order.size} {order.symbol} @ ${fill_price:.2f} (Fees: ${fees:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Order execution error for {order_id}: {e}")
            order.status = "REJECTED"
    
    def _update_position(self, order: PaperOrder):
        """Update paper trading positions"""
        symbol = order.symbol
        
        if symbol not in self.positions:
            self.positions[symbol] = 0.0
        
        if order.side == "BUY":
            self.positions[symbol] += order.size
            self.balance -= (order.size * order.fill_price + order.fees)
        else:
            self.positions[symbol] -= order.size
            self.balance += (order.size * order.fill_price - order.fees)
        
        logger.debug(f"📊 Position updated: {symbol} = {self.positions[symbol]}, Balance = ${self.balance:,.2f}")
    
    def _save_trade_log(self, trade_record: Dict):
        """Save trade to log file"""
        try:
            log_file = "environments/staging/logs/paper_trades.json"
            with open(log_file, 'a') as f:
                f.write(json.dumps(trade_record) + '\n')
        except Exception as e:
            logger.error(f"Error saving trade log: {e}")
    
    def get_portfolio_value(self) -> float:
        """Calculate current paper portfolio value"""
        total_value = self.balance
        
        for symbol, position in self.positions.items():
            if position != 0:
                current_price = self.data_feed.get_current_price(symbol)
                if current_price > 0:
                    total_value += position * current_price
        
        return total_value
    
    def get_positions(self) -> Dict[str, float]:
        """Get current positions"""
        return self.positions.copy()
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trade_history.copy()
    
    def get_order_status(self, order_id: str) -> Optional[PaperOrder]:
        """Get order status"""
        return self.orders.get(order_id)
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trade_history:
            return {"error": "No trades to analyze"}
        
        # Calculate P&L
        total_pnl = 0
        winning_trades = 0
        losing_trades = 0
        
        for trade in self.trade_history:
            if trade['side'] == 'BUY':
                # This is a buy, P&L will be realized when sold
                continue
            else:
                # This is a sell, calculate P&L
                # Find corresponding buy trade
                for buy_trade in self.trade_history:
                    if (buy_trade['side'] == 'BUY' and 
                        buy_trade['symbol'] == trade['symbol'] and
                        buy_trade['timestamp'] < trade['timestamp']):
                        
                        pnl = (trade['fill_price'] - buy_trade['fill_price']) * trade['size'] - trade['fees'] - buy_trade['fees']
                        total_pnl += pnl
                        
                        if pnl > 0:
                            winning_trades += 1
                        else:
                            losing_trades += 1
                        break
        
        total_trades = winning_trades + losing_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate daily metrics
        today = datetime.now().date()
        today_trades = [t for t in self.trade_history if datetime.fromisoformat(t['timestamp']).date() == today]
        daily_trades = len(today_trades)
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'daily_trades': daily_trades,
            'portfolio_value': self.get_portfolio_value(),
            'balance': self.balance,
            'positions': self.get_positions(),
            'daily_trade_limit': self.daily_trade_limit,
            'remaining_daily_trades': self.daily_trade_limit - self.daily_trades
        }
        
        return metrics
    
    def reset_daily_counters(self):
        """Reset daily trade counters (call at start of new day)"""
        self.daily_trades = 0
        logger.info("📅 Daily trade counters reset")
    
    def get_status(self) -> Dict:
        """Get execution engine status"""
        return {
            'engine_status': 'RUNNING',
            'balance': self.balance,
            'portfolio_value': self.get_portfolio_value(),
            'daily_trades': self.daily_trades,
            'daily_trade_limit': self.daily_trade_limit,
            'open_orders': len([o for o in self.orders.values() if o.status == 'PENDING']),
            'total_orders': len(self.orders),
            'positions': self.get_positions(),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Test the paper execution engine"""
    import yaml
    
    # Load config
    with open('environments/staging/config_staging.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Mock data feed for testing
    class MockDataFeed:
        def get_current_price(self, symbol, exchange=None):
            prices = {'BTCUSDT': 45000, 'ETHUSDT': 3200, 'ADAUSDT': 0.45}
            return prices.get(symbol, 100)
    
    # Create execution engine
    feed = MockDataFeed()
    engine = PaperExecutionEngine(feed, config)
    
    # Test orders
    print("🧪 Testing Paper Execution Engine")
    print("=" * 40)
    
    # Place test orders
    order1 = engine.place_order('BTCUSDT', 'BUY', 0.01)
    order2 = engine.place_order('ETHUSDT', 'BUY', 0.1)
    
    # Wait for execution
    time.sleep(2)
    
    # Check status
    status = engine.get_status()
    print(f"Portfolio Value: ${status['portfolio_value']:,.2f}")
    print(f"Balance: ${status['balance']:,.2f}")
    print(f"Positions: {status['positions']}")
    
    # Get performance metrics
    metrics = engine.get_performance_metrics()
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.1%}")

if __name__ == "__main__":
    main()

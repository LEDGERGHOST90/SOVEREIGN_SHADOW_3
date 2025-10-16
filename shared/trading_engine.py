#!/usr/bin/env python3
"""
🏗️ SHARED TRADING ENGINE - SOVEREIGNSHADOW.AI
Core trading logic shared across all environments
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trading_engine")

@dataclass
class TradeSignal:
    """Trade signal data structure"""
    currency: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread: float
    quantity: float
    expected_profit: float
    confidence: float
    timestamp: datetime

@dataclass
class TradeExecution:
    """Trade execution result"""
    signal: TradeSignal
    execution_price: float
    actual_profit: float
    fees: float
    slippage: float
    execution_time: float
    status: str
    error_message: Optional[str] = None

class ExchangeInterface(ABC):
    """Abstract base class for exchange interfaces"""
    
    @abstractmethod
    def get_market_price(self, pair: str) -> float:
        """Get current market price for a trading pair"""
        pass
    
    @abstractmethod
    def execute_buy_order(self, pair: str, quantity: float) -> TradeExecution:
        """Execute a buy order"""
        pass
    
    @abstractmethod
    def execute_sell_order(self, pair: str, quantity: float) -> TradeExecution:
        """Execute a sell order"""
        pass
    
    @abstractmethod
    def get_balance(self, currency: str) -> float:
        """Get account balance for a currency"""
        pass

class ArbitrageDetector:
    """Detects arbitrage opportunities across exchanges"""
    
    def __init__(self, exchanges: Dict[str, ExchangeInterface], config: Dict):
        self.exchanges = exchanges
        self.config = config
        self.min_spread_threshold = config.get('min_spread_threshold', 0.002)
        self.supported_pairs = config.get('supported_pairs', [])
    
    def detect_opportunities(self) -> List[TradeSignal]:
        """Detect arbitrage opportunities"""
        opportunities = []
        
        for pair in self.supported_pairs:
            prices = {}
            
            # Get prices from all exchanges
            for exchange_id, exchange in self.exchanges.items():
                try:
                    price = exchange.get_market_price(pair)
                    prices[exchange_id] = price
                except Exception as e:
                    logger.warning(f"Failed to get price from {exchange_id}: {e}")
                    continue
            
            if len(prices) < 2:
                continue
            
            # Find arbitrage opportunity
            opportunity = self._find_arbitrage(pair, prices)
            if opportunity:
                opportunities.append(opportunity)
        
        return opportunities
    
    def _find_arbitrage(self, pair: str, prices: Dict[str, float]) -> Optional[TradeSignal]:
        """Find arbitrage opportunity for a specific pair"""
        if len(prices) < 2:
            return None
        
        # Find highest and lowest prices
        max_exchange = max(prices, key=prices.get)
        min_exchange = min(prices, key=prices.get)
        max_price = prices[max_exchange]
        min_price = prices[min_exchange]
        
        # Calculate spread
        spread = (max_price - min_price) / min_price
        
        if spread < self.min_spread_threshold:
            return None
        
        # Calculate trade parameters
        currency = pair.replace('USDT', '').replace('USD', '').replace('-', '')
        quantity = self._calculate_position_size(currency, min_price)
        expected_profit = (max_price - min_price) * quantity
        confidence = self._calculate_confidence(spread, max_price, min_price)
        
        return TradeSignal(
            currency=currency,
            buy_exchange=min_exchange,
            sell_exchange=max_exchange,
            buy_price=min_price,
            sell_price=max_price,
            spread=spread,
            quantity=quantity,
            expected_profit=expected_profit,
            confidence=confidence,
            timestamp=datetime.now()
        )
    
    def _calculate_position_size(self, currency: str, price: float) -> float:
        """Calculate position size based on risk management"""
        max_position_value = self.config.get('starting_balance', 1000) * self.config.get('max_position_size', 0.02)
        return max_position_value / price
    
    def _calculate_confidence(self, spread: float, max_price: float, min_price: float) -> float:
        """Calculate confidence score for the arbitrage opportunity"""
        # Higher spread = higher confidence
        # More stable prices = higher confidence
        price_stability = 1.0 - abs(max_price - min_price) / ((max_price + min_price) / 2)
        return min(0.95, spread * 10 + price_stability * 0.5)

class RiskManager:
    """Risk management system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.max_daily_trades = config.get('max_daily_trades', 10)
        self.daily_loss_limit = config.get('daily_loss_limit', 0.02)
        self.stop_loss = config.get('stop_loss', 0.02)
        self.take_profit = config.get('take_profit', 0.01)
    
    def can_execute_trade(self, signal: TradeSignal) -> Tuple[bool, str]:
        """Check if trade can be executed based on risk limits"""
        
        # Check daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            return False, "Daily trade limit reached"
        
        # Check daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit * self.config.get('starting_balance', 1000):
            return False, "Daily loss limit reached"
        
        # Check consecutive losses
        if self.consecutive_losses >= 3:
            return False, "Consecutive loss limit reached"
        
        # Check position size
        position_value = signal.quantity * signal.buy_price
        max_position_value = self.config.get('starting_balance', 1000) * self.config.get('max_position_size', 0.02)
        
        if position_value > max_position_value:
            return False, "Position size exceeds limit"
        
        # Check minimum spread
        if signal.spread < self.config.get('min_spread_threshold', 0.002):
            return False, "Spread below minimum threshold"
        
        return True, "Trade approved"
    
    def update_trade_result(self, execution: TradeExecution):
        """Update risk metrics after trade execution"""
        self.daily_trades += 1
        self.daily_pnl += execution.actual_profit
        
        if execution.actual_profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
    
    def should_stop_trading(self) -> Tuple[bool, str]:
        """Check if trading should be stopped"""
        
        if self.daily_pnl <= -self.daily_loss_limit * self.config.get('starting_balance', 1000):
            return True, "Daily loss limit exceeded"
        
        if self.consecutive_losses >= 3:
            return True, "Too many consecutive losses"
        
        return False, "Trading can continue"

class TradingEngine:
    """Main trading engine that orchestrates all components"""
    
    def __init__(self, config: Dict, exchanges: Dict[str, ExchangeInterface]):
        self.config = config
        self.exchanges = exchanges
        self.arbitrage_detector = ArbitrageDetector(exchanges, config)
        self.risk_manager = RiskManager(config)
        self.trade_history = []
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
    
    def start(self):
        """Start the trading engine"""
        logger.info("🚀 Starting Trading Engine")
        self.is_running = True
        
        while self.is_running:
            try:
                # Check if trading should continue
                should_stop, reason = self.risk_manager.should_stop_trading()
                if should_stop:
                    logger.warning(f"🛑 Trading stopped: {reason}")
                    break
                
                # Detect arbitrage opportunities
                opportunities = self.arbitrage_detector.detect_opportunities()
                
                # Execute trades for good opportunities
                for opportunity in opportunities[:2]:  # Limit to 2 trades per cycle
                    self._execute_opportunity(opportunity)
                
                # Update metrics
                self._update_metrics()
                
                # Wait before next cycle
                time.sleep(self.config.get('scan_interval', 60))
                
            except KeyboardInterrupt:
                logger.info("🛑 Trading engine stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Trading engine error: {e}")
                time.sleep(30)  # Wait before retrying
    
    def _execute_opportunity(self, signal: TradeSignal):
        """Execute an arbitrage opportunity"""
        
        # Check risk management
        can_trade, reason = self.risk_manager.can_execute_trade(signal)
        if not can_trade:
            logger.warning(f"❌ Trade rejected: {reason}")
            return
        
        try:
            # Execute buy order
            buy_exchange = self.exchanges[signal.buy_exchange]
            buy_execution = buy_exchange.execute_buy_order(f"{signal.currency}USDT", signal.quantity)
            
            if buy_execution.status != "success":
                logger.error(f"❌ Buy order failed: {buy_execution.error_message}")
                return
            
            # Execute sell order
            sell_exchange = self.exchanges[signal.sell_exchange]
            sell_execution = sell_exchange.execute_sell_order(f"{signal.currency}USDT", signal.quantity)
            
            if sell_execution.status != "success":
                logger.error(f"❌ Sell order failed: {sell_execution.error_message}")
                return
            
            # Calculate actual profit
            actual_profit = sell_execution.actual_profit - buy_execution.fees - sell_execution.fees
            
            # Update risk manager
            self.risk_manager.update_trade_result(sell_execution)
            
            # Record trade
            self.trade_history.append({
                'signal': signal,
                'buy_execution': buy_execution,
                'sell_execution': sell_execution,
                'actual_profit': actual_profit,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Trade executed: {signal.currency} - Profit: ${actual_profit:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
    
    def _update_metrics(self):
        """Update performance metrics"""
        if not self.trade_history:
            return
        
        successful_trades = [t for t in self.trade_history if t['actual_profit'] > 0]
        self.metrics['total_trades'] = len(self.trade_history)
        self.metrics['successful_trades'] = len(successful_trades)
        self.metrics['total_profit'] = sum(t['actual_profit'] for t in self.trade_history)
        
        if self.metrics['total_trades'] > 0:
            self.metrics['win_rate'] = self.metrics['successful_trades'] / self.metrics['total_trades']
    
    def stop(self):
        """Stop the trading engine"""
        logger.info("🛑 Stopping Trading Engine")
        self.is_running = False
    
    def get_performance_summary(self) -> Dict:
        """Get current performance summary"""
        return {
            'metrics': self.metrics,
            'risk_status': {
                'daily_pnl': self.risk_manager.daily_pnl,
                'daily_trades': self.risk_manager.daily_trades,
                'consecutive_losses': self.risk_manager.consecutive_losses
            },
            'trade_history': self.trade_history[-10:],  # Last 10 trades
            'timestamp': datetime.now().isoformat()
        }

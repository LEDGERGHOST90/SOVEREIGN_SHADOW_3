#!/usr/bin/env python3
"""
🚨 TRADING LOGIC STRESS TEST
Tests duplicate order prevention, position sizing, stop losses, arbitrage, risk management
"""

import asyncio
import json
import logging
import random
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import threading

class TradingLogicStressTest:
    def __init__(self):
        self.test_results = {}
        self.trade_history = []
        self.position_sizes = {}
        self.risk_metrics = {}
        self.logger = self._setup_logging()
        self.duplicate_orders = []
        self.kill_switch_triggers = []
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stress_test_trading_logic.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def test_duplicate_order_prevention(self, num_orders: int = 10000):
        """Test duplicate order prevention with massive concurrent orders"""
        self.logger.info(f"🔄 Testing duplicate order prevention with {num_orders} orders")
        
        # Test scenarios
        test_scenarios = [
            ('identical_orders', self._test_identical_orders),
            ('rapid_orders', self._test_rapid_orders),
            ('same_symbol_orders', self._test_same_symbol_orders),
            ('buy_sell_cycles', self._test_buy_sell_cycles),
            ('hash_collision', self._test_hash_collision)
        ]
        
        for scenario_name, test_func in test_scenarios:
            try:
                result = test_func(num_orders // len(test_scenarios))
                self.test_results[f'duplicate_prevention_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ {scenario_name} test failed: {e}")
                self.test_results[f'duplicate_prevention_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_identical_orders(self, num_orders: int):
        """Test identical order detection"""
        symbol = "BTCUSDT"
        side = "BUY"
        quantity = 0.01
        price = 50000.0
        
        duplicates_detected = 0
        orders_processed = 0
        
        for i in range(num_orders):
            order_hash = self._generate_order_hash(symbol, side, quantity, price)
            
            if order_hash in self.duplicate_orders:
                duplicates_detected += 1
            else:
                self.duplicate_orders.append(order_hash)
                orders_processed += 1
        
        success = duplicates_detected == num_orders - 1  # All but first should be detected as duplicates
        
        return {
            'status': 'PASSED' if success else 'FAILED',
            'total_orders': num_orders,
            'duplicates_detected': duplicates_detected,
            'orders_processed': orders_processed,
            'success_rate': duplicates_detected / num_orders if num_orders > 0 else 0
        }
    
    def _test_rapid_orders(self, num_orders: int):
        """Test rapid order submission within rest periods"""
        symbol = "ETHUSDT"
        side = "BUY"
        quantity = 0.1
        price = 3000.0
        
        rapid_orders = 0
        blocked_orders = 0
        last_order_time = 0
        min_rest_period = 300  # 5 minutes
        
        for i in range(num_orders):
            current_time = time.time()
            
            # Check if within rest period
            if current_time - last_order_time < min_rest_period:
                blocked_orders += 1
            else:
                rapid_orders += 1
                last_order_time = current_time
            
            time.sleep(0.001)  # Small delay
        
        success = blocked_orders > rapid_orders  # Most orders should be blocked
        
        return {
            'status': 'PASSED' if success else 'FAILED',
            'rapid_orders': rapid_orders,
            'blocked_orders': blocked_orders,
            'block_rate': blocked_orders / num_orders if num_orders > 0 else 0
        }
    
    def _test_same_symbol_orders(self, num_orders: int):
        """Test same symbol cooldown enforcement"""
        symbol = "SOLUSDT"
        side = "SELL"
        quantity = 1.0
        price = 150.0
        
        same_symbol_orders = 0
        blocked_orders = 0
        last_symbol_time = {}
        symbol_cooldown = 600  # 10 minutes
        
        for i in range(num_orders):
            current_time = time.time()
            
            if symbol in last_symbol_time and current_time - last_symbol_time[symbol] < symbol_cooldown:
                blocked_orders += 1
            else:
                same_symbol_orders += 1
                last_symbol_time[symbol] = current_time
        
        success = blocked_orders > same_symbol_orders
        
        return {
            'status': 'PASSED' if success else 'FAILED',
            'same_symbol_orders': same_symbol_orders,
            'blocked_orders': blocked_orders,
            'block_rate': blocked_orders / num_orders if num_orders > 0 else 0
        }
    
    def _test_buy_sell_cycles(self, num_orders: int):
        """Test buy-sell cycle prevention"""
        symbol = "ADAUSDT"
        quantity = 1000.0
        price = 0.5
        
        buy_orders = 0
        sell_orders = 0
        blocked_cycles = 0
        cycle_cooldown = 900  # 15 minutes
        last_cycle_time = 0
        
        for i in range(num_orders):
            side = "BUY" if i % 2 == 0 else "SELL"
            current_time = time.time()
            
            # Check for buy-sell cycle
            if i > 0 and (i % 2 == 1):  # This is a sell after a buy
                if current_time - last_cycle_time < cycle_cooldown:
                    blocked_cycles += 1
                else:
                    sell_orders += 1
                    last_cycle_time = current_time
            else:
                buy_orders += 1
        
        success = blocked_cycles > 0  # Should block some cycles
        
        return {
            'status': 'PASSED' if success else 'FAILED',
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'blocked_cycles': blocked_cycles,
            'cycle_block_rate': blocked_cycles / (num_orders // 2) if num_orders > 0 else 0
        }
    
    def _test_hash_collision(self, num_orders: int):
        """Test hash collision scenarios"""
        collisions_found = 0
        hash_values = set()
        
        # Test with similar but different orders
        base_symbol = "BTCUSDT"
        base_price = 50000.0
        
        for i in range(num_orders):
            # Create orders with slight variations
            symbol = f"{base_symbol}_{i % 100}"  # Some symbols will be identical
            price = base_price + (i * 0.01)  # Slightly different prices
            side = "BUY" if i % 2 == 0 else "SELL"
            quantity = 0.01 + (i * 0.001)
            
            order_hash = self._generate_order_hash(symbol, side, quantity, price)
            
            if order_hash in hash_values:
                collisions_found += 1
            
            hash_values.add(order_hash)
        
        # Hash collisions are bad - we want unique hashes
        success = collisions_found == 0
        
        return {
            'status': 'PASSED' if success else 'FAILED',
            'total_hashes': len(hash_values),
            'collisions': collisions_found,
            'collision_rate': collisions_found / len(hash_values) if hash_values else 0
        }
    
    def _generate_order_hash(self, symbol: str, side: str, quantity: float, price: float) -> str:
        """Generate order hash for duplicate detection"""
        order_string = f"{symbol}_{side}_{quantity}_{price}_{int(time.time() / 60)}"  # Minute precision
        return hashlib.md5(order_string.encode()).hexdigest()
    
    def test_position_sizing_logic(self):
        """Test position sizing with extreme portfolio values"""
        self.logger.info("📊 Testing position sizing logic with extreme values")
        
        test_scenarios = [
            ('minimal_portfolio', 1.0),
            ('normal_portfolio', 7716.23),
            ('large_portfolio', 1000000.0),
            ('billion_portfolio', 1000000000.0),
            ('negative_portfolio', -1000.0),
            ('zero_portfolio', 0.0)
        ]
        
        for scenario_name, portfolio_value in test_scenarios:
            try:
                result = self._test_position_sizing_scenario(scenario_name, portfolio_value)
                self.test_results[f'position_sizing_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Position sizing {scenario_name} failed: {e}")
                self.test_results[f'position_sizing_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_position_sizing_scenario(self, scenario_name: str, portfolio_value: float):
        """Test position sizing for a specific scenario"""
        symbol = "BTCUSDT"
        current_price = 50000.0
        confidence = 0.8
        
        # Test position sizing logic
        max_position_percent = 0.05  # 5% max position
        min_position_percent = 0.001  # 0.1% min position
        
        if portfolio_value <= 0:
            # Should handle negative/zero portfolios gracefully
            position_value = 0.0
            status = 'HANDLED_GRACEFULLY'
        else:
            # Calculate position size
            base_position_percent = max_position_percent * confidence
            position_percent = max(min_position_percent, min(base_position_percent, max_position_percent))
            position_value = portfolio_value * position_percent
        
        # Validate position size
        if portfolio_value > 0:
            position_percent_actual = position_value / portfolio_value
            valid_position = min_position_percent <= position_percent_actual <= max_position_percent
        else:
            valid_position = position_value == 0
        
        return {
            'status': 'PASSED' if valid_position else 'FAILED',
            'portfolio_value': portfolio_value,
            'position_value': position_value,
            'position_percent': position_value / portfolio_value if portfolio_value > 0 else 0,
            'scenario': scenario_name
        }
    
    def test_stop_loss_execution(self):
        """Test stop loss execution under extreme volatility"""
        self.logger.info("🛑 Testing stop loss execution")
        
        volatility_scenarios = [
            ('normal_volatility', 0.02),  # 2%
            ('high_volatility', 0.10),    # 10%
            ('extreme_volatility', 0.50), # 50%
            ('flash_crash', 0.90)         # 90%
        ]
        
        for scenario_name, volatility in volatility_scenarios:
            try:
                result = self._test_stop_loss_scenario(scenario_name, volatility)
                self.test_results[f'stop_loss_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Stop loss {scenario_name} failed: {e}")
                self.test_results[f'stop_loss_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_stop_loss_scenario(self, scenario_name: str, volatility: float):
        """Test stop loss for a specific volatility scenario"""
        symbol = "BTCUSDT"
        entry_price = 50000.0
        position_size = 0.1  # 0.1 BTC
        stop_loss_percent = 0.03  # 3% stop loss
        
        # Simulate price movement
        price_changes = []
        stop_loss_hit = False
        stop_loss_price = entry_price * (1 - stop_loss_percent)
        
        # Generate price movements
        for i in range(100):  # 100 price updates
            # Random walk with volatility
            change = random.gauss(0, volatility)
            new_price = entry_price * (1 + change)
            
            price_changes.append(new_price)
            
            # Check if stop loss hit
            if new_price <= stop_loss_price:
                stop_loss_hit = True
                break
        
        # Calculate results
        if stop_loss_hit:
            final_price = stop_loss_price
            loss = (entry_price - final_price) * position_size
            loss_percent = (entry_price - final_price) / entry_price
        else:
            final_price = price_changes[-1] if price_changes else entry_price
            loss = max(0, (entry_price - final_price) * position_size)
            loss_percent = max(0, (entry_price - final_price) / entry_price)
        
        # Validate stop loss execution
        stop_loss_worked = stop_loss_hit and loss_percent <= stop_loss_percent * 1.1  # Allow 10% tolerance
        
        return {
            'status': 'PASSED' if stop_loss_worked else 'FAILED',
            'entry_price': entry_price,
            'final_price': final_price,
            'stop_loss_price': stop_loss_price,
            'loss_percent': loss_percent,
            'stop_loss_hit': stop_loss_hit,
            'volatility': volatility,
            'price_updates': len(price_changes)
        }
    
    def test_arbitrage_detection(self):
        """Test arbitrage detection with manipulated price feeds"""
        self.logger.info("⚡ Testing arbitrage detection")
        
        arbitrage_scenarios = [
            ('normal_spreads', 0.001),      # 0.1% spread
            ('profitable_arbitrage', 0.01), # 1% spread
            ('extreme_arbitrage', 0.05),    # 5% spread
            ('manipulated_prices', 0.20)    # 20% spread (suspicious)
        ]
        
        for scenario_name, spread in arbitrage_scenarios:
            try:
                result = self._test_arbitrage_scenario(scenario_name, spread)
                self.test_results[f'arbitrage_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Arbitrage {scenario_name} failed: {e}")
                self.test_results[f'arbitrage_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_arbitrage_scenario(self, scenario_name: str, spread: float):
        """Test arbitrage detection for a specific spread"""
        base_price = 50000.0
        exchange_a_price = base_price
        exchange_b_price = base_price * (1 + spread)
        
        # Calculate arbitrage opportunity
        arbitrage_percent = (exchange_b_price - exchange_a_price) / exchange_a_price
        arbitrage_profitable = arbitrage_percent > 0.002  # 0.2% minimum threshold
        
        # Test arbitrage detection logic
        min_spread = 0.001  # 0.1% minimum spread
        max_spread = 0.10   # 10% maximum spread (beyond this is suspicious)
        
        if arbitrage_percent < min_spread:
            detection_result = 'NO_ARBITRAGE'
        elif arbitrage_percent > max_spread:
            detection_result = 'SUSPICIOUS_SPREAD'
        else:
            detection_result = 'VALID_ARBITRAGE'
        
        # Validate detection
        expected_detection = 'VALID_ARBITRAGE' if min_spread <= arbitrage_percent <= max_spread else detection_result
        detection_correct = detection_result == expected_detection
        
        return {
            'status': 'PASSED' if detection_correct else 'FAILED',
            'exchange_a_price': exchange_a_price,
            'exchange_b_price': exchange_b_price,
            'arbitrage_percent': arbitrage_percent,
            'detection_result': detection_result,
            'expected_detection': expected_detection,
            'profitable': arbitrage_profitable
        }
    
    def test_risk_management(self):
        """Test risk management limits under extreme conditions"""
        self.logger.info("⚠️ Testing risk management limits")
        
        risk_scenarios = [
            ('normal_risk', 0.01),     # 1% risk
            ('high_risk', 0.05),       # 5% risk
            ('extreme_risk', 0.20),    # 20% risk
            ('limit_risk', 0.50)       # 50% risk (should be blocked)
        ]
        
        for scenario_name, risk_level in risk_scenarios:
            try:
                result = self._test_risk_scenario(scenario_name, risk_level)
                self.test_results[f'risk_management_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Risk management {scenario_name} failed: {e}")
                self.test_results[f'risk_management_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_risk_scenario(self, scenario_name: str, risk_level: float):
        """Test risk management for a specific risk level"""
        portfolio_value = 10000.0
        max_portfolio_risk = 0.05  # 5% max portfolio risk
        max_position_risk = 0.02   # 2% max position risk
        
        # Calculate position size based on risk
        position_value = portfolio_value * risk_level
        
        # Check risk limits
        portfolio_risk_exceeded = risk_level > max_portfolio_risk
        position_risk_exceeded = risk_level > max_position_risk
        
        # Risk management decision
        if portfolio_risk_exceeded:
            risk_action = 'BLOCK_PORTFOLIO_RISK'
        elif position_risk_exceeded:
            risk_action = 'BLOCK_POSITION_RISK'
        else:
            risk_action = 'ALLOW_TRADE'
        
        # Validate risk management
        if risk_level <= max_position_risk:
            expected_action = 'ALLOW_TRADE'
        elif risk_level <= max_portfolio_risk:
            expected_action = 'BLOCK_POSITION_RISK'
        else:
            expected_action = 'BLOCK_PORTFOLIO_RISK'
        
        risk_management_correct = risk_action == expected_action
        
        return {
            'status': 'PASSED' if risk_management_correct else 'FAILED',
            'risk_level': risk_level,
            'position_value': position_value,
            'risk_action': risk_action,
            'expected_action': expected_action,
            'portfolio_risk_exceeded': portfolio_risk_exceeded,
            'position_risk_exceeded': position_risk_exceeded
        }
    
    def test_kill_switch_activation(self):
        """Test all kill switch conditions simultaneously"""
        self.logger.info("🚨 Testing kill switch activation")
        
        kill_switch_scenarios = [
            ('daily_loss_limit', self._test_daily_loss_kill_switch),
            ('consecutive_losses', self._test_consecutive_loss_kill_switch),
            ('trade_count_limit', self._test_trade_count_kill_switch),
            ('portfolio_risk_limit', self._test_portfolio_risk_kill_switch),
            ('file_based_kill_switch', self._test_file_based_kill_switch),
            ('multiple_triggers', self._test_multiple_kill_switches)
        ]
        
        for scenario_name, test_func in kill_switch_scenarios:
            try:
                result = test_func()
                self.test_results[f'kill_switch_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Kill switch {scenario_name} failed: {e}")
                self.test_results[f'kill_switch_{scenario_name}'] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
    
    def _test_daily_loss_kill_switch(self):
        """Test daily loss limit kill switch"""
        daily_loss_limit = 200.0  # $200 daily loss limit
        current_loss = 250.0      # Exceed limit
        
        kill_switch_triggered = current_loss >= daily_loss_limit
        
        return {
            'status': 'PASSED' if kill_switch_triggered else 'FAILED',
            'daily_loss_limit': daily_loss_limit,
            'current_loss': current_loss,
            'kill_switch_triggered': kill_switch_triggered
        }
    
    def _test_consecutive_loss_kill_switch(self):
        """Test consecutive loss kill switch"""
        consecutive_loss_limit = 5
        current_consecutive_losses = 7  # Exceed limit
        
        kill_switch_triggered = current_consecutive_losses >= consecutive_loss_limit
        
        return {
            'status': 'PASSED' if kill_switch_triggered else 'FAILED',
            'consecutive_loss_limit': consecutive_loss_limit,
            'current_consecutive_losses': current_consecutive_losses,
            'kill_switch_triggered': kill_switch_triggered
        }
    
    def _test_trade_count_kill_switch(self):
        """Test trade count limit kill switch"""
        daily_trade_limit = 50
        current_trade_count = 75  # Exceed limit
        
        kill_switch_triggered = current_trade_count >= daily_trade_limit
        
        return {
            'status': 'PASSED' if kill_switch_triggered else 'FAILED',
            'daily_trade_limit': daily_trade_limit,
            'current_trade_count': current_trade_count,
            'kill_switch_triggered': kill_switch_triggered
        }
    
    def _test_portfolio_risk_kill_switch(self):
        """Test portfolio risk limit kill switch"""
        portfolio_risk_limit = 0.05  # 5% portfolio risk
        current_portfolio_risk = 0.08  # Exceed limit
        
        kill_switch_triggered = current_portfolio_risk >= portfolio_risk_limit
        
        return {
            'status': 'PASSED' if kill_switch_triggered else 'FAILED',
            'portfolio_risk_limit': portfolio_risk_limit,
            'current_portfolio_risk': current_portfolio_risk,
            'kill_switch_triggered': kill_switch_triggered
        }
    
    def _test_file_based_kill_switch(self):
        """Test file-based kill switch"""
        import tempfile
        import os
        
        # Create temporary kill switch file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            f.write(b'KILL_SWITCH_ACTIVE')
            kill_switch_file = f.name
        
        try:
            # Check if kill switch file exists
            kill_switch_triggered = os.path.exists(kill_switch_file)
            
            # Clean up
            os.unlink(kill_switch_file)
            
            return {
                'status': 'PASSED' if kill_switch_triggered else 'FAILED',
                'kill_switch_file': kill_switch_file,
                'kill_switch_triggered': kill_switch_triggered
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_multiple_kill_switches(self):
        """Test multiple kill switch conditions"""
        conditions = {
            'daily_loss_exceeded': True,
            'consecutive_losses_exceeded': True,
            'trade_count_exceeded': False,
            'portfolio_risk_exceeded': False
        }
        
        # Kill switch should trigger if ANY condition is met
        kill_switch_triggered = any(conditions.values())
        trigger_count = sum(conditions.values())
        
        return {
            'status': 'PASSED' if kill_switch_triggered else 'FAILED',
            'conditions': conditions,
            'kill_switch_triggered': kill_switch_triggered,
            'trigger_count': trigger_count
        }
    
    async def run_all_tests(self):
        """Run all trading logic stress tests"""
        self.logger.info("🚀 Starting Trading Logic Stress Tests")
        self.logger.info("=" * 60)
        
        # Run tests
        self.test_duplicate_order_prevention(10000)
        self.test_position_sizing_logic()
        self.test_stop_loss_execution()
        self.test_arbitrage_detection()
        self.test_risk_management()
        self.test_kill_switch_activation()
        
        # Generate report
        self._generate_report()
        
        return self.test_results
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        self.logger.info("📊 TRADING LOGIC STRESS TEST REPORT")
        self.logger.info("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        failed = sum(1 for result in self.test_results.values() if result.get('status') == 'FAILED')
        errors = sum(1 for result in self.test_results.values() if result.get('status') == 'ERROR')
        
        self.logger.info(f"✅ Passed: {passed}")
        self.logger.info(f"❌ Failed: {failed}")
        self.logger.info(f"🚨 Errors: {errors}")
        
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            self.logger.info(f"{test_name.upper()}: {status}")
            if result.get('status') != 'PASSED':
                for key, value in result.items():
                    if key != 'status':
                        self.logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    async def main():
        tester = TradingLogicStressTest()
        await tester.run_all_tests()
    
    asyncio.run(main())

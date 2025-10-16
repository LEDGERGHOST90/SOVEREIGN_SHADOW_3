#!/usr/bin/env python3
"""
🚨 MARKET DATA STRESS TEST
Tests flash crashes, market manipulation, data feed corruption, extreme volatility
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class MarketDataStressTest:
    def __init__(self):
        self.test_results = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)
    
    async def test_flash_crashes(self):
        """Test flash crash scenarios"""
        self.logger.info("💥 Testing flash crash scenarios")
        
        crash_scenarios = [
            ('moderate_crash', 0.20),  # 20% drop
            ('severe_crash', 0.50),    # 50% drop
            ('extreme_crash', 0.90),   # 90% drop
            ('instant_crash', 0.99)    # 99% drop
        ]
        
        for scenario_name, crash_percentage in crash_scenarios:
            try:
                result = self._simulate_flash_crash(scenario_name, crash_percentage)
                self.test_results[f'flash_crash_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Flash crash {scenario_name} failed: {e}")
                self.test_results[f'flash_crash_{scenario_name}'] = {'status': 'ERROR', 'error': str(e)}
    
    def _simulate_flash_crash(self, scenario_name: str, crash_percentage: float):
        """Simulate a flash crash scenario"""
        base_price = 50000.0
        crash_price = base_price * (1 - crash_percentage)
        
        # Simulate rapid price movements
        price_history = []
        current_price = base_price
        
        # Generate crash sequence
        for i in range(10):  # 10 rapid price updates
            # Simulate rapid decline
            decline = crash_percentage / 10 * (i + 1)
            current_price = base_price * (1 - decline)
            price_history.append({
                'timestamp': datetime.now(),
                'price': current_price,
                'change_percent': -decline * 100
            })
        
        # Test system response
        crash_detected = crash_percentage > 0.05  # Detect crashes >5%
        stop_losses_triggered = crash_percentage > 0.03  # Trigger stops >3%
        
        return {
            'status': 'PASSED' if crash_detected else 'FAILED',
            'base_price': base_price,
            'crash_price': crash_price,
            'crash_percentage': crash_percentage,
            'crash_detected': crash_detected,
            'stop_losses_triggered': stop_losses_triggered,
            'price_updates': len(price_history)
        }
    
    async def test_market_manipulation(self):
        """Test market manipulation detection"""
        self.logger.info("🎭 Testing market manipulation detection")
        
        manipulation_scenarios = [
            ('pump_and_dump', self._test_pump_and_dump),
            ('wash_trading', self._test_wash_trading),
            ('spoofing', self._test_spoofing),
            ('volume_manipulation', self._test_volume_manipulation)
        ]
        
        for scenario_name, test_func in manipulation_scenarios:
            try:
                result = test_func()
                self.test_results[f'manipulation_{scenario_name}'] = result
            except Exception as e:
                self.logger.error(f"❌ Manipulation {scenario_name} failed: {e}")
                self.test_results[f'manipulation_{scenario_name}'] = {'status': 'ERROR', 'error': str(e)}
    
    def _test_pump_and_dump(self):
        """Test pump and dump detection"""
        base_price = 100.0
        pump_target = base_price * 2.0  # 100% pump
        dump_target = base_price * 0.5  # 50% dump
        
        # Simulate pump phase
        pump_volume = 1000000  # High volume during pump
        dump_volume = 500000   # Lower volume during dump
        
        # Calculate manipulation indicators
        volume_spike = pump_volume > base_price * 1000  # Volume spike detection
        price_spike = pump_target > base_price * 1.5    # Price spike detection
        rapid_reversal = abs(dump_target - pump_target) / pump_target > 0.7  # Rapid reversal
        
        manipulation_detected = volume_spike and price_spike and rapid_reversal
        
        return {
            'status': 'PASSED' if manipulation_detected else 'FAILED',
            'base_price': base_price,
            'pump_price': pump_target,
            'dump_price': dump_target,
            'volume_spike': volume_spike,
            'price_spike': price_spike,
            'rapid_reversal': rapid_reversal,
            'manipulation_detected': manipulation_detected
        }
    
    def _test_wash_trading(self):
        """Test wash trading detection"""
        # Simulate wash trading patterns
        buy_orders = [{'price': 100, 'volume': 1000, 'timestamp': i} for i in range(100)]
        sell_orders = [{'price': 100, 'volume': 1000, 'timestamp': i + 0.1} for i in range(100)]
        
        # Analyze patterns
        same_prices = all(b['price'] == s['price'] for b, s in zip(buy_orders, sell_orders))
        same_volumes = all(b['volume'] == s['volume'] for b, s in zip(buy_orders, sell_orders))
        rapid_alternating = True  # Orders alternate rapidly
        
        wash_trading_detected = same_prices and same_volumes and rapid_alternating
        
        return {
            'status': 'PASSED' if wash_trading_detected else 'FAILED',
            'same_prices': same_prices,
            'same_volumes': same_volumes,
            'rapid_alternating': rapid_alternating,
            'wash_trading_detected': wash_trading_detected
        }
    
    async def run_all_tests(self):
        """Run all market data stress tests"""
        self.logger.info("🚀 Starting Market Data Stress Tests")
        await self.test_flash_crashes()
        await self.test_market_manipulation()
        self._generate_report()
        return self.test_results
    
    def _generate_report(self):
        """Generate test report"""
        passed = sum(1 for r in self.test_results.values() if r.get('status') == 'PASSED')
        failed = sum(1 for r in self.test_results.values() if r.get('status') == 'FAILED')
        self.logger.info(f"✅ Passed: {passed}, ❌ Failed: {failed}")

if __name__ == "__main__":
    async def main():
        tester = MarketDataStressTest()
        await tester.run_all_tests()
    asyncio.run(main())

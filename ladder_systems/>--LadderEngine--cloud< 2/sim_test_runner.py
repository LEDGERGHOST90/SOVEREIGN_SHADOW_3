import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd

from src.execution.paper_trading_engine import paper_trading_engine, MarketSimulator
from src.models.signal import TradingSignal
from src.models.user import db
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

class SimulationTestRunner:
    """Comprehensive simulation test runner for the Ladder Sniper Engine"""
    
    def __init__(self):
        self.test_results = []
        self.test_signals = []
        self.simulation_start_time = None
        self.simulation_end_time = None
        
    def create_test_signals(self) -> List[Dict[str, Any]]:
        """Create test signals for simulation"""
        test_signals = [
            {
                'signal_id': 'test_bonk_001',
                'source': 'simulation',
                'symbol': 'BONKUSDT',
                'action': 'buy',
                'entry_price': 0.00003,
                'quantity': 1000000,  # 1M BONK
                'tp1_price': 0.000033,
                'tp1_quantity': 500000,
                'tp2_price': 0.000036,
                'tp2_quantity': 500000,
                'sl_price': 0.000027,
                'priority': 8,
                'exchange': 'binance_us',
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            },
            {
                'signal_id': 'test_wif_002',
                'source': 'simulation',
                'symbol': 'WIFUSDT',
                'action': 'buy',
                'entry_price': 2.5,
                'quantity': 200,  # 200 WIF
                'tp1_price': 2.75,
                'tp1_quantity': 100,
                'tp2_price': 3.0,
                'tp2_quantity': 100,
                'sl_price': 2.25,
                'priority': 7,
                'exchange': 'binance_us',
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            },
            {
                'signal_id': 'test_rndr_003',
                'source': 'simulation',
                'symbol': 'RNDRUSDT',
                'action': 'buy',
                'entry_price': 8.5,
                'quantity': 50,  # 50 RNDR
                'tp1_price': 9.35,
                'tp1_quantity': 25,
                'tp2_price': 10.2,
                'tp2_quantity': 25,
                'sl_price': 7.65,
                'priority': 6,
                'exchange': 'binance_us',
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            },
            {
                'signal_id': 'test_btc_004',
                'source': 'simulation',
                'symbol': 'BTCUSDT',
                'action': 'buy',
                'entry_price': 45000.0,
                'quantity': 0.01,  # 0.01 BTC
                'tp1_price': 46800.0,
                'tp1_quantity': 0.005,
                'tp2_price': 48600.0,
                'tp2_quantity': 0.005,
                'sl_price': 43200.0,
                'priority': 9,
                'exchange': 'binance_us',
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            },
            {
                'signal_id': 'test_eth_005',
                'source': 'simulation',
                'symbol': 'ETHUSDT',
                'action': 'buy',
                'entry_price': 3000.0,
                'quantity': 0.15,  # 0.15 ETH
                'tp1_price': 3240.0,
                'tp1_quantity': 0.075,
                'tp2_price': 3480.0,
                'tp2_quantity': 0.075,
                'sl_price': 2700.0,
                'priority': 8,
                'exchange': 'binance_us',
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            }
        ]
        
        return test_signals
    
    async def run_simulation(self, duration_minutes: int = 60, signal_interval_minutes: int = 10) -> Dict[str, Any]:
        """Run comprehensive simulation test"""
        logger.info(f"Starting simulation test - Duration: {duration_minutes} minutes")
        
        self.simulation_start_time = datetime.utcnow()
        
        # Reset paper trading engine
        paper_trading_engine.paper_balance = 10000.0
        paper_trading_engine.total_pnl = 0.0
        paper_trading_engine.trade_count = 0
        paper_trading_engine.win_count = 0
        paper_trading_engine.loss_count = 0
        paper_trading_engine.active_positions.clear()
        paper_trading_engine.active_ladders.clear()
        
        # Create test signals
        test_signal_data = self.create_test_signals()
        
        # Start position monitoring
        monitor_task = asyncio.create_task(paper_trading_engine.monitor_positions())
        
        try:
            # Process signals at intervals
            signals_processed = 0
            simulation_end = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            while datetime.utcnow() < simulation_end and signals_processed < len(test_signal_data):
                # Create and process signal
                signal_data = test_signal_data[signals_processed]
                signal = await self._create_test_signal(signal_data)
                
                if signal:
                    # Process signal
                    result = await paper_trading_engine.process_signal(signal)
                    
                    self.test_results.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'signal_id': signal.signal_id,
                        'symbol': signal.symbol,
                        'action': signal.action,
                        'entry_price': signal.entry_price,
                        'ray_score': signal.ray_score,
                        'processing_result': result
                    })
                    
                    logger.info(f"Processed signal {signal.signal_id}: {result}")
                
                signals_processed += 1
                
                # Wait for next signal interval
                if signals_processed < len(test_signal_data):
                    await asyncio.sleep(signal_interval_minutes * 60)
            
            # Continue monitoring for remaining duration
            remaining_time = (simulation_end - datetime.utcnow()).total_seconds()
            if remaining_time > 0:
                logger.info(f"Continuing monitoring for {remaining_time:.0f} seconds")
                await asyncio.sleep(remaining_time)
            
        finally:
            # Stop monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        self.simulation_end_time = datetime.utcnow()
        
        # Generate simulation report
        return await self._generate_simulation_report()
    
    async def _create_test_signal(self, signal_data: Dict[str, Any]) -> TradingSignal:
        """Create test signal in database"""
        try:
            signal = TradingSignal(
                signal_id=signal_data['signal_id'],
                source=signal_data['source'],
                symbol=signal_data['symbol'],
                action=signal_data['action'],
                entry_price=signal_data['entry_price'],
                quantity=signal_data['quantity'],
                tp1_price=signal_data.get('tp1_price'),
                tp1_quantity=signal_data.get('tp1_quantity'),
                tp2_price=signal_data.get('tp2_price'),
                tp2_quantity=signal_data.get('tp2_quantity'),
                sl_price=signal_data.get('sl_price'),
                priority=signal_data.get('priority', 5),
                exchange=signal_data.get('exchange', 'binance_us'),
                signal_time=datetime.utcnow(),
                vault_siphon_enabled=signal_data.get('vault_siphon_enabled', True),
                vault_siphon_percentage=signal_data.get('vault_siphon_percentage', 30.0),
                status='validated'
            )
            
            # Calculate Ray Score
            signal.calculate_ray_score()
            
            # Set raw data
            signal.set_raw_data(signal_data)
            
            # Save to database
            db.session.add(signal)
            db.session.commit()
            
            self.test_signals.append(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"Failed to create test signal: {e}")
            return None
    
    async def _generate_simulation_report(self) -> Dict[str, Any]:
        """Generate comprehensive simulation report"""
        try:
            # Get performance stats
            performance_stats = paper_trading_engine.get_performance_stats()
            
            # Get position summary
            position_summary = paper_trading_engine.get_position_summary()
            
            # Calculate simulation duration
            duration = (self.simulation_end_time - self.simulation_start_time).total_seconds() / 60
            
            # Analyze results
            successful_signals = len([r for r in self.test_results if r['processing_result'].get('success')])
            failed_signals = len(self.test_results) - successful_signals
            
            # Calculate average Ray Score
            ray_scores = [r.get('ray_score', 0) for r in self.test_results if r.get('ray_score')]
            avg_ray_score = sum(ray_scores) / len(ray_scores) if ray_scores else 0
            
            # Generate market data summary
            market_summary = self._generate_market_summary()
            
            report = {
                'simulation_info': {
                    'start_time': self.simulation_start_time.isoformat(),
                    'end_time': self.simulation_end_time.isoformat(),
                    'duration_minutes': round(duration, 2),
                    'signals_processed': len(self.test_results),
                    'successful_signals': successful_signals,
                    'failed_signals': failed_signals,
                    'average_ray_score': round(avg_ray_score, 2)
                },
                'performance_stats': performance_stats,
                'position_summary': position_summary,
                'market_summary': market_summary,
                'signal_results': self.test_results,
                'recommendations': self._generate_recommendations(performance_stats)
            }
            
            # Save report to file
            report_filename = f"simulation_report_{int(time.time())}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Simulation report saved to {report_filename}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate simulation report: {e}")
            return {'error': str(e)}
    
    def _generate_market_summary(self) -> Dict[str, Any]:
        """Generate market data summary"""
        try:
            market_summary = {}
            
            for symbol in ['BONKUSDT', 'WIFUSDT', 'RNDRUSDT', 'BTCUSDT', 'ETHUSDT']:
                current_price = paper_trading_engine.market_simulator.get_current_price(symbol)
                price_history = paper_trading_engine.market_simulator.get_price_history(symbol, hours=1)
                
                if price_history:
                    prices = [data.price for data in price_history]
                    volatility = paper_trading_engine.market_simulator.get_volatility(symbol)
                    
                    market_summary[symbol] = {
                        'current_price': current_price,
                        'price_change': ((current_price - prices[0]) / prices[0] * 100) if prices else 0,
                        'volatility': volatility,
                        'data_points': len(price_history)
                    }
            
            return market_summary
            
        except Exception as e:
            logger.error(f"Failed to generate market summary: {e}")
            return {}
    
    def _generate_recommendations(self, performance_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on simulation results"""
        recommendations = []
        
        # Performance-based recommendations
        if performance_stats['win_rate'] < 60:
            recommendations.append("Consider tightening Ray Score thresholds to improve win rate")
        
        if performance_stats['total_pnl'] < 0:
            recommendations.append("Review risk management settings - negative PnL detected")
        
        if performance_stats['trade_count'] == 0:
            recommendations.append("No trades executed - check signal validation logic")
        
        if performance_stats['active_positions'] > 3:
            recommendations.append("Consider reducing max concurrent positions")
        
        # Ray Score recommendations
        avg_ray_score = sum([r.get('ray_score', 0) for r in self.test_results]) / len(self.test_results) if self.test_results else 0
        if avg_ray_score < 70:
            recommendations.append("Average Ray Score is low - review signal quality")
        
        # Balance recommendations
        if performance_stats['paper_balance'] < 5000:
            recommendations.append("Paper balance is low - consider position sizing adjustments")
        
        if not recommendations:
            recommendations.append("Simulation completed successfully - system performing well")
        
        return recommendations
    
    async def run_quick_test(self) -> Dict[str, Any]:
        """Run a quick 5-minute test with 1 signal"""
        logger.info("Running quick simulation test")
        
        # Create single test signal
        test_signal_data = {
            'signal_id': 'quick_test_001',
            'source': 'quick_test',
            'symbol': 'BONKUSDT',
            'action': 'buy',
            'entry_price': 0.00003,
            'quantity': 500000,
            'tp1_price': 0.000033,
            'tp1_quantity': 250000,
            'tp2_price': 0.000036,
            'tp2_quantity': 250000,
            'sl_price': 0.000027,
            'priority': 8,
            'exchange': 'binance_us',
            'vault_siphon_enabled': True,
            'vault_siphon_percentage': 30.0
        }
        
        # Reset engine
        paper_trading_engine.paper_balance = 10000.0
        paper_trading_engine.total_pnl = 0.0
        paper_trading_engine.active_positions.clear()
        paper_trading_engine.active_ladders.clear()
        
        # Create and process signal
        signal = await self._create_test_signal(test_signal_data)
        if not signal:
            return {'error': 'Failed to create test signal'}
        
        # Process signal
        result = await paper_trading_engine.process_signal(signal)
        
        # Monitor for 5 minutes
        monitor_task = asyncio.create_task(paper_trading_engine.monitor_positions())
        
        try:
            await asyncio.sleep(300)  # 5 minutes
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        # Get final stats
        performance_stats = paper_trading_engine.get_performance_stats()
        position_summary = paper_trading_engine.get_position_summary()
        
        return {
            'test_type': 'quick_test',
            'signal_processing_result': result,
            'performance_stats': performance_stats,
            'position_summary': position_summary,
            'ray_score': signal.ray_score,
            'duration_minutes': 5
        }

# Global simulation test runner instance
sim_test_runner = SimulationTestRunner()

# CLI interface for running tests
async def main():
    """Main CLI interface for simulation testing"""
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'quick':
            result = await sim_test_runner.run_quick_test()
            print(json.dumps(result, indent=2, default=str))
        
        elif test_type == 'full':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            result = await sim_test_runner.run_simulation(duration_minutes=duration)
            print(json.dumps(result, indent=2, default=str))
        
        else:
            print("Usage: python sim_test_runner.py [quick|full] [duration_minutes]")
    
    else:
        print("Usage: python sim_test_runner.py [quick|full] [duration_minutes]")

if __name__ == "__main__":
    asyncio.run(main())


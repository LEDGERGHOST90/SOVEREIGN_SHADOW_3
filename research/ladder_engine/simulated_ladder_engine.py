#!/usr/bin/env python3
"""
Simulated Ladder Engine - Paper Trading System
==============================================

Author: Manus AI
Version: 1.0.0
Date: 2025-01-07
Classification: Production Trading System

Description:
Advanced paper trading simulation engine for ΣIGMA-ΩSNIPER ladder strategies.
Provides realistic market simulation with slippage, fees, and fill dynamics.

Security Level: MAXIMUM
Structure Lock: STRUCTURE_LOCK_0712_SIGMAΩ_FINALIZED
"""

import asyncio
import logging
import time
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import json

from ..utils.secure_config_loader import SecureConfigLoader
from ..utils.vault_siphon_router import VaultSiphonRouter

logger = logging.getLogger(__name__)

class SimulatedLadderEngine:
    """
    Advanced paper trading simulation engine
    Provides realistic ladder execution with market dynamics
    """
    
    def __init__(self, config_loader: SecureConfigLoader):
        self.config = config_loader
        self.vault_router = VaultSiphonRouter()
        
        # Simulation parameters
        self.simulation_speed = 1.0  # 1.0 = real-time, 10.0 = 10x speed
        self.market_volatility = 0.02  # 2% base volatility
        self.slippage_factor = 0.001  # 0.1% slippage
        self.fee_rate = 0.001  # 0.1% trading fees
        
        # Active simulations
        self.active_simulations = {}
        self.simulation_history = []
        
        # Market data simulation
        self.price_feeds = {}
        self.market_conditions = {
            'trend': 'neutral',  # bullish, bearish, neutral
            'volatility': 'normal',  # low, normal, high
            'volume': 'average'  # low, average, high
        }
        
        # Performance tracking
        self.metrics = {
            'total_simulations': 0,
            'successful_simulations': 0,
            'total_profit_usd': 0.0,
            'total_loss_usd': 0.0,
            'win_rate': 0.0,
            'average_roi': 0.0
        }
    
    async def execute_ladder(self, signal: Dict[str, Any], ray_score: float) -> Dict[str, Any]:
        """
        Execute simulated ladder deployment
        
        Args:
            signal: Trading signal with ladder parameters
            ray_score: Ray Score for the signal
            
        Returns:
            Simulation result with detailed metrics
        """
        simulation_id = f"SIM_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            logger.info(f"🎮 Starting ladder simulation: {simulation_id}")
            
            # Create ladder configuration
            ladder_config = await self._create_simulation_config(signal, ray_score)
            
            # Initialize price feed
            await self._initialize_price_feed(signal['symbol'], signal['entry_price'])
            
            # Execute simulation
            simulation_result = await self._run_ladder_simulation(
                simulation_id,
                ladder_config,
                ray_score
            )
            
            # Process vault siphon if profitable
            if simulation_result.get('profit_usd', 0) > 0:
                vault_result = await self.vault_router.process_profit_siphon(
                    simulation_result['profit_usd'],
                    signal['symbol']
                )
                simulation_result['vault_siphon'] = vault_result
            
            # Update metrics
            self._update_simulation_metrics(simulation_result)
            
            # Log simulation
            self._log_simulation(simulation_id, signal, simulation_result, ray_score)
            
            execution_time = (time.time() - start_time) * 1000
            simulation_result['execution_time_ms'] = int(execution_time)
            simulation_result['simulation_id'] = simulation_id
            
            logger.info(f"✅ Simulation complete: {simulation_id} ({execution_time:.0f}ms)")
            return simulation_result
            
        except Exception as e:
            logger.error(f"❌ Ladder simulation failed: {simulation_id} - {e}")
            return {
                'success': False,
                'simulation_id': simulation_id,
                'error': str(e),
                'execution_time_ms': int((time.time() - start_time) * 1000),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _create_simulation_config(self, signal: Dict[str, Any], ray_score: float) -> Dict[str, Any]:
        """Create simulation configuration from signal"""
        try:
            entry_low = signal.get('entry_low', signal['entry_price'] * 0.995)
            entry_high = signal.get('entry_high', signal['entry_price'] * 1.005)
            capital = signal['capital']
            
            # Create 6-tier ladder with dynamic weighting
            tier_weights = [0.30, 0.25, 0.20, 0.15, 0.08, 0.02]
            tier_count = len(tier_weights)
            
            tiers = []
            for i in range(tier_count):
                # Calculate tier price (bias toward lower prices)
                ratio = i / (tier_count - 1)
                curved_ratio = ratio ** 1.2  # Curve for lower bias
                price = entry_low + (entry_high - entry_low) * curved_ratio
                
                # Calculate tier allocation
                weight = tier_weights[i]
                tier_capital = capital * weight
                quantity = tier_capital / price
                
                tiers.append({
                    'tier': i + 1,
                    'price': round(price, 8),
                    'quantity': round(quantity, 6),
                    'capital': round(tier_capital, 2),
                    'weight': weight,
                    'filled': False,
                    'fill_time': None,
                    'fill_price': None
                })
            
            return {
                'simulation_id': f"SIM_{int(time.time() * 1000)}",
                'symbol': signal['symbol'],
                'tiers': tiers,
                'tp1_price': signal['tp1_price'],
                'tp2_price': signal.get('tp2_price', signal['tp1_price'] * 1.1),
                'sl_price': signal['sl_price'],
                'total_capital': capital,
                'ray_score': ray_score,
                'start_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Simulation config creation failed: {e}")
            raise
    
    async def _initialize_price_feed(self, symbol: str, starting_price: float) -> None:
        """Initialize realistic price feed for simulation"""
        try:
            self.price_feeds[symbol] = {
                'current_price': starting_price,
                'starting_price': starting_price,
                'price_history': [starting_price],
                'last_update': time.time(),
                'trend_direction': random.choice([-1, 0, 1]),  # -1: down, 0: sideways, 1: up
                'volatility_multiplier': random.uniform(0.5, 2.0)
            }
            
            logger.info(f"📊 Price feed initialized for {symbol} @ ${starting_price}")
            
        except Exception as e:
            logger.error(f"❌ Price feed initialization failed: {e}")
            raise
    
    async def _run_ladder_simulation(self, simulation_id: str, ladder_config: Dict[str, Any], 
                                   ray_score: float) -> Dict[str, Any]:
        """Run the main ladder simulation"""
        try:
            symbol = ladder_config['symbol']
            tiers = ladder_config['tiers']
            
            # Store active simulation
            self.active_simulations[simulation_id] = {
                'config': ladder_config,
                'status': 'running',
                'start_time': time.time()
            }
            
            # Simulation phases
            phases = {
                'entry_phase': {'duration': 300, 'completed': False},  # 5 minutes
                'monitoring_phase': {'duration': 1800, 'completed': False},  # 30 minutes
                'exit_phase': {'duration': 300, 'completed': False}  # 5 minutes
            }
            
            simulation_start = time.time()
            filled_tiers = []
            exit_orders = []
            final_result = None
            
            # Main simulation loop
            while True:
                current_time = time.time()
                elapsed_time = (current_time - simulation_start) * self.simulation_speed
                
                # Update price feed
                await self._update_price_feed(symbol)
                current_price = self.price_feeds[symbol]['current_price']
                
                # Entry phase - fill ladder tiers
                if not phases['entry_phase']['completed']:
                    new_fills = await self._process_entry_fills(tiers, current_price)
                    filled_tiers.extend(new_fills)
                    
                    if elapsed_time > phases['entry_phase']['duration']:
                        phases['entry_phase']['completed'] = True
                        logger.info(f"📈 Entry phase complete: {len(filled_tiers)} tiers filled")
                
                # Monitoring phase - check for TP/SL triggers
                elif not phases['monitoring_phase']['completed']:
                    # Check for TP1 trigger
                    if current_price >= ladder_config['tp1_price']:
                        tp1_result = await self._execute_tp1_exit(filled_tiers, current_price, ladder_config)
                        exit_orders.append(tp1_result)
                        
                        # Check for TP2 trigger
                        if current_price >= ladder_config['tp2_price']:
                            tp2_result = await self._execute_tp2_exit(filled_tiers, current_price, ladder_config)
                            exit_orders.append(tp2_result)
                            final_result = 'TP2_HIT'
                            break
                        else:
                            final_result = 'TP1_HIT'
                            break
                    
                    # Check for SL trigger
                    elif current_price <= ladder_config['sl_price']:
                        sl_result = await self._execute_sl_exit(filled_tiers, current_price, ladder_config)
                        exit_orders.append(sl_result)
                        final_result = 'SL_HIT'
                        break
                    
                    # Check for cognitive rejection (Ray Score drop)
                    if ray_score < 40:
                        cognitive_exit = await self._execute_cognitive_exit(filled_tiers, current_price)
                        exit_orders.append(cognitive_exit)
                        final_result = 'COGNITIVE_EXIT'
                        break
                    
                    if elapsed_time > phases['monitoring_phase']['duration']:
                        phases['monitoring_phase']['completed'] = True
                        # Timeout exit
                        timeout_exit = await self._execute_timeout_exit(filled_tiers, current_price)
                        exit_orders.append(timeout_exit)
                        final_result = 'TIMEOUT'
                        break
                
                # Sleep for simulation tick
                await asyncio.sleep(0.1 / self.simulation_speed)
            
            # Calculate final results
            result = await self._calculate_simulation_results(
                ladder_config, filled_tiers, exit_orders, final_result
            )
            
            # Clean up
            if simulation_id in self.active_simulations:
                del self.active_simulations[simulation_id]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Simulation execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update_price_feed(self, symbol: str) -> None:
        """Update price feed with realistic market movement"""
        try:
            if symbol not in self.price_feeds:
                return
            
            feed = self.price_feeds[symbol]
            current_time = time.time()
            time_delta = current_time - feed['last_update']
            
            # Generate price movement using geometric Brownian motion
            dt = time_delta * self.simulation_speed
            volatility = self.market_volatility * feed['volatility_multiplier']
            
            # Random walk component
            random_component = np.random.normal(0, 1) * np.sqrt(dt)
            
            # Trend component
            trend_strength = 0.001  # 0.1% per second trend
            trend_component = feed['trend_direction'] * trend_strength * dt
            
            # Price change
            price_change_pct = trend_component + volatility * random_component
            new_price = feed['current_price'] * (1 + price_change_pct)
            
            # Update feed
            feed['current_price'] = max(0.0001, new_price)  # Prevent negative prices
            feed['price_history'].append(feed['current_price'])
            feed['last_update'] = current_time
            
            # Limit history size
            if len(feed['price_history']) > 1000:
                feed['price_history'] = feed['price_history'][-500:]
            
            # Occasionally change trend direction
            if random.random() < 0.01:  # 1% chance per update
                feed['trend_direction'] = random.choice([-1, 0, 1])
            
        except Exception as e:
            logger.error(f"❌ Price feed update failed: {e}")
    
    async def _process_entry_fills(self, tiers: List[Dict[str, Any]], 
                                 current_price: float) -> List[Dict[str, Any]]:
        """Process entry order fills based on current price"""
        new_fills = []
        
        try:
            for tier in tiers:
                if not tier['filled'] and current_price <= tier['price']:
                    # Simulate fill with slippage
                    slippage = random.uniform(0, self.slippage_factor)
                    fill_price = tier['price'] * (1 + slippage)
                    
                    # Apply fees
                    fee_amount = tier['capital'] * self.fee_rate
                    net_quantity = tier['quantity'] * (1 - self.fee_rate)
                    
                    tier['filled'] = True
                    tier['fill_time'] = datetime.utcnow().isoformat()
                    tier['fill_price'] = fill_price
                    tier['net_quantity'] = net_quantity
                    tier['fee_amount'] = fee_amount
                    
                    new_fills.append(tier.copy())
                    
                    logger.info(f"💰 Tier {tier['tier']} filled: {net_quantity:.6f} @ ${fill_price:.6f}")
            
            return new_fills
            
        except Exception as e:
            logger.error(f"❌ Entry fill processing failed: {e}")
            return []
    
    async def _execute_tp1_exit(self, filled_tiers: List[Dict[str, Any]], 
                              current_price: float, ladder_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TP1 exit (60% of position)"""
        try:
            total_quantity = sum(tier['net_quantity'] for tier in filled_tiers)
            tp1_quantity = total_quantity * 0.6
            
            # Simulate exit with slippage
            slippage = random.uniform(-self.slippage_factor, 0)  # Favorable slippage for sells
            exit_price = current_price * (1 + slippage)
            
            # Calculate proceeds
            gross_proceeds = tp1_quantity * exit_price
            fee_amount = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee_amount
            
            return {
                'type': 'TP1',
                'quantity': tp1_quantity,
                'exit_price': exit_price,
                'gross_proceeds': gross_proceeds,
                'fee_amount': fee_amount,
                'net_proceeds': net_proceeds,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ TP1 exit failed: {e}")
            return {'type': 'TP1', 'error': str(e)}
    
    async def _execute_tp2_exit(self, filled_tiers: List[Dict[str, Any]], 
                              current_price: float, ladder_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute TP2 exit (remaining 40% of position)"""
        try:
            total_quantity = sum(tier['net_quantity'] for tier in filled_tiers)
            tp2_quantity = total_quantity * 0.4
            
            # Simulate exit
            slippage = random.uniform(-self.slippage_factor, 0)
            exit_price = current_price * (1 + slippage)
            
            gross_proceeds = tp2_quantity * exit_price
            fee_amount = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee_amount
            
            return {
                'type': 'TP2',
                'quantity': tp2_quantity,
                'exit_price': exit_price,
                'gross_proceeds': gross_proceeds,
                'fee_amount': fee_amount,
                'net_proceeds': net_proceeds,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ TP2 exit failed: {e}")
            return {'type': 'TP2', 'error': str(e)}
    
    async def _execute_sl_exit(self, filled_tiers: List[Dict[str, Any]], 
                             current_price: float, ladder_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stop loss exit"""
        try:
            total_quantity = sum(tier['net_quantity'] for tier in filled_tiers)
            
            # Simulate market order with higher slippage
            slippage = random.uniform(0, self.slippage_factor * 2)  # Unfavorable slippage
            exit_price = current_price * (1 - slippage)
            
            gross_proceeds = total_quantity * exit_price
            fee_amount = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee_amount
            
            return {
                'type': 'SL',
                'quantity': total_quantity,
                'exit_price': exit_price,
                'gross_proceeds': gross_proceeds,
                'fee_amount': fee_amount,
                'net_proceeds': net_proceeds,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ SL exit failed: {e}")
            return {'type': 'SL', 'error': str(e)}
    
    async def _execute_cognitive_exit(self, filled_tiers: List[Dict[str, Any]], 
                                    current_price: float) -> Dict[str, Any]:
        """Execute cognitive rejection exit"""
        try:
            total_quantity = sum(tier['net_quantity'] for tier in filled_tiers)
            
            # Market exit with moderate slippage
            slippage = random.uniform(0, self.slippage_factor * 1.5)
            exit_price = current_price * (1 - slippage)
            
            gross_proceeds = total_quantity * exit_price
            fee_amount = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee_amount
            
            return {
                'type': 'COGNITIVE_EXIT',
                'quantity': total_quantity,
                'exit_price': exit_price,
                'gross_proceeds': gross_proceeds,
                'fee_amount': fee_amount,
                'net_proceeds': net_proceeds,
                'reason': 'Ray Score below 40',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cognitive exit failed: {e}")
            return {'type': 'COGNITIVE_EXIT', 'error': str(e)}
    
    async def _execute_timeout_exit(self, filled_tiers: List[Dict[str, Any]], 
                                  current_price: float) -> Dict[str, Any]:
        """Execute timeout exit"""
        try:
            total_quantity = sum(tier['net_quantity'] for tier in filled_tiers)
            
            # Market exit
            slippage = random.uniform(0, self.slippage_factor)
            exit_price = current_price * (1 - slippage)
            
            gross_proceeds = total_quantity * exit_price
            fee_amount = gross_proceeds * self.fee_rate
            net_proceeds = gross_proceeds - fee_amount
            
            return {
                'type': 'TIMEOUT',
                'quantity': total_quantity,
                'exit_price': exit_price,
                'gross_proceeds': gross_proceeds,
                'fee_amount': fee_amount,
                'net_proceeds': net_proceeds,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Timeout exit failed: {e}")
            return {'type': 'TIMEOUT', 'error': str(e)}
    
    async def _calculate_simulation_results(self, ladder_config: Dict[str, Any], 
                                          filled_tiers: List[Dict[str, Any]], 
                                          exit_orders: List[Dict[str, Any]], 
                                          final_result: str) -> Dict[str, Any]:
        """Calculate final simulation results"""
        try:
            # Calculate total investment
            total_invested = sum(tier['capital'] for tier in filled_tiers)
            total_fees = sum(tier.get('fee_amount', 0) for tier in filled_tiers)
            
            # Calculate total proceeds
            total_proceeds = sum(order.get('net_proceeds', 0) for order in exit_orders)
            exit_fees = sum(order.get('fee_amount', 0) for order in exit_orders)
            
            # Calculate profit/loss
            net_profit = total_proceeds - total_invested
            roi_percentage = (net_profit / total_invested) * 100 if total_invested > 0 else 0
            
            # Determine success
            success = net_profit > 0
            
            return {
                'success': True,
                'execution_status': final_result,
                'ladder_fill_plan': {
                    'total_tiers': len(ladder_config['tiers']),
                    'filled_tiers': len(filled_tiers),
                    'fill_rate': len(filled_tiers) / len(ladder_config['tiers']) * 100
                },
                'financial_summary': {
                    'total_invested_usd': round(total_invested, 2),
                    'total_proceeds_usd': round(total_proceeds, 2),
                    'profit_usd': round(net_profit, 2),
                    'roi_percentage': round(roi_percentage, 2),
                    'total_fees_usd': round(total_fees + exit_fees, 2),
                    'profitable': success
                },
                'execution_details': {
                    'filled_tiers': filled_tiers,
                    'exit_orders': exit_orders,
                    'final_price': self.price_feeds[ladder_config['symbol']]['current_price']
                },
                'profit_projection': max(0, net_profit),  # For vault siphon
                'ray_score': ladder_config['ray_score'],
                'simulation_mode': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Results calculation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_simulation_metrics(self, result: Dict[str, Any]) -> None:
        """Update simulation performance metrics"""
        try:
            self.metrics['total_simulations'] += 1
            
            if result.get('success') and result.get('financial_summary', {}).get('profitable'):
                self.metrics['successful_simulations'] += 1
                profit = result['financial_summary']['profit_usd']
                self.metrics['total_profit_usd'] += profit
            else:
                loss = abs(result.get('financial_summary', {}).get('profit_usd', 0))
                self.metrics['total_loss_usd'] += loss
            
            # Update win rate
            self.metrics['win_rate'] = (
                self.metrics['successful_simulations'] / self.metrics['total_simulations'] * 100
            )
            
            # Update average ROI
            if 'financial_summary' in result:
                roi = result['financial_summary'].get('roi_percentage', 0)
                total_roi = self.metrics.get('total_roi', 0) + roi
                self.metrics['total_roi'] = total_roi
                self.metrics['average_roi'] = total_roi / self.metrics['total_simulations']
            
        except Exception as e:
            logger.error(f"❌ Metrics update failed: {e}")
    
    def _log_simulation(self, simulation_id: str, signal: Dict[str, Any], 
                       result: Dict[str, Any], ray_score: float) -> None:
        """Log simulation for audit trail"""
        try:
            log_entry = {
                'simulation_id': simulation_id,
                'timestamp': datetime.utcnow().isoformat(),
                'signal': signal,
                'result': result,
                'ray_score': ray_score,
                'simulation_mode': True
            }
            
            self.simulation_history.append(log_entry)
            
            # Save to file
            with open('simulation_log.json', 'w') as f:
                json.dump(self.simulation_history, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"❌ Simulation logging failed: {e}")
    
    async def get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        try:
            return {
                'active_simulations': len(self.active_simulations),
                'metrics': self.metrics,
                'market_conditions': self.market_conditions,
                'simulation_parameters': {
                    'simulation_speed': self.simulation_speed,
                    'market_volatility': self.market_volatility,
                    'slippage_factor': self.slippage_factor,
                    'fee_rate': self.fee_rate
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Simulation status check failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Utility functions for external use
async def run_quick_simulation(signal: Dict[str, Any], ray_score: float = 75.0) -> Dict[str, Any]:
    """
    Run a quick simulation for testing
    
    Args:
        signal: Trading signal
        ray_score: Ray Score for the signal
        
    Returns:
        Simulation result
    """
    try:
        config_loader = SecureConfigLoader()
        simulator = SimulatedLadderEngine(config_loader)
        simulator.simulation_speed = 10.0  # 10x speed for quick test
        
        return await simulator.execute_ladder(signal, ray_score)
        
    except Exception as e:
        logger.error(f"❌ Quick simulation failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


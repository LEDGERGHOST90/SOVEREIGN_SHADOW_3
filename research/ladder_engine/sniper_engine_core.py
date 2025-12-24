#!/usr/bin/env python3
"""
ΣIGMA-ΩSNIPER Core Engine
========================

Author: Manus AI
Version: 1.0.0
Date: 2025-01-07
Classification: Production Trading System

Description:
Core execution engine for ΣIGMA-ΩSNIPER ladder deployment system.
Handles live trading execution, order management, and real-time monitoring.

Security Level: MAXIMUM
Structure Lock: STRUCTURE_LOCK_0712_SIGMAΩ_FINALIZED
"""

import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json

from ..utils.secure_config_loader import SecureConfigLoader
from ..utils.cognitive_filter_ray import CognitiveFilterRay
from ..utils.vault_siphon_router import VaultSiphonRouter
from .multi_exchange_adapter import MultiExchangeAdapter

logger = logging.getLogger(__name__)

class SniperEngineCore:
    """
    Core execution engine for ΣIGMA-ΩSNIPER system
    Manages live trading operations with cognitive monitoring
    """
    
    def __init__(self, config_loader: SecureConfigLoader):
        self.config = config_loader
        self.cognitive_filter = CognitiveFilterRay()
        self.vault_router = VaultSiphonRouter()
        self.exchange_adapter = MultiExchangeAdapter(config_loader)
        
        # Execution state
        self.active_ladders = {}
        self.execution_log = []
        self.cognitive_monitoring = True
        
        # Performance metrics
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'cognitive_rejections': 0,
            'vault_siphons': 0,
            'total_profit': 0.0
        }
    
    async def execute_ladder(self, signal: Dict[str, Any], ray_score: float) -> Dict[str, Any]:
        """
        Execute ΣIGMA-ΩSNIPER ladder deployment
        
        Args:
            signal: Trading signal with all parameters
            ray_score: Pre-calculated Ray Score for the signal
            
        Returns:
            Execution result with order IDs and status
        """
        execution_id = f"SIGMA_{int(time.time())}"
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Executing ΣIGMA ladder: {execution_id}")
            
            # Validate signal parameters
            validation_result = await self._validate_signal(signal)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'rejection_reason': validation_result['reason'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Create ladder configuration
            ladder_config = await self._create_ladder_config(signal)
            
            # Execute ladder tiers
            execution_result = await self._execute_ladder_tiers(
                execution_id, 
                ladder_config, 
                ray_score
            )
            
            if execution_result['success']:
                # Start cognitive monitoring
                if self.cognitive_monitoring:
                    asyncio.create_task(
                        self._monitor_cognitive_state(execution_id, ray_score)
                    )
                
                # Update metrics
                self.metrics['total_executions'] += 1
                self.metrics['successful_executions'] += 1
                
                # Log execution
                self._log_execution(execution_id, signal, execution_result, ray_score)
            
            execution_time = (time.time() - start_time) * 1000
            execution_result['execution_time_ms'] = int(execution_time)
            execution_result['execution_id'] = execution_id
            
            logger.info(f"✅ Ladder execution complete: {execution_id} ({execution_time:.0f}ms)")
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ Ladder execution failed: {execution_id} - {e}")
            return {
                'success': False,
                'execution_id': execution_id,
                'error': str(e),
                'execution_time_ms': int((time.time() - start_time) * 1000),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _validate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate signal parameters for execution"""
        try:
            required_fields = ['symbol', 'entry_price', 'tp1_price', 'sl_price', 'capital']
            missing_fields = [field for field in required_fields if field not in signal]
            
            if missing_fields:
                return {
                    'valid': False,
                    'reason': f"Missing required fields: {missing_fields}"
                }
            
            # Validate price relationships
            entry = signal['entry_price']
            tp1 = signal['tp1_price']
            sl = signal['sl_price']
            
            if tp1 <= entry:
                return {
                    'valid': False,
                    'reason': "TP1 must be above entry price"
                }
            
            if sl >= entry:
                return {
                    'valid': False,
                    'reason': "Stop loss must be below entry price"
                }
            
            # Validate capital amount
            if signal['capital'] <= 0:
                return {
                    'valid': False,
                    'reason': "Capital must be positive"
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f"Validation error: {e}"
            }
    
    async def _create_ladder_config(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Create ladder configuration with tier structure"""
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
                curved_ratio = ratio ** 1.2  # Slight curve for lower bias
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
                    'status': 'pending'
                })
            
            return {
                'symbol': signal['symbol'],
                'tiers': tiers,
                'tp1_price': signal['tp1_price'],
                'tp2_price': signal.get('tp2_price', signal['tp1_price'] * 1.1),
                'sl_price': signal['sl_price'],
                'total_capital': capital,
                'execution_mode': 'live'
            }
            
        except Exception as e:
            logger.error(f"❌ Ladder config creation failed: {e}")
            raise
    
    async def _execute_ladder_tiers(self, execution_id: str, ladder_config: Dict[str, Any], 
                                  ray_score: float) -> Dict[str, Any]:
        """Execute all ladder tiers with order placement"""
        try:
            symbol = ladder_config['symbol']
            tiers = ladder_config['tiers']
            
            # Place entry orders
            entry_orders = []
            for tier in tiers:
                order_result = await self.exchange_adapter.place_limit_order(
                    symbol=symbol,
                    side='buy',
                    quantity=tier['quantity'],
                    price=tier['price']
                )
                
                if order_result['success']:
                    entry_orders.append({
                        'tier': tier['tier'],
                        'order_id': order_result['order_id'],
                        'price': tier['price'],
                        'quantity': tier['quantity'],
                        'status': 'placed'
                    })
                    tier['status'] = 'placed'
                    tier['order_id'] = order_result['order_id']
                else:
                    logger.warning(f"⚠️  Failed to place tier {tier['tier']} order: {order_result.get('error')}")
                    tier['status'] = 'failed'
            
            if not entry_orders:
                return {
                    'success': False,
                    'reason': 'No entry orders placed successfully'
                }
            
            # Place TP orders (conditional)
            total_quantity = sum(tier['quantity'] for tier in tiers if tier['status'] == 'placed')
            tp1_quantity = total_quantity * 0.6  # 60% at TP1
            tp2_quantity = total_quantity * 0.4  # 40% at TP2
            
            tp_orders = []
            
            # TP1 Order
            tp1_result = await self.exchange_adapter.place_limit_order(
                symbol=symbol,
                side='sell',
                quantity=tp1_quantity,
                price=ladder_config['tp1_price']
            )
            
            if tp1_result['success']:
                tp_orders.append({
                    'type': 'TP1',
                    'order_id': tp1_result['order_id'],
                    'price': ladder_config['tp1_price'],
                    'quantity': tp1_quantity
                })
            
            # TP2 Order
            tp2_result = await self.exchange_adapter.place_limit_order(
                symbol=symbol,
                side='sell',
                quantity=tp2_quantity,
                price=ladder_config['tp2_price']
            )
            
            if tp2_result['success']:
                tp_orders.append({
                    'type': 'TP2',
                    'order_id': tp2_result['order_id'],
                    'price': ladder_config['tp2_price'],
                    'quantity': tp2_quantity
                })
            
            # Place Stop Loss order
            sl_result = await self.exchange_adapter.place_stop_loss_order(
                symbol=symbol,
                quantity=total_quantity,
                stop_price=ladder_config['sl_price']
            )
            
            sl_order = None
            if sl_result['success']:
                sl_order = {
                    'type': 'SL',
                    'order_id': sl_result['order_id'],
                    'stop_price': ladder_config['sl_price'],
                    'quantity': total_quantity
                }
            
            # Store active ladder
            self.active_ladders[execution_id] = {
                'config': ladder_config,
                'entry_orders': entry_orders,
                'tp_orders': tp_orders,
                'sl_order': sl_order,
                'ray_score': ray_score,
                'start_time': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            return {
                'success': True,
                'execution_status': 'LADDER_DEPLOYED',
                'entry_orders': len(entry_orders),
                'tp_orders': len(tp_orders),
                'sl_order': 1 if sl_order else 0,
                'total_orders': len(entry_orders) + len(tp_orders) + (1 if sl_order else 0),
                'ladder_fill_plan': {
                    'entry_tiers': len(entry_orders),
                    'total_capital': ladder_config['total_capital'],
                    'average_entry': sum(t['price'] * t['quantity'] for t in tiers if t['status'] == 'placed') / total_quantity
                },
                'order_ids': [o['order_id'] for o in entry_orders] + 
                           [o['order_id'] for o in tp_orders] + 
                           ([sl_order['order_id']] if sl_order else [])
            }
            
        except Exception as e:
            logger.error(f"❌ Ladder tier execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _monitor_cognitive_state(self, execution_id: str, initial_ray_score: float) -> None:
        """Monitor cognitive state and trigger auto-exit if needed"""
        try:
            logger.info(f"👁️  Starting cognitive monitoring for {execution_id}")
            
            while execution_id in self.active_ladders:
                # Check if ladder is still active
                ladder = self.active_ladders[execution_id]
                if ladder['status'] != 'active':
                    break
                
                # Recalculate Ray Score for current market conditions
                current_signal = {
                    'symbol': ladder['config']['symbol'],
                    'entry_price': ladder['config']['tiers'][0]['price'],  # Use first tier as reference
                    'tp1_price': ladder['config']['tp1_price'],
                    'sl_price': ladder['config']['sl_price']
                }
                
                current_ray_score = await self.cognitive_filter.calculate_ray_score(current_signal)
                
                # Check for cognitive rejection threshold
                if current_ray_score < 40:
                    logger.warning(f"🧠 Cognitive rejection triggered for {execution_id}: Ray Score {current_ray_score:.1f}")
                    
                    # Trigger auto-exit
                    exit_result = await self._execute_cognitive_exit(execution_id)
                    
                    if exit_result['success']:
                        self.metrics['cognitive_rejections'] += 1
                        logger.info(f"✅ Cognitive exit completed for {execution_id}")
                    else:
                        logger.error(f"❌ Cognitive exit failed for {execution_id}")
                    
                    break
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # 30 second intervals
            
            logger.info(f"👁️  Cognitive monitoring ended for {execution_id}")
            
        except Exception as e:
            logger.error(f"❌ Cognitive monitoring error for {execution_id}: {e}")
    
    async def _execute_cognitive_exit(self, execution_id: str) -> Dict[str, Any]:
        """Execute cognitive rejection exit sequence"""
        try:
            ladder = self.active_ladders[execution_id]
            
            # Cancel all open orders
            cancelled_orders = []
            
            # Cancel entry orders
            for order in ladder['entry_orders']:
                if order['status'] == 'placed':
                    cancel_result = await self.exchange_adapter.cancel_order(
                        ladder['config']['symbol'],
                        order['order_id']
                    )
                    if cancel_result['success']:
                        cancelled_orders.append(order['order_id'])
            
            # Cancel TP orders
            for order in ladder['tp_orders']:
                cancel_result = await self.exchange_adapter.cancel_order(
                    ladder['config']['symbol'],
                    order['order_id']
                )
                if cancel_result['success']:
                    cancelled_orders.append(order['order_id'])
            
            # Cancel SL order
            if ladder['sl_order']:
                cancel_result = await self.exchange_adapter.cancel_order(
                    ladder['config']['symbol'],
                    ladder['sl_order']['order_id']
                )
                if cancel_result['success']:
                    cancelled_orders.append(ladder['sl_order']['order_id'])
            
            # Update ladder status
            ladder['status'] = 'cognitive_exit'
            ladder['exit_time'] = datetime.utcnow().isoformat()
            ladder['exit_reason'] = 'cognitive_rejection'
            
            return {
                'success': True,
                'cancelled_orders': len(cancelled_orders),
                'exit_reason': 'cognitive_rejection'
            }
            
        except Exception as e:
            logger.error(f"❌ Cognitive exit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_execution(self, execution_id: str, signal: Dict[str, Any], 
                      result: Dict[str, Any], ray_score: float) -> None:
        """Log execution details for audit trail"""
        try:
            log_entry = {
                'execution_id': execution_id,
                'timestamp': datetime.utcnow().isoformat(),
                'signal': signal,
                'result': result,
                'ray_score': ray_score,
                'execution_time_ms': result.get('execution_time_ms', 0)
            }
            
            self.execution_log.append(log_entry)
            
            # Save to file
            with open('execution_log.json', 'w') as f:
                json.dump(self.execution_log, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"❌ Execution logging failed: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        try:
            return {
                'status': 'operational',
                'active_ladders': len(self.active_ladders),
                'metrics': self.metrics,
                'cognitive_monitoring': self.cognitive_monitoring,
                'exchange_status': await self.exchange_adapter.get_status(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self) -> None:
        """Graceful system shutdown"""
        try:
            logger.info("🛑 Initiating ΣIGMA-ΩSNIPER shutdown")
            
            # Cancel cognitive monitoring
            self.cognitive_monitoring = False
            
            # Close exchange connections
            await self.exchange_adapter.close()
            
            logger.info("✅ ΣIGMA-ΩSNIPER shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


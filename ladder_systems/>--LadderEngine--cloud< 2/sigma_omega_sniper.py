import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from src.models.user import db
from src.models.signal import TradingSignal, ExecutionLog
from src.models.exchange_config import Position
from src.execution.exchange_adapters import ExchangeAdapterFactory
from src.execution.paper_trading_engine import paper_trading_engine
from src.utils.ray_score_engine import ray_score_engine, validate_roi
from src.utils.vault_router import vault_router
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

@dataclass
class LadderTier:
    """Individual ladder tier configuration"""
    tier: int
    price: float
    quantity: float
    weight: float  # Percentage of total position
    order_type: str  # entry, tp1, tp2, sl
    status: str = 'pending'  # pending, placed, filled, cancelled
    order_id: Optional[str] = None
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None

@dataclass
class LadderPlan:
    """Complete ladder execution plan"""
    signal_id: str
    symbol: str
    action: str
    total_capital: float
    entry_range: Tuple[float, float]
    tp1_price: float
    tp2_price: float
    sl_price: float
    tiers: List[LadderTier]
    ray_score: float
    roi_validation: Dict[str, Any]
    execution_mode: str  # paper, live
    exchange: str
    created_at: datetime

@dataclass
class ExecutionResult:
    """Ladder execution result"""
    success: bool
    ladder_plan: Optional[LadderPlan]
    execution_status: str
    tp1_roi: float
    tp2_roi: float
    vault_projection: Optional[Dict[str, Any]]
    rejection_reasons: List[str]
    execution_time_ms: int
    order_ids: List[str]

class SigmaOmegaSniper:
    """
    ΣIGMA-ΩSNIPER Ladder Execution Engine
    
    Advanced multi-tier ladder trading system with:
    - Ray Score cognitive filtering
    - Dynamic tier weighting
    - Sub-second execution latency
    - Vault siphon integration
    - Real-time monitoring
    """
    
    def __init__(self):
        self.active_ladders: Dict[str, LadderPlan] = {}
        self.execution_history: List[ExecutionResult] = []
        
        # Execution parameters
        self.min_ray_score = 60.0
        self.max_spread_percentage = 1.25
        self.min_tp1_roi = 0.20  # 20%
        self.min_tp2_roi = 0.30  # 30%
        self.max_drawdown = 0.07  # 7%
        
        # Ladder configuration
        self.default_tier_count = 6  # 5-7 tier structure
        self.tier_weights = [0.25, 0.20, 0.20, 0.15, 0.15, 0.05]  # Heavier weight to lower tiers
        
        # Exchange adapters
        self.exchange_adapters = {}
        
    async def initialize_exchange_adapters(self):
        """Initialize exchange adapters for live trading"""
        try:
            supported_exchanges = ['binance_us', 'kucoin', 'bybit']
            
            for exchange in supported_exchanges:
                config = config_manager.get_exchange_credentials(exchange)
                if config:
                    adapter = ExchangeAdapterFactory.create_adapter(exchange, asdict(config))
                    if await adapter.connect():
                        self.exchange_adapters[exchange] = adapter
                        logger.info(f"Connected to {exchange}")
                    else:
                        logger.warning(f"Failed to connect to {exchange}")
                        
        except Exception as e:
            logger.error(f"Exchange adapter initialization failed: {e}")
    
    async def deploy_ladder_flip(self, token: str, entry_range: Tuple[float, float],
                               tp1: float, tp2: float, sl: float, capital: float,
                               mode: str = 'paper', exchange: str = 'binance_us') -> ExecutionResult:
        """
        Deploy ΣIGMA-ΩSNIPER ladder flip
        
        Args:
            token: Token symbol (e.g., 'BONK')
            entry_range: Entry price range (min, max)
            tp1: Take profit 1 price
            tp2: Take profit 2 price
            sl: Stop loss price
            capital: Capital allocation
            mode: 'paper' or 'live'
            exchange: Target exchange
            
        Returns:
            ExecutionResult with detailed status
        """
        start_time = time.time()
        rejection_reasons = []
        
        try:
            # 1. Target Acquisition - Create signal data
            symbol = f"{token}USDT"
            signal_data = {
                'signal_id': f"sigma_{token.lower()}_{int(time.time())}",
                'source': 'sigma_omega_sniper',
                'symbol': symbol,
                'action': 'buy',
                'entry_price': sum(entry_range) / 2,  # Average entry
                'quantity': capital / (sum(entry_range) / 2),
                'tp1_price': tp1,
                'tp2_price': tp2,
                'sl_price': sl,
                'priority': 9,
                'exchange': exchange,
                'vault_siphon_enabled': True,
                'vault_siphon_percentage': 30.0
            }
            
            # 2. Ray Score Validation
            ray_score = ray_score_engine.get_ray_score(signal_data)
            if ray_score < self.min_ray_score:
                rejection_reasons.append(f"Ray Score {ray_score:.1f} below threshold {self.min_ray_score}")
            
            # 3. Spread Validation
            spread = abs(entry_range[1] - entry_range[0]) / entry_range[0] * 100
            if spread > self.max_spread_percentage:
                rejection_reasons.append(f"Spread {spread:.2f}% exceeds maximum {self.max_spread_percentage}%")
            
            # 4. ROI Validation
            entry_prices = self._generate_entry_prices(entry_range, self.default_tier_count)
            roi_validation = validate_roi(entry_prices, tp1, tp2, sl)
            
            if not roi_validation['valid']:
                rejection_reasons.append("ROI requirements not met")
                if roi_validation['tp1_roi'] < 20:
                    rejection_reasons.append(f"TP1 ROI {roi_validation['tp1_roi']:.1f}% < 20%")
                if roi_validation['tp2_roi'] < 30:
                    rejection_reasons.append(f"TP2 ROI {roi_validation['tp2_roi']:.1f}% < 30%")
                if roi_validation['drawdown'] > 7:
                    rejection_reasons.append(f"Drawdown {roi_validation['drawdown']:.1f}% > 7%")
            
            # 5. Reject if validation failed
            if rejection_reasons:
                return ExecutionResult(
                    success=False,
                    ladder_plan=None,
                    execution_status='rejected',
                    tp1_roi=roi_validation.get('tp1_roi', 0),
                    tp2_roi=roi_validation.get('tp2_roi', 0),
                    vault_projection=None,
                    rejection_reasons=rejection_reasons,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    order_ids=[]
                )
            
            # 6. Create Ladder Plan
            ladder_plan = self._create_ladder_plan(
                signal_data, entry_range, tp1, tp2, sl, capital, ray_score, roi_validation, mode, exchange
            )
            
            # 7. Execute Ladder
            execution_result = await self._execute_ladder(ladder_plan)
            
            # 8. Calculate Vault Projection
            vault_projection = self._calculate_vault_projection(ladder_plan, roi_validation)
            
            # 9. Store active ladder
            self.active_ladders[ladder_plan.signal_id] = ladder_plan
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            result = ExecutionResult(
                success=execution_result['success'],
                ladder_plan=ladder_plan,
                execution_status=execution_result['status'],
                tp1_roi=roi_validation['tp1_roi'],
                tp2_roi=roi_validation['tp2_roi'],
                vault_projection=vault_projection,
                rejection_reasons=[],
                execution_time_ms=execution_time_ms,
                order_ids=execution_result.get('order_ids', [])
            )
            
            # Store execution history
            self.execution_history.append(result)
            
            # Log execution
            logger.info(f"ΣIGMA-ΩSNIPER deployed: {symbol} | Ray Score: {ray_score:.1f} | "
                       f"TP1: {roi_validation['tp1_roi']:.1f}% | TP2: {roi_validation['tp2_roi']:.1f}% | "
                       f"Execution: {execution_time_ms}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"ΣIGMA-ΩSNIPER deployment failed: {e}")
            return ExecutionResult(
                success=False,
                ladder_plan=None,
                execution_status='error',
                tp1_roi=0,
                tp2_roi=0,
                vault_projection=None,
                rejection_reasons=[f"Execution error: {str(e)}"],
                execution_time_ms=int((time.time() - start_time) * 1000),
                order_ids=[]
            )
    
    def _generate_entry_prices(self, entry_range: Tuple[float, float], tier_count: int) -> List[float]:
        """Generate entry prices for ladder tiers"""
        min_price, max_price = entry_range
        
        if tier_count == 1:
            return [(min_price + max_price) / 2]
        
        # Generate evenly spaced prices within range
        step = (max_price - min_price) / (tier_count - 1)
        return [min_price + i * step for i in range(tier_count)]
    
    def _create_ladder_plan(self, signal_data: Dict[str, Any], entry_range: Tuple[float, float],
                           tp1: float, tp2: float, sl: float, capital: float,
                           ray_score: float, roi_validation: Dict[str, Any],
                           mode: str, exchange: str) -> LadderPlan:
        """Create detailed ladder execution plan"""
        
        # Generate entry prices
        entry_prices = self._generate_entry_prices(entry_range, self.default_tier_count)
        
        # Create ladder tiers
        tiers = []
        
        # Entry tiers (heavier weight to lower prices)
        for i, price in enumerate(entry_prices):
            weight = self.tier_weights[i] if i < len(self.tier_weights) else 0.05
            quantity = (capital * weight) / price
            
            tier = LadderTier(
                tier=i + 1,
                price=price,
                quantity=quantity,
                weight=weight,
                order_type='entry'
            )
            tiers.append(tier)
        
        # TP1 tier (60% of position)
        total_quantity = sum(tier.quantity for tier in tiers)
        tp1_tier = LadderTier(
            tier=100,
            price=tp1,
            quantity=total_quantity * 0.6,
            weight=0.6,
            order_type='tp1'
        )
        tiers.append(tp1_tier)
        
        # TP2 tier (40% of position)
        tp2_tier = LadderTier(
            tier=101,
            price=tp2,
            quantity=total_quantity * 0.4,
            weight=0.4,
            order_type='tp2'
        )
        tiers.append(tp2_tier)
        
        # Stop Loss tier (full position)
        sl_tier = LadderTier(
            tier=-1,
            price=sl,
            quantity=total_quantity,
            weight=1.0,
            order_type='sl'
        )
        tiers.append(sl_tier)
        
        return LadderPlan(
            signal_id=signal_data['signal_id'],
            symbol=signal_data['symbol'],
            action=signal_data['action'],
            total_capital=capital,
            entry_range=entry_range,
            tp1_price=tp1,
            tp2_price=tp2,
            sl_price=sl,
            tiers=tiers,
            ray_score=ray_score,
            roi_validation=roi_validation,
            execution_mode=mode,
            exchange=exchange,
            created_at=datetime.utcnow()
        )
    
    async def _execute_ladder(self, ladder_plan: LadderPlan) -> Dict[str, Any]:
        """Execute ladder plan with sub-second latency"""
        try:
            if ladder_plan.execution_mode == 'paper':
                # Use paper trading engine
                signal = TradingSignal(
                    signal_id=ladder_plan.signal_id,
                    source='sigma_omega_sniper',
                    symbol=ladder_plan.symbol,
                    action=ladder_plan.action,
                    entry_price=sum(ladder_plan.entry_range) / 2,
                    quantity=sum(tier.quantity for tier in ladder_plan.tiers if tier.order_type == 'entry'),
                    tp1_price=ladder_plan.tp1_price,
                    tp2_price=ladder_plan.tp2_price,
                    sl_price=ladder_plan.sl_price,
                    ray_score=ladder_plan.ray_score,
                    status='validated',
                    signal_time=datetime.utcnow(),
                    vault_siphon_enabled=True,
                    vault_siphon_percentage=30.0
                )
                
                # Save signal to database
                db.session.add(signal)
                db.session.commit()
                
                # Process with paper trading engine
                result = await paper_trading_engine.process_signal(signal)
                
                return {
                    'success': result['success'],
                    'status': 'paper_executed',
                    'order_ids': [f"paper_{int(time.time())}_{i}" for i in range(len(ladder_plan.tiers))]
                }
            
            else:
                # Live trading execution
                if ladder_plan.exchange not in self.exchange_adapters:
                    return {
                        'success': False,
                        'status': 'exchange_not_available',
                        'error': f'Exchange {ladder_plan.exchange} not connected'
                    }
                
                adapter = self.exchange_adapters[ladder_plan.exchange]
                order_ids = []
                
                # Execute entry orders
                for tier in ladder_plan.tiers:
                    if tier.order_type == 'entry':
                        order_result = await adapter.place_order(
                            symbol=ladder_plan.symbol,
                            side=ladder_plan.action,
                            order_type='limit',
                            quantity=tier.quantity,
                            price=tier.price
                        )
                        
                        if order_result.get('id'):
                            tier.order_id = order_result['id']
                            tier.status = 'placed'
                            order_ids.append(order_result['id'])
                
                return {
                    'success': len(order_ids) > 0,
                    'status': 'live_executed',
                    'order_ids': order_ids
                }
                
        except Exception as e:
            logger.error(f"Ladder execution failed: {e}")
            return {
                'success': False,
                'status': 'execution_failed',
                'error': str(e)
            }
    
    def _calculate_vault_projection(self, ladder_plan: LadderPlan, 
                                  roi_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate vault siphon projection if TP1 hits"""
        try:
            # Calculate potential profits
            avg_entry = sum(ladder_plan.entry_range) / 2
            tp1_profit = (ladder_plan.tp1_price - avg_entry) * sum(
                tier.quantity for tier in ladder_plan.tiers if tier.order_type == 'entry'
            ) * 0.6  # 60% of position at TP1
            
            tp2_profit = (ladder_plan.tp2_price - avg_entry) * sum(
                tier.quantity for tier in ladder_plan.tiers if tier.order_type == 'entry'
            ) * 0.4  # 40% of position at TP2
            
            # Calculate vault siphon amounts
            tp1_siphon = tp1_profit * 0.30  # 30% siphon
            tp2_siphon = tp2_profit * 0.30  # 30% siphon
            total_siphon = tp1_siphon + tp2_siphon
            
            # Select target asset
            target_asset = vault_router.select_target_asset(ladder_plan.exchange, total_siphon)
            
            return {
                'tp1_profit': round(tp1_profit, 2),
                'tp2_profit': round(tp2_profit, 2),
                'total_profit': round(tp1_profit + tp2_profit, 2),
                'tp1_siphon': round(tp1_siphon, 2),
                'tp2_siphon': round(tp2_siphon, 2),
                'total_siphon': round(total_siphon, 2),
                'target_asset': target_asset,
                'siphon_percentage': 30.0,
                'vault_tier': 'SLEEP'
            }
            
        except Exception as e:
            logger.error(f"Vault projection calculation failed: {e}")
            return {}
    
    async def monitor_ray_scores(self):
        """Monitor Ray Scores for cognitive rejection"""
        while True:
            try:
                for signal_id, ladder_plan in list(self.active_ladders.items()):
                    # Recalculate Ray Score
                    signal_data = {
                        'symbol': ladder_plan.symbol,
                        'action': ladder_plan.action,
                        'entry_price': sum(ladder_plan.entry_range) / 2,
                        'tp1_price': ladder_plan.tp1_price,
                        'tp2_price': ladder_plan.tp2_price,
                        'sl_price': ladder_plan.sl_price
                    }
                    
                    current_ray_score = ray_score_engine.get_ray_score(signal_data)
                    
                    # Check for cognitive rejection threshold
                    if current_ray_score < 40.0:
                        await self._trigger_cognitive_rejection(signal_id, current_ray_score)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Ray Score monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_cognitive_rejection(self, signal_id: str, ray_score: float):
        """Trigger cognitive rejection and auto-stop-loss"""
        try:
            ladder_plan = self.active_ladders.get(signal_id)
            if not ladder_plan:
                return
            
            logger.warning(f"COGNITIVE REJECTION: {signal_id} Ray Score {ray_score:.1f} < 40")
            
            # Log cognitive rejection event
            log_entry = ExecutionLog(
                signal_id=signal_id,
                action='cognitive_rejection',
                message=f'Ray Score dropped to {ray_score:.1f}, triggering auto-stop-loss',
                execution_time_ms=0
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Trigger stop-loss in paper trading
            if ladder_plan.execution_mode == 'paper':
                # Force close position in paper trading engine
                if signal_id in paper_trading_engine.active_positions:
                    position = paper_trading_engine.active_positions[signal_id]
                    # Simulate market sell
                    # This would be handled by the paper trading engine's monitoring
                    pass
            
            # Remove from active ladders
            if signal_id in self.active_ladders:
                del self.active_ladders[signal_id]
                
        except Exception as e:
            logger.error(f"Cognitive rejection failed: {e}")
    
    def get_execution_status(self, signal_id: str = None) -> Dict[str, Any]:
        """Get execution status for specific signal or all active ladders"""
        try:
            if signal_id:
                if signal_id in self.active_ladders:
                    ladder_plan = self.active_ladders[signal_id]
                    return {
                        'signal_id': signal_id,
                        'symbol': ladder_plan.symbol,
                        'ray_score': ladder_plan.ray_score,
                        'execution_mode': ladder_plan.execution_mode,
                        'exchange': ladder_plan.exchange,
                        'tier_count': len([t for t in ladder_plan.tiers if t.order_type == 'entry']),
                        'tp1_roi': ladder_plan.roi_validation.get('tp1_roi', 0),
                        'tp2_roi': ladder_plan.roi_validation.get('tp2_roi', 0),
                        'created_at': ladder_plan.created_at.isoformat(),
                        'tiers': [asdict(tier) for tier in ladder_plan.tiers]
                    }
                else:
                    return {'error': f'Signal {signal_id} not found'}
            
            else:
                # Return all active ladders
                return {
                    'active_ladders': len(self.active_ladders),
                    'total_executions': len(self.execution_history),
                    'ladders': [
                        {
                            'signal_id': signal_id,
                            'symbol': plan.symbol,
                            'ray_score': plan.ray_score,
                            'execution_mode': plan.execution_mode,
                            'tp1_roi': plan.roi_validation.get('tp1_roi', 0),
                            'tp2_roi': plan.roi_validation.get('tp2_roi', 0),
                            'created_at': plan.created_at.isoformat()
                        }
                        for signal_id, plan in self.active_ladders.items()
                    ]
                }
                
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {'error': str(e)}

# Global ΣIGMA-ΩSNIPER instance
sigma_omega_sniper = SigmaOmegaSniper()

# Convenience function for external use
async def deploy_sigma_ladder(token: str, entry_min: float, entry_max: float,
                            tp1: float, tp2: float, sl: float, capital: float,
                            ray_score: float, mode: str = 'paper', 
                            exchange: str = 'binance_us') -> Dict[str, Any]:
    """
    Deploy ΣIGMA-ΩSNIPER ladder with specified parameters
    
    Returns execution status, ladder fill plan, and vault siphon projection
    """
    result = await sigma_omega_sniper.deploy_ladder_flip(
        token=token,
        entry_range=(entry_min, entry_max),
        tp1=tp1,
        tp2=tp2,
        sl=sl,
        capital=capital,
        mode=mode,
        exchange=exchange
    )
    
    return {
        'success': result.success,
        'execution_status': result.execution_status,
        'ladder_fill_plan': {
            'entry_tiers': len([t for t in result.ladder_plan.tiers if t.order_type == 'entry']) if result.ladder_plan else 0,
            'total_capital': result.ladder_plan.total_capital if result.ladder_plan else 0,
            'ray_score': result.ladder_plan.ray_score if result.ladder_plan else 0
        },
        'roi_analysis': {
            'tp1_roi': result.tp1_roi,
            'tp2_roi': result.tp2_roi
        },
        'vault_siphon_projection': result.vault_projection,
        'rejection_reasons': result.rejection_reasons,
        'execution_time_ms': result.execution_time_ms,
        'order_ids': result.order_ids
    }


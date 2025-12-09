"""
Advanced Real-Time Arbitrage Detection Engine - FIXED VERSION
Sophisticated arbitrage opportunity detection with:
- Real-time price streaming with memory management
- Advanced profit calculations with accurate fee modeling
- Risk-adjusted opportunity scoring with ML-ready features
- Market depth analysis and liquidity assessment
- Execution feasibility assessment with volatility analysis
- Performance optimization and error recovery
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json
import math

from enhanced_exchanges_fixed import ExchangeManager, ArbitrageOpportunity

logger = logging.getLogger(__name__)

@dataclass
class MarketDepth:
    """Market depth information for order book analysis"""
    exchange: str
    symbol: str
    bids: List[Tuple[float, float]]  # [(price, size), ...]
    asks: List[Tuple[float, float]]  # [(price, size), ...]
    timestamp: datetime
    
    def get_liquidity_score(self, target_amount: float = 1000.0) -> float:
        """Calculate liquidity score based on order book depth"""
        try:
            # Calculate how much slippage for target amount
            bid_liquidity = sum(price * size for price, size in self.bids[:5])
            ask_liquidity = sum(price * size for price, size in self.asks[:5])
            
            avg_liquidity = (bid_liquidity + ask_liquidity) / 2
            
            # Score from 0-100 based on liquidity vs target
            score = min(100, (avg_liquidity / target_amount) * 100)
            return score
            
        except Exception:
            return 0.0

@dataclass
class ArbitrageSignal:
    """Enhanced arbitrage signal with comprehensive risk metrics"""
    opportunity: ArbitrageOpportunity
    confidence_score: float  # 0-100
    execution_risk: str  # 'low', 'medium', 'high'
    market_impact: float  # Expected slippage %
    liquidity_score: float  # 0-100
    volatility_risk: float  # Recent price volatility
    time_decay_risk: float  # How quickly opportunity might disappear
    recommended_size: float  # Optimal position size
    priority_score: float  # Overall priority ranking
    
    # Additional risk factors
    correlation_risk: float = 0.0  # Cross-exchange correlation
    execution_time_estimate: float = 0.0  # Estimated execution time in seconds
    profit_confidence: float = 0.0  # Confidence in profit estimate

@dataclass
class PriceHistory:
    """Price history tracking for volatility analysis with memory management"""
    symbol: str
    exchange: str
    max_history: int = 100  # Limit memory usage
    prices: deque = field(default_factory=lambda: deque(maxlen=100))
    timestamps: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def __post_init__(self):
        """Ensure deques have correct maxlen"""
        if not hasattr(self.prices, 'maxlen') or self.prices.maxlen != self.max_history:
            self.prices = deque(self.prices, maxlen=self.max_history)
        if not hasattr(self.timestamps, 'maxlen') or self.timestamps.maxlen != self.max_history:
            self.timestamps = deque(self.timestamps, maxlen=self.max_history)
    
    def add_price(self, price: float, timestamp: datetime = None):
        """Add price with automatic memory management"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Validate inputs
        if not isinstance(price, (int, float)) or price <= 0:
            logger.warning(f"Invalid price {price} for {self.symbol} on {self.exchange}")
            return
        
        self.prices.append(float(price))
        self.timestamps.append(timestamp)
    
    def get_volatility(self, window_minutes: int = 5) -> float:
        """Calculate price volatility over specified window with improved algorithm"""
        if len(self.prices) < 2:
            return 0.0
        
        try:
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_prices = []
            
            for price, timestamp in zip(self.prices, self.timestamps):
                if timestamp >= cutoff_time:
                    recent_prices.append(price)
            
            if len(recent_prices) < 2:
                # Use all available data if insufficient recent data
                recent_prices = list(self.prices)
            
            if len(recent_prices) < 2:
                return 0.0
            
            # Calculate coefficient of variation (std dev / mean)
            mean_price = statistics.mean(recent_prices)
            if mean_price == 0:
                return 0.0
            
            # Use sample standard deviation for better accuracy
            if len(recent_prices) > 1:
                std_dev = statistics.stdev(recent_prices)
            else:
                std_dev = 0.0
            
            volatility = (std_dev / mean_price) * 100  # Return as percentage
            
            # Cap volatility at reasonable maximum
            return min(volatility, 100.0)
            
        except Exception as e:
            logger.warning(f"Error calculating volatility for {self.symbol}: {e}")
            return 0.0
    
    def get_trend(self, window_minutes: int = 10) -> float:
        """Calculate price trend over specified window (-1 to 1)"""
        if len(self.prices) < 2:
            return 0.0
        
        try:
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_data = []
            
            for price, timestamp in zip(self.prices, self.timestamps):
                if timestamp >= cutoff_time:
                    recent_data.append((price, timestamp))
            
            if len(recent_data) < 2:
                recent_data = list(zip(self.prices, self.timestamps))
            
            if len(recent_data) < 2:
                return 0.0
            
            # Simple linear trend calculation
            first_price = recent_data[0][0]
            last_price = recent_data[-1][0]
            
            if first_price == 0:
                return 0.0
            
            trend = (last_price - first_price) / first_price
            
            # Normalize to -1 to 1 range
            return max(-1.0, min(1.0, trend * 10))
            
        except Exception as e:
            logger.warning(f"Error calculating trend for {self.symbol}: {e}")
            return 0.0

class ArbitrageEngine:
    """Advanced arbitrage detection and analysis engine with comprehensive optimization"""
    
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
        
        # Price history with memory management
        self.price_history: Dict[str, Dict[str, PriceHistory]] = defaultdict(dict)
        
        # Opportunity tracking with automatic cleanup
        self.opportunity_history: deque = deque(maxlen=1000)  # Limit memory usage
        self.active_monitors: Dict[str, asyncio.Task] = {}
        self.callbacks: List[Callable] = []
        
        # Performance tracking
        self.statistics = {
            'total_opportunities': 0,
            'recent_opportunities': 0,
            'last_reset': datetime.now(),
            'average_profit': 0.0,
            'best_profit': 0.0,
            'processing_times': deque(maxlen=100),
            'error_count': 0,
            'success_count': 0
        }
        
        # Enhanced configuration with validation
        self.config = {
            'min_profit_threshold': 0.2,  # Minimum profit %
            'max_execution_risk': 'medium',  # Maximum acceptable risk
            'min_confidence_score': 70.0,  # Minimum confidence
            'price_update_interval': 5,  # Seconds between price updates
            'volatility_window': 5,  # Minutes for volatility calculation
            'max_opportunities': 100,  # Maximum opportunities to track
            'cleanup_interval': 300,  # Seconds between cleanup operations
            'correlation_threshold': 0.8,  # Maximum correlation for risk assessment
            'min_liquidity_score': 50.0,  # Minimum liquidity score
            'max_volatility_risk': 80.0,  # Maximum volatility risk
        }
        
        # Risk assessment weights
        self.risk_weights = {
            'volatility': 0.3,
            'liquidity': 0.25,
            'execution_time': 0.2,
            'market_impact': 0.15,
            'correlation': 0.1
        }
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start automatic cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of old data"""
        while True:
            try:
                await asyncio.sleep(self.config['cleanup_interval'])
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old price history and opportunities"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            # Clean up old opportunities
            initial_count = len(self.opportunity_history)
            self.opportunity_history = deque(
                [opp for opp in self.opportunity_history if opp.opportunity.timestamp > cutoff_time],
                maxlen=self.config['max_opportunities']
            )
            
            cleaned_count = initial_count - len(self.opportunity_history)
            if cleaned_count > 0:
                logger.debug(f"Cleaned up {cleaned_count} old opportunities")
            
            # Reset recent statistics hourly
            if (datetime.now() - self.statistics['last_reset']).total_seconds() > 3600:
                self.statistics['recent_opportunities'] = 0
                self.statistics['last_reset'] = datetime.now()
                logger.debug("Reset recent statistics")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def add_callback(self, callback: Callable[[List[ArbitrageSignal]], None]):
        """Add callback for new arbitrage signals"""
        if callable(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError("Callback must be callable")

    async def start_monitoring(self, symbols: List[str]):
        """Start real-time monitoring for arbitrage opportunities"""
        logger.info(f"🚀 Starting arbitrage monitoring for {len(symbols)} symbols")
        
        # Validate symbols
        valid_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and '/' in symbol:
                valid_symbols.append(symbol)
            else:
                logger.warning(f"Invalid symbol format: {symbol}")
        
        if not valid_symbols:
            raise ValueError("No valid symbols provided")
        
        # Stop existing monitors
        await self.stop_monitoring()
        
        # Start new monitors
        for symbol in valid_symbols:
            task = asyncio.create_task(self._monitor_symbol(symbol))
            self.active_monitors[symbol] = task
            logger.info(f"📊 Started monitoring {symbol}")
        
        logger.info(f"✅ Monitoring active for {len(self.active_monitors)} symbols")

    async def stop_monitoring(self):
        """Stop all active monitoring"""
        if self.active_monitors:
            logger.info(f"🛑 Stopping {len(self.active_monitors)} monitors")
            
            for symbol, task in self.active_monitors.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.debug(f"Stopped monitoring {symbol}")
            
            self.active_monitors.clear()
        
        # Stop cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _monitor_symbol(self, symbol: str):
        """Monitor a single symbol for arbitrage opportunities"""
        logger.debug(f"Starting monitor for {symbol}")
        
        while True:
            try:
                start_time = time.time()
                
                # Get current prices
                prices = await self.exchange_manager.get_price_map(symbol)
                
                if len(prices) < 2:
                    logger.debug(f"Insufficient price data for {symbol}: {len(prices)} exchanges")
                    await asyncio.sleep(self.config['price_update_interval'])
                    continue
                
                # Update price history
                timestamp = datetime.now()
                for exchange, price in prices.items():
                    if exchange not in self.price_history[symbol]:
                        self.price_history[symbol][exchange] = PriceHistory(symbol, exchange)
                    
                    self.price_history[symbol][exchange].add_price(price, timestamp)
                
                # Detect arbitrage opportunities
                opportunities = await self._detect_opportunities(symbol, prices)
                
                # Process and score opportunities
                signals = []
                for opp in opportunities:
                    signal = await self._create_arbitrage_signal(opp)
                    if signal and self._meets_criteria(signal):
                        signals.append(signal)
                        self.opportunity_history.append(signal)
                
                # Update statistics
                processing_time = (time.time() - start_time) * 1000
                self.statistics['processing_times'].append(processing_time)
                self.statistics['success_count'] += 1
                
                if signals:
                    self.statistics['total_opportunities'] += len(signals)
                    self.statistics['recent_opportunities'] += len(signals)
                    
                    # Update profit statistics
                    profits = [s.opportunity.estimated_profit_percent for s in signals]
                    self.statistics['average_profit'] = statistics.mean(profits)
                    self.statistics['best_profit'] = max(profits)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            await callback(signals)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                
                await asyncio.sleep(self.config['price_update_interval'])
                
            except asyncio.CancelledError:
                logger.debug(f"Monitor for {symbol} cancelled")
                break
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")
                self.statistics['error_count'] += 1
                await asyncio.sleep(self.config['price_update_interval'] * 2)  # Back off on error

    async def _detect_opportunities(self, symbol: str, prices: Dict[str, float]) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities with enhanced profit calculation"""
        opportunities = []
        exchanges = list(prices.keys())
        
        # Compare all exchange pairs
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                buy_exchange = exchanges[i]
                sell_exchange = exchanges[j]
                buy_price = prices[buy_exchange]
                sell_price = prices[sell_exchange]
                
                # Ensure buy_price < sell_price
                if buy_price > sell_price:
                    buy_exchange, sell_exchange = sell_exchange, buy_exchange
                    buy_price, sell_price = sell_price, buy_price
                
                # Calculate spread
                if buy_price <= 0:
                    continue
                
                spread_percent = ((sell_price - buy_price) / buy_price) * 100
                
                # Calculate estimated profit after fees
                buy_fee = self.exchange_manager.exchange_fees.get(buy_exchange, {}).get('taker', 0.001)
                sell_fee = self.exchange_manager.exchange_fees.get(sell_exchange, {}).get('taker', 0.001)
                
                total_fees_percent = (buy_fee + sell_fee) * 100
                estimated_profit = spread_percent - total_fees_percent
                
                if estimated_profit >= self.config['min_profit_threshold']:
                    # Estimate order sizes (would need real order book data for accuracy)
                    min_order_size = max(10.0, buy_price * 0.01)  # $10 minimum or 0.01 units
                    max_order_size = min(10000.0, buy_price * 100)  # $10k maximum or 100 units
                    
                    opportunities.append(ArbitrageOpportunity(
                        symbol=symbol,
                        buy_exchange=buy_exchange,
                        sell_exchange=sell_exchange,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        spread_percent=spread_percent,
                        estimated_profit_percent=estimated_profit,
                        min_order_size=min_order_size,
                        max_order_size=max_order_size,
                        timestamp=datetime.now()
                    ))
        
        return opportunities

    async def _create_arbitrage_signal(self, opportunity: ArbitrageOpportunity) -> Optional[ArbitrageSignal]:
        """Create comprehensive arbitrage signal with risk analysis"""
        try:
            symbol = opportunity.symbol
            buy_exchange = opportunity.buy_exchange
            sell_exchange = opportunity.sell_exchange
            
            # Calculate volatility risk
            volatility_risk = self._calculate_volatility_risk(symbol, buy_exchange, sell_exchange)
            
            # Calculate liquidity score (simplified - would need order book data)
            liquidity_score = self._estimate_liquidity_score(opportunity)
            
            # Calculate market impact
            market_impact = self._estimate_market_impact(opportunity)
            
            # Calculate time decay risk
            time_decay_risk = self._calculate_time_decay_risk(opportunity)
            
            # Calculate execution risk
            execution_risk = self._assess_execution_risk(volatility_risk, liquidity_score, market_impact)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                opportunity, volatility_risk, liquidity_score, market_impact
            )
            
            # Calculate recommended size
            recommended_size = self._calculate_recommended_size(opportunity, volatility_risk, liquidity_score)
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                opportunity.estimated_profit_percent, confidence_score, execution_risk
            )
            
            # Additional risk factors
            correlation_risk = self._calculate_correlation_risk(buy_exchange, sell_exchange)
            execution_time_estimate = self._estimate_execution_time(opportunity)
            profit_confidence = min(confidence_score, 100 - volatility_risk)
            
            return ArbitrageSignal(
                opportunity=opportunity,
                confidence_score=confidence_score,
                execution_risk=execution_risk,
                market_impact=market_impact,
                liquidity_score=liquidity_score,
                volatility_risk=volatility_risk,
                time_decay_risk=time_decay_risk,
                recommended_size=recommended_size,
                priority_score=priority_score,
                correlation_risk=correlation_risk,
                execution_time_estimate=execution_time_estimate,
                profit_confidence=profit_confidence
            )
            
        except Exception as e:
            logger.error(f"Error creating arbitrage signal: {e}")
            return None

    def _calculate_volatility_risk(self, symbol: str, buy_exchange: str, sell_exchange: str) -> float:
        """Calculate volatility risk for the arbitrage pair"""
        try:
            volatilities = []
            
            for exchange in [buy_exchange, sell_exchange]:
                if exchange in self.price_history[symbol]:
                    vol = self.price_history[symbol][exchange].get_volatility()
                    volatilities.append(vol)
            
            if not volatilities:
                return 50.0  # Default medium risk
            
            # Use maximum volatility as risk indicator
            max_volatility = max(volatilities)
            
            # Normalize to 0-100 scale
            return min(100.0, max_volatility)
            
        except Exception:
            return 50.0

    def _estimate_liquidity_score(self, opportunity: ArbitrageOpportunity) -> float:
        """Estimate liquidity score based on available data"""
        try:
            # Simplified liquidity estimation based on price and exchange
            base_score = 70.0
            
            # Adjust based on exchanges (some have better liquidity)
            exchange_scores = {
                'binanceus': 85.0,
                'kraken': 75.0,
                'okx': 80.0
            }
            
            buy_score = exchange_scores.get(opportunity.buy_exchange, 60.0)
            sell_score = exchange_scores.get(opportunity.sell_exchange, 60.0)
            
            # Average the scores
            avg_score = (buy_score + sell_score) / 2
            
            # Adjust based on price level (higher prices generally have better liquidity)
            if opportunity.buy_price > 1000:
                avg_score += 10
            elif opportunity.buy_price < 1:
                avg_score -= 10
            
            return max(0.0, min(100.0, avg_score))
            
        except Exception:
            return 50.0

    def _estimate_market_impact(self, opportunity: ArbitrageOpportunity) -> float:
        """Estimate market impact as slippage percentage"""
        try:
            # Simplified market impact estimation
            base_impact = 0.05  # 0.05% base impact
            
            # Adjust based on profit margin (higher margins suggest less liquid markets)
            if opportunity.estimated_profit_percent > 1.0:
                base_impact += 0.1
            elif opportunity.estimated_profit_percent > 0.5:
                base_impact += 0.05
            
            # Adjust based on order size relative to typical volumes
            size_ratio = opportunity.max_order_size / 10000.0  # Assume $10k is typical
            base_impact += size_ratio * 0.1
            
            return min(1.0, base_impact)  # Cap at 1%
            
        except Exception:
            return 0.1

    def _calculate_time_decay_risk(self, opportunity: ArbitrageOpportunity) -> float:
        """Calculate how quickly the opportunity might disappear"""
        try:
            # Higher profit opportunities tend to disappear faster
            base_decay = opportunity.estimated_profit_percent * 10
            
            # Adjust based on volatility
            symbol = opportunity.symbol
            avg_volatility = 0.0
            vol_count = 0
            
            for exchange in [opportunity.buy_exchange, opportunity.sell_exchange]:
                if exchange in self.price_history[symbol]:
                    vol = self.price_history[symbol][exchange].get_volatility()
                    avg_volatility += vol
                    vol_count += 1
            
            if vol_count > 0:
                avg_volatility /= vol_count
                base_decay += avg_volatility
            
            return min(100.0, base_decay)
            
        except Exception:
            return 50.0

    def _assess_execution_risk(self, volatility_risk: float, liquidity_score: float, market_impact: float) -> str:
        """Assess overall execution risk level"""
        try:
            # Weighted risk score
            risk_score = (
                volatility_risk * self.risk_weights['volatility'] +
                (100 - liquidity_score) * self.risk_weights['liquidity'] +
                market_impact * 100 * self.risk_weights['market_impact']
            )
            
            if risk_score < 30:
                return 'low'
            elif risk_score < 60:
                return 'medium'
            else:
                return 'high'
                
        except Exception:
            return 'medium'

    def _calculate_confidence_score(
        self, 
        opportunity: ArbitrageOpportunity, 
        volatility_risk: float, 
        liquidity_score: float, 
        market_impact: float
    ) -> float:
        """Calculate confidence score for the opportunity"""
        try:
            # Start with base confidence based on profit margin
            base_confidence = min(90.0, opportunity.estimated_profit_percent * 30)
            
            # Adjust for risk factors
            confidence = base_confidence
            confidence -= volatility_risk * 0.3
            confidence += (liquidity_score - 50) * 0.4
            confidence -= market_impact * 100 * 0.2
            
            # Bonus for established exchanges
            established_exchanges = {'binanceus', 'kraken', 'okx'}
            if (opportunity.buy_exchange in established_exchanges and 
                opportunity.sell_exchange in established_exchanges):
                confidence += 10
            
            return max(0.0, min(100.0, confidence))
            
        except Exception:
            return 50.0

    def _calculate_recommended_size(
        self, 
        opportunity: ArbitrageOpportunity, 
        volatility_risk: float, 
        liquidity_score: float
    ) -> float:
        """Calculate recommended position size"""
        try:
            # Start with a base size
            base_size = 1000.0  # $1000 base
            
            # Adjust for risk
            risk_multiplier = 1.0
            
            if volatility_risk < 30:
                risk_multiplier *= 1.5
            elif volatility_risk > 70:
                risk_multiplier *= 0.5
            
            if liquidity_score > 80:
                risk_multiplier *= 1.3
            elif liquidity_score < 50:
                risk_multiplier *= 0.7
            
            # Adjust for profit potential
            profit_multiplier = min(2.0, 1 + opportunity.estimated_profit_percent / 2)
            
            recommended = base_size * risk_multiplier * profit_multiplier
            
            # Ensure within bounds
            return max(
                opportunity.min_order_size,
                min(opportunity.max_order_size, recommended)
            )
            
        except Exception:
            return opportunity.min_order_size

    def _calculate_priority_score(self, profit_percent: float, confidence_score: float, execution_risk: str) -> float:
        """Calculate overall priority score"""
        try:
            # Base score from profit and confidence
            base_score = (profit_percent * 30 + confidence_score * 0.7)
            
            # Adjust for execution risk
            risk_multipliers = {'low': 1.2, 'medium': 1.0, 'high': 0.7}
            risk_multiplier = risk_multipliers.get(execution_risk, 1.0)
            
            return base_score * risk_multiplier
            
        except Exception:
            return 0.0

    def _calculate_correlation_risk(self, exchange1: str, exchange2: str) -> float:
        """Calculate correlation risk between exchanges"""
        # Simplified correlation risk (would need historical data for accuracy)
        if exchange1 == exchange2:
            return 100.0
        
        # Some exchanges are more correlated than others
        correlation_matrix = {
            ('binanceus', 'okx'): 0.8,
            ('binanceus', 'kraken'): 0.7,
            ('kraken', 'okx'): 0.75
        }
        
        pair = tuple(sorted([exchange1, exchange2]))
        return correlation_matrix.get(pair, 0.6) * 100

    def _estimate_execution_time(self, opportunity: ArbitrageOpportunity) -> float:
        """Estimate execution time in seconds"""
        # Base execution time
        base_time = 10.0  # 10 seconds base
        
        # Adjust based on exchanges (some are faster)
        exchange_speeds = {
            'binanceus': 1.0,
            'kraken': 1.5,
            'okx': 1.2
        }
        
        buy_speed = exchange_speeds.get(opportunity.buy_exchange, 1.5)
        sell_speed = exchange_speeds.get(opportunity.sell_exchange, 1.5)
        
        # Use the slower exchange as bottleneck
        return base_time * max(buy_speed, sell_speed)

    def _meets_criteria(self, signal: ArbitrageSignal) -> bool:
        """Check if signal meets minimum criteria"""
        try:
            criteria = [
                signal.confidence_score >= self.config['min_confidence_score'],
                signal.liquidity_score >= self.config['min_liquidity_score'],
                signal.volatility_risk <= self.config['max_volatility_risk'],
                signal.opportunity.estimated_profit_percent >= self.config['min_profit_threshold']
            ]
            
            # Check execution risk
            if self.config['max_execution_risk'] == 'low':
                criteria.append(signal.execution_risk == 'low')
            elif self.config['max_execution_risk'] == 'medium':
                criteria.append(signal.execution_risk in ['low', 'medium'])
            
            return all(criteria)
            
        except Exception:
            return False

    def get_top_opportunities(self, limit: int = 10) -> List[ArbitrageSignal]:
        """Get top arbitrage opportunities sorted by priority"""
        try:
            # Filter recent opportunities (last 5 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=5)
            recent_opportunities = [
                signal for signal in self.opportunity_history
                if signal.opportunity.timestamp > cutoff_time
            ]
            
            # Sort by priority score
            sorted_opportunities = sorted(
                recent_opportunities,
                key=lambda x: x.priority_score,
                reverse=True
            )
            
            return sorted_opportunities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top opportunities: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        try:
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_count = sum(
                1 for signal in self.opportunity_history
                if signal.opportunity.timestamp > recent_cutoff
            )
            
            avg_processing_time = 0.0
            if self.statistics['processing_times']:
                avg_processing_time = statistics.mean(self.statistics['processing_times'])
            
            return {
                'total_opportunities': self.statistics['total_opportunities'],
                'recent_opportunities': recent_count,
                'active_monitors': len(self.active_monitors),
                'average_profit': self.statistics['average_profit'],
                'best_profit': self.statistics['best_profit'],
                'success_rate': (
                    self.statistics['success_count'] / 
                    max(1, self.statistics['success_count'] + self.statistics['error_count'])
                ) * 100,
                'average_processing_time_ms': avg_processing_time,
                'memory_usage': {
                    'opportunity_history_size': len(self.opportunity_history),
                    'price_history_symbols': len(self.price_history),
                    'total_price_points': sum(
                        len(exchange_data) for symbol_data in self.price_history.values()
                        for exchange_data in symbol_data.values()
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def format_signal_report(self, signals: List[ArbitrageSignal]) -> str:
        """Format arbitrage signals into a comprehensive report"""
        if not signals:
            return "🔍 No arbitrage opportunities currently detected.\n"
        
        report = "🚨 **ARBITRAGE OPPORTUNITIES DETECTED**\n"
        report += "=" * 60 + "\n\n"
        
        for i, signal in enumerate(signals[:5], 1):  # Top 5 opportunities
            opp = signal.opportunity
            
            report += f"**#{i} - {opp.symbol}**\n"
            report += f"• **Profit**: {opp.estimated_profit_percent:.3f}% (${opp.estimated_profit_percent/100 * signal.recommended_size:.2f})\n"
            report += f"• **Route**: Buy on {opp.buy_exchange.upper()} @ ${opp.buy_price:.4f} → Sell on {opp.sell_exchange.upper()} @ ${opp.sell_price:.4f}\n"
            report += f"• **Spread**: {opp.spread_percent:.3f}%\n"
            report += f"• **Confidence**: {signal.confidence_score:.1f}% | **Risk**: {signal.execution_risk.title()}\n"
            report += f"• **Recommended Size**: ${signal.recommended_size:.2f}\n"
            report += f"• **Priority Score**: {signal.priority_score:.2f}\n"
            
            # Risk breakdown
            report += f"• **Risk Analysis**:\n"
            report += f"  - Volatility: {signal.volatility_risk:.1f}%\n"
            report += f"  - Liquidity: {signal.liquidity_score:.1f}%\n"
            report += f"  - Market Impact: {signal.market_impact:.3f}%\n"
            report += f"  - Time Decay: {signal.time_decay_risk:.1f}%\n"
            
            report += f"• **Execution Est.**: {signal.execution_time_estimate:.1f}s\n"
            report += f"• **Age**: {(datetime.now() - opp.timestamp).total_seconds():.1f}s\n\n"
        
        if len(signals) > 5:
            report += f"... and {len(signals) - 5} more opportunities\n\n"
        
        # Summary statistics
        avg_profit = statistics.mean([s.opportunity.estimated_profit_percent for s in signals])
        avg_confidence = statistics.mean([s.confidence_score for s in signals])
        low_risk_count = len([s for s in signals if s.execution_risk == 'low'])
        
        report += f"**📊 Summary**:\n"
        report += f"• Total Opportunities: {len(signals)}\n"
        report += f"• Average Profit: {avg_profit:.3f}%\n"
        report += f"• Average Confidence: {avg_confidence:.1f}%\n"
        report += f"• Low Risk Opportunities: {low_risk_count}\n"
        
        report += f"\n⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        return report

# Example usage
async def example_usage():
    """Example of how to use the enhanced arbitrage engine"""
    
    # Initialize exchange manager
    from enhanced_exchanges_fixed import ExchangeManager
    exchange_manager = ExchangeManager()
    await exchange_manager.initialize_exchanges()
    
    # Create arbitrage engine
    engine = ArbitrageEngine(exchange_manager)
    
    # Add callback for new opportunities
    async def opportunity_callback(signals: List[ArbitrageSignal]):
        if signals:
            print(f"🚨 {len(signals)} new opportunities detected!")
            for signal in signals[:3]:  # Show top 3
                opp = signal.opportunity
                print(f"  {opp.symbol}: {opp.estimated_profit_percent:.3f}% profit")
    
    engine.add_callback(opportunity_callback)
    
    # Start monitoring
    await engine.start_monitoring(['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    
    # Let it run for a while
    await asyncio.sleep(60)
    
    # Get results
    opportunities = engine.get_top_opportunities(10)
    if opportunities:
        report = engine.format_signal_report(opportunities)
        print(report)
    
    # Get statistics
    stats = engine.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
    
    # Stop monitoring
    await engine.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(example_usage())

"""
🧠 ShadowScope - Core Market Intelligence Layer

The "eye of the market" - real-time price, volume, volatility, and correlation analytics
across 4 exchanges and 8 trading pairs.

Target Performance: 640 ticks/second processing
Data Quality: >95% uptime
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import logging

logger = logging.getLogger("shadow_sdk.scope")


class ShadowScope:
    """
    🧠 ShadowScope - Core Intelligence Layer
    
    Your master market scanner for real-time price, volume, volatility,
    and correlation analytics.
    
    Features:
        - Real-time tick processing (target: 640/sec)
        - Multi-exchange monitoring (Coinbase, OKX, Kraken, Binance)
        - Volume & volatility tracking
        - Correlation matrix generation
        - VWAP calculations
        - Data quality monitoring
    
    Example:
        >>> scope = ShadowScope()
        >>> await scope.start_scanner()
        >>> intelligence = await scope.get_market_intelligence()
        >>> print(intelligence['current_prices'])
    """
    
    def __init__(self, exchanges: Optional[List[str]] = None, pairs: Optional[List[str]] = None):
        """
        Initialize ShadowScope intelligence layer.
        
        Args:
            exchanges: List of exchange names (default: ["coinbase", "okx", "kraken", "binance"])
            pairs: List of trading pairs (default: 8 major pairs)
        """
        from . import EXCHANGES, PAIRS
        
        self.exchanges = exchanges if exchanges else EXCHANGES
        self.pairs = pairs if pairs else PAIRS
        self.market_data: Dict[str, Dict[str, Any]] = {}
        self.tick_history: Dict[str, Dict[str, deque]] = {}
        self.tick_count = 0
        self.start_time = time.time()
        self.data_quality = 100.0
        self.is_running = False
        
        # Initialize tick history
        for exchange in self.exchanges:
            self.tick_history[exchange] = {}
            for pair in self.pairs:
                self.tick_history[exchange][pair] = deque(maxlen=100)
        
        logger.info(f"🧠 ShadowScope initialized: {len(self.exchanges)} exchanges, {len(self.pairs)} pairs")
    
    async def start_scanner(self, interval: float = 1.0):
        """
        Start the real-time market scanner.
        
        Args:
            interval: Scan interval in seconds (default: 1.0)
        """
        self.is_running = True
        logger.info("🚀 ShadowScope scanner starting...")
        
        while self.is_running:
            start_cycle = time.time()
            
            # Fetch market data for all exchange-pair combinations
            tasks = []
            for exchange in self.exchanges:
                for pair in self.pairs:
                    tasks.append(self._fetch_market_tick(exchange, pair))
            
            ticks = await asyncio.gather(*tasks)
            
            for tick in ticks:
                await self._process_tick(tick['exchange'], tick['pair'], tick)
            
            # Performance metrics
            cycle_time = time.time() - start_cycle
            ticks_per_sec = len(ticks) / cycle_time if cycle_time > 0 else 0
            
            if self.tick_count % 100 == 0:
                logger.info(f"📊 ShadowScope: {ticks_per_sec:.0f} ticks/sec | Quality: {self.data_quality:.1f}%")
            
            await asyncio.sleep(max(0, interval - cycle_time))
    
    def stop_scanner(self):
        """Stop the market scanner."""
        self.is_running = False
        logger.info("🛑 ShadowScope scanner stopped")
    
    async def _fetch_market_tick(self, exchange: str, pair: str) -> Dict[str, Any]:
        """Fetch a single market data tick (mock implementation)."""
        # In production, this would use ccxt or exchange-specific APIs
        await asyncio.sleep(0.01)  # Simulate network latency
        
        base_prices = {
            "BTC/USD": 60000, "ETH/USD": 3000, "SOL/USD": 150, "XRP/USD": 0.5,
            "ADA/USD": 0.6, "DOGE/USD": 0.15, "LTC/USD": 70, "BNB/USD": 500
        }
        
        price = base_prices.get(pair, 100) * (1 + (time.time() % 100 / 10000 - 0.005))
        volume = 1000000 * (1 + (time.time() % 100 / 5000))
        
        return {
            "exchange": exchange,
            "pair": pair,
            "price": round(price, 2),
            "volume": round(volume, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _process_tick(self, exchange: str, pair: str, data: Dict[str, Any]):
        """Process a single market tick."""
        if exchange not in self.market_data:
            self.market_data[exchange] = {}
        
        self.market_data[exchange][pair] = data
        self.tick_history[exchange][pair].append(data['price'])
        self.tick_count += 1
    
    async def get_market_intelligence(self) -> Dict[str, Any]:
        """
        Get comprehensive market intelligence snapshot.
        
        Returns:
            Dict containing:
                - current_prices: Latest prices across exchanges
                - volumes: Trading volumes
                - volatility: Historical volatility metrics
                - correlations: Pair correlation matrix
                - vwap: Volume-weighted average prices
                - health: System health metrics
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "health": await self.get_health_status(),
            "current_prices": self._get_current_prices(),
            "volumes": self._get_volumes(),
            "volatility": await self._calculate_volatility_all(),
            "correlations": await self._calculate_correlations(),
            "vwap": self._calculate_vwap()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get scanner health metrics."""
        uptime = time.time() - self.start_time
        return {
            "exchanges_monitored": len(self.exchanges),
            "pairs_monitored": len(self.pairs),
            "data_quality_percent": self.data_quality,
            "tick_count": self.tick_count,
            "uptime_seconds": uptime,
            "ticks_per_second": self.tick_count / uptime if uptime > 0 else 0,
            "is_running": self.is_running
        }
    
    def _get_current_prices(self) -> Dict[str, Dict[str, float]]:
        """Get latest prices for all exchange-pair combinations."""
        prices = {}
        for exchange, pairs_data in self.market_data.items():
            prices[exchange] = {pair: data['price'] for pair, data in pairs_data.items()}
        return prices
    
    def _get_volumes(self) -> Dict[str, Dict[str, float]]:
        """Get trading volumes for all exchange-pair combinations."""
        volumes = {}
        for exchange, pairs_data in self.market_data.items():
            volumes[exchange] = {pair: data['volume'] for pair, data in pairs_data.items()}
        return volumes
    
    async def _calculate_volatility_all(self) -> Dict[str, Dict[str, float]]:
        """Calculate historical volatility for all pairs."""
        volatility = {}
        for exchange in self.exchanges:
            volatility[exchange] = {}
            for pair in self.pairs:
                volatility[exchange][pair] = await self._calculate_volatility(exchange, pair)
        return volatility
    
    async def _calculate_volatility(self, exchange: str, pair: str) -> float:
        """Calculate historical volatility for a single pair."""
        prices = list(self.tick_history[exchange][pair])
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        if not returns:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        variance = sum([(x - avg_return)**2 for x in returns]) / len(returns)
        return variance**0.5
    
    async def _calculate_correlations(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between pairs."""
        # Simplified correlation - in production would use proper statistical methods
        correlation_matrix = {}
        all_pairs = list(set(p for ex_data in self.market_data.values() for p in ex_data.keys()))
        
        for p1 in all_pairs:
            correlation_matrix[p1] = {}
            for p2 in all_pairs:
                if p1 == p2:
                    correlation_matrix[p1][p2] = 1.0
                else:
                    # Mock correlation
                    correlation_matrix[p1][p2] = round(0.5 + (time.time() % 100 / 200 - 0.25), 2)
        
        return correlation_matrix
    
    def _calculate_vwap(self) -> Dict[str, float]:
        """Calculate volume-weighted average price for each pair."""
        vwap = {}
        for pair in self.pairs:
            # Simplified VWAP calculation
            total_volume = 0
            volume_price = 0
            for exchange in self.exchanges:
                if exchange in self.market_data and pair in self.market_data[exchange]:
                    data = self.market_data[exchange][pair]
                    total_volume += data['volume']
                    volume_price += data['price'] * data['volume']
            
            vwap[pair] = volume_price / total_volume if total_volume > 0 else 0
        
        return vwap


"""
⚡ ShadowPulse - Live Signal Streaming & Heartbeat

Real-time opportunity detection and signal broadcasting to the orchestrator.
Monitors micro-movements, liquidity shifts, and breakout patterns.

Target: <100ms signal latency
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
import logging

logger = logging.getLogger("shadow_sdk.pulse")


class ShadowPulse:
    """
    ⚡ ShadowPulse - Live Signal & Heartbeat Layer
    
    Real-time opportunity detection and signal streaming for the trading engine.
    
    Features:
        - Micro-movement detection (0.05% scalping opportunities)
        - Liquidity shift monitoring
        - Breakout pattern recognition
        - Signal broadcasting to subscribers
        - Heartbeat monitoring (<100ms latency)
    
    Example:
        >>> pulse = ShadowPulse()
        >>> pulse.subscribe(my_strategy_handler)
        >>> await pulse.start_streaming()
    """
    
    def __init__(self):
        """Initialize ShadowPulse signal streaming layer."""
        self.subscribers: List[Callable] = []
        self.signals_sent = 0
        self.is_streaming = False
        self.heartbeat_interval = 1.0  # seconds
        self.signal_history: List[Dict[str, Any]] = []
        
        logger.info("⚡ ShadowPulse initialized")
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to live signal stream.
        
        Args:
            callback: Function to call when signals are detected
        """
        self.subscribers.append(callback)
        logger.info(f"📡 New subscriber added: {len(self.subscribers)} total")
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from signal stream."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"📡 Subscriber removed: {len(self.subscribers)} remaining")
    
    async def start_streaming(self, interval: float = 0.1):
        """
        Start live signal streaming.
        
        Args:
            interval: Signal check interval in seconds (default: 0.1 for 10Hz)
        """
        self.is_streaming = True
        logger.info("🚀 ShadowPulse streaming started...")
        
        # Start heartbeat monitor
        heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        
        while self.is_streaming:
            start_time = time.time()
            
            # Detect opportunities
            signals = await self._detect_opportunities()
            
            # Broadcast to subscribers
            for signal in signals:
                await self._broadcast_signal(signal)
            
            # Maintain target latency
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, interval - elapsed))
        
        heartbeat_task.cancel()
    
    def stop_streaming(self):
        """Stop signal streaming."""
        self.is_streaming = False
        logger.info("🛑 ShadowPulse streaming stopped")
    
    async def _detect_opportunities(self) -> List[Dict[str, Any]]:
        """
        Detect trading opportunities from live market data.
        
        Returns:
            List of detected signals
        """
        # In production, this would integrate with ShadowScope
        # and apply strategy-specific filters
        
        signals = []
        
        # Mock opportunity detection
        if time.time() % 10 < 1:  # Detect opportunity every 10 seconds
            signals.append({
                "type": "micro_movement",
                "pair": "BTC/USD",
                "exchanges": ["coinbase", "okx"],
                "spread": 0.0005,  # 0.05%
                "direction": "up",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
                "latency_ms": 45
            })
        
        return signals
    
    async def _broadcast_signal(self, signal: Dict[str, Any]):
        """Broadcast signal to all subscribers."""
        self.signals_sent += 1
        self.signal_history.append(signal)
        
        # Keep only last 100 signals
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]
        
        logger.info(f"📡 Signal broadcast: {signal['type']} on {signal['pair']} ({signal['spread']:.4%})")
        
        # Call all subscribers
        for callback in self.subscribers:
            try:
                await callback(signal) if asyncio.iscoroutinefunction(callback) else callback(signal)
            except Exception as e:
                logger.error(f"❌ Subscriber callback error: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor system heartbeat and latency."""
        while self.is_streaming:
            heartbeat = {
                "timestamp": datetime.now().isoformat(),
                "signals_sent": self.signals_sent,
                "subscribers": len(self.subscribers),
                "is_streaming": self.is_streaming
            }
            logger.debug(f"💓 Heartbeat: {heartbeat}")
            await asyncio.sleep(self.heartbeat_interval)
    
    def get_signal_stats(self) -> Dict[str, Any]:
        """Get signal streaming statistics."""
        return {
            "signals_sent": self.signals_sent,
            "subscribers": len(self.subscribers),
            "is_streaming": self.is_streaming,
            "recent_signals": self.signal_history[-10:] if self.signal_history else []
        }


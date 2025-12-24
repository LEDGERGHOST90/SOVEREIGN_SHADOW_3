#!/usr/bin/env python3
"""
REAL-TIME RISK BRIDGE - Connects live feeds to SS_III risk modules

Bridges:
- Coinbase WebSocket → SENTINEL (ATR, circuit breaker)
- CryptoCompare API → ORACLE (Fear & Greed, DXY)
- CCXT Pipeline → REGIME (HMM detection)
- CoinGlass API → FLOW (on-chain signals)
- yfinance OHLCV → MOONDEV (verified signals from 450 backtested strategies)
- All modules → TacticalRiskGate + REFLECT (AI critique)

Active Modules:
1. SENTINEL - AdvancedRiskManager (circuit breaker, ATR sizing)
2. ORACLE - MarketFilters (Fear & Greed, DXY correlation)
3. REGIME - HMMRegimeDetector (Trending/MeanReverting/Volatile)
4. FLOW - OnChainSignals (exchange flows, whale alerts)
5. REFLECT - ReflectAgent (self-critique, 11-22% decision improvement)
6. MOONDEV - Top 3 verified signals from 450 backtested:
   - MomentumBreakout_AI7: +12.5% return, +23.2% alpha
   - BandedMACD: +6.9% return, high frequency
   - VolCliffArbitrage: +6.4% return, 75% win rate

Created: 2025-12-23
Part of SOVEREIGN_SHADOW_3
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import requests
import threading
from queue import Queue

# Project imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.trading.tactical_risk_gate import TacticalRiskGate, TradeRequest, ValidationResult
from core.risk.advanced_risk_module import AdvancedRiskManager
from core.filters.market_filters import MarketFilters
from core.regime.hmm_regime_detector import HMMRegimeDetector
from core.signals.onchain_signals import OnChainSignals
from core.agents.reflect_agent import ReflectAgent

# MoonDev verified signals (top 3 from 450 backtested)
try:
    from core.signals.moondev_signals import MoonDevSignals
    MOONDEV_AVAILABLE = True
except ImportError:
    MOONDEV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PriceTick:
    """Real-time price tick from WebSocket"""
    symbol: str
    price: float
    high_24h: float
    low_24h: float
    volume_24h: float
    timestamp: datetime
    source: str


@dataclass
class RiskState:
    """Current aggregated risk state"""
    sentinel_breakers: Dict[str, bool]
    oracle_fng_signal: str
    oracle_dxy_signal: str
    current_regime: str
    flow_exchange_signals: Dict[str, str]
    atr_values: Dict[str, float]
    kelly_sizes: Dict[str, float]
    moondev_signals: Dict[str, str]  # Top 3 strategy consensus
    moondev_confidence: float
    last_update: datetime


class RealtimeRiskBridge:
    """
    Central bridge connecting real-time data feeds to all risk modules.

    Features:
    - WebSocket price ingestion with automatic reconnection
    - Async event-driven updates to all modules
    - Thread-safe state management
    - Callback system for alerts
    - Integrated trade validation
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # Initialize all risk modules with graceful fallbacks
        try:
            self.tactical_gate = TacticalRiskGate()
        except Exception as e:
            logger.warning(f"TacticalRiskGate init warning: {e}")
            self.tactical_gate = None

        try:
            self.sentinel = AdvancedRiskManager()
        except Exception as e:
            logger.warning(f"AdvancedRiskManager init failed: {e}")
            self.sentinel = None

        try:
            self.oracle = MarketFilters()
        except Exception as e:
            logger.warning(f"MarketFilters init failed: {e}")
            self.oracle = None

        try:
            self.regime_detector = HMMRegimeDetector()
        except Exception as e:
            logger.warning(f"HMMRegimeDetector init failed: {e}")
            self.regime_detector = None

        try:
            self.flow_signals = OnChainSignals()
        except Exception as e:
            logger.warning(f"OnChainSignals init failed: {e}")
            self.flow_signals = None

        try:
            self.reflect_agent = ReflectAgent()
        except Exception as e:
            logger.warning(f"ReflectAgent init failed (API key needed?): {e}")
            self.reflect_agent = None

        # MoonDev verified signals (top 3 from 450 backtested strategies)
        if MOONDEV_AVAILABLE:
            try:
                self.moondev_signals = MoonDevSignals()
                logger.info("MoonDev signals loaded: MomentumBreakout, BandedMACD, VolCliffArbitrage")
            except Exception as e:
                logger.warning(f"MoonDevSignals init failed: {e}")
                self.moondev_signals = None
        else:
            self.moondev_signals = None

        # Log active modules
        active = [name for name, mod in [
            ("SENTINEL", self.sentinel),
            ("ORACLE", self.oracle),
            ("REGIME", self.regime_detector),
            ("FLOW", self.flow_signals),
            ("REFLECT", self.reflect_agent),
            ("MOONDEV", self.moondev_signals)
        ] if mod is not None]
        logger.info(f"Active modules: {', '.join(active) if active else 'None'}")

        # State tracking
        self.price_history: Dict[str, List[PriceTick]] = {}
        self.current_prices: Dict[str, float] = {}
        self.risk_state = RiskState(
            sentinel_breakers={},
            oracle_fng_signal="unknown",
            oracle_dxy_signal="unknown",
            current_regime="unknown",
            flow_exchange_signals={},
            atr_values={},
            kelly_sizes={},
            moondev_signals={},
            moondev_confidence=0.0,
            last_update=datetime.now()
        )

        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []

        # Thread-safe queue for price updates
        self.price_queue: Queue = Queue()

        # NTFY topic for push alerts
        self.ntfy_topic = "sovereignshadow_dc4d2fa1"

        # Track update frequencies
        self.last_oracle_update = datetime.min
        self.last_regime_update = datetime.min
        self.last_flow_update = datetime.min
        self.last_moondev_update = datetime.min

        logger.info("RealtimeRiskBridge initialized with all modules")

    # =========================================================================
    # PRICE DATA INGESTION
    # =========================================================================

    def ingest_price_tick(self, tick: PriceTick):
        """
        Ingest a single price tick from WebSocket or API.
        Updates all relevant modules.
        """
        symbol = tick.symbol

        # Update current prices
        self.current_prices[symbol] = tick.price

        # Store in history (keep last 100 ticks per symbol)
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(tick)
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]

        # Check circuit breaker via SENTINEL
        if self.sentinel:
            try:
                breaker_status = self.sentinel.check_circuit_breaker()
                if breaker_status.active:
                    self.risk_state.sentinel_breakers[symbol] = True
                    self._fire_alert(
                        title=f"CIRCUIT BREAKER: {symbol}",
                        message=f"{symbol} triggered circuit breaker at ${tick.price:.4f}",
                        priority="urgent"
                    )
                else:
                    self.risk_state.sentinel_breakers[symbol] = False
            except Exception as e:
                logger.debug(f"Circuit breaker check failed: {e}")

        self.risk_state.last_update = datetime.now()
        logger.debug(f"Ingested tick: {symbol} @ ${tick.price:.4f}")

    def ingest_from_websocket_data(self, ws_message: Dict):
        """
        Parse Coinbase WebSocket message and ingest.
        Compatible with ai_basket_ws_scanner.py format.
        """
        if ws_message.get('type') != 'ticker':
            return

        product_id = ws_message.get('product_id', '')
        price_str = ws_message.get('price')

        if not price_str:
            return

        # Extract symbol from pair (e.g., "BTC-USD" -> "BTC")
        symbol = product_id.split('-')[0] if '-' in product_id else product_id

        tick = PriceTick(
            symbol=symbol,
            price=float(price_str),
            high_24h=float(ws_message.get('high_24h', price_str)),
            low_24h=float(ws_message.get('low_24h', price_str)),
            volume_24h=float(ws_message.get('volume_24h', 0)),
            timestamp=datetime.now(),
            source='coinbase_ws'
        )

        self.ingest_price_tick(tick)

    # =========================================================================
    # PERIODIC UPDATES (ORACLE, REGIME, FLOW)
    # =========================================================================

    def update_oracle_filters(self, force: bool = False):
        """Update Fear & Greed and DXY from external APIs"""
        now = datetime.now()

        # Update every 5 minutes unless forced
        if not force and (now - self.last_oracle_update).seconds < 300:
            return

        self.last_oracle_update = now

        if not self.oracle:
            return

        try:
            # Fetch Fear & Greed
            fng_data = self.oracle.get_fear_greed(use_cache=not force)
            self.risk_state.oracle_fng_signal = fng_data.get("signal", "unknown")

            # Fetch DXY
            dxy_data = self.oracle.get_dxy_signal(use_cache=not force)
            self.risk_state.oracle_dxy_signal = dxy_data.get("signal", "unknown")

            logger.info(f"ORACLE updated: F&G={self.risk_state.oracle_fng_signal}, DXY={self.risk_state.oracle_dxy_signal}")
        except Exception as e:
            logger.error(f"ORACLE update failed: {e}")

    def update_regime_detection(self, symbol: str = "BTC", force: bool = False):
        """Update HMM regime detection"""
        now = datetime.now()

        # Update every 15 minutes unless forced
        if not force and (now - self.last_regime_update).seconds < 900:
            return

        self.last_regime_update = now

        if not self.regime_detector:
            return

        try:
            # Get OHLCV data from CCXT
            from core.integrations.live_data_pipeline import LiveDataPipeline
            pipeline = LiveDataPipeline()
            ohlcv = pipeline.get_ohlcv(symbol, days=30)

            if not ohlcv.empty:
                # Fit model if needed
                if self.regime_detector.should_retrain():
                    self.regime_detector.fit(ohlcv)

                # Predict current regime
                regime_type, regime_info = self.regime_detector.predict_regime(ohlcv)
                self.risk_state.current_regime = regime_type.value if hasattr(regime_type, 'value') else str(regime_type)

                logger.info(f"REGIME updated: {self.risk_state.current_regime}")
        except Exception as e:
            logger.error(f"Regime update failed: {e}")

    def update_flow_signals(self, assets: List[str] = None, force: bool = False):
        """Update on-chain flow signals"""
        now = datetime.now()

        # Update every 10 minutes unless forced
        if not force and (now - self.last_flow_update).seconds < 600:
            return

        self.last_flow_update = now
        assets = assets or ["BTC", "ETH"]

        if not self.flow_signals:
            return

        try:
            for asset in assets:
                flow_data = self.flow_signals.get_exchange_flows(symbol=asset)
                signal = flow_data.get("signal", "neutral")
                self.risk_state.flow_exchange_signals[asset] = signal

            logger.info(f"FLOW updated: {self.risk_state.flow_exchange_signals}")
        except Exception as e:
            logger.error(f"FLOW update failed: {e}")

    def update_moondev_signals(self, symbols: List[str] = None, force: bool = False):
        """
        Update MoonDev verified signals (top 3 from 450 backtested).

        Strategies:
        - MomentumBreakout_AI7: +12.5% return, 55.6% WR
        - BandedMACD: +6.9% return, 38.0% WR
        - VolCliffArbitrage: +6.4% return, 75.0% WR
        """
        now = datetime.now()

        # Update every 30 minutes unless forced (these are hourly timeframe signals)
        if not force and (now - self.last_moondev_update).seconds < 1800:
            return

        self.last_moondev_update = now
        symbols = symbols or ["BTC", "ETH"]

        if not self.moondev_signals:
            return

        try:
            import yfinance as yf
            import pandas as pd

            for symbol in symbols:
                ticker = f"{symbol}-USD"

                # Download recent data for signal calculation
                data = yf.download(ticker, period='3mo', interval='1h', progress=False)

                if data.empty:
                    logger.warning(f"MOONDEV: No data for {symbol}")
                    continue

                # Flatten MultiIndex if present
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)

                data = data.rename(columns={
                    'Open': 'open', 'High': 'high', 'Low': 'low',
                    'Close': 'close', 'Volume': 'volume'
                })

                # Get consensus from top 3 strategies
                result = self.moondev_signals.get_consensus(data)

                self.risk_state.moondev_signals[symbol] = result['action']
                self.risk_state.moondev_confidence = result['confidence']

                if result['action'] != 'WAIT':
                    logger.info(f"MOONDEV {symbol}: {result['action']} (conf: {result['confidence']:.0%})")

                    # Fire alert for high-confidence signals
                    if result['confidence'] >= 0.7:
                        self._fire_alert(
                            title=f"MOONDEV SIGNAL: {symbol}",
                            message=f"{result['action']} signal at {result['confidence']:.0%} confidence",
                            priority="high" if result['confidence'] >= 0.8 else "default"
                        )

        except Exception as e:
            logger.error(f"MOONDEV update failed: {e}")

    # =========================================================================
    # TRADE VALIDATION
    # =========================================================================

    def validate_trade(self, request: TradeRequest) -> ValidationResult:
        """
        Full trade validation through all risk modules.

        Checks:
        1. TacticalRiskGate (LSR, funding, HF, OI)
        2. SENTINEL (circuit breaker, ATR sizing)
        3. ORACLE (F&G, DXY filters)
        4. REGIME (HMM state check)
        5. FLOW (on-chain signals)
        6. REFLECT (AI critique)
        """
        warnings = []
        size_adj = 1.0

        # 1. Check SENTINEL circuit breaker
        if self.risk_state.sentinel_breakers.get(request.asset, False):
            return ValidationResult(
                approved=False,
                reason=f"CIRCUIT BREAKER active for {request.asset}"
            )

        # 2. Get ATR-based stop loss
        atr_stop = self.risk_state.atr_values.get(request.asset)
        suggested_stop = None
        if atr_stop:
            suggested_stop = int(atr_stop * 2 * 100)  # 2x ATR in bps
            if suggested_stop > request.stop_loss_bps:
                warnings.append(f"ATR suggests wider stop: {suggested_stop} bps vs {request.stop_loss_bps}")

        # 3. Check ORACLE Fear & Greed
        fng = self.risk_state.oracle_fng_signal
        if fng == "extreme_fear" and request.side == "short":
            warnings.append("ORACLE: Extreme Fear - consider long bias")
            size_adj *= 0.7
        elif fng == "extreme_greed" and request.side == "long":
            warnings.append("ORACLE: Extreme Greed - consider short bias")
            size_adj *= 0.7

        # 4. Check DXY signal
        dxy = self.risk_state.oracle_dxy_signal
        if dxy == "rising" and request.side == "long":
            warnings.append("ORACLE: DXY rising - headwind for crypto longs")
            size_adj *= 0.9

        # 5. Check REGIME
        regime = self.risk_state.current_regime
        if regime == "high_volatility" and request.notional_usd > 50:
            warnings.append(f"REGIME: High volatility - reduce size")
            size_adj *= 0.8

        # 6. Check FLOW signals
        flow_signal = self.risk_state.flow_exchange_signals.get(request.asset, "neutral")
        if flow_signal == "heavy_inflow" and request.side == "long":
            warnings.append(f"FLOW: Heavy exchange inflows - selling pressure")
            size_adj *= 0.85

        # 7. Get REFLECT critique
        if self.reflect_agent:
            try:
                proposed_trade = {
                    "symbol": request.asset,
                    "direction": request.side.upper(),
                    "size_usd": request.notional_usd,
                    "stop_loss_pct": request.stop_loss_bps / 100,
                    "entry_price": request.entry_price,
                    "strategy": request.strategy_name
                }
                critique = self.reflect_agent.analyze_trade(proposed_trade)
                if critique.decision.value == "REJECT":
                    warnings.append(f"REFLECT: {critique.summary}")
                    size_adj *= 0.75
                elif critique.decision.value == "MODIFY":
                    warnings.append(f"REFLECT suggests: {critique.modifications}")
            except Exception as e:
                logger.debug(f"REFLECT critique failed: {e}")

        # 8. Check MOONDEV verified signals (top 3 from 450 backtested)
        moondev_signal = self.risk_state.moondev_signals.get(request.asset, "WAIT")
        moondev_conf = self.risk_state.moondev_confidence

        if moondev_signal != "WAIT" and moondev_conf >= 0.6:
            # Signal alignment check
            if moondev_signal == "LONG" and request.side == "short":
                warnings.append(f"MOONDEV: {moondev_signal} signal ({moondev_conf:.0%}) conflicts with short")
                size_adj *= 0.7
            elif moondev_signal == "SHORT" and request.side == "long":
                warnings.append(f"MOONDEV: {moondev_signal} signal ({moondev_conf:.0%}) conflicts with long")
                size_adj *= 0.7
            elif moondev_signal == request.side.upper():
                # Signal confirms direction - boost confidence
                if moondev_conf >= 0.8:
                    size_adj *= 1.15  # 15% size boost for high-confidence alignment
                    logger.info(f"MOONDEV confirms {request.side} with {moondev_conf:.0%} confidence")

        # 9. Pass through TacticalRiskGate
        if not self.tactical_gate:
            return ValidationResult(
                approved=True,
                reason="TacticalRiskGate not available",
                size_adjustment=size_adj,
                warnings=warnings
            )

        result = self.tactical_gate.validate_trade(request)

        if not result.approved:
            return result

        # Combine adjustments
        final_size_adj = result.size_adjustment * size_adj
        all_warnings = result.warnings + warnings

        return ValidationResult(
            approved=True,
            reason=f"All gates passed (size: {final_size_adj:.2f}x)",
            size_adjustment=final_size_adj,
            stop_adjustment_bps=suggested_stop or result.stop_adjustment_bps,
            warnings=all_warnings
        )

    def calculate_kelly_size(self, win_prob: float, payout_ratio: float, capital: float) -> float:
        """Calculate Kelly bet size through SENTINEL"""
        if not self.sentinel:
            return capital * 0.02  # Default to 2%

        try:
            kelly_fraction = self.sentinel.get_kelly_fraction(
                win_rate=win_prob,
                avg_win=payout_ratio,
                avg_loss=1.0
            )
            return capital * kelly_fraction
        except Exception as e:
            logger.debug(f"Kelly calculation failed: {e}")
            return capital * 0.02  # Default to 2%

    # =========================================================================
    # ALERTS
    # =========================================================================

    def register_alert_callback(self, callback: Callable):
        """Register a callback for alerts"""
        self.alert_callbacks.append(callback)

    def _fire_alert(self, title: str, message: str, priority: str = "default"):
        """Fire alert to all callbacks and NTFY"""
        alert = {
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }

        # Fire callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        # Send to NTFY
        try:
            requests.post(
                f"https://ntfy.sh/{self.ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    "Title": title,
                    "Priority": priority,
                    "Tags": "warning" if priority == "urgent" else "bell"
                },
                timeout=5
            )
        except Exception as e:
            logger.error(f"NTFY alert failed: {e}")

        logger.warning(f"ALERT: {title} - {message}")

    # =========================================================================
    # STATE EXPORT
    # =========================================================================

    def get_risk_state(self) -> Dict:
        """Get current aggregated risk state"""
        return asdict(self.risk_state)

    def get_full_status(self) -> Dict:
        """Get comprehensive system status"""
        tactical_stats = None
        if self.tactical_gate:
            try:
                tactical_stats = self.tactical_gate.get_session_stats()
            except Exception:
                tactical_stats = "unavailable"

        return {
            "risk_state": self.get_risk_state(),
            "current_prices": self.current_prices.copy(),
            "tactical_session": tactical_stats,
            "modules": {
                "sentinel": "active" if self.sentinel else "disabled",
                "oracle": f"fng={self.risk_state.oracle_fng_signal}, dxy={self.risk_state.oracle_dxy_signal}",
                "regime": self.risk_state.current_regime,
                "flow": self.risk_state.flow_exchange_signals,
                "reflect": "active" if self.reflect_agent else "disabled",
                "moondev": {
                    "signals": self.risk_state.moondev_signals,
                    "confidence": self.risk_state.moondev_confidence,
                    "strategies": ["MomentumBreakout_AI7", "BandedMACD", "VolCliffArbitrage"]
                }
            },
            "last_update": self.risk_state.last_update.isoformat()
        }


# =============================================================================
# WEBSOCKET INTEGRATION
# =============================================================================

class WebSocketRiskMonitor:
    """
    WebSocket monitor that feeds RealtimeRiskBridge.
    Drop-in enhancement for ai_basket_ws_scanner.py
    """

    def __init__(self, bridge: RealtimeRiskBridge):
        self.bridge = bridge
        self.positions = {}  # Will be loaded from config
        self.running = False

    async def connect_coinbase(self, product_ids: List[str]):
        """Connect to Coinbase WebSocket and feed bridge"""
        try:
            import websockets
        except ImportError:
            os.system(f"{sys.executable} -m pip install websockets")
            import websockets

        ws_url = "wss://ws-feed.exchange.coinbase.com"
        subscribe_message = {
            "type": "subscribe",
            "product_ids": product_ids,
            "channels": ["ticker"]
        }

        self.running = True
        reconnect_count = 0

        while self.running and reconnect_count < 100:
            try:
                logger.info(f"Connecting to Coinbase WebSocket...")
                async with websockets.connect(ws_url, ping_interval=30) as ws:
                    await ws.send(json.dumps(subscribe_message))
                    logger.info(f"Connected! Subscribed to {product_ids}")
                    reconnect_count = 0

                    async for message in ws:
                        try:
                            data = json.loads(message)
                            self.bridge.ingest_from_websocket_data(data)
                        except json.JSONDecodeError:
                            pass
                        except Exception as e:
                            logger.error(f"Message processing error: {e}")

            except Exception as e:
                reconnect_count += 1
                logger.error(f"WebSocket error: {e}, reconnecting in 5s ({reconnect_count}/100)")
                await asyncio.sleep(5)

        logger.warning("WebSocket monitor stopped")

    def stop(self):
        """Stop the monitor"""
        self.running = False


# =============================================================================
# MAIN LOOP
# =============================================================================

async def run_realtime_bridge(
    assets: List[str] = None,
    update_interval: int = 60
):
    """
    Main entry point for real-time risk bridge.

    Args:
        assets: List of assets to monitor (default: AI basket)
        update_interval: Seconds between periodic updates
    """
    assets = assets or ["FET", "RENDER", "SUI", "BTC", "ETH"]
    product_ids = [f"{a}-USD" for a in assets]

    # Initialize bridge
    bridge = RealtimeRiskBridge()

    # Initialize WebSocket monitor
    ws_monitor = WebSocketRiskMonitor(bridge)

    # Start WebSocket in background
    ws_task = asyncio.create_task(ws_monitor.connect_coinbase(product_ids))

    # Periodic update loop
    logger.info(f"Starting real-time risk bridge for {assets}")

    try:
        while True:
            # Update ORACLE, REGIME, FLOW, MOONDEV periodically
            bridge.update_oracle_filters()
            bridge.update_regime_detection()
            bridge.update_flow_signals(assets=["BTC", "ETH"])
            bridge.update_moondev_signals(symbols=["BTC", "ETH"])

            # Log status
            status = bridge.get_full_status()
            logger.info(f"Risk State: {json.dumps(status['modules'], indent=2)}")

            await asyncio.sleep(update_interval)

    except KeyboardInterrupt:
        logger.info("Stopping real-time bridge...")
        ws_monitor.stop()
        await ws_task


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Real-Time Risk Bridge")
    parser.add_argument("--assets", nargs="+", default=["FET", "RENDER", "SUI", "BTC", "ETH"])
    parser.add_argument("--interval", type=int, default=60)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    asyncio.run(run_realtime_bridge(
        assets=args.assets,
        update_interval=args.interval
    ))


if __name__ == "__main__":
    main()

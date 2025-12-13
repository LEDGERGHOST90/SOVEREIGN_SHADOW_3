#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - Master Orchestrator

The Master Orchestrator implements the complete D.O.E. Pattern:

    ┌─────────────────────────────────────────────────┐
    │            SOVEREIGN SHADOW II                   │
    │              D.O.E. PATTERN                      │
    ├─────────────────────────────────────────────────┤
    │                                                  │
    │  ┌──────────────┐     ┌──────────────────────┐  │
    │  │  DIRECTIVE   │────▶│   Market Regime      │  │
    │  │    LAYER     │     │   Detector           │  │
    │  └──────────────┘     └──────────────────────┘  │
    │         │                       │               │
    │         ▼                       ▼               │
    │  ┌──────────────┐     ┌──────────────────────┐  │
    │  │ ORCHESTRATION│────▶│   AI Strategy        │  │
    │  │    LAYER     │     │   Selector           │  │
    │  └──────────────┘     └──────────────────────┘  │
    │         │                       │               │
    │         ▼                       ▼               │
    │  ┌──────────────┐     ┌──────────────────────┐  │
    │  │  EXECUTION   │────▶│   Strategy Engine    │  │
    │  │    LAYER     │     │   + Exchange API     │  │
    │  └──────────────┘     └──────────────────────┘  │
    │         │                       │               │
    │         ▼                       ▼               │
    │  ┌──────────────┐     ┌──────────────────────┐  │
    │  │  LEARNING    │────▶│   Performance        │  │
    │  │    LAYER     │     │   Tracker            │  │
    │  └──────────────┘     └──────────────────────┘  │
    │                                                  │
    └─────────────────────────────────────────────────┘

Main Loop:
1. Fetch market data from exchange
2. Detect market regime
3. Select optimal strategy
4. Execute strategy signals
5. Track performance
6. Update strategy rankings (learning loop)
"""

import os
import sys
import time
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.intelligence.performance_tracker import PerformanceTracker, get_performance_tracker
from core.intelligence.regime_detector import (
    MarketRegimeDetector, MarketRegime, RegimeAnalysis, get_regime_detector
)
from core.intelligence.strategy_selector import (
    AIStrategySelector, StrategyRecommendation, get_strategy_selector
)

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Active trading position"""
    trade_id: str
    strategy_name: str
    symbol: str
    side: str
    entry_price: float
    quantity: float
    entry_time: str
    stop_loss: float
    take_profit: float
    regime: str
    exchange: str
    status: str = "open"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""
    # Trading mode
    paper_trading: bool = True
    sandbox_mode: bool = True

    # Capital and risk
    initial_capital: float = 10000.0
    max_position_size_percent: float = 10.0  # 10% max per position
    max_open_positions: int = 3
    risk_per_trade_percent: float = 1.0

    # Timing
    regime_check_interval_seconds: int = 300  # 5 minutes
    strategy_check_interval_seconds: int = 60  # 1 minute

    # Exchange priority
    exchange_priority: List[str] = None

    # Safety
    max_daily_loss_percent: float = 5.0
    trading_hours_only: bool = False

    def __post_init__(self):
        if self.exchange_priority is None:
            self.exchange_priority = ["coinbase", "kraken", "binance_us", "okx"]


class SovereignShadowOrchestrator:
    """
    Master Orchestrator for Sovereign Shadow II.

    Coordinates all components:
    - MarketRegimeDetector (Directive)
    - AIStrategySelector (Orchestration)
    - Strategy Execution (Execution)
    - PerformanceTracker (Learning)
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        exchange_connectors: Optional[Dict] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            config: Orchestrator configuration
            exchange_connectors: Dict of exchange name -> connector instance
        """
        self.config = config or OrchestratorConfig()
        self.exchange_connectors = exchange_connectors or {}

        # Initialize D.O.E. components
        self.performance_tracker = get_performance_tracker()
        self.regime_detector = get_regime_detector()
        self.strategy_selector = get_strategy_selector()

        # Runtime state
        self.running = False
        self.current_regime: Optional[RegimeAnalysis] = None
        self.active_positions: Dict[str, Position] = {}
        self.portfolio_value = self.config.initial_capital
        self.daily_pnl = 0.0
        self.daily_trades = 0

        # Strategy modules cache
        self.strategy_cache: Dict[str, Any] = {}

        # Logging
        self._setup_logging()

        logger.info("SovereignShadowOrchestrator initialized")
        logger.info(f"Mode: {'PAPER' if self.config.paper_trading else 'LIVE'}")
        logger.info(f"Initial capital: ${self.config.initial_capital:,.2f}")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )

        logger.addHandler(file_handler)

    def add_exchange_connector(self, name: str, connector: Any):
        """Add an exchange connector"""
        self.exchange_connectors[name] = connector
        logger.info(f"Exchange connector added: {name}")

    def get_primary_exchange(self) -> Optional[Any]:
        """Get the primary exchange connector based on priority"""
        for exchange_name in self.config.exchange_priority:
            if exchange_name in self.exchange_connectors:
                return self.exchange_connectors[exchange_name]
        return None

    async def fetch_market_data(
        self,
        symbol: str = "BTC/USD",
        timeframe: str = "15m",
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch market data from exchange.

        Returns:
            List of OHLCV candles
        """
        exchange = self.get_primary_exchange()

        if exchange is None:
            # Return synthetic data for testing
            logger.warning("No exchange connected - using synthetic data")
            return self._generate_synthetic_data(limit)

        try:
            # Fetch OHLCV data
            ohlcv = exchange.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            return [
                {
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
                for candle in ohlcv
            ]

        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return self._generate_synthetic_data(limit)

    def _generate_synthetic_data(self, limit: int = 100) -> List[Dict]:
        """Generate synthetic market data for testing"""
        import random

        base_price = 95000
        data = []

        for i in range(limit):
            noise = random.uniform(-500, 500)
            trend = i * 10  # Slight uptrend
            close = base_price + trend + noise

            data.append({
                'timestamp': int((datetime.now() - timedelta(minutes=15 * (limit - i))).timestamp() * 1000),
                'open': close + random.uniform(-100, 100),
                'high': close + random.uniform(0, 300),
                'low': close - random.uniform(0, 300),
                'close': close,
                'volume': random.uniform(100, 1000)
            })

        return data

    def detect_regime(self, market_data: List[Dict], symbol: str = "BTC/USD") -> RegimeAnalysis:
        """
        Directive Layer: Detect current market regime.
        """
        analysis = self.regime_detector.analyze(market_data, symbol)
        self.current_regime = analysis

        logger.info(
            f"[DIRECTIVE] Regime: {analysis.regime.value} "
            f"(confidence: {analysis.confidence:.1f}%)"
        )

        return analysis

    def select_strategy(self) -> StrategyRecommendation:
        """
        Orchestration Layer: Select optimal strategy for current regime.
        """
        if self.current_regime is None:
            raise ValueError("No regime detected - run detect_regime first")

        # Check daily loss limit
        if self._check_daily_loss_limit():
            logger.warning("Daily loss limit reached - no new trades")
            return StrategyRecommendation(
                strategy_name="WAIT",
                regime=self.current_regime.regime,
                confidence=100,
                expected_win_rate=0,
                expected_pnl_percent=0,
                risk_level="none",
                reasoning=["Daily loss limit reached"],
                position_size_multiplier=0,
                timeframe="N/A"
            )

        recommendation = self.strategy_selector.select_strategy(
            regime=self.current_regime.regime,
            portfolio_value=self.portfolio_value,
            current_positions=len(self.active_positions),
            max_positions=self.config.max_open_positions,
            risk_tolerance="medium"
        )

        logger.info(
            f"[ORCHESTRATION] Strategy: {recommendation.strategy_name} "
            f"(confidence: {recommendation.confidence:.1f}%)"
        )

        return recommendation

    async def execute_strategy(
        self,
        recommendation: StrategyRecommendation,
        market_data: List[Dict],
        symbol: str = "BTC/USD"
    ) -> Optional[Dict]:
        """
        Execution Layer: Execute the selected strategy.

        Returns:
            Trade result dict or None if no trade
        """
        if recommendation.strategy_name == "WAIT":
            logger.info("[EXECUTION] Waiting - no action")
            return None

        # Load strategy module
        strategy = self._load_strategy(recommendation.strategy_name)

        if strategy is None:
            logger.warning(f"Strategy not found: {recommendation.strategy_name}")
            return None

        # Check for entry signal
        entry_signal = strategy['entry'].generate_signal(market_data)

        if entry_signal.get('signal') != 'BUY':
            logger.debug(f"[EXECUTION] No entry signal from {recommendation.strategy_name}")
            return None

        # Calculate position size
        current_price = market_data[-1]['close']
        position_sizing = self._calculate_position_size(
            recommendation,
            current_price,
            market_data
        )

        if position_sizing['position_value_usd'] < 10:
            logger.info("[EXECUTION] Position size too small")
            return None

        # Execute trade
        trade_result = await self._execute_trade(
            symbol=symbol,
            side="buy",
            quantity=position_sizing['quantity'],
            price=current_price,
            stop_loss=position_sizing['stop_loss_price'],
            take_profit=position_sizing['take_profit_price'],
            strategy_name=recommendation.strategy_name,
            regime=self.current_regime.regime.value
        )

        if trade_result and trade_result.get('success'):
            logger.info(
                f"[EXECUTION] Trade executed: {trade_result['trade_id']} "
                f"@ ${current_price:,.2f}"
            )

        return trade_result

    def _load_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Load a modularized strategy"""
        if strategy_name in self.strategy_cache:
            return self.strategy_cache[strategy_name]

        try:
            # Convert strategy name to module path
            module_name = strategy_name.lower().replace(" ", "_")
            strategy_path = Path(__file__).parent.parent.parent / "strategies" / "modularized"

            # Look for the strategy in agent directories
            for agent_dir in strategy_path.iterdir():
                if agent_dir.is_dir() and agent_dir.name.startswith("agent_"):
                    strategy_dir = agent_dir / module_name
                    if strategy_dir.exists():
                        # Load entry, exit, risk modules
                        entry_module = importlib.import_module(
                            f"strategies.modularized.{agent_dir.name}.{module_name}.entry"
                        )
                        exit_module = importlib.import_module(
                            f"strategies.modularized.{agent_dir.name}.{module_name}.exit"
                        )
                        risk_module = importlib.import_module(
                            f"strategies.modularized.{agent_dir.name}.{module_name}.risk"
                        )

                        strategy = {
                            'entry': entry_module,
                            'exit': exit_module,
                            'risk': risk_module
                        }

                        self.strategy_cache[strategy_name] = strategy
                        return strategy

            # Try loading from simple built-in strategies
            return self._get_builtin_strategy(strategy_name)

        except Exception as e:
            logger.error(f"Failed to load strategy {strategy_name}: {e}")
            return self._get_builtin_strategy(strategy_name)

    def _get_builtin_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Get a built-in strategy implementation"""
        # Import the builtin strategies
        from .builtin_strategies import (
            ElderReversionEntry, ElderReversionExit, ElderReversionRisk,
            RSIReversionEntry, RSIReversionExit, RSIReversionRisk,
            TrendFollowEMAEntry, TrendFollowEMAExit, TrendFollowEMARisk
        )

        builtin = {
            "ElderReversion": {
                'entry': ElderReversionEntry(),
                'exit': ElderReversionExit(),
                'risk': ElderReversionRisk()
            },
            "RSIReversion": {
                'entry': RSIReversionEntry(),
                'exit': RSIReversionExit(),
                'risk': RSIReversionRisk()
            },
            "TrendFollowEMA": {
                'entry': TrendFollowEMAEntry(),
                'exit': TrendFollowEMAExit(),
                'risk': TrendFollowEMARisk()
            }
        }

        return builtin.get(strategy_name)

    def _calculate_position_size(
        self,
        recommendation: StrategyRecommendation,
        current_price: float,
        market_data: List[Dict]
    ) -> Dict:
        """Calculate position size with risk management"""
        # Base position size from config
        max_position = self.portfolio_value * (self.config.max_position_size_percent / 100)

        # Apply recommendation multiplier
        position_value = max_position * recommendation.position_size_multiplier

        # Risk-based sizing (1% risk per trade)
        risk_amount = self.portfolio_value * (self.config.risk_per_trade_percent / 100)

        # Calculate ATR for stop loss distance
        atr = self._calculate_atr(market_data)
        stop_distance = atr * 2  # 2 ATR stop

        # Position size based on risk
        risk_based_size = risk_amount / stop_distance if stop_distance > 0 else 0

        # Use smaller of the two
        final_value = min(position_value, risk_based_size * current_price)

        return {
            'position_value_usd': final_value,
            'quantity': final_value / current_price,
            'stop_loss_price': current_price - stop_distance,
            'take_profit_price': current_price + (stop_distance * 2)  # 2:1 R:R
        }

    def _calculate_atr(self, market_data: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(market_data) < period + 1:
            return 0

        tr_list = []
        for i in range(1, len(market_data)):
            tr = max(
                market_data[i]['high'] - market_data[i]['low'],
                abs(market_data[i]['high'] - market_data[i-1]['close']),
                abs(market_data[i]['low'] - market_data[i-1]['close'])
            )
            tr_list.append(tr)

        return sum(tr_list[-period:]) / period

    async def _execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_loss: float,
        take_profit: float,
        strategy_name: str,
        regime: str
    ) -> Dict:
        """Execute a trade (paper or live)"""
        trade_id = f"SS2_{int(datetime.now().timestamp())}_{strategy_name[:4].upper()}"

        if self.config.paper_trading:
            # Paper trade - simulate execution
            result = {
                'success': True,
                'trade_id': trade_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'paper_trade': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            # Live trade - use exchange connector
            exchange = self.get_primary_exchange()
            if exchange is None:
                return {'success': False, 'error': 'No exchange connected'}

            try:
                order = exchange.create_order(
                    symbol=symbol,
                    side=side,
                    order_type='market',
                    amount=quantity
                )
                result = {
                    'success': True,
                    'trade_id': order.get('order_id', trade_id),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': order.get('price', price),
                    'paper_trade': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}

        # Create position
        position = Position(
            trade_id=result['trade_id'],
            strategy_name=strategy_name,
            symbol=symbol,
            side=side,
            entry_price=price,
            quantity=quantity,
            entry_time=result['timestamp'],
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime=regime,
            exchange="paper" if self.config.paper_trading else "live"
        )

        self.active_positions[trade_id] = position

        # Record in performance tracker
        self.performance_tracker.record_trade(
            trade_id=trade_id,
            strategy_name=strategy_name,
            symbol=symbol,
            side=side,
            entry_price=price,
            quantity=quantity,
            entry_time=result['timestamp'],
            regime=regime,
            exchange=position.exchange
        )

        self.daily_trades += 1

        return result

    async def check_positions(self, market_data: List[Dict]):
        """Check active positions for exit signals"""
        current_price = market_data[-1]['close']
        positions_to_close = []

        for trade_id, position in self.active_positions.items():
            # Check stop loss
            if current_price <= position.stop_loss:
                positions_to_close.append((trade_id, "STOP_LOSS", current_price))
                continue

            # Check take profit
            if current_price >= position.take_profit:
                positions_to_close.append((trade_id, "TAKE_PROFIT", current_price))
                continue

            # Check strategy exit signal
            strategy = self._load_strategy(position.strategy_name)
            if strategy:
                exit_signal = strategy['exit'].generate_signal(market_data, position.entry_price)
                if exit_signal.get('signal') == 'SELL':
                    positions_to_close.append((trade_id, exit_signal.get('reason', 'SIGNAL_EXIT'), current_price))

        # Close positions
        for trade_id, reason, exit_price in positions_to_close:
            await self._close_position(trade_id, exit_price, reason)

    async def _close_position(self, trade_id: str, exit_price: float, reason: str):
        """Close a position"""
        position = self.active_positions.get(trade_id)
        if not position:
            return

        # Calculate PnL
        if position.side == 'buy':
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity

        # Update portfolio value
        self.portfolio_value += pnl
        self.daily_pnl += pnl

        # Record in performance tracker
        self.performance_tracker.close_trade(
            trade_id=trade_id,
            exit_price=exit_price,
            exit_time=datetime.utcnow().isoformat(),
            exit_reason=reason
        )

        # Remove from active positions
        del self.active_positions[trade_id]

        logger.info(
            f"[LEARNING] Position closed: {trade_id} | "
            f"PnL: ${pnl:,.2f} | Reason: {reason}"
        )

    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        max_loss = self.config.initial_capital * (self.config.max_daily_loss_percent / 100)
        return self.daily_pnl <= -max_loss

    def update_learning_loop(self):
        """
        Learning Layer: Update strategy rankings based on performance.

        This is the self-annealing loop - strategies that perform well
        get ranked higher for future selection.
        """
        logger.info("[LEARNING] Updating strategy rankings...")

        for regime in MarketRegime:
            if regime != MarketRegime.UNKNOWN:
                self.performance_tracker.update_strategy_rankings(regime.value)

        logger.info("[LEARNING] Rankings updated for all regimes")

    async def run_single_cycle(self, symbol: str = "BTC/USD"):
        """Run a single orchestration cycle"""
        logger.info("=" * 60)
        logger.info("SOVEREIGN SHADOW II - CYCLE START")
        logger.info("=" * 60)

        # 1. Fetch market data
        market_data = await self.fetch_market_data(symbol, "15m", 100)

        # 2. Directive: Detect regime
        regime = self.detect_regime(market_data, symbol)

        # 3. Orchestration: Select strategy
        recommendation = self.select_strategy()

        # 4. Execution: Check positions first
        await self.check_positions(market_data)

        # 5. Execution: Execute new strategy if recommended
        if recommendation.strategy_name != "WAIT":
            trade_result = await self.execute_strategy(recommendation, market_data, symbol)
            if trade_result:
                logger.info(f"Trade result: {trade_result}")

        # 6. Learning: Periodic ranking update
        if self.daily_trades > 0 and self.daily_trades % 5 == 0:
            self.update_learning_loop()

        # Status report
        self._log_status()

        logger.info("CYCLE COMPLETE")
        logger.info("=" * 60)

    def _log_status(self):
        """Log current status"""
        logger.info(f"\n--- STATUS ---")
        logger.info(f"Portfolio Value: ${self.portfolio_value:,.2f}")
        logger.info(f"Daily PnL: ${self.daily_pnl:,.2f}")
        logger.info(f"Open Positions: {len(self.active_positions)}")
        logger.info(f"Daily Trades: {self.daily_trades}")
        if self.current_regime:
            logger.info(f"Current Regime: {self.current_regime.regime.value}")

    async def run(self, symbol: str = "BTC/USD"):
        """Main orchestration loop"""
        self.running = True

        logger.info("=" * 60)
        logger.info("SOVEREIGN SHADOW II - STARTING")
        logger.info(f"Mode: {'PAPER TRADING' if self.config.paper_trading else 'LIVE TRADING'}")
        logger.info(f"Symbol: {symbol}")
        logger.info("=" * 60)

        while self.running:
            try:
                await self.run_single_cycle(symbol)

                # Wait for next cycle
                await asyncio.sleep(self.config.strategy_check_interval_seconds)

            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                self.running = False

            except Exception as e:
                logger.error(f"Cycle error: {e}")
                await asyncio.sleep(30)  # Wait before retry

        logger.info("SOVEREIGN SHADOW II - SHUTDOWN COMPLETE")

    def stop(self):
        """Stop the orchestrator"""
        self.running = False
        logger.info("Stop signal received")

    def get_status(self) -> Dict:
        """Get current status as dict"""
        return {
            'running': self.running,
            'portfolio_value': self.portfolio_value,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'open_positions': len(self.active_positions),
            'current_regime': self.current_regime.regime.value if self.current_regime else None,
            'regime_confidence': self.current_regime.confidence if self.current_regime else 0,
            'paper_trading': self.config.paper_trading,
            'positions': [p.to_dict() for p in self.active_positions.values()]
        }


def create_orchestrator(
    paper_trading: bool = True,
    initial_capital: float = 10000.0
) -> SovereignShadowOrchestrator:
    """Factory function to create configured orchestrator"""
    config = OrchestratorConfig(
        paper_trading=paper_trading,
        sandbox_mode=paper_trading,
        initial_capital=initial_capital
    )

    return SovereignShadowOrchestrator(config=config)


if __name__ == "__main__":
    # Test the orchestrator
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        orchestrator = create_orchestrator(
            paper_trading=True,
            initial_capital=10000.0
        )

        # Run a single cycle for testing
        await orchestrator.run_single_cycle("BTC/USD")

        print("\n=== ORCHESTRATOR STATUS ===")
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2, default=str))

    asyncio.run(main())

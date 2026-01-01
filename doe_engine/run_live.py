#!/usr/bin/env python3
"""
D.O.E. Engine - Live Coinbase Connection
Connects to Coinbase via CDP API and runs D.O.E. pattern trading
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('doe_live')

# Import D.O.E. components
from core.orchestration.orchestrator import SovereignShadowOrchestrator, OrchestratorConfig
from core.intelligence.regime_detector import get_regime_detector
from core.intelligence.strategy_selector import get_strategy_selector
from core.intelligence.performance_tracker import get_performance_tracker


class CoinbaseLiveConnector:
    """Coinbase CDP API connector for live data"""

    def __init__(self):
        self.api_key = os.getenv("COINBASE_API_KEY")
        self.api_secret_file = os.getenv("COINBASE_API_SECRET_FILE")
        self.client = None
        self.connected = False

        # Load secret from file
        if self.api_secret_file and Path(self.api_secret_file).exists():
            self.api_secret = Path(self.api_secret_file).read_text()
        else:
            self.api_secret = os.getenv("COINBASE_API_SECRET")

    def connect(self) -> bool:
        """Connect to Coinbase CDP API"""
        try:
            from coinbase.rest import RESTClient

            self.client = RESTClient(
                api_key=self.api_key,
                api_secret=self.api_secret
            )

            # Test connection
            accounts = self.client.get_accounts()
            self.connected = True
            # Handle both dict and object responses
            if hasattr(accounts, 'accounts'):
                num_accounts = len(accounts.accounts)
            elif isinstance(accounts, dict):
                num_accounts = len(accounts.get('accounts', []))
            else:
                num_accounts = 0
            logger.info(f"✅ Connected to Coinbase CDP - {num_accounts} accounts")
            return True

        except Exception as e:
            logger.error(f"❌ Coinbase connection failed: {e}")
            return False

    def fetch_ohlcv(self, symbol: str = "BTC-USD", granularity: str = "ONE_HOUR", limit: int = 100):
        """
        Fetch OHLCV candles from Coinbase

        Args:
            symbol: Product ID (e.g., "BTC-USD")
            granularity: Candle size (ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, ONE_HOUR, etc.)
            limit: Number of candles
        """
        if not self.connected:
            logger.warning("Not connected to Coinbase")
            return []

        try:
            # Calculate time range
            end = datetime.utcnow()

            # Granularity to seconds mapping
            granularity_seconds = {
                "ONE_MINUTE": 60,
                "FIVE_MINUTE": 300,
                "FIFTEEN_MINUTE": 900,
                "ONE_HOUR": 3600,
                "TWO_HOUR": 7200,
                "SIX_HOUR": 21600,
                "ONE_DAY": 86400
            }

            seconds = granularity_seconds.get(granularity, 3600)
            start = end - timedelta(seconds=seconds * limit)

            # Fetch candles
            candles_resp = self.client.get_candles(
                product_id=symbol,
                start=int(start.timestamp()),
                end=int(end.timestamp()),
                granularity=granularity
            )

            # Handle both dict and object responses
            if hasattr(candles_resp, 'candles'):
                candles_list = candles_resp.candles
            elif isinstance(candles_resp, dict):
                candles_list = candles_resp.get('candles', [])
            else:
                candles_list = []

            # Convert to standard OHLCV format
            ohlcv = []
            for candle in candles_list:
                # Handle both dict and object format
                if hasattr(candle, 'start'):
                    ohlcv.append({
                        'timestamp': int(candle.start),
                        'open': float(candle.open),
                        'high': float(candle.high),
                        'low': float(candle.low),
                        'close': float(candle.close),
                        'volume': float(candle.volume)
                    })
                else:
                    ohlcv.append({
                        'timestamp': int(candle.get('start', 0)),
                        'open': float(candle.get('open', 0)),
                        'high': float(candle.get('high', 0)),
                        'low': float(candle.get('low', 0)),
                        'close': float(candle.get('close', 0)),
                        'volume': float(candle.get('volume', 0))
                    })

            # Sort by timestamp (oldest first)
            ohlcv.sort(key=lambda x: x['timestamp'])

            logger.info(f"📊 Fetched {len(ohlcv)} candles for {symbol}")
            return ohlcv

        except Exception as e:
            logger.error(f"❌ Failed to fetch OHLCV: {e}")
            return []

    def get_ticker(self, symbol: str = "BTC-USD"):
        """Get current ticker price"""
        if not self.connected:
            return None

        try:
            ticker = self.client.get_product(product_id=symbol)
            # Handle object response
            if hasattr(ticker, 'price'):
                return {
                    'symbol': symbol,
                    'price': float(ticker.price) if ticker.price else 0,
                    'volume_24h': float(ticker.volume_24h) if hasattr(ticker, 'volume_24h') and ticker.volume_24h else 0
                }
            else:
                return {
                    'symbol': symbol,
                    'price': float(ticker.get('price', 0)),
                    'volume_24h': float(ticker.get('volume_24h', 0))
                }
        except Exception as e:
            logger.error(f"❌ Failed to get ticker: {e}")
            return None


def run_doe_with_coinbase(symbol: str = "BTC-USD", cycles: int = 1):
    """
    Run D.O.E. Engine with live Coinbase data

    Args:
        symbol: Trading pair (e.g., "BTC-USD")
        cycles: Number of cycles to run (0 = infinite)
    """
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║             SOVEREIGN SHADOW III                              ║
    ║             D.O.E. Engine - LIVE MODE                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    # Connect to Coinbase
    logger.info("Connecting to Coinbase...")
    coinbase = CoinbaseLiveConnector()

    if not coinbase.connect():
        logger.error("Failed to connect to Coinbase. Exiting.")
        return

    # Get current price
    ticker = coinbase.get_ticker(symbol)
    if ticker:
        logger.info(f"💰 {symbol} Current Price: ${ticker['price']:,.2f}")

    # Initialize D.O.E. components
    config = OrchestratorConfig(
        paper_trading=True,  # SAFETY: Always paper trade unless explicitly enabled
        initial_capital=10000.0,
        max_position_size_percent=10.0,  # 10% max per position
        max_daily_loss_percent=5.0,  # 5% max daily loss
        risk_per_trade_percent=1.0
    )

    orchestrator = SovereignShadowOrchestrator(config=config)
    regime_detector = get_regime_detector()
    strategy_selector = get_strategy_selector()

    logger.info(f"🚀 Starting D.O.E. Engine - {cycles if cycles > 0 else '∞'} cycles")
    logger.info(f"📊 Symbol: {symbol}")
    logger.info(f"📝 Mode: {'PAPER' if config.paper_trading else '🔴 LIVE'}")

    cycle_count = 0

    try:
        while cycles == 0 or cycle_count < cycles:
            cycle_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"CYCLE {cycle_count}")
            logger.info(f"{'='*60}")

            # 1. DIRECTIVE LAYER - Fetch data and detect regime
            logger.info("\n[1/4] DIRECTIVE LAYER - Fetching market data...")
            ohlcv = coinbase.fetch_ohlcv(symbol, "ONE_HOUR", 100)

            if len(ohlcv) < 50:
                logger.warning(f"Insufficient data ({len(ohlcv)} candles). Need at least 50.")
                continue

            # Detect regime
            regime = regime_detector.analyze(ohlcv)
            logger.info(f"  Regime: {regime.regime.value} ({regime.confidence:.1f}% confidence)")
            logger.info(f"  Volatility: {regime.volatility_percentile:.1f}%")
            logger.info(f"  Trend Strength: {regime.trend_strength:.2f}")

            # 2. ORCHESTRATION LAYER - Select strategy
            logger.info("\n[2/4] ORCHESTRATION LAYER - Selecting strategy...")
            strategy = strategy_selector.select_strategy(
                regime=regime.regime,
                portfolio_value=config.initial_capital,
                current_positions=0,
                max_positions=3,
                risk_tolerance="medium"
            )
            logger.info(f"  Strategy: {strategy.strategy_name} ({strategy.confidence:.1f}% confidence)")
            logger.info(f"  Reasoning: {strategy.reasoning}")

            # 3. EXECUTION LAYER - Generate signals
            logger.info("\n[3/4] EXECUTION LAYER - Generating signals...")
            current_price = ohlcv[-1]['close']
            logger.info(f"  Current Price: ${current_price:,.2f}")

            # In paper mode, log the recommended action
            if config.paper_trading:
                if strategy.strategy_name != "WAIT":
                    logger.info(f"  📝 PAPER: Would execute {strategy.strategy_name}")
                    logger.info(f"  📝 Position size multiplier: {strategy.position_size_multiplier}x")
                    logger.info(f"  📝 Risk level: {strategy.risk_level}")
                else:
                    logger.info(f"  ⏸️  Strategy recommends: WAIT")

            # 4. LEARNING LAYER - Log performance
            logger.info("\n[4/4] LEARNING LAYER - Updating metrics...")
            tracker = get_performance_tracker()

            # Check for existing strategy performance data
            top_strategies = tracker.get_top_strategies_for_regime(
                regime.regime.value,
                limit=5,
                min_trades=1
            )
            if top_strategies:
                logger.info(f"  Top strategies for {regime.regime.value}:")
                for s in top_strategies[:3]:
                    logger.info(f"    - {s.get('strategy_name')}: {s.get('win_rate', 0)*100:.1f}% win rate")
            else:
                logger.info(f"  {strategy.strategy_name}: No historical data yet (learning mode)")

            logger.info(f"\n✅ Cycle {cycle_count} complete")

            # Wait between cycles (if running multiple)
            if cycles == 0 or cycle_count < cycles:
                import time
                logger.info("Waiting 60 seconds until next cycle...")
                time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n🛑 Stopped by user")

    logger.info("\n" + "="*60)
    logger.info("D.O.E. ENGINE SHUTDOWN")
    logger.info("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="D.O.E. Engine - Live Coinbase Mode")
    parser.add_argument("--symbol", default="BTC-USD", help="Trading pair (e.g., BTC-USD)")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles (0 = infinite)")

    args = parser.parse_args()

    run_doe_with_coinbase(args.symbol, args.cycles)

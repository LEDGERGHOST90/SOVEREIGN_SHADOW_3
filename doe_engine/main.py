#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - Main Entry Point

D.O.E. Pattern Autonomous Trading System

Usage:
    python main.py                    # Run in paper trading mode
    python main.py --live             # Run in live mode (requires confirmation)
    python main.py --backtest         # Run backtest on historical data
    python main.py --status           # Show current status

Safety:
    - Defaults to PAPER TRADING mode
    - Live trading requires explicit --live flag AND confirmation
    - All trades are logged to SQLite database
    - Daily loss limits enforced
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Ensure required directories exist BEFORE imports that might use them
_base_dir = Path(__file__).parent
(_base_dir / 'logs').mkdir(exist_ok=True)
(_base_dir / 'data').mkdir(exist_ok=True)

from doe_engine.core.orchestration import (
    SovereignShadowOrchestrator,
    OrchestratorConfig,
    create_orchestrator
)
from doe_engine.core.intelligence.performance_tracker import get_performance_tracker
from doe_engine.core.intelligence.regime_detector import get_regime_detector
from doe_engine.core.intelligence.strategy_selector import get_strategy_selector
from core.backtesting.backtest_engine import BacktestEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_base_dir / 'logs' / f'sovereign_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║             SOVEREIGN SHADOW III                               ║
    ║             D.O.E. Pattern Trading System                     ║
    ║                                                               ║
    ║    ┌──────────────┐     ┌──────────────────────┐              ║
    ║    │  DIRECTIVE   │────▶│ Market Regime        │              ║
    ║    │    LAYER     │     │ Detector             │              ║
    ║    └──────────────┘     └──────────────────────┘              ║
    ║           │                                                   ║
    ║           ▼                                                   ║
    ║    ┌──────────────┐     ┌──────────────────────┐              ║
    ║    │ ORCHESTRATION│────▶│ AI Strategy          │              ║
    ║    │    LAYER     │     │ Selector             │              ║
    ║    └──────────────┘     └──────────────────────┘              ║
    ║           │                                                   ║
    ║           ▼                                                   ║
    ║    ┌──────────────┐     ┌──────────────────────┐              ║
    ║    │  EXECUTION   │────▶│ Strategy Engine      │              ║
    ║    │    LAYER     │     │ + Exchange API       │              ║
    ║    └──────────────┘     └──────────────────────┘              ║
    ║           │                                                   ║
    ║           ▼                                                   ║
    ║    ┌──────────────┐     ┌──────────────────────┐              ║
    ║    │  LEARNING    │────▶│ Performance          │              ║
    ║    │    LAYER     │     │ Tracker              │              ║
    ║    └──────────────┘     └──────────────────────┘              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_status():
    """Print current system status"""
    print("\n" + "=" * 60)
    print("SOVEREIGN SHADOW III - SYSTEM STATUS")
    print("=" * 60)

    # Check components
    print("\nComponents:")

    # Performance Tracker
    try:
        tracker = get_performance_tracker()
        trades = tracker.get_all_trades(limit=5)
        print(f"  [OK] Performance Tracker - {len(trades)} recent trades")
    except Exception as e:
        print(f"  [ERROR] Performance Tracker: {e}")

    # Regime Detector
    try:
        detector = get_regime_detector()
        regime = detector.get_current_regime()
        if regime:
            print(f"  [OK] Regime Detector - Current: {regime.regime.value}")
        else:
            print(f"  [OK] Regime Detector - No regime detected yet")
    except Exception as e:
        print(f"  [ERROR] Regime Detector: {e}")

    # Strategy Selector
    try:
        selector = get_strategy_selector()
        print(f"  [OK] Strategy Selector - Initialized")
    except Exception as e:
        print(f"  [ERROR] Strategy Selector: {e}")

    # Environment
    print("\nEnvironment:")
    print(f"  ENV: {os.getenv('ENV', 'development')}")
    print(f"  ALLOW_LIVE_EXCHANGE: {os.getenv('ALLOW_LIVE_EXCHANGE', '0')}")

    # API Keys (check if set, don't show values)
    print("\nAPI Keys:")
    for key in ['COINBASE_API_KEY', 'KRAKEN_API_KEY', 'BINANCE_API_KEY', 'OKX_API_KEY']:
        status = "[SET]" if os.getenv(key) else "[NOT SET]"
        print(f"  {key}: {status}")

    print("\n" + "=" * 60)


async def run_paper_trading(config: OrchestratorConfig, symbol: str):
    """Run the system in paper trading mode"""
    print_banner()

    print("\n" + "=" * 60)
    print("STARTING PAPER TRADING MODE")
    print("=" * 60)
    print(f"\nSymbol: {symbol}")
    print(f"Initial Capital: ${config.initial_capital:,.2f}")
    print(f"Max Position Size: {config.max_position_size_percent}%")
    print(f"Max Positions: {config.max_open_positions}")
    print(f"Daily Loss Limit: {config.max_daily_loss_percent}%")
    print("\nPress Ctrl+C to stop...")
    print("=" * 60)

    orchestrator = SovereignShadowOrchestrator(config=config)

    try:
        await orchestrator.run(symbol)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        orchestrator.stop()


async def run_live_trading(config: OrchestratorConfig, symbol: str):
    """Run the system in live trading mode"""
    print_banner()

    print("\n" + "=" * 60)
    print("!!! LIVE TRADING MODE !!!")
    print("=" * 60)
    print("\nWARNING: This will execute REAL trades with REAL money!")
    print(f"\nSymbol: {symbol}")
    print(f"Initial Capital: ${config.initial_capital:,.2f}")
    print(f"Max Position Size: {config.max_position_size_percent}%")

    # Safety checks
    if os.getenv('ENV') != 'production':
        print("\nERROR: ENV must be set to 'production' for live trading")
        return

    if os.getenv('ALLOW_LIVE_EXCHANGE') != '1':
        print("\nERROR: ALLOW_LIVE_EXCHANGE must be set to '1' for live trading")
        return

    # Confirmation
    confirm = input("\nType 'I UNDERSTAND THE RISKS' to proceed: ")
    if confirm != "I UNDERSTAND THE RISKS":
        print("Live trading cancelled.")
        return

    config.paper_trading = False
    config.sandbox_mode = False

    orchestrator = SovereignShadowOrchestrator(config=config)

    try:
        await orchestrator.run(symbol)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        orchestrator.stop()


def run_backtest(symbol: str):
    """Run backtest on historical data"""
    print_banner()

    print("\n" + "=" * 60)
    print("BACKTEST MODE")
    print("=" * 60)

    engine = BacktestEngine(initial_capital=10000.0)

    # Generate synthetic data for testing
    print("\nGenerating synthetic market data...")
    engine.generate_synthetic_data(num_candles=1000, trend="bullish")

    # Run backtests
    print("\nRunning backtests for all strategies...")
    strategies = ["ElderReversion", "RSIReversion", "TrendFollowEMA"]
    results = engine.run_all_backtests(strategies)

    # Generate and print report
    report = engine.generate_report(results)
    print(report)

    # Save results
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    import json
    results_file = output_dir / f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump({k: v.to_dict() for k, v in results.items()}, f, indent=2)

    print(f"\nResults saved to: {results_file}")


async def run_single_cycle(symbol: str):
    """Run a single trading cycle (for testing)"""
    print_banner()

    print("\n" + "=" * 60)
    print("SINGLE CYCLE TEST MODE")
    print("=" * 60)

    config = OrchestratorConfig(
        paper_trading=True,
        initial_capital=10000.0
    )

    orchestrator = SovereignShadowOrchestrator(config=config)
    await orchestrator.run_single_cycle(symbol)

    status = orchestrator.get_status()
    print("\nCycle Complete!")
    print(f"Current Regime: {status['current_regime']}")
    print(f"Portfolio Value: ${status['portfolio_value']:,.2f}")
    print(f"Open Positions: {status['open_positions']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Sovereign Shadow III - D.O.E. Pattern Trading System'
    )

    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live trading mode (requires confirmation)'
    )

    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run backtest on historical data'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current system status'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run single cycle test'
    )

    parser.add_argument(
        '--symbol',
        type=str,
        default='BTC/USD',
        help='Trading symbol (default: BTC/USD)'
    )

    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial capital (default: 10000)'
    )

    parser.add_argument(
        '--max-positions',
        type=int,
        default=3,
        help='Maximum open positions (default: 3)'
    )

    args = parser.parse_args()

    # Ensure logs directory exists
    (Path(__file__).parent / 'logs').mkdir(exist_ok=True)

    # Status mode
    if args.status:
        print_status()
        return

    # Backtest mode
    if args.backtest:
        run_backtest(args.symbol)
        return

    # Test mode
    if args.test:
        asyncio.run(run_single_cycle(args.symbol))
        return

    # Create config
    config = OrchestratorConfig(
        paper_trading=not args.live,
        sandbox_mode=not args.live,
        initial_capital=args.capital,
        max_open_positions=args.max_positions
    )

    # Run trading
    if args.live:
        asyncio.run(run_live_trading(config, args.symbol))
    else:
        asyncio.run(run_paper_trading(config, args.symbol))


if __name__ == "__main__":
    main()

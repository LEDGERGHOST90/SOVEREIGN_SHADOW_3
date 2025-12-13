#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - STARTUP SCRIPT
Initializes and runs the autonomous trading system

Usage:
    python scripts/start_sovereign_shadow.py [--mode=fake|sandbox|live] [--capital=10000]

Safety Notes:
    - Default mode is FAKE (paper trading)
    - LIVE mode requires: ALLOW_LIVE_TRADING=YES_I_UNDERSTAND_THE_RISKS
    - Always run pre-flight checks before live trading

Author: SovereignShadow Trading System
"""

import os
import sys
import argparse
import asyncio
import logging
import signal
from datetime import datetime
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/workspace')

from core.orchestrator import SovereignOrchestrator, TradingMode, create_orchestrator
from core.safety.guardrails import PreflightChecklist, SafetyGuardrails

# Import strategies
from strategies.modularized.elder_reversion import get_strategy as get_elder_reversion
from strategies.modularized.trend_follow_ema import get_strategy as get_trend_follow
from strategies.modularized.rsi_reversion import get_strategy as get_rsi_reversion
from strategies.modularized.bollinger_bounce import get_strategy as get_bollinger_bounce
from strategies.modularized.volatility_breakout import get_strategy as get_volatility_breakout
from strategies.modularized.banded_stochastic import get_strategy as get_banded_stochastic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="🏴 Sovereign Shadow II - Autonomous Trading System"
    )
    parser.add_argument(
        '--mode',
        choices=['fake', 'sandbox', 'live'],
        default='fake',
        help='Trading mode (default: fake)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000,
        help='Initial capital in USD (default: 10000)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='sovereign_shadow.db',
        help='Database path (default: sovereign_shadow.db)'
    )
    parser.add_argument(
        '--skip-preflight',
        action='store_true',
        help='Skip pre-flight checks (not recommended)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Initialize but do not run trading loop'
    )
    
    return parser.parse_args()


def load_all_strategies(orchestrator: SovereignOrchestrator):
    """Load all available strategies"""
    strategies = [
        get_elder_reversion(),
        get_trend_follow(),
        get_rsi_reversion(),
        get_bollinger_bounce(),
        get_volatility_breakout(),
        get_banded_stochastic()
    ]
    
    for strategy in strategies:
        orchestrator.register_strategy(strategy)
    
    logger.info(f"📚 Loaded {len(strategies)} strategies")
    return strategies


async def main():
    """Main entry point"""
    args = parse_args()
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🏴 SOVEREIGN SHADOW II                                      ║
    ║   Autonomous Trading System                                   ║
    ║                                                               ║
    ║   D.O.E. Pattern: Directive → Orchestration → Execution       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Run pre-flight checks
    if not args.skip_preflight:
        logger.info("🛫 Running pre-flight checks...")
        passed, checks = PreflightChecklist.run_all_checks()
        
        if not passed:
            logger.error("❌ Pre-flight checks failed. Fix issues before continuing.")
            if args.mode == 'live':
                logger.critical("🚨 LIVE mode blocked due to failed checks")
                sys.exit(1)
            else:
                logger.warning("⚠️  Continuing in FAKE mode despite failed checks")
    
    # Validate live mode
    if args.mode == 'live':
        env_flag = os.getenv('ALLOW_LIVE_TRADING')
        if env_flag != 'YES_I_UNDERSTAND_THE_RISKS':
            logger.critical("""
🚨 LIVE TRADING BLOCKED

To enable live trading, set:
    export ALLOW_LIVE_TRADING=YES_I_UNDERSTAND_THE_RISKS

WARNING: Live trading involves real money and real risk.
Only enable after thorough testing in FAKE mode.
""")
            sys.exit(1)
    
    # Create orchestrator
    logger.info(f"🔧 Creating orchestrator (mode={args.mode}, capital=${args.capital:,.2f})")
    orchestrator = create_orchestrator(
        mode=args.mode,
        initial_capital=args.capital,
        db_path=args.db
    )
    
    # Load strategies
    load_all_strategies(orchestrator)
    
    # Setup signal handlers for graceful shutdown
    def handle_shutdown(signum, frame):
        logger.info("🛑 Shutdown signal received")
        orchestrator.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Print startup summary
    print(f"""
📊 SYSTEM CONFIGURATION
=======================
Mode: {args.mode.upper()}
Capital: ${args.capital:,.2f}
Database: {args.db}
Strategies Loaded: {len(orchestrator.loaded_strategies)}
  - {chr(10).join(f"  • {s}" for s in orchestrator.loaded_strategies.keys())}

⚙️  SAFETY LIMITS
================
Max Position Size: 10%
Max Daily Loss: 3%
Max Positions: 3
Cooldown: 5 minutes
    """)
    
    if args.dry_run:
        logger.info("🏁 Dry run complete - system initialized but not running")
        print("\n✅ System ready. Use --dry-run=false to start trading loop.")
        orchestrator.shutdown()
        return
    
    # Start trading loop
    logger.info("🚀 Starting trading loop...")
    print("\n💫 Sovereign Shadow II is now active")
    print("   Press Ctrl+C to stop\n")
    
    # Note: In a real deployment, this would fetch live market data
    # For now, this is a demonstration of the system startup
    import pandas as pd
    import numpy as np
    
    # Generate sample data for demonstration
    np.random.seed(42)
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            
            # Generate sample market data (replace with real data feed)
            dates = pd.date_range(end=datetime.utcnow(), periods=200, freq='1h')
            base_price = 100000
            trend = np.cumsum(np.random.randn(200) * 500)
            
            df = pd.DataFrame({
                'open': base_price + trend + np.random.randn(200) * 100,
                'high': base_price + trend + abs(np.random.randn(200)) * 200,
                'low': base_price + trend - abs(np.random.randn(200)) * 200,
                'close': base_price + trend + np.random.randn(200) * 100,
                'volume': np.random.randint(100, 1000, 200)
            }, index=dates)
            
            df['high'] = df[['open', 'high', 'close']].max(axis=1)
            df['low'] = df[['open', 'low', 'close']].min(axis=1)
            
            market_data = {
                'ohlcv': df,
                'asset': 'BTC/USDT',
                'timeframe': '1h'
            }
            
            # Run trading cycle
            result = await orchestrator.run_cycle(market_data)
            
            # Log result
            if result.get('regime'):
                logger.info(f"Cycle {cycle_count}: Regime={result['regime']['type']}, Strategy={result.get('strategy_selected', {}).get('name', 'None')}")
            
            # Print summary every 10 cycles
            if cycle_count % 10 == 0:
                print(orchestrator.get_summary())
            
            # Wait before next cycle (5 minutes in production, 10 seconds for demo)
            await asyncio.sleep(10)
            
        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
            await asyncio.sleep(30)  # Wait longer after error
    
    orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

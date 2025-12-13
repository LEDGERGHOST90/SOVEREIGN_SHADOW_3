#!/usr/bin/env python3
"""
Sovereign Shadow II - Main Entry Point
Autonomous Trading System with Skills-Based AI Architecture
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from core import SovereignShadowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sovereign_shadow.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("SOVEREIGN SHADOW II - AUTONOMOUS TRADING SYSTEM")
    logger.info("=" * 60)
    
    # Check environment variables
    env = os.getenv('ENV', 'development')
    allow_live = os.getenv('ALLOW_LIVE_EXCHANGE', '0')
    use_sandbox = os.getenv('USE_SANDBOX', 'true').lower() == 'true'
    
    logger.info(f"Environment: {env}")
    logger.info(f"Live Trading Allowed: {allow_live == '1'}")
    logger.info(f"Sandbox Mode: {use_sandbox}")
    
    if env != 'production' or allow_live != '1':
        logger.warning("⚠️  SYSTEM RUNNING IN SAFE MODE - NO REAL TRADES WILL BE EXECUTED")
        logger.warning("Set ENV=production and ALLOW_LIVE_EXCHANGE=1 to enable live trading")
    
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    Path('strategies/modularized').mkdir(parents=True, exist_ok=True)
    
    # Initialize orchestrator
    orchestrator = SovereignShadowOrchestrator(
        db_path="data/performance.db",
        strategies_path="strategies/modularized",
        use_sandbox=use_sandbox
    )
    
    try:
        # Initialize components
        await orchestrator.initialize()
        
        # Start main loop
        await orchestrator.start()
    
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await orchestrator.stop()
        logger.info("Sovereign Shadow II shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
🤖 AUTONOMOUS TRADING LOOP
24/7 automated trading system with AI swarms

Components:
1. Signal monitoring (10min cycle)
2. Ray Score filtering (threshold: 60)
3. Ladder deployment (high-quality signals)
4. Profit extraction (milestone checks)
5. Swarm coordination (Agent/Shadow/Hive)
6. Exchange injection (120min cache)
"""

import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add modules to path
MODULES_PATH = Path(__file__).parent / "modules"
sys.path.insert(0, str(MODULES_PATH))

# Import components
from ladder import UnifiedLadderSystem, TieredLadderSystem
from tracking import InjectionManager
from hybrid_system.swarm_intelligence_bridge import SwarmIntelligenceBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("autonomous_trading")


class AutonomousTradingLoop:
    """
    24/7 autonomous trading system

    Features:
    - Signal monitoring every 10 minutes
    - Ray Score filtering (min 60)
    - Auto ladder deployment
    - Profit milestone extraction
    - Swarm intelligence coordination
    - Exchange data injection
    """

    def __init__(
        self,
        mode: str = 'paper',
        ray_score_threshold: int = 60,
        max_concurrent_ladders: int = 3,
        cycle_interval_seconds: int = 600  # 10 minutes
    ):
        self.mode = mode
        self.ray_score_threshold = ray_score_threshold
        self.max_concurrent_ladders = max_concurrent_ladders
        self.cycle_interval_seconds = cycle_interval_seconds

        # Initialize components
        self.ladder_system = UnifiedLadderSystem()
        self.profit_extraction = TieredLadderSystem()
        self.injection_manager = InjectionManager()
        self.swarm_bridge = SwarmIntelligenceBridge()

        # State tracking
        self.cycle_count = 0
        self.total_signals_processed = 0
        self.total_ladders_deployed = 0
        self.total_extractions = 0
        self.running = False

        logger.info(f"🤖 Autonomous Trading Loop initialized (mode: {mode})")

    def get_mock_signals(self) -> List[Dict[str, Any]]:
        """
        Generate mock trading signals for testing

        In production, replace with:
        - Telegram signal parser
        - Discord bot integration
        - TradingView webhook receiver
        - Technical analysis signal generator
        """
        import random

        mock_signals = []

        # Generate 2-5 random signals
        num_signals = random.randint(2, 5)

        for i in range(num_signals):
            signal = {
                'symbol': random.choice(['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']),
                'direction': random.choice(['LONG', 'SHORT']),
                'entry_price': random.uniform(100, 50000),
                'stop_loss': None,
                'take_profit_levels': [1.02, 1.05, 1.10],  # 2%, 5%, 10% targets
                'confidence': random.uniform(0.5, 0.95),
                'source': 'mock_generator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            mock_signals.append(signal)

        return mock_signals

    def calculate_ray_score(self, signal: Dict[str, Any]) -> float:
        """
        Calculate Ray Score for signal quality filtering

        Factors:
        - Confidence level (40%)
        - Signal source reputation (30%)
        - Technical indicators (20%)
        - Market conditions (10%)

        Returns:
            Ray Score (0-100)
        """
        score = 0.0

        # Confidence level (40 points max)
        confidence = signal.get('confidence', 0.5)
        score += confidence * 40

        # Source reputation (30 points max)
        source = signal.get('source', 'unknown')
        source_scores = {
            'premium_telegram': 30,
            'verified_discord': 25,
            'trading_view': 20,
            'technical_analysis': 15,
            'mock_generator': 10
        }
        score += source_scores.get(source, 5)

        # Technical alignment (20 points max)
        if signal.get('has_technicals', False):
            score += 20
        else:
            score += 10  # Partial credit

        # Market conditions (10 points max)
        # TODO: Check BTC dominance, volatility, volume
        score += 5  # Placeholder

        return round(score, 2)

    async def process_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Process a single trading signal

        Steps:
        1. Calculate Ray Score
        2. Filter by threshold
        3. Check concurrent ladder limit
        4. Deploy ladder if conditions met

        Returns:
            True if ladder deployed, False otherwise
        """
        ray_score = self.calculate_ray_score(signal)
        signal['ray_score'] = ray_score

        logger.info(f"📊 Signal: {signal['symbol']} {signal['direction']} | Ray Score: {ray_score}")

        # Filter by Ray Score
        if ray_score < self.ray_score_threshold:
            logger.info(f"   ❌ Rejected: Ray Score {ray_score} < {self.ray_score_threshold}")
            return False

        # Check concurrent ladder limit
        active_ladders = self.ladder_system.get_active_ladders()
        if len(active_ladders) >= self.max_concurrent_ladders:
            logger.info(f"   ⏸️  Queued: Max concurrent ladders reached ({self.max_concurrent_ladders})")
            return False

        # Deploy ladder
        try:
            capital = 500.0  # TODO: Dynamic capital allocation based on Ray Score
            logger.info(f"   ✅ Deploying ladder with ${capital:.2f}")

            result = self.ladder_system.deploy_ladder(signal, capital, mode=self.mode)

            if result.get('status') == 'success':
                self.total_ladders_deployed += 1
                logger.info(f"   🚀 Ladder deployed successfully")
                return True
            else:
                logger.warning(f"   ⚠️  Ladder deployment failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error deploying ladder: {e}")
            return False

    async def run_trading_cycle(self):
        """
        Execute one complete trading cycle

        Steps:
        1. Fetch signals from sources
        2. Calculate Ray Scores
        3. Deploy high-quality signals
        4. Check profit extraction milestones
        5. Update exchange injections
        6. Sync swarm intelligence
        """
        self.cycle_count += 1
        cycle_start = datetime.now(timezone.utc)

        logger.info("="*70)
        logger.info(f"🔄 CYCLE #{self.cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info("="*70)

        try:
            # Step 1: Fetch signals
            logger.info("\n📡 Step 1: Fetching trading signals...")
            signals = self.get_mock_signals()
            logger.info(f"   Found {len(signals)} signals")
            self.total_signals_processed += len(signals)

            # Step 2: Process signals
            logger.info("\n🎯 Step 2: Processing signals with Ray Score filter...")
            deployed_count = 0
            for signal in signals:
                deployed = await self.process_signal(signal)
                if deployed:
                    deployed_count += 1

            logger.info(f"   Deployed: {deployed_count}/{len(signals)} ladders")

            # Step 3: Check profit milestones
            logger.info("\n💰 Step 3: Checking profit extraction milestones...")
            extraction_result = self.profit_extraction.run_ladder_check()
            if extraction_result.get('extraction_triggered'):
                self.total_extractions += 1
                logger.info(f"   ✅ Extraction triggered: {extraction_result}")
            else:
                logger.info(f"   ⏳ No milestone reached yet")

            # Step 4: Update exchange injections (cached 120min)
            logger.info("\n🔄 Step 4: Updating exchange injections...")
            injection_result = self.injection_manager.inject_all()
            logger.info(f"   Exchanges updated: {injection_result}")

            # Step 5: Sync swarm intelligence
            logger.info("\n🐝 Step 5: Syncing swarm intelligence...")
            swarm_success = self.swarm_bridge.sync_to_profit_tracker()
            if swarm_success:
                logger.info(f"   ✅ Swarm data synced")
            else:
                logger.info(f"   ⚠️  Swarm sync with warnings")

            # Cycle complete
            cycle_duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
            logger.info("\n" + "="*70)
            logger.info(f"✅ CYCLE #{self.cycle_count} COMPLETE ({cycle_duration:.1f}s)")
            logger.info(f"   Signals Processed: {len(signals)}")
            logger.info(f"   Ladders Deployed: {deployed_count}")
            logger.info(f"   Total Lifetime: {self.total_signals_processed} signals, {self.total_ladders_deployed} ladders")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"\n❌ Error in trading cycle: {e}")
            import traceback
            traceback.print_exc()

    async def run(self):
        """
        Main autonomous loop

        Runs continuously until interrupted
        """
        logger.info("\n" + "="*70)
        logger.info("🤖 AUTONOMOUS TRADING LOOP - STARTING")
        logger.info("="*70)
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Ray Score Threshold: {self.ray_score_threshold}")
        logger.info(f"Max Concurrent Ladders: {self.max_concurrent_ladders}")
        logger.info(f"Cycle Interval: {self.cycle_interval_seconds}s ({self.cycle_interval_seconds/60:.1f} min)")
        logger.info("="*70)
        logger.info("\nPress Ctrl+C to stop\n")

        self.running = True

        try:
            while self.running:
                await self.run_trading_cycle()

                # Wait for next cycle
                logger.info(f"\n⏳ Waiting {self.cycle_interval_seconds}s until next cycle...\n")
                await asyncio.sleep(self.cycle_interval_seconds)

        except KeyboardInterrupt:
            logger.info("\n\n🛑 Shutdown requested...")
            self.running = False

        except Exception as e:
            logger.error(f"\n❌ Fatal error: {e}")
            self.running = False

        finally:
            logger.info("\n" + "="*70)
            logger.info("🛑 AUTONOMOUS TRADING LOOP - STOPPED")
            logger.info("="*70)
            logger.info(f"Total Cycles: {self.cycle_count}")
            logger.info(f"Total Signals: {self.total_signals_processed}")
            logger.info(f"Total Ladders: {self.total_ladders_deployed}")
            logger.info(f"Total Extractions: {self.total_extractions}")
            logger.info("="*70)


async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Autonomous trading loop')
    parser.add_argument(
        '--mode',
        choices=['paper', 'live'],
        default='paper',
        help='Trading mode (default: paper)'
    )
    parser.add_argument(
        '--ray-threshold',
        type=int,
        default=60,
        help='Minimum Ray Score to deploy ladder (default: 60)'
    )
    parser.add_argument(
        '--max-ladders',
        type=int,
        default=3,
        help='Maximum concurrent ladders (default: 3)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=600,
        help='Cycle interval in seconds (default: 600 = 10 min)'
    )

    args = parser.parse_args()

    loop = AutonomousTradingLoop(
        mode=args.mode,
        ray_score_threshold=args.ray_threshold,
        max_concurrent_ladders=args.max_ladders,
        cycle_interval_seconds=args.interval
    )

    await loop.run()


if __name__ == "__main__":
    asyncio.run(main())

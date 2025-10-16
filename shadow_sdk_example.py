#!/usr/bin/env python3
"""
🏴 Shadow SDK - Example Usage

Demonstrates the complete Shadow SDK in action.
"""

import asyncio
import sys
from pathlib import Path

# Add shadow_sdk to path
sys.path.insert(0, str(Path(__file__).parent))

from shadow_sdk import ShadowScope, ShadowPulse, ShadowSnaps, ShadowSynapse
from shadow_sdk import CAPITAL_TOTAL, TARGET_CAPITAL, PHILOSOPHY
from shadow_sdk.utils import setup_logger, RiskManager

# Setup logging
logger = setup_logger("shadow_example", log_file="logs/shadow_example.log")


async def main():
    """Main example function."""
    logger.info("=" * 60)
    logger.info("🏴 SHADOW SDK EXAMPLE - Sovereign Shadow Empire")
    logger.info("=" * 60)
    logger.info(f"Capital: ${CAPITAL_TOTAL:,.2f} → Target: ${TARGET_CAPITAL:,.2f}")
    logger.info(f"Philosophy: {PHILOSOPHY}")
    logger.info("=" * 60)
    
    # Initialize all SDK components
    logger.info("\n🔧 Initializing Shadow SDK components...")
    
    scope = ShadowScope()
    pulse = ShadowPulse()
    snaps = ShadowSnaps()
    synapse = ShadowSynapse()
    risk_mgr = RiskManager()
    
    # Connect layers to synapse
    synapse.connect_scope(scope)
    synapse.connect_pulse(pulse)
    synapse.connect_snaps(snaps)
    
    logger.info("✅ All components initialized")
    
    # Start market scanner
    logger.info("\n📊 Starting ShadowScope market scanner...")
    scanner_task = asyncio.create_task(scope.start_scanner(interval=2.0))
    
    # Wait for initial data
    await asyncio.sleep(5)
    
    # Get market intelligence
    logger.info("\n🧠 Fetching market intelligence...")
    intelligence = await scope.get_market_intelligence()
    
    logger.info(f"Exchanges monitored: {intelligence['health']['exchanges_monitored']}")
    logger.info(f"Pairs monitored: {intelligence['health']['pairs_monitored']}")
    logger.info(f"Tick count: {intelligence['health']['tick_count']}")
    logger.info(f"Data quality: {intelligence['health']['data_quality_percent']:.1f}%")
    
    # Display current prices
    logger.info("\n💰 Current Prices:")
    for exchange, pairs in intelligence['current_prices'].items():
        logger.info(f"  {exchange.upper()}:")
        for pair, price in list(pairs.items())[:3]:  # First 3 pairs
            logger.info(f"    {pair}: ${price:,.2f}")
    
    # Get sentiment
    logger.info("\n📸 Sentiment Analysis:")
    for asset in ["BTC", "ETH", "SOL"]:
        sentiment = await snaps.get_sentiment(asset)
        emoji = "🔥" if sentiment['trending'] else "📊"
        logger.info(f"  {emoji} {asset}: {sentiment['score']:+.2f} ({sentiment['magnitude']:.2f} magnitude)")
    
    # Setup signal handler
    logger.info("\n⚡ Setting up signal handler...")
    
    signal_count = [0]  # Use list to modify in nested function
    
    async def handle_signal(signal):
        signal_count[0] += 1
        logger.info(f"\n📡 Signal #{signal_count[0]} received:")
        logger.info(f"   Type: {signal['type']}")
        logger.info(f"   Pair: {signal['pair']}")
        logger.info(f"   Spread: {signal['spread']:.4%}")
        logger.info(f"   Confidence: {signal['confidence']:.2%}")
        
        # Check risk management
        if not risk_mgr.can_trade(amount=100):
            logger.warning("   ⚠️ Risk manager blocked trade")
            return
        
        # Analyze with synapse
        decision = await synapse.analyze_opportunity(signal)
        
        logger.info(f"   🧠 Synapse Decision: {decision['action'].upper()}")
        logger.info(f"   Strategy: {decision['strategy']}")
        logger.info(f"   Confidence: {decision['confidence']:.2%}")
        logger.info(f"   Reasoning: {decision['reasoning']}")
        
        if decision['action'] == 'execute':
            logger.info(f"   ✅ Would execute with ${decision['risk_assessment']['position_size']:.2f}")
    
    pulse.subscribe(handle_signal)
    
    # Start signal streaming
    logger.info("⚡ Starting ShadowPulse signal streaming...")
    streaming_task = asyncio.create_task(pulse.start_streaming(interval=0.5))
    
    # Run for 30 seconds
    logger.info("\n⏳ Running for 30 seconds...")
    await asyncio.sleep(30)
    
    # Cleanup
    logger.info("\n🛑 Stopping all components...")
    scope.stop_scanner()
    pulse.stop_streaming()
    
    await asyncio.sleep(1)  # Allow tasks to cleanup
    
    # Final stats
    logger.info("\n📊 FINAL STATISTICS:")
    logger.info("=" * 60)
    
    scope_health = await scope.get_health_status()
    logger.info(f"ShadowScope: {scope_health['tick_count']} ticks processed")
    logger.info(f"             {scope_health['ticks_per_second']:.0f} ticks/second average")
    
    pulse_stats = pulse.get_signal_stats()
    logger.info(f"ShadowPulse: {pulse_stats['signals_sent']} signals sent")
    
    synapse_stats = synapse.get_performance_stats()
    logger.info(f"ShadowSynapse: {synapse_stats['decisions_made']} decisions made")
    
    risk_status = risk_mgr.get_status()
    logger.info(f"Risk Manager: Daily P&L ${risk_status['daily_pnl']:.2f}")
    logger.info(f"              {risk_status['daily_trades']} trades executed")
    
    logger.info("=" * 60)
    logger.info("🏴 Shadow SDK Example Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)


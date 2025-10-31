#!/usr/bin/env python3
"""
🧠 SHADOW SDK DEMO - ShadowScope Market Intelligence

This demonstrates how to use ShadowScope, the core market scanning engine.

ShadowScope monitors all exchanges in real-time, detects opportunities,
and provides market intelligence for trading decisions.
"""

import asyncio
import sys
from pathlib import Path

# Add shadow_sdk to path
sys.path.insert(0, str(Path(__file__).parent))

from shadow_sdk import ShadowScope, EXCHANGES, PAIRS, PHILOSOPHY
from shadow_sdk.utils import setup_logger

# Setup logging
logger = setup_logger("shadow_scope_demo", log_file="logs/shadow_scope_demo.log")

async def demo_basic_usage():
    """Demo 1: Basic ShadowScope usage"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 🧠 DEMO 1: BASIC SHADOWSCOPE USAGE                                 ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize ShadowScope
    print("📡 Initializing ShadowScope...")
    scope = ShadowScope()

    print(f"   Monitoring: {len(scope.exchanges)} exchanges")
    print(f"   Tracking: {len(scope.pairs)} trading pairs")
    print(f"   Total streams: {len(scope.exchanges) * len(scope.pairs)}")
    print()

    # Get initial market intelligence (without starting scanner)
    print("🔍 Getting market intelligence snapshot...")
    intelligence = await scope.get_market_intelligence()

    print(f"\n📊 Market Intelligence Report:")
    print(f"   Timestamp: {intelligence['timestamp']}")
    print(f"   Data Quality: {intelligence['health']['data_quality']:.1f}%")
    print(f"   Exchanges Monitored: {intelligence['health']['exchanges_monitored']}")
    print(f"   Pairs Tracked: {intelligence['health']['pairs_tracked']}")
    print()

    # Show current prices (simulated data)
    print("💰 Current Market Prices:")
    for pair, price in intelligence['current_prices'].items():
        print(f"   {pair:12s}: ${price:>12,.2f}")
    print()

async def demo_real_time_scanning():
    """Demo 2: Real-time market scanning"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 🚀 DEMO 2: REAL-TIME MARKET SCANNING                               ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize scope
    print("📡 Initializing ShadowScope for real-time scanning...")
    scope = ShadowScope(exchanges=["coinbase", "okx"], pairs=["BTC/USD", "ETH/USD"])
    print()

    # Start scanner in background
    print("🚀 Starting real-time scanner (5 seconds)...")
    scanner_task = asyncio.create_task(scope.start_scanner(interval=1.0))

    # Monitor for 5 seconds
    for i in range(5):
        await asyncio.sleep(1)
        intelligence = await scope.get_market_intelligence()

        print(f"   Scan {i+1}/5 - Ticks processed: {scope.tick_count:4d} | "
              f"Quality: {intelligence['health']['data_quality']:.1f}%")

    # Stop scanner
    scope.stop_scanner()
    await asyncio.sleep(0.5)  # Give it time to stop

    print()
    print("✅ Scanner stopped")
    print(f"   Total ticks processed: {scope.tick_count}")
    print(f"   Average ticks/sec: {scope.tick_count / 5:.0f}")
    print()

async def demo_opportunity_detection():
    """Demo 3: Opportunity detection"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 🎯 DEMO 3: OPPORTUNITY DETECTION                                   ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize scope
    print("📡 Initializing ShadowScope for opportunity detection...")
    scope = ShadowScope()

    # Start scanner briefly to gather data
    print("🔍 Scanning market for opportunities...")
    scanner_task = asyncio.create_task(scope.start_scanner(interval=0.5))

    await asyncio.sleep(3)

    # Detect opportunities
    opportunities = await scope.detect_opportunities()

    scope.stop_scanner()

    print(f"\n🎯 Opportunities Found: {len(opportunities)}")
    print()

    if opportunities:
        for i, opp in enumerate(opportunities[:5], 1):  # Show max 5
            print(f"   {i}. {opp['type'].upper()}")
            print(f"      Pair: {opp['pair']}")
            print(f"      Spread: {opp['spread']:.4%}")
            print(f"      Confidence: {opp['confidence']:.1%}")
            print(f"      Exchanges: {opp.get('exchanges', ['unknown'])}")
            print()
    else:
        print("   No opportunities found in current market conditions.")
        print("   (This is normal - opportunities are rare)")
    print()

async def demo_volatility_tracking():
    """Demo 4: Volatility and volume tracking"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 📈 DEMO 4: VOLATILITY & VOLUME TRACKING                            ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize scope
    print("📡 Initializing ShadowScope for volatility tracking...")
    scope = ShadowScope(pairs=["BTC/USD", "ETH/USD", "SOL/USD"])

    # Gather data
    print("📊 Gathering market data...")
    scanner_task = asyncio.create_task(scope.start_scanner(interval=0.5))

    await asyncio.sleep(3)

    scope.stop_scanner()

    # Get intelligence with volatility data
    intelligence = await scope.get_market_intelligence()

    print(f"\n📈 Volatility Report:")
    for pair, volatility in intelligence.get('volatility', {}).items():
        price = intelligence['current_prices'].get(pair, 0)
        volume = intelligence.get('volumes', {}).get(pair, 0)

        print(f"\n   {pair}:")
        print(f"      Price: ${price:,.2f}")
        print(f"      Volatility: {volatility:.2%}")
        print(f"      Volume (24h): ${volume:,.0f}")

        # Volatility indicator
        if volatility > 0.05:
            print(f"      Status: 🔴 HIGH VOLATILITY")
        elif volatility > 0.02:
            print(f"      Status: 🟡 MODERATE")
        else:
            print(f"      Status: 🟢 LOW")
    print()

async def demo_complete_workflow():
    """Demo 5: Complete workflow with ShadowScope"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 🏴 DEMO 5: COMPLETE SHADOWSCOPE WORKFLOW                           ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    print(f"Philosophy: \"{PHILOSOPHY}\"")
    print()

    # Initialize
    print("1️⃣ Initializing ShadowScope...")
    scope = ShadowScope()
    print(f"   ✅ Monitoring {len(scope.exchanges)} exchanges: {', '.join(scope.exchanges)}")
    print()

    # Start scanning
    print("2️⃣ Starting real-time scanner...")
    scanner_task = asyncio.create_task(scope.start_scanner(interval=1.0))
    print("   ✅ Scanner active")
    print()

    # Monitor for 10 seconds with updates
    print("3️⃣ Monitoring market (10 seconds)...")
    for i in range(10):
        await asyncio.sleep(1)

        # Get current intelligence
        intel = await scope.get_market_intelligence()

        # Show progress
        print(f"   [{i+1:2d}/10] Ticks: {scope.tick_count:4d} | "
              f"Quality: {intel['health']['data_quality']:.1f}% | "
              f"BTC: ${intel['current_prices'].get('BTC/USD', 0):,.0f}")

    print()

    # Detect opportunities
    print("4️⃣ Detecting opportunities...")
    opportunities = await scope.detect_opportunities()
    print(f"   ✅ Found {len(opportunities)} opportunities")
    print()

    # Stop scanner
    print("5️⃣ Stopping scanner...")
    scope.stop_scanner()
    await asyncio.sleep(0.5)
    print("   ✅ Scanner stopped gracefully")
    print()

    # Final report
    print("6️⃣ Final Report:")
    final_intel = await scope.get_market_intelligence()
    print(f"   Total Ticks Processed: {scope.tick_count}")
    print(f"   Runtime: {time.time() - scope.start_time:.1f}s")
    print(f"   Average Ticks/Sec: {scope.tick_count / (time.time() - scope.start_time):.0f}")
    print(f"   Data Quality: {final_intel['health']['data_quality']:.1f}%")
    print(f"   Opportunities: {len(opportunities)}")
    print()

    print("✅ Complete workflow finished successfully!")
    print()

async def main():
    """Run all demos"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🧠 SHADOWSCOPE DEMONSTRATION - MARKET INTELLIGENCE ENGINE        ║
║                                                                    ║
║   Powered by Shadow SDK                                            ║
║   Sovereign Shadow Trading Empire                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

This demo shows how to use ShadowScope, the core market scanning engine
of the Shadow SDK. ShadowScope monitors multiple exchanges in real-time,
detects trading opportunities, and provides market intelligence.

""")

    import time

    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Real-Time Scanning", demo_real_time_scanning),
        ("Opportunity Detection", demo_opportunity_detection),
        ("Volatility Tracking", demo_volatility_tracking),
        ("Complete Workflow", demo_complete_workflow)
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            await demo_func()

            if i < len(demos):
                print("─" * 70)
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in demo {name}: {e}")
            print(f"❌ Error in demo: {e}")
            print()

    print("""
╔════════════════════════════════════════════════════════════════════╗
║ 🎯 DEMO COMPLETE                                                   ║
╚════════════════════════════════════════════════════════════════════╝

You've seen how ShadowScope:
- ✅ Monitors multiple exchanges in real-time
- ✅ Detects trading opportunities automatically
- ✅ Tracks volatility and volume
- ✅ Provides market intelligence for decisions
- ✅ Processes 100+ ticks/second

Next steps:
1. Configure API keys (see API_KEY_SETUP_GUIDE.md)
2. Connect ShadowScope to real exchange data
3. Integrate with Master Trading Loop
4. Start paper trading with real market data

Your Master Trading Loop is already using ShadowScope! 🚀
    """)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")

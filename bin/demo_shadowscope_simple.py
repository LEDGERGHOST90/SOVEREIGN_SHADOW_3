#!/usr/bin/env python3
"""
🧠 SHADOW SDK - SIMPLE SHADOWSCOPE DEMO

Quick demonstration of ShadowScope market intelligence capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add shadow_sdk to path
sys.path.insert(0, str(Path(__file__).parent))

from shadow_sdk import ShadowScope, EXCHANGES, PAIRS, PHILOSOPHY

async def main():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🧠 SHADOWSCOPE - MARKET INTELLIGENCE ENGINE                      ║
║   Sovereign Shadow Trading Empire                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

Philosophy: "{}"\n""".format(PHILOSOPHY))

    # 1. Initialize ShadowScope
    print("=" * 70)
    print("📡 STEP 1: INITIALIZE SHADOWSCOPE")
    print("=" * 70)

    scope = ShadowScope()
    print(f"✅ ShadowScope initialized")
    print(f"   • Exchanges: {', '.join(scope.exchanges)}")
    print(f"   • Pairs: {', '.join(scope.pairs)}")
    print(f"   • Total streams: {len(scope.exchanges) * len(scope.pairs)}")
    print()

    # 2. Check initial health
    print("=" * 70)
    print("🏥 STEP 2: CHECK SYSTEM HEALTH")
    print("=" * 70)

    health = await scope.get_health_status()
    print(f"✅ System Health:")
    print(f"   • Exchanges monitored: {health['exchanges_monitored']}")
    print(f"   • Pairs monitored: {health['pairs_monitored']}")
    print(f"   • Data quality: {health['data_quality_percent']:.1f}%")
    print(f"   • Running: {health['is_running']}")
    print(f"   • Ticks processed: {health['tick_count']}")
    print()

    # 3. Start scanner
    print("=" * 70)
    print("🚀 STEP 3: START REAL-TIME SCANNER (10 seconds)")
    print("=" * 70)

    # Start scanner task
    scanner_task = asyncio.create_task(scope.start_scanner(interval=0.5))

    # Monitor for 10 seconds
    for i in range(10):
        await asyncio.sleep(1)
        health = await scope.get_health_status()

        print(f"   [{i+1:2d}/10] Ticks: {health['tick_count']:4d} | "
              f"Rate: {health['ticks_per_second']:3.0f}/s | "
              f"Quality: {health['data_quality_percent']:.1f}%")

    print()

    # 4. Get market intelligence
    print("=" * 70)
    print("📊 STEP 4: GET MARKET INTELLIGENCE")
    print("=" * 70)

    intelligence = await scope.get_market_intelligence()

    print(f"✅ Intelligence Report:")
    print(f"   • Timestamp: {intelligence['timestamp']}")
    print()

    # Show prices per exchange
    print("   💰 Current Prices:")
    for exchange, pairs_data in intelligence['current_prices'].items():
        print(f"\n      {exchange.upper()}:")
        for pair, price in sorted(pairs_data.items()):
            print(f"         {pair:12s}: ${price:>10,.2f}")

    print()

    # Show VWAP (Volume-Weighted Average Price)
    print("   📊 Volume-Weighted Average Prices (VWAP):")
    for pair, vwap in sorted(intelligence['vwap'].items()):
        print(f"      {pair:12s}: ${vwap:>10,.2f}")

    print()

    # Show volatility
    print("   📈 Volatility (by exchange):")
    for exchange, pairs_data in intelligence['volatility'].items():
        print(f"\n      {exchange.upper()}:")
        for pair, vol in sorted(pairs_data.items()):
            vol_indicator = "🔴 HIGH" if vol > 0.01 else "🟡 MED" if vol > 0.005 else "🟢 LOW"
            print(f"         {pair:12s}: {vol:6.4f} {vol_indicator}")

    print()

    # 5. Stop scanner
    print("=" * 70)
    print("🛑 STEP 5: STOP SCANNER")
    print("=" * 70)

    scope.stop_scanner()
    await asyncio.sleep(0.5)

    final_health = await scope.get_health_status()
    print(f"✅ Scanner stopped")
    print(f"   • Total ticks: {final_health['tick_count']}")
    print(f"   • Uptime: {final_health['uptime_seconds']:.1f}s")
    print(f"   • Average rate: {final_health['ticks_per_second']:.0f} ticks/sec")
    print()

    # Summary
    print("=" * 70)
    print("🎯 SUMMARY")
    print("=" * 70)
    print("""
ShadowScope provides real-time market intelligence by:

✅ Monitoring multiple exchanges simultaneously
✅ Processing hundreds of ticks per second
✅ Calculating volatility metrics
✅ Computing volume-weighted prices (VWAP)
✅ Tracking correlations between pairs
✅ Maintaining high data quality (>95%)

This is the foundation of your trading empire's intelligence layer.

Next steps:
1. Configure API keys for live exchange data
2. Connect ShadowScope to your Master Trading Loop
3. Use intelligence data for trading decisions

Your Master Trading Loop already uses ShadowScope internally! 🚀
""")

    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")

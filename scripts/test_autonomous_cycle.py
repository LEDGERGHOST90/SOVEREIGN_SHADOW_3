#!/usr/bin/env python3
"""Quick test of a single autonomous trading cycle"""

import asyncio
from autonomous_trading_loop import AutonomousTradingLoop

async def test_single_cycle():
    """Run a single cycle and exit"""
    loop = AutonomousTradingLoop(
        mode='paper',
        ray_score_threshold=60,
        max_concurrent_ladders=3,
        cycle_interval_seconds=600
    )

    await loop.run_trading_cycle()
    print("\n✅ Single cycle test complete")

if __name__ == "__main__":
    asyncio.run(test_single_cycle())

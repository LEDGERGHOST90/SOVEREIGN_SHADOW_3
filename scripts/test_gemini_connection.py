#!/usr/bin/env python3
"""
Test script for ShadowMind (Gemini AI integration)
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from shadow_sdk.gemini import ShadowMind


def main():
    """Test ShadowMind functionality."""

    print("="*60)
    print("🧠 SHADOWMIND - GEMINI AI INTEGRATION TEST")
    print("="*60)

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return

    print(f"✅ API Key loaded: {api_key[:10]}...")

    # Initialize ShadowMind with Gemini 2.5 Pro (powerful, free tier compatible)
    print("\n🧠 Initializing ShadowMind with Gemini 2.5 Pro...")
    try:
        mind = ShadowMind(model="gemini-2.5-pro")
        print("✅ ShadowMind initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # Test 1: Simple query
    print("\n" + "="*60)
    print("TEST 1: Simple Trading Query")
    print("="*60)

    try:
        response = mind.ask(
            "What are the top 3 factors to consider when trading Bitcoin?"
        )
        print(f"\n{response}")
        print("\n✅ Test 1 passed")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Market analysis
    print("\n" + "="*60)
    print("TEST 2: Market Analysis")
    print("="*60)

    try:
        price_data = {
            "price": 101746.31,
            "change_24h": -1.2,
            "volume": "28.5B",
            "indicators": {
                "RSI": 52,
                "MACD": "bullish_crossover",
                "200MA": 95000,
                "Support": 99000,
                "Resistance": 103000
            }
        }

        news = [
            "Bitcoin ETF sees $100M inflow",
            "Fed signals no rate hike in December",
            "Major institution adds BTC to balance sheet"
        ]

        analysis = mind.analyze_market("BTC", price_data, news, "4H")
        print(f"\n{analysis['analysis']}")
        print("\n✅ Test 2 passed")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Trade recommendation
    print("\n" + "="*60)
    print("TEST 3: Trade Recommendation")
    print("="*60)

    try:
        market_data = {
            "btc_price": 101746,
            "trend_4h": "bullish",
            "support": 99000,
            "volatility": "moderate"
        }

        recommendation = mind.get_trade_recommendation(
            asset="BTC",
            direction="long",
            position_size=0.02,
            market_data=market_data
        )
        print(f"\n{recommendation['recommendation']}")
        print("\n✅ Test 3 passed")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    # Test 4: Portfolio analysis
    print("\n" + "="*60)
    print("TEST 4: Portfolio Analysis")
    print("="*60)

    try:
        current = {"BTC": 36.2, "ETH": 0, "SOL": 0, "XRP": 0}
        target = {"BTC": 40, "ETH": 30, "SOL": 20, "XRP": 10}

        portfolio_analysis = mind.analyze_portfolio(
            current_allocation=current,
            target_allocation=target
        )
        print(f"\n{portfolio_analysis['analysis']}")
        print("\n✅ Test 4 passed")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")

    # Get stats
    print("\n" + "="*60)
    print("SHADOWMIND STATISTICS")
    print("="*60)

    stats = mind.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()

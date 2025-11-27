#!/usr/bin/env python3
"""
🧠 ShadowMind Demo - Gemini AI Trading Intelligence

Quick demo showing how to use ShadowMind for AI-powered trading insights.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from shadow_sdk import ShadowMind


def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*60)
    print(f"🧠 {title}")
    print("="*60 + "\n")


def main():
    """Run ShadowMind demo."""

    print_section("SHADOWMIND - AI TRADING INTELLIGENCE")

    # Initialize with Gemini 2.5 Pro (powerful, free tier compatible)
    print("Initializing ShadowMind with Gemini 2.5 Pro...")
    mind = ShadowMind()  # Uses default gemini-2.5-pro
    print("✅ Connected\n")

    # Demo 1: Simple Trading Question
    print_section("DEMO 1: Trading Philosophy")
    question = "What's more important for long-term crypto trading success: timing the market or consistent strategy execution?"
    print(f"Question: {question}\n")

    answer = mind.ask(question)
    print(f"ShadowMind: {answer}")

    # Demo 2: Market Analysis
    print_section("DEMO 2: BTC Market Analysis")

    btc_data = {
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
        "Bitcoin ETF sees $100M daily inflow",
        "Fed signals pause on rate hikes",
        "Major bank adds BTC exposure"
    ]

    print("Analyzing BTC market conditions...")
    analysis = mind.analyze_market("BTC", btc_data, news, "4H")
    print(f"\n{analysis['analysis']}")

    # Demo 3: Trade Recommendation
    print_section("DEMO 3: Trade Decision Support")

    print("Evaluating: BTC Long, 2% position size")

    recommendation = mind.get_trade_recommendation(
        asset="BTC",
        direction="long",
        position_size=0.02,
        market_data={"trend_4h": "bullish", "volatility": "moderate"}
    )

    print(f"\n{recommendation['recommendation']}")

    # Demo 4: Portfolio Analysis
    print_section("DEMO 4: Portfolio Rebalancing")

    current = {"BTC": 36.2, "ETH": 0, "SOL": 0, "XRP": 0}
    target = {"BTC": 40, "ETH": 30, "SOL": 20, "XRP": 10}

    print(f"Current: {current}")
    print(f"Target: {target}\n")

    portfolio = mind.analyze_portfolio(current, target)
    print(f"{portfolio['analysis']}")

    # Stats
    print_section("SESSION STATS")
    stats = mind.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)
    print("✅ Demo complete!")
    print("="*60 + "\n")

    print("💡 Usage in your code:")
    print("  from shadow_sdk import ShadowMind")
    print("  mind = ShadowMind()")
    print("  answer = mind.ask('Your question here')")
    print()


if __name__ == "__main__":
    main()

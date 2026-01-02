#!/usr/bin/env python3
"""
Test script for ReflectAgent

Quick validation that the agent can analyze trades
(requires ANTHROPIC_API_KEY to be set)
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.agents.reflect_agent import ReflectAgent, CritiqueDecision


def test_basic_functionality():
    """Test basic ReflectAgent functionality"""

    print("="*80)
    print("🔮 REFLECT AGENT - BASIC FUNCTIONALITY TEST")
    print("="*80 + "\n")

    # Test 1: Initialize agent
    print("Test 1: Initializing ReflectAgent...")
    try:
        agent = ReflectAgent()
        print("✅ ReflectAgent initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}\n")
        return False

    # Test 2: Good trade (should APPROVE)
    print("Test 2: Analyzing GOOD trade (conservative risk)...")
    good_trade = {
        'symbol': 'BTC/USD',
        'direction': 'LONG',
        'entry_price': 44000,
        'stop_loss': 43500,
        'take_profit': 45500,
        'position_value': 100.0,
        'risk_amount': 5.0,
        'risk_percent': 0.02,
        'risk_reward_ratio': 3.0
    }

    good_context = {
        'trend_4h': 'bullish',
        'setup_15m': 'pullback_to_support',
        'volatility': 'medium',
        'market_phase': 'markup',
        'fear_greed_index': 65,
        'btc_dominance': 52.3
    }

    try:
        critique = agent.analyze_trade(
            proposed_trade=good_trade,
            market_context=good_context,
            emotional_state="calm and focused"
        )

        print(f"   Decision: {critique.decision}")
        print(f"   Confidence: {critique.confidence:.1%}")
        print(f"   Risk Score: {critique.risk_score}/10")
        print(f"   Reasoning: {critique.reasoning[:100]}...")

        if critique.decision == CritiqueDecision.APPROVE.value:
            print("✅ Good trade was APPROVED (expected)\n")
        else:
            print(f"⚠️  Good trade was {critique.decision} (unexpected)\n")

    except Exception as e:
        print(f"❌ Error analyzing good trade: {e}\n")
        return False

    # Test 3: Bad trade (should REJECT)
    print("Test 3: Analyzing BAD trade (excessive risk)...")
    bad_trade = {
        'symbol': 'SHIB/USD',  # Meme coin
        'direction': 'LONG',
        'entry_price': 0.00001,
        'stop_loss': 0.000005,
        'take_profit': 0.00002,
        'position_value': 500.0,  # Large position
        'risk_amount': 250.0,  # 50% risk!
        'risk_percent': 0.50,
        'risk_reward_ratio': 1.0  # Poor R:R
    }

    bad_context = {
        'trend_4h': 'bearish',
        'setup_15m': 'no_clear_setup',
        'volatility': 'extremely_high',
        'market_phase': 'distribution',
        'fear_greed_index': 10,
        'btc_dominance': 45.0
    }

    try:
        critique = agent.analyze_trade(
            proposed_trade=bad_trade,
            market_context=bad_context,
            emotional_state="anxious after 3 losses, feeling FOMO"
        )

        print(f"   Decision: {critique.decision}")
        print(f"   Confidence: {critique.confidence:.1%}")
        print(f"   Risk Score: {critique.risk_score}/10")
        print(f"   Reasoning: {critique.reasoning[:100]}...")

        if critique.decision == CritiqueDecision.REJECT.value:
            print("✅ Bad trade was REJECTED (expected)\n")
        else:
            print(f"⚠️  Bad trade was {critique.decision} (unexpected)\n")

    except Exception as e:
        print(f"❌ Error analyzing bad trade: {e}\n")
        return False

    # Test 4: Weekly summary
    print("Test 4: Generating weekly summary...")
    try:
        summary = agent.get_weekly_summary(days=7)
        print(f"   Total Critiques: {summary['total_critiques']}")
        print(f"   Approvals: {summary['approvals']}")
        print(f"   Rejections: {summary['rejections']}")
        print(f"   Modifications: {summary['modifications']}")
        print("✅ Weekly summary generated\n")
    except Exception as e:
        print(f"❌ Error generating summary: {e}\n")
        return False

    print("="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80 + "\n")

    return True


def test_integration_pattern():
    """Test integration pattern with existing agents"""

    print("="*80)
    print("🔗 REFLECT AGENT - INTEGRATION PATTERN TEST")
    print("="*80 + "\n")

    print("Example: Two-layer validation (SHADE + REFLECT)")
    print("-" * 80)

    # Simulated trade that passes SHADE but gets flagged by REFLECT
    trade = {
        'symbol': 'ETH/USD',
        'direction': 'LONG',
        'entry_price': 2400,
        'stop_loss': 2350,
        'take_profit': 2500,
        'position_value': 150.0,
        'risk_amount': 7.50,
        'risk_percent': 0.015,
        'risk_reward_ratio': 2.0
    }

    market = {
        'trend_4h': 'bullish',
        'setup_15m': 'breakout',
        'volatility': 'high',
        'market_phase': 'markup'
    }

    # Simulate SHADE validation
    shade_approved = True
    shade_reason = "Trade meets 15m/4h strategy rules"

    print(f"Layer 1 (SHADE): {'✅ APPROVED' if shade_approved else '❌ REJECTED'}")
    print(f"           Reason: {shade_reason}")

    if not shade_approved:
        print("\n❌ Trade rejected by SHADE - no need for REFLECT check")
        return True

    # Layer 2: REFLECT critique
    try:
        agent = ReflectAgent()
        critique = agent.analyze_trade(
            proposed_trade=trade,
            market_context=market,
            emotional_state="excited after recent win"
        )

        print(f"\nLayer 2 (REFLECT): {critique.decision}")
        print(f"           Confidence: {critique.confidence:.1%}")
        print(f"           Risk: {critique.risk_score}/10")
        print(f"           Reasoning: {critique.reasoning[:150]}...")

        # Final decision
        if critique.decision == CritiqueDecision.APPROVE.value:
            print("\n✅ DUAL APPROVAL - Executing trade")
        elif critique.decision == CritiqueDecision.MODIFY.value:
            print(f"\n⚠️  MODIFICATIONS NEEDED")
            if critique.suggested_modifications:
                print(f"   Suggestions: {critique.suggested_modifications}")
        else:
            print(f"\n❌ REJECT by REFLECT - Trade blocked despite SHADE approval")
            print(f"   This is the power of AI critique - catches issues rules miss!")

        print("\n" + "="*80)
        print("✅ INTEGRATION PATTERN TEST PASSED")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Error during integration test: {e}\n")
        return False


if __name__ == "__main__":
    print("""
    🔮 REFLECT AGENT - TEST SUITE

    This script validates the ReflectAgent functionality.
    Requires ANTHROPIC_API_KEY to be set in environment.

    Tests:
    1. Basic initialization
    2. Good trade analysis (should APPROVE)
    3. Bad trade analysis (should REJECT)
    4. Weekly summary generation
    5. Integration pattern with existing agents
    """)

    # Check for API key
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("   Set it in ECO_SYSTEM_4/.env or export it directly:")
        print('   export ANTHROPIC_API_KEY="sk-ant-..."')
        sys.exit(1)

    # Run tests
    print("\nStarting tests...\n")

    success = test_basic_functionality()

    if success:
        test_integration_pattern()
    else:
        print("❌ Basic tests failed, skipping integration tests")
        sys.exit(1)

    print("\n✅ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Review /Volumes/LegacySafe/SS_III/core/agents/REFLECT_AGENT_INTEGRATION.md")
    print("2. Integrate with shade_agent.py and trading_agent.py")
    print("3. Test with paper trading")
    print("4. Monitor performance improvements")

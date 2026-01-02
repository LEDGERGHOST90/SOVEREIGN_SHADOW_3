#!/usr/bin/env python3
"""
Simple test script for on-chain signals module

Usage:
    python test_onchain.py
    python test_onchain.py --clear-cache
    python test_onchain.py --symbol ETH
"""

import sys
import argparse
from onchain_signals import OnChainSignals


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_exchange_flows(signals, symbol):
    """Test exchange flow analysis"""
    print_section(f"{symbol} Exchange Flow Analysis")

    try:
        data = signals.get_exchange_flows(symbol)

        print(f"Signal:       {data['signal']}")
        print(f"Score:        {data['score']:.2f}/100")
        print(f"Reason:       {data['reason']}")
        print(f"Inflow 24h:   ${data['inflow_24h']:,.2f}")
        print(f"Outflow 24h:  ${data['outflow_24h']:,.2f}")
        print(f"Net Flow:     ${data['net_flow']:,.2f}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_whale_movements(signals, symbol):
    """Test whale movement tracking"""
    print_section(f"{symbol} Whale Movement Analysis")

    try:
        data = signals.get_whale_movements(symbol)

        print(f"Signal:          {data['signal']}")
        print(f"Score:           {data['score']:.2f}/100")
        print(f"Reason:          {data['reason']}")
        print(f"Total Movements: {data['total_movements']}")
        print(f"To Exchanges:    {data['to_exchanges']}")
        print(f"From Exchanges:  {data['from_exchanges']}")
        print(f"Net Flow:        {data['net_exchange_flow']}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_onchain_score(signals, symbol):
    """Test aggregated on-chain score"""
    print_section(f"{symbol} Aggregated On-Chain Score")

    try:
        data = signals.get_onchain_score(symbol)

        print(f"Overall Signal:    {data['overall_signal']}")
        print(f"Overall Score:     {data['overall_score']:.2f}/100")
        print(f"Confidence:        {data['confidence']:.2f}%")
        print(f"Recommendation:    {data['recommendation']}")

        print(f"\nBreakdown:")
        for component, details in data['breakdown'].items():
            component_name = component.replace('_', ' ').title()
            print(f"  {component_name}:")
            print(f"    Score:  {details['score']:.2f} (weight: {details['weight']:.0%})")
            print(f"    Signal: {details['signal']}")
            print(f"    Reason: {details['reason']}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test on-chain signals module')
    parser.add_argument('--symbol', default='BTC', help='Symbol to test (BTC or ETH)')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before testing')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')

    args = parser.parse_args()

    print_section("On-Chain Signals Test Suite")
    print(f"Testing symbol: {args.symbol}")
    print(f"Cache enabled:  {not args.no_cache}")

    # Initialize signals module
    signals = OnChainSignals(cache_enabled=not args.no_cache)

    # Clear cache if requested
    if args.clear_cache:
        print("\nClearing cache...")
        signals.clear_cache()

    # Run tests
    results = {
        'exchange_flows': test_exchange_flows(signals, args.symbol),
        'whale_movements': test_whale_movements(signals, args.symbol),
        'onchain_score': test_onchain_score(signals, args.symbol)
    }

    # Print summary
    print_section("Test Summary")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        symbol = "✓" if passed_test else "✗"
        print(f"{symbol} {test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    # Print integration hints
    if passed == total:
        print_section("Integration Ready!")
        print("""
All tests passed! You can now integrate with whale_agent.py:

1. Add to imports:
   from core.signals.onchain_signals import OnChainSignals

2. Initialize in __init__():
   self.onchain = OnChainSignals(cache_enabled=True)

3. Use in analysis:
   onchain = self.onchain.get_onchain_score('BTC')

See INTEGRATION_EXAMPLE.py for complete code.
""")
    else:
        print_section("Some Tests Failed")
        print("""
This is normal if APIs are not yet configured.
The module will still work, returning neutral signals.

To improve data quality:
1. Add API keys to .env
2. Implement blockchain APIs
3. Configure CoinGlass endpoints

See README.md for details.
""")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

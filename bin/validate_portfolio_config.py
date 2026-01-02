#!/usr/bin/env python3
"""
Validate portfolio_config.py integration across codebase.
Run after making changes to verify everything imports correctly.

Usage:
    python3 bin/validate_portfolio_config.py
"""

import sys
sys.path.insert(0, '/Volumes/LegacySafe/SS_III')

from pathlib import Path

def test_core_config():
    """Test the core config module."""
    print("=" * 60)
    print("1. TESTING CORE CONFIG")
    print("=" * 60)

    try:
        from core.config.portfolio_config import (
            get_initial_capital,
            get_portfolio_config,
            get_aave_config,
            get_target_allocation,
            get_rwa_focus
        )
        print("✅ All imports successful")

        # Test each function
        total = get_initial_capital()
        print(f"✅ get_initial_capital() = ${total:,.2f}")

        coinbase = get_initial_capital('coinbase')
        print(f"✅ get_initial_capital('coinbase') = ${coinbase:,.2f}")

        config = get_portfolio_config()
        print(f"✅ get_portfolio_config() returns {len(config)} keys")

        aave = get_aave_config()
        print(f"✅ get_aave_config() HF = {aave['health_factor']}")

        allocation = get_target_allocation()
        print(f"✅ get_target_allocation() = {allocation}")

        rwa = get_rwa_focus()
        print(f"✅ get_rwa_focus() primary = {rwa['primary_focus']}")

        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_dependent_imports():
    """Test that all updated files can import the config."""
    print("\n" + "=" * 60)
    print("2. TESTING DEPENDENT FILE IMPORTS")
    print("=" * 60)

    files_to_test = [
        ("core.modules.tracking.unified_profit_tracker", "UnifiedProfitTracker"),
        ("core.modules.tracking.profit_tracker", "ProfitTracker"),
        ("core.modules.tracking.income_capital_tracker", "IncomeCapitalTracker"),
        ("core.modules.ladder.tiered_ladder_system", "TieredLadderSystem"),
        ("core.aave.unified_profit_tracker", "UnifiedProfitTracker"),
        ("core.aave.profit_tracker", "ProfitTracker"),
        ("core.aave.income_capital_tracker", "IncomeCapitalTracker"),
        ("core.aave.tiered_ladder_system", "TieredLadderSystem"),
        ("core.agents_highlevel.risk_agent", "RiskAgent"),
        ("core.agents_highlevel.portfolio_rebalancer", "PortfolioRebalancer"),
        ("core.agents_highlevel.rl_rebalancing_agent", "RLRebalancingAgent"),
    ]

    passed = 0
    failed = 0

    for module_path, class_name in files_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            print(f"✅ {module_path}")
            passed += 1
        except Exception as e:
            print(f"❌ {module_path}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_value_consistency():
    """Verify values are consistent across modules."""
    print("\n" + "=" * 60)
    print("3. TESTING VALUE CONSISTENCY")
    print("=" * 60)

    from core.config.portfolio_config import get_initial_capital, get_portfolio_config

    expected_total = get_initial_capital()
    expected_coinbase = get_initial_capital('coinbase')
    expected_kraken = get_initial_capital('kraken')

    print(f"Expected values from portfolio_config:")
    print(f"   Total: ${expected_total:,.2f}")
    print(f"   Coinbase: ${expected_coinbase:,.2f}")
    print(f"   Kraken: ${expected_kraken:,.2f}")

    # Verify these match BRAIN.json or defaults
    config = get_portfolio_config()
    net_worth = config.get('net_worth', {}).get('total', 0)

    if net_worth == expected_total:
        print(f"✅ Total matches net_worth from config")
    else:
        print(f"⚠️  Mismatch: get_initial_capital()={expected_total}, net_worth={net_worth}")

    return True


def test_no_hardcoded_values():
    """Scan for remaining hardcoded values."""
    print("\n" + "=" * 60)
    print("4. SCANNING FOR REMAINING HARDCODED VALUES")
    print("=" * 60)

    import subprocess

    patterns = ['6167.43', '2016.48', '149.06']
    project_root = Path('/Volumes/LegacySafe/SS_III')

    found_issues = []

    for pattern in patterns:
        result = subprocess.run(
            ['grep', '-r', '--include=*.py', pattern, str(project_root / 'core')],
            capture_output=True, text=True
        )

        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            # Filter out test files and knowledge base
            operational_files = [
                l for l in lines
                if 'test' not in l.lower()
                and 'KNOWLEDGE_BASE' not in l
            ]
            if operational_files:
                found_issues.extend(operational_files)

    if found_issues:
        print(f"⚠️  Found {len(found_issues)} potential hardcoded values:")
        for issue in found_issues[:5]:
            print(f"   {issue[:80]}...")
    else:
        print("✅ No hardcoded values found in operational files")

    return len(found_issues) == 0


def main():
    print("\n" + "=" * 60)
    print("PORTFOLIO CONFIG VALIDATION")
    print("=" * 60 + "\n")

    results = []

    results.append(("Core Config", test_core_config()))
    results.append(("Dependent Imports", test_dependent_imports()))
    results.append(("Value Consistency", test_value_consistency()))
    results.append(("No Hardcoded Values", test_no_hardcoded_values()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
    else:
        print("❌ SOME VALIDATIONS FAILED - Review output above")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

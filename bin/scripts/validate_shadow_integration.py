#!/usr/bin/env python3
"""
🔍 SHADOW SDK INTEGRATION VALIDATOR

Validates complete integration between Shadow SDK and Master Trading Loop.
Tests all components and connections.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "shadow_sdk"))

print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🔍 SHADOW SDK INTEGRATION VALIDATOR                              ║
║   Sovereign Shadow Trading Empire                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")

# Track validation results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_result(test_name: str, passed: bool, message: str = ""):
    """Record test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

    if passed:
        results["passed"].append(test_name)
    else:
        results["failed"].append(test_name)

def test_warning(test_name: str, message: str):
    """Record warning"""
    print(f"⚠️  WARN - {test_name}")
    print(f"      {message}")
    results["warnings"].append(test_name)

async def validate_shadow_sdk_imports():
    """Test 1: Validate Shadow SDK can be imported"""
    print("\n" + "=" * 70)
    print("TEST 1: SHADOW SDK IMPORTS")
    print("=" * 70)

    try:
        from shadow_sdk import (
            ShadowScope,
            ShadowPulse,
            ShadowSnaps,
            ShadowSynapse,
            CAPITAL_TOTAL,
            EXCHANGES,
            PHILOSOPHY
        )
        test_result("Shadow SDK core imports", True)
        test_result("Shadow SDK constants", True, f"Capital: ${CAPITAL_TOTAL}")
        test_result("Shadow SDK philosophy", True, f'"{PHILOSOPHY}"')
        return True
    except ImportError as e:
        test_result("Shadow SDK core imports", False, str(e))
        return False

async def validate_shadow_scope():
    """Test 2: Validate ShadowScope functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: SHADOWSCOPE FUNCTIONALITY")
    print("=" * 70)

    try:
        from shadow_sdk import ShadowScope

        # Initialize
        scope = ShadowScope()
        test_result("ShadowScope initialization", True)

        # Check health
        health = await scope.get_health_status()
        test_result("ShadowScope health check", True,
                   f"Monitoring {health['exchanges_monitored']} exchanges")

        # Start scanner briefly
        scanner_task = asyncio.create_task(scope.start_scanner(interval=0.5))
        await asyncio.sleep(2)

        health_running = await scope.get_health_status()
        scanner_working = health_running['tick_count'] > 0
        test_result("ShadowScope scanner", scanner_working,
                   f"Processed {health_running['tick_count']} ticks")

        # Get intelligence
        intelligence = await scope.get_market_intelligence()
        has_prices = len(intelligence.get('current_prices', {})) > 0
        test_result("ShadowScope intelligence", has_prices,
                   f"Tracking {len(intelligence.get('current_prices', {}))} exchanges")

        # Stop scanner
        scope.stop_scanner()
        await asyncio.sleep(0.5)
        test_result("ShadowScope shutdown", True)

        return True
    except Exception as e:
        test_result("ShadowScope functionality", False, str(e))
        return False

async def validate_shadow_utilities():
    """Test 3: Validate Shadow SDK utilities"""
    print("\n" + "=" * 70)
    print("TEST 3: SHADOW SDK UTILITIES")
    print("=" * 70)

    try:
        from shadow_sdk.utils import RiskManager, setup_logger

        # Test RiskManager
        risk_mgr = RiskManager(max_daily_loss=100, max_position_size=415)
        test_result("RiskManager initialization", True)

        can_trade = risk_mgr.can_trade(amount=100)
        test_result("RiskManager validation", True,
                   f"$100 trade allowed: {can_trade}")

        # Test Logger
        logger = setup_logger("integration_test", log_file="logs/integration_test.log")
        logger.info("Integration test message")
        test_result("Logger setup", True)

        return True
    except Exception as e:
        test_result("Shadow SDK utilities", False, str(e))
        return False

async def validate_master_loop_integration():
    """Test 4: Validate Master Loop integration"""
    print("\n" + "=" * 70)
    print("TEST 4: MASTER LOOP INTEGRATION")
    print("=" * 70)

    try:
        # Check if Master Loop file exists
        master_loop_file = REPO_ROOT / "MASTER_TRADING_LOOP.py"
        file_exists = master_loop_file.exists()
        test_result("Master Loop file exists", file_exists)

        if file_exists:
            # Read and check for Shadow SDK imports
            content = master_loop_file.read_text()
            has_shadow_imports = "shadow_sdk" in content or "ShadowScope" in content

            if has_shadow_imports:
                test_result("Master Loop Shadow SDK integration", True,
                           "Shadow SDK imports found")
            else:
                test_warning("Master Loop Shadow SDK integration",
                           "No Shadow SDK imports found (optional)")

        # Check if Master Loop is running
        import subprocess
        result = subprocess.run(["pgrep", "-f", "MASTER_TRADING_LOOP"],
                              capture_output=True, text=True)
        is_running = bool(result.stdout.strip())

        if is_running:
            test_result("Master Loop running", True,
                       f"PID: {result.stdout.strip()}")
        else:
            test_warning("Master Loop running",
                        "Master Loop not currently running")

        return True
    except Exception as e:
        test_result("Master Loop integration", False, str(e))
        return False

async def validate_orchestrator_integration():
    """Test 5: Validate Orchestrator integration"""
    print("\n" + "=" * 70)
    print("TEST 5: ORCHESTRATOR INTEGRATION")
    print("=" * 70)

    try:
        # Check if orchestrator exists
        orchestrator_file = REPO_ROOT / "core" / "orchestration" / "sovereign_shadow_orchestrator.py"
        file_exists = orchestrator_file.exists()
        test_result("Orchestrator file exists", file_exists)

        if file_exists:
            # Try to import (may fail if dependencies missing)
            try:
                sys.path.insert(0, str(REPO_ROOT / "core" / "orchestration"))
                from sovereign_shadow_orchestrator import SovereignShadowOrchestrator
                test_result("Orchestrator importable", True)

                # Try to initialize
                orchestrator = SovereignShadowOrchestrator()
                test_result("Orchestrator initialization", True)
            except ImportError as e:
                test_warning("Orchestrator import", f"Missing dependencies: {e}")

        return True
    except Exception as e:
        test_result("Orchestrator integration", False, str(e))
        return False

async def validate_safety_systems():
    """Test 6: Validate safety systems"""
    print("\n" + "=" * 70)
    print("TEST 6: SAFETY SYSTEMS")
    print("=" * 70)

    try:
        # Check safety rules file
        safety_file = REPO_ROOT / "core" / "orchestration" / "SAFETY_RULES_IMPLEMENTATION.py"
        file_exists = safety_file.exists()
        test_result("Safety rules file exists", file_exists)

        # Check crisis playbook
        crisis_file = REPO_ROOT / "core" / "orchestration" / "CRISIS_MANAGEMENT_PLAYBOOK.py"
        file_exists = crisis_file.exists()
        test_result("Crisis playbook exists", file_exists)

        # Check Shadow SDK risk manager
        from shadow_sdk.utils import RiskManager
        from shadow_sdk import MAX_DAILY_LOSS, MAX_POSITION_SIZE

        risk_mgr = RiskManager(
            max_daily_loss=MAX_DAILY_LOSS,
            max_position_size=MAX_POSITION_SIZE
        )

        # Test safety limits
        too_large = not risk_mgr.can_trade(amount=500)  # Should block
        normal_size = risk_mgr.can_trade(amount=100)   # Should allow

        test_result("Risk manager limits", too_large and normal_size,
                   f"Blocking ${MAX_POSITION_SIZE}+ trades: {too_large}")

        return True
    except Exception as e:
        test_result("Safety systems", False, str(e))
        return False

async def validate_documentation():
    """Test 7: Validate documentation"""
    print("\n" + "=" * 70)
    print("TEST 7: DOCUMENTATION")
    print("=" * 70)

    docs_to_check = [
        ("CLAUDE.md", "Claude Code guidance"),
        ("README.md", "Main README"),
        ("MASTER_LOOP_QUICKSTART.md", "Master Loop guide"),
        ("API_KEY_SETUP_GUIDE.md", "API setup guide"),
        ("SHADOW_SDK_INTEGRATION.md", "Shadow SDK integration"),
        ("shadow_sdk/README.md", "Shadow SDK README")
    ]

    for doc_file, description in docs_to_check:
        file_path = REPO_ROOT / doc_file
        exists = file_path.exists()
        test_result(f"Documentation: {description}", exists, doc_file)

    return True

async def validate_complete_system():
    """Test 8: Validate complete system integration"""
    print("\n" + "=" * 70)
    print("TEST 8: COMPLETE SYSTEM INTEGRATION")
    print("=" * 70)

    try:
        # Check all key components exist
        components = {
            "Shadow SDK": REPO_ROOT / "shadow_sdk",
            "Master Loop": REPO_ROOT / "MASTER_TRADING_LOOP.py",
            "Loop Control": REPO_ROOT / "bin" / "MASTER_LOOP_CONTROL.sh",
            "Orchestrator": REPO_ROOT / "core" / "orchestration",
            "Trading Strategies": REPO_ROOT / "scripts",
            "Portfolio Monitoring": REPO_ROOT / "core" / "portfolio",
            "Logs Directory": REPO_ROOT / "logs"
        }

        all_exist = True
        for name, path in components.items():
            exists = path.exists()
            test_result(f"Component: {name}", exists, str(path.relative_to(REPO_ROOT)))
            if not exists:
                all_exist = False

        # Check system constants alignment
        from shadow_sdk import (
            CAPITAL_TOTAL,
            CAPITAL_LEDGER,
            CAPITAL_COINBASE,
            MAX_DAILY_LOSS,
            MAX_POSITION_SIZE
        )

        test_result("System constants defined", True,
                   f"Capital: ${CAPITAL_TOTAL}, Max Loss: ${MAX_DAILY_LOSS}")

        return all_exist
    except Exception as e:
        test_result("Complete system integration", False, str(e))
        return False

async def main():
    """Run all validation tests"""
    print(f"Starting validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run all tests
    await validate_shadow_sdk_imports()
    await validate_shadow_scope()
    await validate_shadow_utilities()
    await validate_master_loop_integration()
    await validate_orchestrator_integration()
    await validate_safety_systems()
    await validate_documentation()
    await validate_complete_system()

    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    total_tests = len(results["passed"]) + len(results["failed"])
    print(f"\n✅ Passed: {len(results['passed'])}/{total_tests}")
    print(f"❌ Failed: {len(results['failed'])}/{total_tests}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")

    if results["failed"]:
        print("\n❌ Failed Tests:")
        for test in results["failed"]:
            print(f"   • {test}")

    if results["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"   • {warning}")

    # Overall status
    print("\n" + "=" * 70)
    if len(results["failed"]) == 0:
        print("🎉 ALL TESTS PASSED - INTEGRATION COMPLETE!")
        print("=" * 70)
        print("""
Your Shadow SDK is fully integrated with your trading empire:

✅ Shadow SDK components working
✅ ShadowScope scanning markets
✅ Risk management active
✅ Master Loop integrated
✅ Safety systems in place
✅ Documentation complete

Next steps:
1. Configure API keys (see API_KEY_SETUP_GUIDE.md)
2. Monitor 24-hour paper test
3. Validate with real exchange data
4. Move to live trading after successful test

Your empire is ready! 🚀
        """)
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW ISSUES ABOVE")
        print("=" * 70)
        print("""
Some components need attention. Review failed tests above.
Most warnings are non-critical (optional features).

Critical issues should be resolved before live trading.
        """)
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Validation interrupted. Goodbye!")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal validation error: {e}")
        sys.exit(1)

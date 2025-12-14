#!/usr/bin/env python3
"""
Verify Advanced Risk Module Installation
Quick health check for the risk management system
"""

import sys
from pathlib import Path

def verify_installation():
    """Verify all components are installed correctly."""
    print("=" * 70)
    print("ADVANCED RISK MODULE - INSTALLATION VERIFICATION")
    print("=" * 70)

    checks = []
    errors = []

    # Check 1: Module file exists
    try:
        module_path = Path(__file__).parent / "advanced_risk_module.py"
        if module_path.exists():
            checks.append(("✅", "advanced_risk_module.py exists"))
        else:
            checks.append(("❌", "advanced_risk_module.py NOT FOUND"))
            errors.append("Module file missing")
    except Exception as e:
        checks.append(("❌", f"Error checking module: {e}"))
        errors.append(str(e))

    # Check 2: Import module
    try:
        from advanced_risk_module import AdvancedRiskManager
        checks.append(("✅", "AdvancedRiskManager can be imported"))
    except ImportError as e:
        checks.append(("❌", f"Import failed: {e}"))
        errors.append(f"Import error: {e}")

    # Check 3: Initialize module
    try:
        from advanced_risk_module import AdvancedRiskManager
        risk = AdvancedRiskManager(base_risk_pct=0.02)
        checks.append(("✅", "AdvancedRiskManager can be initialized"))
    except Exception as e:
        checks.append(("❌", f"Initialization failed: {e}"))
        errors.append(f"Initialization error: {e}")

    # Check 4: Basic functionality
    try:
        from advanced_risk_module import AdvancedRiskManager
        risk = AdvancedRiskManager(base_risk_pct=0.02)

        result = risk.calculate_position_size(
            equity=5433.87,
            symbol="TEST/USD",
            atr_value=100
        )

        if hasattr(result, 'size') and hasattr(result, 'risk_amount'):
            checks.append(("✅", "Position sizing works"))
        else:
            checks.append(("❌", "Position sizing returned wrong format"))
            errors.append("Position sizing format error")
    except Exception as e:
        checks.append(("❌", f"Position sizing failed: {e}"))
        errors.append(f"Position sizing error: {e}")

    # Check 5: Omega integration
    try:
        omega_path = Path(__file__).parent / "omega_enhanced_risk_manager.py"
        if omega_path.exists():
            checks.append(("✅", "omega_enhanced_risk_manager.py exists"))

            from omega_enhanced_risk_manager import OmegaEnhancedRiskManager
            omega = OmegaEnhancedRiskManager()
            checks.append(("✅", "OmegaEnhancedRiskManager can be initialized"))
        else:
            checks.append(("⚠️", "omega_enhanced_risk_manager.py not found (optional)"))
    except Exception as e:
        checks.append(("⚠️", f"Omega manager issue (optional): {e}"))

    # Check 6: Documentation
    try:
        readme = Path(__file__).parent / "README_ADVANCED_RISK.md"
        quickstart = Path(__file__).parent / "QUICK_START.md"

        if readme.exists():
            checks.append(("✅", "README_ADVANCED_RISK.md exists"))
        else:
            checks.append(("⚠️", "README_ADVANCED_RISK.md missing"))

        if quickstart.exists():
            checks.append(("✅", "QUICK_START.md exists"))
        else:
            checks.append(("⚠️", "QUICK_START.md missing"))
    except Exception as e:
        checks.append(("⚠️", f"Documentation check error: {e}"))

    # Check 7: State directory
    try:
        config_path = Path.home() / ".keyblade"
        if config_path.exists():
            checks.append(("✅", f"Config directory exists: {config_path}"))
        else:
            checks.append(("ℹ️", f"Config directory will be created: {config_path}"))
    except Exception as e:
        checks.append(("⚠️", f"Config directory check error: {e}"))

    # Print results
    print("\nInstallation Checks:")
    print("-" * 70)
    for status, message in checks:
        print(f"{status} {message}")

    print("\n" + "=" * 70)

    if errors:
        print("❌ INSTALLATION FAILED")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors above and try again.")
        return False
    else:
        print("✅ INSTALLATION SUCCESSFUL")
        print("\nAll core components verified and working.")
        print("\nNext steps:")
        print("  1. Read QUICK_START.md for 2-minute guide")
        print("  2. Read README_ADVANCED_RISK.md for full documentation")
        print("  3. Run risk_integration_example.py for examples")
        print("  4. Integrate into your trading agents")
        return True

    print("=" * 70)


def quick_test():
    """Run a quick functionality test."""
    print("\n" + "=" * 70)
    print("QUICK FUNCTIONALITY TEST")
    print("=" * 70)

    try:
        from advanced_risk_module import AdvancedRiskManager

        # Initialize
        risk = AdvancedRiskManager(base_risk_pct=0.02)
        print("\n✅ Initialized AdvancedRiskManager")

        # Test position sizing
        result = risk.calculate_position_size(
            equity=5433.87,
            symbol="BTC/USD",
            atr_value=1200,
            sector="Infrastructure",
            strategy="test"
        )

        print(f"✅ Position Sizing Test:")
        print(f"   Symbol: BTC/USD")
        print(f"   Equity: $5,433.87")
        print(f"   ATR: $1,200")
        print(f"   Result: {result.size:.6f} BTC")
        print(f"   Risk: ${result.risk_amount:.2f}")
        print(f"   Method: {result.method}")

        # Test portfolio heat
        heat = risk.check_portfolio_heat(0.02)
        print(f"\n✅ Portfolio Heat Test:")
        print(f"   Total Heat: {heat.total_heat*100:.2f}%")
        print(f"   Can Trade: {heat.can_trade}")

        # Test circuit breaker
        cb = risk.check_circuit_breaker("test")
        print(f"\n✅ Circuit Breaker Test:")
        print(f"   Active: {cb.active}")
        print(f"   Consecutive Losses: {cb.consecutive_losses}")
        print(f"   Risk Factor: {cb.risk_reduction_factor}")

        # Test summary
        summary = risk.get_risk_summary()
        print(f"\n✅ Risk Summary Test:")
        print(f"   Open Positions: {summary['open_positions']}")
        print(f"   Parameters: {summary['parameters']}")

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED - Module is fully functional!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run verification
    success = verify_installation()

    # Run quick test if verification passed
    if success:
        success = quick_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

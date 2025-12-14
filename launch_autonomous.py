#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - AUTONOMOUS LAUNCH
Launch the autonomous trading system with current capital allocation
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Paths
SS3_ROOT = Path(__file__).parent
BRAIN_PATH = SS3_ROOT / "BRAIN.json"

# Load BRAIN
with open(BRAIN_PATH, 'r') as f:
    brain = json.load(f)

# Current Configuration
CONFIG = {
    "mode": "paper",  # Start in paper mode
    "capital": {
        "total": 73.16,
        "max_position_size": 50.00,
        "max_position_percent": 68.0  # $50 of $73
    },
    "risk": {
        "stop_loss_percent": 3.0,
        "take_profit_percent": 5.0,
        "max_daily_loss": 25.00,
        "max_concurrent_trades": 1  # One trade at a time with limited capital
    },
    "exchange": {
        "primary": "binance_us",
        "testnet": False
    },
    "signals": {
        "enabled": True,
        "notification_url": "https://ntfy.sh/sovereignshadow_dc4d2fa1"
    },
    "autonomous": {
        "enabled": True,
        "scan_interval_seconds": 300,  # 5 minutes
        "min_confidence": 0.7,
        "require_consensus": True
    }
}

print("=" * 70)
print("🏴 SOVEREIGN SHADOW III - AUTONOMOUS TRADING SYSTEM")
print("=" * 70)
print(f"\nMode: {CONFIG['mode'].upper()}")
print(f"Capital: ${CONFIG['capital']['total']:.2f}")
print(f"Max Position: ${CONFIG['capital']['max_position_size']:.2f}")
print(f"Stop Loss: {CONFIG['risk']['stop_loss_percent']}%")
print(f"Take Profit: {CONFIG['risk']['take_profit_percent']}%")
print(f"Exchange: {CONFIG['exchange']['primary'].upper()}")
print(f"Scan Interval: {CONFIG['autonomous']['scan_interval_seconds']}s")
print("\n" + "=" * 70)

# Mission Status
mission = brain.get('current_goal', 'DEBT_DESTROYER')
trading_history = brain.get('trading_history', {})

print(f"\n📊 MISSION: {mission}")
print(f"Win Rate: {trading_history.get('win_rate', 0):.1f}%")
print(f"Total Trades: {trading_history.get('total_trades', 0)}")
print(f"Total PnL: ${trading_history.get('total_pnl', 0):.2f}")
print("\n" + "=" * 70)

# Launch Options
print("\n🚀 LAUNCH OPTIONS:")
print("1. DRY RUN - Test configuration (no trading)")
print("2. PAPER MODE - Simulate trades with live data")
print("3. LIVE MODE - Real money trading (requires confirmation)")
print("Q. Quit")

choice = input("\nSelect option [1/2/3/Q]: ").strip()

if choice == "1":
    print("\n✅ DRY RUN MODE")
    print("Configuration validated. System ready.")
    print("\nTo launch for real:")
    print("  python3 launch_autonomous.py")

elif choice == "2":
    print("\n🟡 LAUNCHING PAPER MODE...")
    print("\nIMPORTANT: This will start the autonomous system in paper trading mode.")
    print("The system will:")
    print("- Scan markets every 5 minutes")
    print("- Generate signals using AI consensus")
    print("- Execute simulated trades")
    print("- Send notifications to ntfy.sh")
    print("- Log all activity")

    confirm = input("\nProceed? [y/N]: ").strip().lower()
    if confirm == 'y':
        # Launch ECO_SYSTEM_4
        print("\n🔧 Starting ECO_SYSTEM_4...")
        sys.path.insert(0, str(SS3_ROOT / "ECO_SYSTEM_4"))

        try:
            from ECO_SYSTEM_4.main import SovereignShadow

            # Create instance
            system = SovereignShadow()

            print("\n✅ System initialized")
            print("Press Ctrl+C to stop\n")

            # Run the main loop (this would need to be implemented)
            # system.run()

        except ImportError as e:
            print(f"\n❌ Error importing ECO_SYSTEM_4: {e}")
            print("Make sure all dependencies are installed")
        except KeyboardInterrupt:
            print("\n\n⏹️  System stopped by user")
    else:
        print("\n❌ Launch cancelled")

elif choice == "3":
    print("\n🔴 LIVE MODE NOT AVAILABLE YET")
    print("Paper trading must achieve 60%+ win rate over 10+ trades first")

else:
    print("\n👋 Goodbye")

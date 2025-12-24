#!/usr/bin/env python3
"""
LIVE SYSTEM CHECK - Always Current Data
Runs before every Claude session to ensure 100% live context

Usage: python3 scripts/live_system_check.py
Output: memory/LIVE_STATUS.json (read by Claude first)
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Set base path
BASE_PATH = Path("/Volumes/LegacySafe/SOVEREIGN_SHADOW_3")
os.chdir(BASE_PATH)

def get_live_status():
    """Gather 100% current system state"""

    status = {
        "check_timestamp": datetime.now().isoformat(),
        "system": "SOVEREIGN_SHADOW_3",
        "status": "LIVE_CHECK_COMPLETE"
    }

    # 1. Load persistent state
    try:
        with open(BASE_PATH / "PERSISTENT_STATE.json", "r") as f:
            persistent = json.load(f)
            status["persistent_state"] = {
                "last_updated": persistent.get("last_updated"),
                "portfolio_value": persistent.get("portfolio", {}).get("total_value_usd"),
                "aave_health_factor": persistent.get("defi_positions", {}).get("aave", {}).get("health_factor"),
                "exchanges_connected": len([
                    ex for ex, data in persistent.get("exchange_accounts", {}).items()
                    if data.get("status") == "connected"
                ])
            }
    except Exception as e:
        status["persistent_state"] = {"error": str(e)}

    # 2. Check trade journal
    try:
        with open(BASE_PATH / "logs/trading/trade_journal.json", "r") as f:
            trades = json.load(f)
            status["trade_journal"] = {
                "total_trades": len(trades),
                "last_trade": trades[-1] if trades else None,
                "win_rate": sum(1 for t in trades if t.get("profitable")) / len(trades) * 100 if trades else 0
            }
    except Exception as e:
        status["trade_journal"] = {"error": str(e)}

    # 3. Check market scanner
    try:
        scanner_logs = sorted((BASE_PATH / "logs/market_scanner").glob("*.jsonl"))
        if scanner_logs:
            with open(scanner_logs[-1], "r") as f:
                last_scan = f.readlines()[-1] if f.readlines() else None
                if last_scan:
                    status["market_scanner"] = {
                        "last_scan": json.loads(last_scan),
                        "scanner_active": True
                    }
    except Exception as e:
        status["market_scanner"] = {"error": str(e), "scanner_active": False}

    # 4. Check latest session
    try:
        sessions = sorted((BASE_PATH / "memory/SESSIONS").rglob("*.md"))
        if sessions:
            latest_session = sessions[-1]
            status["latest_session"] = {
                "file": str(latest_session.relative_to(BASE_PATH)),
                "modified": datetime.fromtimestamp(latest_session.stat().st_mtime).isoformat()
            }
    except Exception as e:
        status["latest_session"] = {"error": str(e)}

    # 5. Git status
    try:
        import subprocess
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=BASE_PATH
        )
        status["git"] = {
            "uncommitted_files": len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0,
            "has_changes": bool(result.stdout.strip())
        }
    except Exception as e:
        status["git"] = {"error": str(e)}

    # 6. System health
    status["health_checks"] = {
        "persistent_state_exists": (BASE_PATH / "PERSISTENT_STATE.json").exists(),
        "trade_journal_exists": (BASE_PATH / "logs/trading/trade_journal.json").exists(),
        "env_file_exists": (BASE_PATH / ".env").exists(),
        "agents_folder_exists": (BASE_PATH / "agents").exists(),
        "memory_folder_exists": (BASE_PATH / "memory").exists()
    }

    status["all_systems_go"] = all(status["health_checks"].values())

    return status


def main():
    """Run live system check and save to JSON"""

    print("🔍 Running LIVE System Check...")
    print(f"📍 Working Directory: {BASE_PATH}")

    status = get_live_status()

    # Save to memory folder
    output_path = BASE_PATH / "memory/LIVE_STATUS.json"
    with open(output_path, "w") as f:
        json.dump(status, f, indent=2)

    print(f"\n✅ Live status saved to: {output_path}")
    print(f"⏰ Check timestamp: {status['check_timestamp']}")

    # Print summary
    print("\n📊 QUICK SUMMARY:")
    if "persistent_state" in status and "error" not in status["persistent_state"]:
        ps = status["persistent_state"]
        print(f"   Portfolio: ${ps.get('portfolio_value', 'N/A')}")
        print(f"   AAVE HF: {ps.get('aave_health_factor', 'N/A')}")
        print(f"   Exchanges: {ps.get('exchanges_connected', 0)} connected")

    if "trade_journal" in status and "error" not in status["trade_journal"]:
        tj = status["trade_journal"]
        print(f"   Trades: {tj.get('total_trades', 0)} | Win Rate: {tj.get('win_rate', 0):.1f}%")

    print(f"\n🟢 All Systems Go: {status['all_systems_go']}")

    return status


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DAILY PORTFOLIO SNAPSHOT
Takes a daily snapshot of all balances and appends to history

Run manually or via cron:
    0 0 * * * cd /Volumes/LegacySafe/SOVEREIGN_SHADOW_3 && venv/bin/python bin/daily_snapshot.py
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BRAIN_FILE = BASE_DIR / "BRAIN.json"
HISTORY_FILE = BASE_DIR / "data/history/portfolio_snapshots.json"

def get_fear_greed():
    """Get current Fear & Greed Index"""
    try:
        import requests
        resp = requests.get("https://api.alternative.me/fng/", timeout=10)
        data = resp.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"]
        }
    except:
        return {"value": 0, "classification": "Unknown"}

def take_snapshot():
    """Take a portfolio snapshot and append to history"""

    # First refresh cold storage balances
    print("Refreshing blockchain balances...")
    try:
        subprocess.run(
            ["python", str(BASE_DIR / "bin/refresh_cold_storage.py")],
            cwd=str(BASE_DIR),
            capture_output=True,
            timeout=60
        )
    except:
        print("Warning: Could not refresh cold storage")

    # Load current brain state
    brain = json.loads(BRAIN_FILE.read_text())
    portfolio = brain.get("portfolio", {})
    prices = brain.get("prices", {})

    # Get market conditions
    fg = get_fear_greed()

    # Create snapshot
    snapshot = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "daily_auto",
        "portfolio": {
            "total_assets": portfolio.get("ledger_total", 0) + portfolio.get("exchange_total", 0),
            "total_debt": portfolio.get("aave_debt", 0),
            "net_worth": portfolio.get("net_worth", 0),
            "breakdown": {
                "ledger": portfolio.get("ledger", {}),
                "exchanges": portfolio.get("exchanges", {}),
                "defi": {
                    "aave": portfolio.get("aave", {})
                }
            }
        },
        "prices": prices,
        "market_conditions": {
            "fear_greed": fg["value"],
            "classification": fg["classification"]
        }
    }

    # Load existing history
    if HISTORY_FILE.exists():
        history = json.loads(HISTORY_FILE.read_text())
    else:
        history = {
            "metadata": {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "description": "Daily portfolio snapshots for growth tracking",
                "frequency": "daily"
            },
            "snapshots": []
        }

    # Append snapshot
    history["snapshots"].append(snapshot)

    # Keep last 365 days
    if len(history["snapshots"]) > 365:
        history["snapshots"] = history["snapshots"][-365:]

    # Save
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

    print(f"{'=' * 60}")
    print(f"DAILY SNAPSHOT SAVED")
    print(f"{'=' * 60}")
    print(f"Time:      {snapshot['timestamp']}")
    print(f"Net Worth: ${snapshot['portfolio']['net_worth']:,.2f}")
    print(f"Assets:    ${snapshot['portfolio']['total_assets']:,.2f}")
    print(f"Debt:      ${snapshot['portfolio']['total_debt']:,.2f}")
    print(f"Fear/Greed: {fg['value']} ({fg['classification']})")
    print(f"{'=' * 60}")
    print(f"History: {len(history['snapshots'])} snapshots saved")

    # Calculate growth if we have history
    if len(history["snapshots"]) >= 2:
        first = history["snapshots"][0]
        latest = history["snapshots"][-1]

        first_nw = first["portfolio"]["net_worth"]
        latest_nw = latest["portfolio"]["net_worth"]

        if first_nw > 0:
            growth = (latest_nw - first_nw) / first_nw * 100
            print(f"Growth since {first['timestamp'][:10]}: {growth:+.1f}%")

    print(f"{'=' * 60}")

if __name__ == "__main__":
    take_snapshot()

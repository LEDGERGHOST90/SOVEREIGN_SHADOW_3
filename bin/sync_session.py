#!/usr/bin/env python3
"""
SS3-SYNC: Sync session state from Replit to local BRAIN.json
Part of Three-System Architecture: Local ↔ Replit ↔ Voice App
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import requests

# Paths
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
BRAIN_PATH = SS3_ROOT / "BRAIN.json"
REPLIT_URL = os.getenv(
    "REPLIT_API_URL",
    "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
)


def fetch_replit_sync():
    """Fetch live data from Shadow.AI Replit"""
    try:
        response = requests.get(f"{REPLIT_URL}/api/brain/sync", timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to fetch from Replit: {e}")
        return None


def get_git_status():
    """Get current git status"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SS3_ROOT,
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return {
            "modified_files": len([l for l in lines if l.startswith(" M") or l.startswith("M ")]),
            "untracked_files": len([l for l in lines if l.startswith("??")]),
            "branch": get_git_branch()
        }
    except:
        return {"error": "git not available"}


def get_git_branch():
    """Get current git branch"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=SS3_ROOT,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def get_recent_files(n=10):
    """Get most recently modified files"""
    try:
        result = subprocess.run(
            ["find", str(SS3_ROOT), "-type", "f", "-mmin", "-60",
             "-not", "-path", "*/.git/*", "-not", "-name", "*.pyc"],
            capture_output=True,
            text=True
        )
        files = result.stdout.strip().split("\n")[:n]
        return [f.replace(str(SS3_ROOT) + "/", "") for f in files if f]
    except:
        return []


def update_brain(replit_data):
    """Update BRAIN.json with Replit data and local state"""
    try:
        # Load existing BRAIN.json
        with open(BRAIN_PATH) as f:
            brain = json.load(f)
    except:
        brain = {}

    # Update from Replit
    if replit_data and replit_data.get("success"):
        data = replit_data.get("data", {})

        # Update AAVE position
        if "aave" in data:
            brain["aave"] = {
                "collateral": data["aave"].get("collateral_usd", 0),
                "debt": data["aave"].get("debt_usd", 0),
                "health_factor": data["aave"].get("health_factor", 0),
                "net_worth": data["aave"].get("net_worth_usd", 0),
                "last_sync": data["aave"].get("last_updated")
            }

        # Update exchange status
        if "exchanges" in data:
            brain["exchange_status"] = data["exchanges"]

    # Add local session info
    brain["last_session"] = {
        "sync_time": datetime.now().isoformat(),
        "git": get_git_status(),
        "recent_files": get_recent_files(),
        "replit_connected": replit_data is not None and replit_data.get("success", False)
    }

    # Update timestamp
    brain["last_updated"] = datetime.now().isoformat()

    # Save
    with open(BRAIN_PATH, "w") as f:
        json.dump(brain, f, indent=2)

    return brain


def main():
    print("🔄 SS3-SYNC: Syncing session state...")
    print(f"   Replit: {REPLIT_URL}")
    print(f"   Local:  {BRAIN_PATH}")
    print()

    # Fetch from Replit
    print("📡 Fetching from Shadow.AI Replit...")
    replit_data = fetch_replit_sync()

    if replit_data and replit_data.get("success"):
        data = replit_data.get("data", {})
        aave = data.get("aave", {})
        print(f"   ✅ AAVE: ${aave.get('collateral_usd', 0):,.2f} collateral, HF {aave.get('health_factor', 0)}")
        print(f"   ✅ Exchanges: {sum(data.get('exchanges', {}).values())}/5 connected")
    else:
        print("   ⚠️  Replit fetch failed, using local state only")

    # Update BRAIN.json
    print("\n📝 Updating BRAIN.json...")
    brain = update_brain(replit_data)

    session = brain.get("last_session", {})
    git = session.get("git", {})
    print(f"   Git: {git.get('branch', 'unknown')} ({git.get('modified_files', 0)} modified)")
    print(f"   Recent files: {len(session.get('recent_files', []))}")

    print("\n✅ Sync complete!")
    print(f"   BRAIN.json updated: {brain.get('last_updated')}")


if __name__ == "__main__":
    main()

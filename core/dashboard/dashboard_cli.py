#!/usr/bin/env python3
"""
🔱 SOVEREIGN COUNCIL - CLI Dashboard
Designed by: ARCHITECT PRIME (GPT)
Implemented by: AURORA (Claude)

Reads Council_Log.md and shows a concise mission/agent view.

Usage:
    python3 council/dashboard_cli.py           # show latest entries
    python3 council/dashboard_cli.py --agent GIO
    python3 council/dashboard_cli.py --mission sniper_intel
"""

from pathlib import Path
import argparse
import re

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "council" / "logs" / "Council_Log.md"

MISSION_ENTRY_RE = re.compile(
    r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) \| (\w+) \| (\w+)"
)


def parse_log():
    if not LOG_PATH.exists():
        print(f"[!] No log file at {LOG_PATH}")
        return []

    text = LOG_PATH.read_text(encoding="utf-8")
    missions = []

    for match in MISSION_ENTRY_RE.finditer(text):
        timestamp, agent, mission, status = match.groups()
        missions.append({
            "timestamp": timestamp,
            "agent": agent,
            "mission": mission,
            "status": status
        })

    return missions


def print_table(missions, agent_filter=None, mission_filter=None):
    print("🔱 SOVEREIGN COUNCIL - DASHBOARD (CLI)")
    print("────────────────────────────────────────")

    if not missions:
        print("No missions logged yet.")
        return

    for m in missions[::-1]:  # newest first
        if agent_filter and agent_filter.upper() != m["agent"].upper():
            continue
        if mission_filter and mission_filter.lower() not in m["mission"].lower():
            continue

        icon = "✅" if m["status"] == "COMPLETED" else "⏳"
        print(f"{icon} {m['mission']:<20} [{m['timestamp']}]")
        print(f"   Agent: {m['agent']}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", help="Filter by agent (GIO, AURORA, ARCHITECT)")
    parser.add_argument("--mission", help="Filter by mission name substring")
    args = parser.parse_args()

    missions = parse_log()
    print_table(missions, agent_filter=args.agent, mission_filter=args.mission)


if __name__ == "__main__":
    main()

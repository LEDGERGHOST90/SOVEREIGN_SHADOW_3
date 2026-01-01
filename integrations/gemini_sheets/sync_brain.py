#!/usr/bin/env python3
"""
sync_brain.py – Pull data from Google Sheets and merge into BRAIN.json

Usage:
  python sync_brain.py --once            # Run a single sync
  python sync_brain.py --daemon [--interval N]  # Run continuously, default every 300 seconds
"""
import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Ensure the project root is in PYTHONPATH for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from integrations.gemini_sheets.sheets_client import SheetsClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BRAIN_JSON_PATH = os.getenv("BRAIN_JSON_PATH", str(PROJECT_ROOT / "BRAIN.json"))

def load_brain() -> Dict[str, Any]:
    """Load existing BRAIN.json or return an empty dict if missing."""
    path = Path(BRAIN_JSON_PATH)
    if path.is_file():
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded existing BRAIN.json ({path})")
            return data
        except Exception as e:
            logger.error(f"Failed to parse BRAIN.json: {e}")
            return {}
    else:
        logger.info("BRAIN.json not found – will create a new one")
        return {}

def write_brain(data: Dict[str, Any]):
    """Write data atomically to BRAIN.json."""
    path = Path(BRAIN_JSON_PATH)
    tmp_path = path.with_suffix(".tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        tmp_path.replace(path)
        logger.info(f"BRAIN.json updated ({path})")
    except Exception as e:
        logger.error(f"Failed to write BRAIN.json: {e}")

def sync_once(client: SheetsClient):
    """Perform a single synchronization cycle."""
    if not client.connect():
        logger.error("Unable to connect to Google Sheets – aborting sync")
        return
    sheet_data = client.get_all_data()
    brain = load_brain()
    # Merge – replace the top‑level keys with fresh data
    brain["portfolio"] = sheet_data.get("portfolio", {})
    brain["signals"] = sheet_data.get("signals", [])
    brain["research"] = sheet_data.get("research", [])
    brain["last_sync"] = sheet_data.get("fetched_at")
    brain["sheet_id"] = sheet_data.get("sheet_id")
    brain["sheet_url"] = sheet_data.get("sheet_url")
    write_brain(brain)

def daemon_loop(client: SheetsClient, interval: int):
    """Run sync repeatedly every *interval* seconds."""
    logger.info(f"Starting daemon sync every {interval} seconds")
    while True:
        sync_once(client)
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Sync Google Sheets data to BRAIN.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--once", action="store_true", help="Run a single sync and exit")
    group.add_argument("--daemon", action="store_true", help="Run continuously as a daemon")
    parser.add_argument("--interval", type=int, default=300, help="Interval in seconds for daemon mode (default 300)")
    args = parser.parse_args()

    client = SheetsClient()
    if args.once:
        sync_once(client)
    else:
        daemon_loop(client, args.interval)

if __name__ == "__main__":
    main()

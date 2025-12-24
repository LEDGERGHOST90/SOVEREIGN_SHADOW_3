#!/usr/bin/env python3
"""
Voice Research Ingester for SS_III
Polls WealthWhisperer API and processes local JSON exports

Sources:
1. API: WealthWhisperer Replit /api/research-feed
2. Local: voice_research/ folder (manual drops)
3. GDrive: Synced via symlink to voice_research_gdrive/
"""

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# Configuration
INGEST_DIR = Path(__file__).parent / "voice_research"
GDRIVE_DIR = Path(__file__).parent / "voice_research_gdrive"
BRAIN_PATH = Path(__file__).parent.parent / "BRAIN.json"
PROCESSED_DIR = INGEST_DIR / "processed"

# WealthWhisperer API (update when deployed)
WEALTHWHISPERER_URL = os.getenv("WEALTHWHISPERER_URL", "")
WEALTHWHISPERER_KEY = os.getenv("WEALTHWHISPERER_KEY", "")

# State tracking
LAST_FETCH_FILE = INGEST_DIR / ".last_fetch"


def load_brain() -> dict:
    """Load current BRAIN.json"""
    with open(BRAIN_PATH) as f:
        return json.load(f)


def save_brain(brain: dict):
    """Save updated BRAIN.json"""
    brain["last_updated"] = datetime.now().isoformat()
    with open(BRAIN_PATH, 'w') as f:
        json.dump(brain, f, indent=2)


def get_last_fetch_time() -> Optional[str]:
    """Get timestamp of last successful API fetch"""
    if LAST_FETCH_FILE.exists():
        return LAST_FETCH_FILE.read_text().strip()
    return None


def set_last_fetch_time():
    """Update last fetch timestamp"""
    LAST_FETCH_FILE.write_text(datetime.now().isoformat())


def fetch_from_api() -> List[Dict]:
    """Poll WealthWhisperer API for new research items"""
    if not WEALTHWHISPERER_URL:
        print("API URL not configured - skipping API fetch")
        return []

    try:
        headers = {}
        if WEALTHWHISPERER_KEY:
            headers["Authorization"] = f"Bearer {WEALTHWHISPERER_KEY}"

        params = {}
        last_fetch = get_last_fetch_time()
        if last_fetch:
            params["since"] = last_fetch

        response = requests.get(
            f"{WEALTHWHISPERER_URL}/api/research-feed",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"API: Fetched {len(items)} research items")
            set_last_fetch_time()
            return items
        else:
            print(f"API Error: {response.status_code} - {response.text[:100]}")
            return []

    except requests.RequestException as e:
        print(f"API Connection Error: {e}")
        return []


def process_research_item(item: dict) -> dict:
    """Normalize a research item for BRAIN.json"""
    # Handle both API format and local file format
    if "recording" in item:
        # Local export format
        return {
            "id": item.get("recording", {}).get("id", str(datetime.now().timestamp())),
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "title": item.get("recording", {}).get("title", "Untitled"),
            "ticker": item.get("analysis", {}).get("ticker"),
            "sentiment": item.get("analysis", {}).get("sentiment", {}),
            "signals": item.get("analysis", {}).get("signals", []),
            "insights": item.get("analysis", {}).get("key_insights", []),
            "transcript_summary": item.get("analysis", {}).get("summary", ""),
            "source": "voice_app_local"
        }
    else:
        # API format (adjust based on actual WealthWhisperer response)
        return {
            "id": item.get("id", str(datetime.now().timestamp())),
            "timestamp": item.get("created_at", datetime.now().isoformat()),
            "title": item.get("title", "Untitled"),
            "ticker": item.get("ticker"),
            "sentiment": item.get("sentiment", {}),
            "signals": item.get("signals", []),
            "insights": item.get("insights", []),
            "transcript_summary": item.get("summary", ""),
            "source": "wealthwhisperer_api"
        }


def process_local_files(directory: Path) -> List[Dict]:
    """Process JSON files from a local directory"""
    if not directory.exists():
        return []

    PROCESSED_DIR.mkdir(exist_ok=True)
    items = []

    # Find all JSON files (research_*.json pattern)
    files = list(directory.glob("research_*.json")) + list(directory.glob("*.json"))
    files = [f for f in files if not f.name.startswith('.')]

    for filepath in files:
        try:
            with open(filepath) as f:
                data = json.load(f)

            item = process_research_item(data)
            items.append(item)

            # Move to processed (only for INGEST_DIR, not GDrive)
            if directory == INGEST_DIR:
                filepath.rename(PROCESSED_DIR / filepath.name)
                print(f"  Processed: {filepath.name}")
            else:
                print(f"  Read: {filepath.name}")

        except json.JSONDecodeError as e:
            print(f"  JSON Error in {filepath.name}: {e}")
        except Exception as e:
            print(f"  Error processing {filepath.name}: {e}")

    return items


def merge_to_brain(items: List[Dict]):
    """Merge research items into BRAIN.json"""
    if not items:
        return

    brain = load_brain()

    # Initialize research feed if not exists
    if "research_feed" not in brain:
        brain["research_feed"] = {
            "items": [],
            "last_ingested": None,
            "total_count": 0
        }

    # Get existing IDs to avoid duplicates
    existing_ids = {item["id"] for item in brain["research_feed"]["items"]}

    new_items = []
    for item in items:
        if item["id"] not in existing_ids:
            new_items.append(item)
            existing_ids.add(item["id"])

    if new_items:
        brain["research_feed"]["items"].extend(new_items)
        brain["research_feed"]["last_ingested"] = datetime.now().isoformat()
        brain["research_feed"]["total_count"] = len(brain["research_feed"]["items"])

        save_brain(brain)
        print(f"BRAIN.json updated with {len(new_items)} new items")
    else:
        print("No new items to add (all duplicates)")


def extract_signals(brain: dict) -> List[Dict]:
    """Extract actionable trading signals from research feed"""
    signals = []

    for item in brain.get("research_feed", {}).get("items", []):
        for signal in item.get("signals", []):
            signals.append({
                "source_id": item["id"],
                "timestamp": item["timestamp"],
                "ticker": item.get("ticker"),
                "signal": signal,
                "sentiment": item.get("sentiment", {})
            })

    return signals


def ingest_all():
    """Main ingestion pipeline"""
    print("=" * 50)
    print("VOICE RESEARCH INGESTER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_items = []

    # 1. Fetch from API
    print("\n[1/3] Checking WealthWhisperer API...")
    api_items = fetch_from_api()
    all_items.extend(api_items)

    # 2. Process local files
    print("\n[2/3] Processing local files...")
    local_items = process_local_files(INGEST_DIR)
    all_items.extend(local_items)
    print(f"  Found {len(local_items)} local items")

    # 3. Check GDrive sync folder
    print("\n[3/3] Checking GDrive sync folder...")
    if GDRIVE_DIR.exists():
        gdrive_items = process_local_files(GDRIVE_DIR)
        all_items.extend(gdrive_items)
        print(f"  Found {len(gdrive_items)} GDrive items")
    else:
        print("  GDrive folder not available")

    # Merge to BRAIN.json
    print("\n[MERGE] Updating BRAIN.json...")
    merge_to_brain(all_items)

    # Summary
    print("\n" + "=" * 50)
    print(f"COMPLETE: Processed {len(all_items)} total items")
    print("=" * 50)

    return all_items


if __name__ == "__main__":
    ingest_all()

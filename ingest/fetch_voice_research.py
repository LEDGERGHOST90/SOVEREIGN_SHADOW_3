#!/usr/bin/env python3
"""
📥 Voice Research Ingester
Polls for exports from Replit Voice App and updates BRAIN.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

INGEST_DIR = Path(__file__).parent / "voice_research"
BRAIN_PATH = Path(__file__).parent.parent / "BRAIN.json"
PROCESSED_DIR = INGEST_DIR / "processed"

def load_brain():
    """Load current BRAIN.json"""
    with open(BRAIN_PATH) as f:
        return json.load(f)

def save_brain(brain):
    """Save updated BRAIN.json"""
    brain["last_updated"] = datetime.now().isoformat()
    with open(BRAIN_PATH, 'w') as f:
        json.dump(brain, f, indent=2)

def process_research_file(filepath: Path) -> dict:
    """Process a single voice research export"""
    with open(filepath) as f:
        research = json.load(f)

    print(f"📥 Processing: {filepath.name}")

    # Extract key data
    result = {
        "id": research.get("recording", {}).get("id", filepath.stem),
        "timestamp": research.get("timestamp"),
        "ticker": research.get("analysis", {}).get("ticker"),
        "sentiment": research.get("analysis", {}).get("sentiment", {}),
        "signals": research.get("analysis", {}).get("signals", []),
        "insights": research.get("analysis", {}).get("key_insights", []),
        "source": "voice_research_app"
    }

    return result

def ingest_all():
    """Process all pending research files"""
    PROCESSED_DIR.mkdir(exist_ok=True)

    brain = load_brain()

    # Initialize research array if not exists
    if "voice_research" not in brain:
        brain["voice_research"] = []

    # Find all JSON files
    files = list(INGEST_DIR.glob("research_*.json"))

    if not files:
        print("📭 No new research files to process")
        return

    for filepath in files:
        try:
            research = process_research_file(filepath)
            brain["voice_research"].append(research)

            # Move to processed
            filepath.rename(PROCESSED_DIR / filepath.name)
            print(f"✅ Processed: {filepath.name}")

        except Exception as e:
            print(f"❌ Error processing {filepath.name}: {e}")

    save_brain(brain)
    print(f"💾 BRAIN.json updated with {len(files)} research items")

if __name__ == "__main__":
    print("🎙️ Voice Research Ingester")
    print("=" * 40)
    ingest_all()

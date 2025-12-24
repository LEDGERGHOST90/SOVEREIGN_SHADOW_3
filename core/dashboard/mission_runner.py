#!/usr/bin/env python3
"""
🔱 SOVEREIGN COUNCIL - Mission Runner
Executes GIO (Gemini) missions and logs results for AURORA ingestion.

Usage:
    python mission_runner.py rotation_hunter
    python mission_runner.py catalyst_radar
    python mission_runner.py --all
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
MISSIONS_DIR = BASE_DIR / "council" / "missions" / "gemini"
LOG_FILE = BASE_DIR / "council" / "logs" / "Council_Log.md"

# Available missions
MISSIONS = {
    "rotation_hunter": "gemini_rotation_hunter.md",
    "catalyst_radar": "gemini_catalyst_radar.md",
    "narrative_map": "gemini_narrative_map.md",
    "volatility_map": "gemini_volatility_map.md",
    "alt_discovery": "gemini_alt_discovery.md",
    "sector_strength": "gemini_sector_strength.md",
    "macro_scan": "gemini_macro_scan.md",
    "sniper_intel": "gemini_sniper_intel.md",
}


def load_mission_template(mission_name: str) -> str:
    """Load mission template content."""
    if mission_name not in MISSIONS:
        raise ValueError(f"Unknown mission: {mission_name}")

    template_path = MISSIONS_DIR / MISSIONS[mission_name]
    with open(template_path, "r") as f:
        return f.read()


def execute_gemini_mission(mission_name: str, template: str) -> str:
    """Execute mission via Gemini API."""
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "ERROR: GEMINI_API_KEY not found in environment"

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Build the prompt
        prompt = f"""
You are GIO, the Research Intelligence Agent of the Sovereign Shadow Council.

Execute the following mission and provide a complete report following the exact output format specified.

Be specific, use real current market data and analysis. Provide actionable intelligence.

MISSION TEMPLATE:
{template}

Execute this mission NOW. Provide the full report with all sections filled in.
Use real current crypto market data and analysis.
Today's date: {datetime.now().strftime('%Y-%m-%d')}
"""

        response = model.generate_content(prompt)
        return response.text

    except ImportError:
        return "ERROR: google-generativeai not installed. Run: pip install google-generativeai"
    except Exception as e:
        return f"ERROR: {str(e)}"


def append_to_council_log(mission_name: str, result: str):
    """Append mission result to Council Log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
---

## [{timestamp}] GIO | {mission_name.upper()} | COMPLETED

{result}

---
"""

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    print(f"✅ Logged to Council_Log.md")


def run_mission(mission_name: str):
    """Run a single mission."""
    print(f"\n🔱 SOVEREIGN COUNCIL - Mission Runner")
    print(f"━" * 50)
    print(f"Mission: {mission_name}")
    print(f"Agent: GIO (Gemini)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"━" * 50)

    # Load template
    print(f"\n📋 Loading mission template...")
    template = load_mission_template(mission_name)

    # Execute
    print(f"🚀 Executing mission via Gemini...")
    result = execute_gemini_mission(mission_name, template)

    # Log
    print(f"\n📝 Logging results...")
    append_to_council_log(mission_name, result)

    # Output
    print(f"\n{'━' * 50}")
    print(f"MISSION REPORT:")
    print(f"{'━' * 50}")
    print(result)

    return result


def run_all_missions():
    """Run all missions sequentially."""
    results = {}
    for mission_name in MISSIONS.keys():
        print(f"\n{'=' * 60}")
        results[mission_name] = run_mission(mission_name)
        print(f"{'=' * 60}\n")
    return results


def list_missions():
    """List available missions."""
    print("\n🔱 Available GIO Missions:")
    print("━" * 40)
    for name, filename in MISSIONS.items():
        print(f"  • {name}")
    print("━" * 40)
    print("\nUsage: python mission_runner.py <mission_name>")
    print("       python mission_runner.py --all")
    print("       python mission_runner.py --list")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_missions()
        sys.exit(0)

    arg = sys.argv[1]

    if arg == "--list":
        list_missions()
    elif arg == "--all":
        run_all_missions()
    elif arg in MISSIONS:
        run_mission(arg)
    else:
        print(f"❌ Unknown mission: {arg}")
        list_missions()
        sys.exit(1)

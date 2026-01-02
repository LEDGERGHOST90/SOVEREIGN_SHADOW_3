#!/usr/bin/env python3
"""
AUTO-COMPACT SAVE (ACC) - Emergency Session Preservation

Triggers when context is about to compact. Saves everything before it's lost.

Protocol:
1. Save full session to memory/SESSIONS/{date}_{time}_ACC.md
2. Update BRAIN.json with session changes
3. Patch any files discussed
4. Push summary to Replit
5. Send NTFY confirmation

Usage:
    python3 core/session/auto_save.py "Summary of what we did"

Or from Claude:
    from core.session.auto_save import emergency_save
    emergency_save(summary="What was accomplished", changes={...})
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Paths
PROJECT_ROOT = Path("/Volumes/LegacySafe/SS_III")
SESSIONS_DIR = PROJECT_ROOT / "memory" / "SESSIONS"
BRAIN_PATH = PROJECT_ROOT / "BRAIN.json"
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "sovereignshadow_dc4d2fa1")
REPLIT_URL = os.getenv(
    "REPLIT_API_URL",
    "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
)


class AutoCompactSave:
    """
    Emergency session preservation system.
    Call this when context is about to compact.
    """

    def __init__(self):
        self.timestamp = datetime.now()
        self.date_str = self.timestamp.strftime("%Y-%m-%d")
        self.time_str = self.timestamp.strftime("%H-%M")
        self.session_file = SESSIONS_DIR / f"{self.date_str}_{self.time_str}_ACC.md"

    def save_session(
        self,
        summary: str,
        accomplishments: List[str] = None,
        issues_found: List[str] = None,
        files_created: List[str] = None,
        files_modified: List[str] = None,
        next_steps: List[str] = None,
        brain_updates: Dict[str, Any] = None,
        raw_context: str = None
    ) -> Dict[str, Any]:
        """
        Save complete session state before compaction.

        Args:
            summary: Brief summary of session
            accomplishments: List of what was done
            issues_found: Problems discovered
            files_created: New files made
            files_modified: Existing files changed
            next_steps: What to do next
            brain_updates: Dict of BRAIN.json updates
            raw_context: Optional raw conversation dump

        Returns:
            Status dict with file paths
        """
        results = {
            "success": True,
            "timestamp": self.timestamp.isoformat(),
            "files_saved": []
        }

        # 1. Save session markdown
        session_content = self._build_session_md(
            summary=summary,
            accomplishments=accomplishments or [],
            issues_found=issues_found or [],
            files_created=files_created or [],
            files_modified=files_modified or [],
            next_steps=next_steps or []
        )

        try:
            SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
            self.session_file.write_text(session_content)
            results["files_saved"].append(str(self.session_file))
            print(f"✅ Session saved: {self.session_file}")
        except Exception as e:
            results["success"] = False
            results["session_error"] = str(e)
            print(f"❌ Session save failed: {e}")

        # 2. Update BRAIN.json
        if brain_updates:
            try:
                self._update_brain(brain_updates)
                results["brain_updated"] = True
                print(f"✅ BRAIN.json updated")
            except Exception as e:
                results["brain_error"] = str(e)
                print(f"❌ BRAIN.json update failed: {e}")

        # 3. Push to Replit
        try:
            self._push_to_replit(summary, accomplishments or [])
            results["replit_pushed"] = True
            print(f"✅ Pushed to Replit")
        except Exception as e:
            results["replit_error"] = str(e)
            print(f"⚠️ Replit push failed: {e}")

        # 4. Send NTFY notification
        try:
            self._send_notification(summary)
            results["notification_sent"] = True
            print(f"✅ Notification sent")
        except Exception as e:
            results["notification_error"] = str(e)
            print(f"⚠️ Notification failed: {e}")

        # 5. Save raw context if provided
        if raw_context:
            try:
                raw_file = SESSIONS_DIR / f"{self.date_str}_{self.time_str}_ACC_raw.txt"
                raw_file.write_text(raw_context)
                results["files_saved"].append(str(raw_file))
                print(f"✅ Raw context saved")
            except Exception as e:
                results["raw_context_error"] = str(e)

        return results

    def _build_session_md(
        self,
        summary: str,
        accomplishments: List[str],
        issues_found: List[str],
        files_created: List[str],
        files_modified: List[str],
        next_steps: List[str]
    ) -> str:
        """Build session markdown content."""
        lines = [
            f"# Auto-Compact Save: {self.date_str} {self.time_str}",
            "",
            "**Type:** ACC (Auto-Compact Call)",
            f"**Timestamp:** {self.timestamp.isoformat()}",
            "",
            "---",
            "",
            "## Summary",
            summary,
            "",
        ]

        if accomplishments:
            lines.append("## Accomplishments")
            for item in accomplishments:
                lines.append(f"- {item}")
            lines.append("")

        if issues_found:
            lines.append("## Issues Found")
            for item in issues_found:
                lines.append(f"- {item}")
            lines.append("")

        if files_created:
            lines.append("## Files Created")
            for item in files_created:
                lines.append(f"- `{item}`")
            lines.append("")

        if files_modified:
            lines.append("## Files Modified")
            for item in files_modified:
                lines.append(f"- `{item}`")
            lines.append("")

        if next_steps:
            lines.append("## Next Steps")
            for item in next_steps:
                lines.append(f"- [ ] {item}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "*Saved automatically before context compaction.*"
        ])

        return "\n".join(lines)

    def _update_brain(self, updates: Dict[str, Any]):
        """Update BRAIN.json with session changes."""
        try:
            brain = json.loads(BRAIN_PATH.read_text())
        except:
            brain = {}

        # Add session record
        if "sessions" not in brain:
            brain["sessions"] = []

        brain["sessions"].append({
            "date": self.date_str,
            "time": self.time_str,
            "type": "ACC",
            "file": str(self.session_file)
        })

        # Keep only last 30 sessions
        brain["sessions"] = brain["sessions"][-30:]

        # Apply custom updates
        for key, value in updates.items():
            if isinstance(value, dict) and key in brain and isinstance(brain[key], dict):
                brain[key].update(value)
            else:
                brain[key] = value

        # Update last_session timestamp
        brain["last_session"] = self.timestamp.isoformat()

        BRAIN_PATH.write_text(json.dumps(brain, indent=2))

    def _push_to_replit(self, summary: str, accomplishments: List[str]):
        """Push session summary to Replit."""
        payload = {
            "update": {
                "session_type": "ACC",
                "timestamp": self.timestamp.isoformat(),
                "summary": summary,
                "accomplishments": accomplishments
            },
            "source": "auto_compact_save"
        }

        resp = requests.post(
            f"{REPLIT_URL}/api/brain/push",
            json=payload,
            timeout=15
        )
        resp.raise_for_status()

    def _send_notification(self, summary: str):
        """Send NTFY notification."""
        message = f"ACC Save: {summary[:100]}"
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Session Auto-Saved",
                "Priority": "high",
                "Tags": "floppy_disk,warning"
            },
            timeout=10
        )


def emergency_save(
    summary: str,
    accomplishments: List[str] = None,
    issues_found: List[str] = None,
    files_created: List[str] = None,
    files_modified: List[str] = None,
    next_steps: List[str] = None,
    brain_updates: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Quick function to save session before compaction.

    Example:
        emergency_save(
            summary="Fixed Gemini API, created SmartAI router",
            accomplishments=["Created smart_ai.py", "Fixed neural_signals"],
            next_steps=["Start RWA alerts", "Fix GitHub token"]
        )
    """
    saver = AutoCompactSave()
    return saver.save_session(
        summary=summary,
        accomplishments=accomplishments,
        issues_found=issues_found,
        files_created=files_created,
        files_modified=files_modified,
        next_steps=next_steps,
        brain_updates=brain_updates
    )


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auto_save.py 'Summary of session'")
        print("\nThis saves the current session before context compaction.")
        sys.exit(1)

    summary = sys.argv[1]

    print("=" * 60)
    print("AUTO-COMPACT SAVE (ACC)")
    print("=" * 60)

    result = emergency_save(summary=summary)

    print("\n" + "=" * 60)
    if result["success"]:
        print("✅ SESSION PRESERVED")
        for f in result.get("files_saved", []):
            print(f"   {f}")
    else:
        print("❌ SAVE HAD ERRORS - Check output above")
    print("=" * 60)

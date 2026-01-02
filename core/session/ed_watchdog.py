#!/usr/bin/env python3
"""
ED - Engineer Chief Watchdog
Your AI oversight system that monitors sessions 24/7

Ed watches for:
- Context filling up (triggers ACC save)
- Duplicate file creation attempts
- Going in circles (repeating same work)
- Session duration without saves
- Critical mistakes before they happen
- Focus drift (straying from RWA thesis)

Usage (Claude should call periodically):
    from core.session.ed_watchdog import ed

    # Check in with Ed
    ed.check_in(action="reading files", files_touched=5)

    # Ed will alert if something's wrong
    ed.status()

Ed alerts via NTFY when intervention needed.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Paths
PROJECT_ROOT = Path("/Volumes/LegacySafe/SS_III")
ED_STATE_FILE = PROJECT_ROOT / "data" / "ed_state.json"
BRAIN_JOT_FILE = PROJECT_ROOT / "BRAIN_JOT.json"
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "sovereignshadow_dc4d2fa1")


def load_brain_jot() -> Dict[str, Any]:
    """Load ecosystem config from BRAIN_JOT.json"""
    try:
        if BRAIN_JOT_FILE.exists():
            return json.loads(BRAIN_JOT_FILE.read_text())
    except Exception:
        pass
    return {}


class EdWatchdog:
    """
    ED - The Engineer Chief

    Monitors Claude sessions and intervenes when needed.
    Named after a chief engineer who keeps the ship running.
    """

    DUPLICATE_WARNING_KEYWORDS = [
        "let me create", "i'll build", "creating new",
        "new file", "let me write", "building a"
    ]

    def __init__(self):
        # Load config from BRAIN_JOT ecosystem schema
        jot = load_brain_jot()
        thresholds = jot.get("oversight", {}).get("thresholds", {})
        alignment = jot.get("alignment", {})

        # Thresholds from ecosystem config
        self.MAX_FILES_WITHOUT_SAVE = thresholds.get("files_before_save", 15)
        self.MAX_MINUTES_WITHOUT_SAVE = thresholds.get("minutes_before_save", 20)
        self.MAX_TOOL_CALLS_WITHOUT_SAVE = thresholds.get("tool_calls_before_save", 30)
        self.FOCUS_DRIFT_THRESHOLD = thresholds.get("focus_drift_score", 50)

        # Focus keywords from ecosystem alignment
        self.FOCUS_KEYWORDS = [kw.lower() for kw in alignment.get("primary_focus", ["rwa", "link", "inj", "qnt", "ondo", "plume"])]
        self.FOCUS_KEYWORDS.extend([kw.lower() for kw in alignment.get("secondary_focus", [])])
        self.FOCUS_KEYWORDS.append("manus")  # Research source

        self.DRIFT_KEYWORDS = [kw.lower().replace("_", " ") for kw in alignment.get("drift_indicators", ["outrageous", "aave", "siphon"])]
        self.session_start = datetime.now()
        self.last_save = datetime.now()
        self.files_touched = 0
        self.tool_calls = 0
        self.actions_log = []
        self.warnings_sent = []
        self.focus_score = 100  # Starts at 100, decreases with drift

        # Load previous state if exists
        self._load_state()

    def _load_state(self):
        """Load Ed's state from disk."""
        try:
            if ED_STATE_FILE.exists():
                data = json.loads(ED_STATE_FILE.read_text())
                # Only load if from today
                if data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    self.files_touched = data.get("files_touched", 0)
                    self.tool_calls = data.get("tool_calls", 0)
                    self.warnings_sent = data.get("warnings_sent", [])
        except Exception:
            pass

    def _save_state(self):
        """Persist Ed's state and update BRAIN_JOT telemetry."""
        try:
            ED_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "files_touched": self.files_touched,
                "tool_calls": self.tool_calls,
                "warnings_sent": self.warnings_sent,
                "last_check": datetime.now().isoformat()
            }
            ED_STATE_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

        # Also update BRAIN_JOT telemetry
        try:
            if BRAIN_JOT_FILE.exists():
                jot = json.loads(BRAIN_JOT_FILE.read_text())
                jot["telemetry"]["current_session"] = {
                    "started": self.session_start.isoformat(),
                    "files_touched": self.files_touched,
                    "tool_calls": self.tool_calls,
                    "focus_score": self.focus_score,
                    "last_save": self.last_save.isoformat(),
                    "warnings": len(self.warnings_sent)
                }
                BRAIN_JOT_FILE.write_text(json.dumps(jot, indent=2))
        except Exception:
            pass

    def _alert(self, title: str, message: str, priority: str = "high", tag: str = "warning"):
        """Send alert via NTFY."""
        try:
            full_title = f"ED: {title}"
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=message.encode('utf-8'),
                headers={
                    "Title": full_title,
                    "Priority": priority,
                    "Tags": f"robot,{tag}"
                },
                timeout=10
            )
            self.warnings_sent.append({
                "title": title,
                "time": datetime.now().isoformat()
            })
            print(f"🤖 ED ALERT: {title}")
            print(f"   {message}")
        except Exception as e:
            print(f"ED alert failed: {e}")

    def check_in(
        self,
        action: str = None,
        files_touched: int = 0,
        tool_calls: int = 1,
        message_text: str = None
    ) -> Dict[str, Any]:
        """
        Regular check-in with Ed.
        Claude should call this periodically.

        Args:
            action: What Claude is doing
            files_touched: Number of files read/written
            tool_calls: Number of tool calls made
            message_text: Optional text to analyze for drift/duplicates

        Returns:
            Status dict with any warnings
        """
        self.files_touched += files_touched
        self.tool_calls += tool_calls

        if action:
            self.actions_log.append({
                "action": action,
                "time": datetime.now().isoformat()
            })

        warnings = []

        # Check 1: Files without save
        if self.files_touched >= self.MAX_FILES_WITHOUT_SAVE:
            warnings.append("TOO_MANY_FILES")
            if "files_warning" not in [w.get("title") for w in self.warnings_sent[-5:]]:
                self._alert(
                    "Save Needed - Files",
                    f"Touched {self.files_touched} files without saving. Run ACC now!",
                    priority="high"
                )

        # Check 2: Time without save
        minutes_since_save = (datetime.now() - self.last_save).total_seconds() / 60
        if minutes_since_save >= self.MAX_MINUTES_WITHOUT_SAVE:
            warnings.append("TOO_LONG_NO_SAVE")
            if "time_warning" not in [w.get("title") for w in self.warnings_sent[-5:]]:
                self._alert(
                    "Save Needed - Time",
                    f"{int(minutes_since_save)} minutes without save. Context may compact soon!",
                    priority="high"
                )

        # Check 3: Tool calls accumulating
        if self.tool_calls >= self.MAX_TOOL_CALLS_WITHOUT_SAVE:
            warnings.append("TOO_MANY_CALLS")
            if "calls_warning" not in [w.get("title") for w in self.warnings_sent[-5:]]:
                self._alert(
                    "Save Needed - Context",
                    f"{self.tool_calls} tool calls. Context is filling up. ACC NOW!",
                    priority="urgent"
                )

        # Check 4: Duplicate creation attempt
        if message_text:
            text_lower = message_text.lower()
            for keyword in self.DUPLICATE_WARNING_KEYWORDS:
                if keyword in text_lower:
                    warnings.append("POSSIBLE_DUPLICATE")
                    # Don't spam, just log
                    break

            # Check 5: Focus drift
            drift_count = sum(1 for kw in self.DRIFT_KEYWORDS if kw in text_lower)
            focus_count = sum(1 for kw in self.FOCUS_KEYWORDS if kw in text_lower)

            if drift_count > focus_count and drift_count > 0:
                self.focus_score = max(0, self.focus_score - 5)
                if self.focus_score < 50:
                    warnings.append("FOCUS_DRIFT")
                    if "drift_warning" not in [w.get("title") for w in self.warnings_sent[-10:]]:
                        self._alert(
                            "Focus Drift Detected",
                            "Conversation drifting from RWA thesis. Refocus on LINK/INJ/QNT/ONDO/PLUME.",
                            priority="default",
                            tag="brain"
                        )

        self._save_state()

        return {
            "status": "ok" if not warnings else "warning",
            "warnings": warnings,
            "files_touched": self.files_touched,
            "tool_calls": self.tool_calls,
            "minutes_active": int((datetime.now() - self.session_start).total_seconds() / 60),
            "focus_score": self.focus_score
        }

    def mark_saved(self):
        """Call this after ACC or EOD save to reset counters."""
        self.last_save = datetime.now()
        self.files_touched = 0
        self.tool_calls = 0
        self.focus_score = 100
        self._save_state()
        print("🤖 ED: Save acknowledged. Counters reset.")

    def status(self) -> str:
        """Get Ed's current assessment."""
        minutes_active = int((datetime.now() - self.session_start).total_seconds() / 60)
        minutes_since_save = int((datetime.now() - self.last_save).total_seconds() / 60)

        # Determine overall status
        if self.tool_calls > 25 or self.files_touched > 12 or minutes_since_save > 15:
            status = "⚠️ SAVE RECOMMENDED"
            urgency = "Save soon to prevent data loss"
        elif self.tool_calls > 15 or self.files_touched > 8 or minutes_since_save > 10:
            status = "🟡 MONITORING"
            urgency = "Getting close to save threshold"
        else:
            status = "🟢 ALL CLEAR"
            urgency = "Healthy session state"

        report = f"""
🤖 ED STATUS REPORT
{'='*40}
Status: {status}
{urgency}

Session Active: {minutes_active} minutes
Since Last Save: {minutes_since_save} minutes
Files Touched: {self.files_touched}/{self.MAX_FILES_WITHOUT_SAVE}
Tool Calls: {self.tool_calls}/{self.MAX_TOOL_CALLS_WITHOUT_SAVE}
Focus Score: {self.focus_score}/100
Warnings Sent: {len(self.warnings_sent)}
{'='*40}
"""
        return report.strip()

    def force_acc(self, summary: str = None):
        """Ed forces an ACC save."""
        from core.session.auto_save import emergency_save

        self._alert(
            "Forcing ACC Save",
            "Ed is forcing a session save to prevent data loss.",
            priority="high"
        )

        result = emergency_save(
            summary=summary or f"Ed-triggered save. Files: {self.files_touched}, Calls: {self.tool_calls}",
            accomplishments=[f"Ed watchdog monitoring ({self.tool_calls} tool calls)"],
            next_steps=["Continue session with fresh counters"]
        )

        if result.get("success"):
            self.mark_saved()

        return result


# Global Ed instance
ed = EdWatchdog()


# Quick functions for Claude to use
def checkin(action: str = None, files: int = 0):
    """Quick check-in with Ed."""
    return ed.check_in(action=action, files_touched=files)

def status():
    """Print Ed's status."""
    print(ed.status())

def saved():
    """Tell Ed we saved."""
    ed.mark_saved()


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            print(ed.status())
        elif cmd == "force":
            summary = sys.argv[2] if len(sys.argv) > 2 else None
            ed.force_acc(summary)
        elif cmd == "reset":
            ed.mark_saved()
            print("Ed counters reset.")
    else:
        print(ed.status())
        print("\nCommands:")
        print("  python3 ed_watchdog.py status  - Show status")
        print("  python3 ed_watchdog.py force   - Force ACC save")
        print("  python3 ed_watchdog.py reset   - Reset counters")

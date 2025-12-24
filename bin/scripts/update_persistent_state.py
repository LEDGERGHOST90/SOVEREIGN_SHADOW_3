#!/usr/bin/env python3
"""
PERSISTENT STATE UPDATER - FULL SYSTEM SNAPSHOT
Auto-updates PERSISTENT_STATE.json with comprehensive system monitoring
Tracks: files, configs, git state, packages, APIs, databases, and more
Run hourly via cron/launchd to maintain complete system inventory
"""

import json
import os
import sys
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PERSISTENT_STATE_PATH = PROJECT_ROOT / "PERSISTENT_STATE.json"
LOG_PATH = PROJECT_ROOT / "logs" / "persistent_state_updates.log"

# Folders to monitor for changes
MONITORED_FOLDERS = [
    "agents", "modules", "core", "scripts", "config",
    "exchanges", "ladder_systems", "hybrid_system",
    "tools", "tests", "docs", "schemas", "memory"
]

# Config files to track
MONITORED_CONFIGS = [
    ".env",
    "config/exchange_config.json",
    "config/safety_config.json",
    "config/ladder_config.json",
    "memory/SHADE_AGENT_REGISTRY.yaml"
]


def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)

    # Append to log file
    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(log_message + "\n")


def get_file_hash(filepath):
    """Get SHA256 hash of a file"""
    try:
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]  # First 16 chars
    except Exception:
        return None


def get_git_info():
    """Get current git state"""
    try:
        # Current branch
        branch = subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Latest commit hash
        commit = subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Uncommitted changes
        status = subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), "status", "--short"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Count modified/untracked files
        modified_count = len([line for line in status.split('\n') if line and line.startswith(' M')])
        untracked_count = len([line for line in status.split('\n') if line and line.startswith('??')])

        return {
            "branch": branch,
            "commit_hash": commit,
            "has_uncommitted_changes": len(status) > 0,
            "modified_files": modified_count,
            "untracked_files": untracked_count
        }
    except Exception as e:
        log(f"⚠️ Could not get git info: {e}")
        return None


def scan_folder_stats(folder_name):
    """Get comprehensive stats for a folder"""
    folder_path = PROJECT_ROOT / folder_name

    if not folder_path.exists():
        return None

    stats = {
        "exists": True,
        "file_count": 0,
        "py_file_count": 0,
        "total_size_kb": 0,
        "last_modified": None,
        "lines_of_code": 0
    }

    try:
        # Walk through all files
        for root, dirs, files in os.walk(folder_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue

                filepath = Path(root) / file
                stats["file_count"] += 1

                # Get file size
                try:
                    size = filepath.stat().st_size
                    stats["total_size_kb"] += size / 1024

                    # Get last modified time
                    mtime = filepath.stat().st_mtime
                    if stats["last_modified"] is None or mtime > stats["last_modified"]:
                        stats["last_modified"] = mtime

                    # Count Python files and LOC
                    if filepath.suffix == '.py':
                        stats["py_file_count"] += 1
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                # Count non-empty, non-comment lines
                                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                                stats["lines_of_code"] += len(code_lines)
                        except Exception:
                            pass

                except Exception:
                    pass

        # Convert timestamp to ISO format
        if stats["last_modified"]:
            stats["last_modified"] = datetime.fromtimestamp(stats["last_modified"]).isoformat() + "-08:00"

        stats["total_size_kb"] = round(stats["total_size_kb"], 2)

    except Exception as e:
        log(f"⚠️ Error scanning {folder_name}: {e}")

    return stats


def track_config_files():
    """Track hashes and modification times of config files"""
    configs = {}

    for config_path in MONITORED_CONFIGS:
        filepath = PROJECT_ROOT / config_path

        if filepath.exists():
            try:
                mtime = filepath.stat().st_mtime
                file_hash = get_file_hash(filepath)

                configs[config_path] = {
                    "exists": True,
                    "last_modified": datetime.fromtimestamp(mtime).isoformat() + "-08:00",
                    "hash": file_hash,
                    "size_bytes": filepath.stat().st_size
                }
            except Exception as e:
                configs[config_path] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            configs[config_path] = {
                "exists": False
            }

    return configs


def get_python_packages():
    """Get installed Python package versions"""
    try:
        result = subprocess.run(
            ["pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        if result.returncode == 0:
            packages = json.loads(result.stdout)
            # Only track key packages
            key_packages = ["ccxt", "web3", "pandas", "numpy", "requests", "flask", "nextjs"]
            tracked = {}

            for pkg in packages:
                if any(key in pkg["name"].lower() for key in key_packages):
                    tracked[pkg["name"]] = pkg["version"]

            return tracked
    except Exception as e:
        log(f"⚠️ Could not get package info: {e}")

    return {}


def get_balance_data():
    """Try to fetch current balance data"""
    try:
        balance_file = PROJECT_ROOT / "logs" / "ai_enhanced" / "real_balances.json"
        if balance_file.exists():
            with open(balance_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        log(f"⚠️ Could not read balance data: {e}")
    return None


def get_psychology_state():
    """Get current psychology tracker state"""
    try:
        psychology_file = PROJECT_ROOT / "logs" / "psychology_log.jsonl"
        if psychology_file.exists():
            with open(psychology_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return {
                        "strikes": last_entry.get("strikes", 0),
                        "locked_out": last_entry.get("locked_out", False),
                        "last_emotion": last_entry.get("emotion", "neutral"),
                        "total_entries": len(lines)
                    }
    except Exception as e:
        log(f"⚠️ Could not read psychology state: {e}")
    return None


def get_trade_journal_stats():
    """Get trade journal statistics"""
    try:
        journal_file = PROJECT_ROOT / "logs" / "trade_journal.jsonl"
        if journal_file.exists():
            with open(journal_file, "r") as f:
                lines = f.readlines()
                total_trades = len(lines)

                if total_trades > 0:
                    wins = sum(1 for line in lines if json.loads(line).get("outcome") == "win")
                    win_rate = (wins / total_trades) * 100

                    return {
                        "total_trades": total_trades,
                        "wins": wins,
                        "losses": total_trades - wins,
                        "win_rate_percent": round(win_rate, 2)
                    }
    except Exception as e:
        log(f"⚠️ Could not read trade journal: {e}")
    return None


def get_mentor_progress():
    """Get mentor system progress"""
    try:
        mentor_file = PROJECT_ROOT / "logs" / "mentor_progress.json"
        if mentor_file.exists():
            with open(mentor_file, "r") as f:
                return json.load(f)
    except Exception as e:
        log(f"⚠️ Could not read mentor progress: {e}")
    return None


def load_current_state():
    """Load existing persistent state"""
    try:
        with open(PERSISTENT_STATE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log("❌ PERSISTENT_STATE.json not found")
        return None
    except json.JSONDecodeError as e:
        log(f"❌ Invalid JSON in persistent state: {e}")
        return None


def update_state():
    """Main update function - FULL SYSTEM SNAPSHOT"""
    log("🔄 Starting FULL SYSTEM SNAPSHOT update...")

    # Load current state
    state = load_current_state()
    if not state:
        log("❌ Cannot update - no existing state found")
        return False

    # Update timestamp
    state["last_updated"] = datetime.now().isoformat() + "-08:00"

    # ==== GIT STATE ====
    git_info = get_git_info()
    if git_info:
        state["git_state"] = git_info
        log(f"✅ Git: {git_info['branch']}@{git_info['commit_hash']} ({git_info['modified_files']} modified)")
    else:
        log("⚠️ Could not get git state")

    # ==== FOLDER MONITORING ====
    folder_stats = {}
    total_py_files = 0
    total_loc = 0

    for folder in MONITORED_FOLDERS:
        stats = scan_folder_stats(folder)
        if stats:
            folder_stats[folder] = stats
            total_py_files += stats["py_file_count"]
            total_loc += stats["lines_of_code"]
            log(f"✅ {folder}/: {stats['file_count']} files, {stats['py_file_count']} .py, {stats['lines_of_code']} LOC")

    state["code_inventory"] = {
        "folders": folder_stats,
        "summary": {
            "total_monitored_folders": len([f for f in folder_stats if folder_stats[f]]),
            "total_python_files": total_py_files,
            "total_lines_of_code": total_loc,
            "last_scanned": datetime.now().isoformat() + "-08:00"
        }
    }

    log(f"✅ Code inventory: {total_py_files} Python files, {total_loc:,} lines of code")

    # ==== CONFIG FILE TRACKING ====
    config_tracking = track_config_files()
    state["config_files"] = config_tracking

    config_count = len([c for c in config_tracking.values() if c.get("exists")])
    log(f"✅ Tracked {config_count} config files")

    # ==== PYTHON PACKAGES ====
    packages = get_python_packages()
    if packages:
        state["python_packages"] = packages
        log(f"✅ Tracked {len(packages)} Python packages")

    # ==== BALANCE DATA ====
    balance_data = get_balance_data()
    if balance_data:
        state["recent_actions"]["last_balance_fetch"] = {
            "timestamp": balance_data.get("timestamp"),
            "total_exchanges": balance_data.get("total_exchanges", 0)
        }
        log("✅ Updated balance data")
    else:
        log("⚠️ Using cached balance data")

    # ==== PSYCHOLOGY STATE ====
    psych_state = get_psychology_state()
    if psych_state:
        state["trading_systems"]["psychology_tracker"].update({
            "strikes": psych_state["strikes"],
            "locked_out": psych_state["locked_out"],
            "total_log_entries": psych_state["total_entries"]
        })
        log(f"✅ Psychology: {psych_state['strikes']}/3 strikes, {psych_state['total_entries']} entries")

    # ==== TRADE JOURNAL ====
    journal_stats = get_trade_journal_stats()
    if journal_stats:
        state["trading_systems"]["trade_journal"].update(journal_stats)
        log(f"✅ Trades: {journal_stats['total_trades']} total, {journal_stats['win_rate_percent']}% win rate")

    # ==== MENTOR PROGRESS ====
    mentor_progress = get_mentor_progress()
    if mentor_progress:
        state["trading_systems"]["mentor_system"].update(mentor_progress)
        log(f"✅ Updated mentor progress")

    # ==== DISK SPACE ====
    try:
        import shutil
        disk_stats = shutil.disk_usage("/Volumes/LegacySafe")
        state["disk_space"].update({
            "total_tb": round(disk_stats.total / (1024**4), 2),
            "used_gb": round(disk_stats.used / (1024**3), 1),
            "available_tb": round(disk_stats.free / (1024**4), 2),
            "used_percent": round((disk_stats.used / disk_stats.total) * 100, 1),
            "last_checked": datetime.now().isoformat() + "-08:00"
        })
        log(f"✅ Disk: {state['disk_space']['used_percent']}% used")
    except Exception as e:
        log(f"⚠️ Could not update disk space: {e}")

    # ==== UPDATE METADATA ====
    state["recent_actions"]["last_auto_update"] = {
        "timestamp": datetime.now().isoformat() + "-08:00",
        "method": "automated_hourly_full_snapshot",
        "sections_updated": [
            "git_state", "code_inventory", "config_files",
            "python_packages", "disk_space", "trading_systems"
        ]
    }

    # ==== WRITE UPDATED STATE ====
    try:
        with open(PERSISTENT_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)

        log("✅ FULL SYSTEM SNAPSHOT completed successfully")
        log(f"📊 Summary: {total_py_files} files, {total_loc:,} LOC, {config_count} configs tracked")
        return True

    except Exception as e:
        log(f"❌ Failed to write persistent state: {e}")
        return False


if __name__ == "__main__":
    try:
        success = update_state()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)

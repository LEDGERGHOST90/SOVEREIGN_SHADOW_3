#!/usr/bin/env python3
"""
DEBT DESTROYER - MISSION 001 LAUNCHER
Paper Trading Campaign for AAVE Debt Repayment

"The chains of debt will break. Victory is inevitable."
"""

import os
import sys
import time
import json
import subprocess
import glob as globlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
MISSION_FILE = BASE_DIR / "data/missions/mission_001_aave_debt.json"
BRAIN_FILE = BASE_DIR / "BRAIN.json"

# Aurora voice integration
def aurora_speak(text: str, async_mode: bool = True):
    """Have Aurora speak a message"""
    try:
        if async_mode:
            subprocess.Popen(
                [sys.executable, str(BASE_DIR / "bin/speak.py"), text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.run(
                [sys.executable, str(BASE_DIR / "bin/speak.py"), text],
                cwd=str(BASE_DIR)
            )
    except Exception:
        pass  # Silent fail if voice unavailable

# SS_III COLOR SCHEME - Off-white, Matte Black, Crimson, Shadow
CRIMSON = "\033[38;5;160m"      # Deep crimson red
BLOOD = "\033[38;5;124m"        # Darker blood red
SHADOW = "\033[38;5;236m"       # Matte black shadow
SMOKE = "\033[38;5;240m"        # Smoke gray
BONE = "\033[38;5;255m"         # Off-white bone
ASH = "\033[38;5;250m"          # Ash gray (muted white)
EMBER = "\033[38;5;196m"        # Bright ember for accents

# Legacy colors for compatibility
RED = CRIMSON
GREEN = "\033[38;5;29m"         # Muted dark green
YELLOW = BONE                   # Use bone instead of yellow
BLUE = SHADOW
MAGENTA = BLOOD
CYAN = ASH
WHITE = BONE
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

LOGO = f"""
{SHADOW}                                                                              {RESET}
{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░{RESET}{CRIMSON}▓▓▓▓▓▓{SHADOW}░░{RESET}{CRIMSON}▓▓▓▓▓▓▓{SHADOW}░{RESET}{CRIMSON}▓▓▓▓▓▓{SHADOW}░░{RESET}{CRIMSON}▓▓▓▓▓▓▓▓{SHADOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░{RESET}{BLOOD}▓▓{SHADOW}░░{RESET}{BLOOD}▓▓{SHADOW}░{RESET}{BLOOD}▓▓{SHADOW}░░░░░{RESET}{BLOOD}▓▓{SHADOW}░░{RESET}{BLOOD}▓▓{SHADOW}░░░{RESET}{BLOOD}▓▓{SHADOW}░░░░{RESET}{BONE}SOVEREIGN SHADOW III{SHADOW}░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░{RESET}{CRIMSON}▓▓{SHADOW}░░{RESET}{CRIMSON}▓▓{SHADOW}░{RESET}{CRIMSON}▓▓▓▓▓{SHADOW}░░{RESET}{CRIMSON}▓▓▓▓▓▓{SHADOW}░░░░{RESET}{CRIMSON}▓▓{SHADOW}░░░░{RESET}{ASH}━━━━━━━━━━━━━━━━━━━━━{SHADOW}░░░░  {RESET}
{SHADOW}  ░{RESET}{BLOOD}▓▓{SHADOW}░░{RESET}{BLOOD}▓▓{SHADOW}░{RESET}{BLOOD}▓▓{SHADOW}░░░░░{RESET}{BLOOD}▓▓{SHADOW}░░{RESET}{BLOOD}▓▓{SHADOW}░░░{RESET}{BLOOD}▓▓{SHADOW}░░░░{RESET}{SMOKE}M I S S I O N  0 0 1{SHADOW}░░░░░░░░░  {RESET}
{SHADOW}  ░{RESET}{CRIMSON}▓▓▓▓▓▓{SHADOW}░░{RESET}{CRIMSON}▓▓▓▓▓▓▓{SHADOW}░{RESET}{CRIMSON}▓▓▓▓▓▓{SHADOW}░░░░{RESET}{CRIMSON}▓▓{SHADOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░{RESET}{EMBER}█▀▄{SHADOW}░{RESET}{EMBER}█▀▀{SHADOW}░{RESET}{EMBER}█▀▄{SHADOW}░{RESET}{EMBER}▀█▀{SHADOW}░░░{RESET}{EMBER}█▀▄{SHADOW}░{RESET}{EMBER}█▀▀{SHADOW}░{RESET}{EMBER}█▀▀{SHADOW}░{RESET}{EMBER}▀█▀{SHADOW}░{RESET}{EMBER}█▀▄{SHADOW}░{RESET}{EMBER}█▀█{SHADOW}░{RESET}{EMBER}█{SHADOW}░░{RESET}{EMBER}█{SHADOW}░{RESET}{EMBER}█▀▀{SHADOW}░{RESET}{EMBER}█▀▄{SHADOW}░░  {RESET}
{SHADOW}  ░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█▀▀{SHADOW}░{RESET}{CRIMSON}█▀▄{SHADOW}░░{RESET}{CRIMSON}█{SHADOW}░░░░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█▀▀{SHADOW}░{RESET}{CRIMSON}▀▀█{SHADOW}░░{RESET}{CRIMSON}█{SHADOW}░░{RESET}{CRIMSON}█▀▄{SHADOW}░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█{SHADOW}░░{RESET}{CRIMSON}█{SHADOW}░{RESET}{CRIMSON}█▀▀{SHADOW}░{RESET}{CRIMSON}█▀▄{SHADOW}░░  {RESET}
{SHADOW}  ░{RESET}{BLOOD}▀▀░{SHADOW}░{RESET}{BLOOD}▀▀▀{SHADOW}░{RESET}{BLOOD}▀▀░{SHADOW}░░{RESET}{BLOOD}▀{SHADOW}░░░░{RESET}{BLOOD}▀▀░{SHADOW}░{RESET}{BLOOD}▀▀▀{SHADOW}░{RESET}{BLOOD}▀▀▀{SHADOW}░░{RESET}{BLOOD}▀{SHADOW}░░{RESET}{BLOOD}▀{SHADOW}░{RESET}{BLOOD}▀{SHADOW}░{RESET}{BLOOD}▀▀▀{SHADOW}░{RESET}{BLOOD}░▀░{SHADOW}░{RESET}{BLOOD}▀▀▀{SHADOW}░{RESET}{BLOOD}▀{SHADOW}░{RESET}{BLOOD}▀{SHADOW}░░  {RESET}
{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░{RESET}{SMOKE}  忍  {ASH}NINJA PROTOCOL ACTIVE{SMOKE}  忍  {SHADOW}░░░░░░░░░░░░░░░░  {RESET}
{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  {RESET}
"""

MOTIVATION_QUOTES = [
    "Move in silence. Strike with precision. 忍",
    "The shadow waits. The shadow wins.",
    "Debt is the chain. Trading is the blade.",
    "Patience is the ninja's greatest weapon.",
    "In darkness, we find clarity.",
    "The market bleeds. We collect.",
    "Silent execution. Inevitable victory.",
    "From the shadows, sovereignty rises.",
    "One cut. One kill. No hesitation.",
    "The debt will fall. The sovereign will rise.",
    "Fear nothing. Execute everything.",
    "Invisible entry. Visible profit.",
]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def type_text(text: str, delay: float = 0.02):
    """Type text with a typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def load_mission() -> dict:
    if MISSION_FILE.exists():
        return json.loads(MISSION_FILE.read_text())
    return {}

def load_brain() -> dict:
    if BRAIN_FILE.exists():
        return json.loads(BRAIN_FILE.read_text())
    return {}

def print_progress_bar(current: float, target: float, width: int = 40):
    """Print a colored progress bar"""
    pct = min(100, max(0, current / target * 100))
    filled = int(width * pct / 100)

    # Color based on progress
    if pct >= 75:
        color = GREEN
    elif pct >= 50:
        color = YELLOW
    elif pct >= 25:
        color = CYAN
    else:
        color = RED

    bar = f"{color}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"
    print(f"  [{bar}] {pct:.1f}%")

def show_mission_briefing():
    """Display mission briefing - SS_III Ninja Style"""
    mission = load_mission()
    brain = load_brain()

    if not mission:
        print(f"\n{CRIMSON}ERROR: Mission file not found{RESET}")
        return

    progress = mission.get("progress", {})
    target = mission.get("objective", {}).get("target_profit", 661.46)
    current_pnl = progress.get("paper_pnl", 0)

    # Get AAVE debt from brain
    aave_debt = brain.get("portfolio", {}).get("aave", {}).get("debt", 661.46)

    print(f"\n{SHADOW}╔{'═' * 58}╗{RESET}")
    print(f"{SHADOW}║{RESET}  {BONE}{BOLD}忍  M I S S I O N   B R I E F I N G  忍{RESET}                 {SHADOW}║{RESET}")
    print(f"{SHADOW}╠{'═' * 58}╣{RESET}")

    print(f"{SHADOW}║{RESET}  {SMOKE}CODENAME:{RESET}     {CRIMSON}{BOLD}DEBT_DESTROYER{RESET}                         {SHADOW}║{RESET}")
    print(f"{SHADOW}║{RESET}  {SMOKE}OBJECTIVE:{RESET}    {ASH}Acquire ${target:,.2f}{RESET}                        {SHADOW}║{RESET}")
    print(f"{SHADOW}║{RESET}  {SMOKE}TARGET:{RESET}       {BLOOD}AAVE Debt (${aave_debt:,.2f}){RESET}                    {SHADOW}║{RESET}")
    status_color = CRIMSON if mission.get('status') == 'active' else SMOKE
    print(f"{SHADOW}║{RESET}  {SMOKE}STATUS:{RESET}       {status_color}{mission.get('status', 'unknown').upper()}{RESET}                                {SHADOW}║{RESET}")

    print(f"{SHADOW}╠{'═' * 58}╣{RESET}")
    print(f"{SHADOW}║{RESET}  {BONE}PROGRESS:{RESET}                                              {SHADOW}║{RESET}")
    print_progress_bar(current_pnl, target)
    print(f"{SHADOW}║{RESET}  {ASH}${current_pnl:,.2f} / ${target:,.2f}{RESET}                                  {SHADOW}║{RESET}")

    print(f"{SHADOW}╠{'═' * 58}╣{RESET}")
    print(f"{SHADOW}║{RESET}  {BONE}COMBAT STATS:{RESET}                                         {SHADOW}║{RESET}")
    print(f"{SHADOW}║{RESET}  {SMOKE}Strikes:{RESET}      {ASH}{progress.get('paper_trades', 0)}{RESET}                                      {SHADOW}║{RESET}")
    print(f"{SHADOW}║{RESET}  {SMOKE}Kills:{RESET}        {CRIMSON}{progress.get('paper_wins', 0)}{RESET}                                      {SHADOW}║{RESET}")
    print(f"{SHADOW}║{RESET}  {SMOKE}Misses:{RESET}       {BLOOD}{progress.get('paper_losses', 0)}{RESET}                                      {SHADOW}║{RESET}")
    win_rate = progress.get('paper_win_rate', 0)
    wr_color = CRIMSON if win_rate >= 60 else ASH if win_rate >= 40 else BLOOD
    print(f"{SHADOW}║{RESET}  {SMOKE}Accuracy:{RESET}     {wr_color}{win_rate:.1f}%{RESET}                                   {SHADOW}║{RESET}")

    print(f"{SHADOW}╠{'═' * 58}╣{RESET}")
    print(f"{SHADOW}║{RESET}  {BONE}MILESTONES:{RESET}                                           {SHADOW}║{RESET}")
    for m in mission.get("milestones", []):
        status = f"{CRIMSON}▓{RESET}" if m.get("reached") else f"{SHADOW}░{RESET}"
        print(f"{SHADOW}║{RESET}  {status} {ASH}{m['pct']}%:{RESET} {SMOKE}${m['target']:,.2f}{RESET}                                   {SHADOW}║{RESET}")

    # Gateway status
    print(f"{SHADOW}╠{'═' * 58}╣{RESET}")
    req = mission.get("objective", {}).get("success_criteria", {})

    profit_met = current_pnl >= req.get("paper_profit", 661.46)
    win_rate_met = win_rate >= req.get("win_rate_min", 60)
    trades_met = progress.get("paper_trades", 0) >= req.get("trades_min", 10)

    if all([profit_met, win_rate_met, trades_met]):
        print(f"{SHADOW}║{RESET}  {EMBER}{BOLD}忍 GATEWAY UNLOCKED - HEAVY ARTILLERY READY 忍{RESET}        {SHADOW}║{RESET}")
        print(f"{SHADOW}║{RESET}  {CRIMSON}   Awaiting Commander approval for live deployment{RESET}    {SHADOW}║{RESET}")
    else:
        print(f"{SHADOW}║{RESET}  {BLOOD}⛩  GATEWAY SEALED{RESET}                                      {SHADOW}║{RESET}")
        check = f"{CRIMSON}▓{RESET}"
        empty = f"{SHADOW}░{RESET}"
        print(f"{SHADOW}║{RESET}  {check if profit_met else empty} {SMOKE}Profit:{RESET} {ASH}${current_pnl:,.2f} / ${req.get('paper_profit', 661.46):,.2f}{RESET}            {SHADOW}║{RESET}")
        print(f"{SHADOW}║{RESET}  {check if win_rate_met else empty} {SMOKE}Accuracy:{RESET} {ASH}{win_rate:.1f}% / {req.get('win_rate_min', 60)}%{RESET}                       {SHADOW}║{RESET}")
        print(f"{SHADOW}║{RESET}  {check if trades_met else empty} {SMOKE}Strikes:{RESET} {ASH}{progress.get('paper_trades', 0)} / {req.get('trades_min', 10)}{RESET}                            {SHADOW}║{RESET}")

    print(f"{SHADOW}╚{'═' * 58}╝{RESET}")

def show_menu():
    """Display main menu - SS_III Ninja Style"""
    print(f"\n{SHADOW}┌{'─' * 44}┐{RESET}")
    print(f"{SHADOW}│{RESET}  {BONE}{BOLD}忍 COMMAND CENTER 忍{RESET}                      {SHADOW}│{RESET}")
    print(f"{SHADOW}├{'─' * 44}┤{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[1]{RESET} {BONE}{BOLD}BEGIN{RESET}    {SMOKE}- Deploy trading agent{RESET}      {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[2]{RESET} {ASH}SCAN{RESET}     {SMOKE}- Single recon scan{RESET}          {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[3]{RESET} {ASH}STATUS{RESET}   {SMOKE}- Mission intel{RESET}              {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[4]{RESET} {ASH}MANUAL{RESET}   {SMOKE}- Log manual strike{RESET}          {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[5]{RESET} {ASH}CLOSE{RESET}    {SMOKE}- Extract from position{RESET}      {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[6]{RESET} {ASH}GATEWAY{RESET}  {SMOKE}- Check unlock status{RESET}        {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {CRIMSON}[7]{RESET} {ASH}SIGNALS{RESET}  {SMOKE}- View intel signals{RESET}         {SHADOW}│{RESET}")
    print(f"{SHADOW}├{'─' * 44}┤{RESET}")
    print(f"{SHADOW}│{RESET}  {BLOOD}[8]{RESET} {SMOKE}PURGE{RESET}    {SHADOW}- Eliminate old data{RESET}         {SHADOW}│{RESET}")
    print(f"{SHADOW}│{RESET}  {BLOOD}[9]{RESET} {SMOKE}AURORA{RESET}   {SHADOW}- Voice activation{RESET}           {SHADOW}│{RESET}")
    print(f"{SHADOW}├{'─' * 44}┤{RESET}")
    print(f"{SHADOW}│{RESET}  {EMBER}[0]{RESET} {BONE}{BOLD}EXIT{RESET}     {SMOKE}- Vanish into shadows{RESET}       {SHADOW}│{RESET}")
    print(f"{SHADOW}└{'─' * 44}┘{RESET}")

def show_purge_menu():
    """Display purge menu and handle cleanup - SS_III Ninja Style"""
    clear_screen()
    print(f"\n{SHADOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")
    print(f"{SHADOW}░{RESET}  {BONE}{BOLD}忍  P U R G E   P R O T O C O L  忍{RESET}                       {SHADOW}░{RESET}")
    print(f"{SHADOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")
    print(f"\n{ASH}  Eliminate traces. Leave no evidence:{RESET}\n")

    # Calculate sizes
    purge_items = get_purge_items()

    for i, item in enumerate(purge_items, 1):
        status = f"{EMBER}▲" if item['size'] > 1000000 else f"{BLOOD}●" if item['size'] > 100000 else f"{SMOKE}○"
        size_str = format_size(item['size'])
        print(f"  {CRIMSON}[{i}]{RESET} {ASH}{item['name']:30s}{RESET} {status}{RESET} {BONE}{size_str:>10s}{RESET}  {SHADOW}{item['count']} files{RESET}")

    print(f"\n  {EMBER}[A]{RESET} {BONE}PURGE ALL{RESET} {SMOKE}(scorched earth){RESET}")
    print(f"  {ASH}[0]{RESET} {SMOKE}Return to shadows{RESET}")

    print(f"\n{SHADOW}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")

    choice = input(f"\n{BONE}Select:{RESET} ").strip().upper()

    if choice == "0":
        return
    elif choice == "A":
        confirm = input(f"{EMBER}Execute scorched earth protocol? (yes/no):{RESET} ").strip().lower()
        if confirm == "yes":
            for item in purge_items:
                if not item.get('essential', False):
                    purge_category(item)
            print(f"\n{BONE}All traces eliminated.{RESET} {CRIMSON}忍{RESET}")
            aurora_speak("Purge complete. All traces eliminated.")
    elif choice.isdigit() and 1 <= int(choice) <= len(purge_items):
        item = purge_items[int(choice) - 1]
        confirm = input(f"{CRIMSON}Eliminate {item['name']}? (y/n):{RESET} ").strip().lower()
        if confirm == "y":
            purge_category(item)
            print(f"\n{ASH}{item['name']} eliminated.{RESET} {SHADOW}忍{RESET}")

    input(f"\n{DIM}Press ENTER to continue...{RESET}")

def get_purge_items():
    """Get list of purgeable items with sizes"""
    items = []

    # 1. Old logs
    log_files = list((BASE_DIR / "logs").glob("**/*.log")) if (BASE_DIR / "logs").exists() else []
    log_size = sum(f.stat().st_size for f in log_files if f.exists())
    items.append({
        'name': 'Log files (.log)',
        'pattern': 'logs/**/*.log',
        'size': log_size,
        'count': len(log_files),
        'files': log_files
    })

    # 2. JSON cache files
    cache_files = list((BASE_DIR / "logs").glob("**/*.json")) if (BASE_DIR / "logs").exists() else []
    cache_size = sum(f.stat().st_size for f in cache_files if f.exists())
    items.append({
        'name': 'Log JSON caches',
        'pattern': 'logs/**/*.json',
        'size': cache_size,
        'count': len(cache_files),
        'files': cache_files
    })

    # 3. __pycache__ directories
    pycache_files = list(BASE_DIR.glob("**/__pycache__/**/*.pyc"))
    pycache_size = sum(f.stat().st_size for f in pycache_files if f.exists())
    items.append({
        'name': 'Python cache (__pycache__)',
        'pattern': '**/__pycache__',
        'size': pycache_size,
        'count': len(pycache_files),
        'files': pycache_files,
        'is_dir': True
    })

    # 4. Old session files (keep last 5)
    session_dir = BASE_DIR / "memory/SESSIONS"
    if session_dir.exists():
        session_files = sorted(session_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        old_sessions = session_files[5:] if len(session_files) > 5 else []
        old_size = sum(f.stat().st_size for f in old_sessions if f.exists())
        items.append({
            'name': 'Old session files (keep 5)',
            'pattern': 'memory/SESSIONS/*.json',
            'size': old_size,
            'count': len(old_sessions),
            'files': old_sessions
        })

    # 5. Temp files
    temp_files = list(BASE_DIR.glob("**/*.tmp")) + list(BASE_DIR.glob("**/tmp_*"))
    temp_size = sum(f.stat().st_size for f in temp_files if f.exists())
    items.append({
        'name': 'Temp files (*.tmp)',
        'pattern': '**/*.tmp',
        'size': temp_size,
        'count': len(temp_files),
        'files': temp_files
    })

    # 6. Old backup files
    backup_files = list(BASE_DIR.glob("**/*.bak")) + list(BASE_DIR.glob("**/*.backup"))
    backup_size = sum(f.stat().st_size for f in backup_files if f.exists())
    items.append({
        'name': 'Backup files (*.bak)',
        'pattern': '**/*.bak',
        'size': backup_size,
        'count': len(backup_files),
        'files': backup_files
    })

    # 7. Closed paper trades (reset mission)
    mission = load_mission()
    closed_trades = [t for t in mission.get('paper_trades', []) if t.get('status') == 'closed']
    items.append({
        'name': 'Closed paper trades',
        'pattern': 'MISSION_RESET',
        'size': len(json.dumps(closed_trades)),
        'count': len(closed_trades),
        'files': [],
        'special': 'reset_closed_trades'
    })

    return items

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def purge_category(item: dict):
    """Purge a category of files"""
    if item.get('special') == 'reset_closed_trades':
        mission = load_mission()
        # Keep only open trades
        mission['paper_trades'] = [t for t in mission.get('paper_trades', []) if t.get('status') == 'open']
        # Don't reset progress - that's mission history
        MISSION_FILE.write_text(json.dumps(mission, indent=2))
        print(f"  {GREEN}Closed trades cleared from mission file{RESET}")
        return

    for f in item.get('files', []):
        try:
            if f.exists():
                if item.get('is_dir'):
                    import shutil
                    shutil.rmtree(f.parent)
                else:
                    f.unlink()
                print(f"  {DIM}Deleted: {f.name}{RESET}")
        except Exception as e:
            print(f"  {RED}Error: {e}{RESET}")

def run_aurora_test():
    """Test Aurora voice"""
    print(f"\n{CYAN}Testing Aurora voice...{RESET}")
    aurora_speak("Debt Destroyer online. Mission 001 active. Ready to execute.", async_mode=False)
    print(f"{GREEN}Aurora voice test complete{RESET}")

def run_agent_watch():
    """Start the paper trading agent in watch mode"""
    print(f"\n{GREEN}Starting Paper Trading Agent...{RESET}")
    print(f"{DIM}Press Ctrl+C to stop{RESET}\n")

    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR / "bin/paper_trading_agent.py"), "--watch"],
            cwd=str(BASE_DIR)
        )
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Agent stopped{RESET}")

def run_single_scan():
    """Run a single scan"""
    print(f"\n{CYAN}Running single scan...{RESET}\n")
    subprocess.run(
        [sys.executable, str(BASE_DIR / "bin/paper_trading_agent.py")],
        cwd=str(BASE_DIR)
    )

def run_status():
    """Show paper trade status"""
    subprocess.run(
        [sys.executable, str(BASE_DIR / "bin/paper_trade.py"), "--status"],
        cwd=str(BASE_DIR)
    )

def run_manual_trade():
    """Log a manual paper trade"""
    print(f"\n{CYAN}Manual Paper Trade Entry{RESET}")
    print(f"{DIM}{'─' * 40}{RESET}")

    symbol = input(f"  Symbol (BTC/ETH/SOL/XRP): ").upper()
    direction = input(f"  Direction (long/short): ").lower()
    entry = input(f"  Entry Price: $")
    stop_loss = input(f"  Stop Loss: $")
    size = input(f"  Position Size: $")

    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR / "bin/paper_trade.py"),
             "--log", symbol, direction, entry, stop_loss, size],
            cwd=str(BASE_DIR)
        )
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def run_close_trade():
    """Close an open paper trade"""
    print(f"\n{CYAN}Close Paper Trade{RESET}")
    print(f"{DIM}{'─' * 40}{RESET}")

    trade_id = input(f"  Trade ID (e.g., PT001): ").upper()
    exit_price = input(f"  Exit Price: $")

    try:
        subprocess.run(
            [sys.executable, str(BASE_DIR / "bin/paper_trade.py"),
             "--close", trade_id, exit_price],
            cwd=str(BASE_DIR)
        )
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def run_gateway_check():
    """Check gateway unlock status"""
    subprocess.run(
        [sys.executable, str(BASE_DIR / "bin/paper_trade.py"), "--gateway"],
        cwd=str(BASE_DIR)
    )

def run_smart_signals():
    """Show current smart signals"""
    subprocess.run(
        [sys.executable, str(BASE_DIR / "bin/smart_signals.py")],
        cwd=str(BASE_DIR)
    )

def intro_sequence():
    """Play intro sequence - SS_III Ninja Style"""
    clear_screen()

    # Logo reveal with shadow effect
    print(LOGO)
    time.sleep(0.3)

    # Mission date - ninja style
    print(f"{SHADOW}  ┌{'─' * 56}┐{RESET}")
    print(f"{SHADOW}  │{RESET}  {SMOKE}DATE:{RESET}    {ASH}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}                     {SHADOW}│{RESET}")
    print(f"{SHADOW}  │{RESET}  {SMOKE}MISSION:{RESET} {CRIMSON}001 - DEBT_DESTROYER{RESET}                        {SHADOW}│{RESET}")
    print(f"{SHADOW}  │{RESET}  {SMOKE}PHASE:{RESET}   {BLOOD}PAPER TRADING{RESET}                               {SHADOW}│{RESET}")
    print(f"{SHADOW}  └{'─' * 56}┘{RESET}")

    # Motivation quote - ninja wisdom
    import random
    quote = random.choice(MOTIVATION_QUOTES)
    print(f"\n{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")
    print(f"{SHADOW}  ░{RESET}  {BONE}\"{quote}\"{RESET}")
    print(f"{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")

    # Aurora voice intro
    mission = load_mission()
    progress = mission.get("progress", {})
    current_pnl = progress.get("paper_pnl", 0)

    if current_pnl > 0:
        aurora_speak(f"Shadow protocol active. Paper profit at {current_pnl:.0f} dollars. Continuing the hunt.")
    else:
        aurora_speak("Shadow protocol initialized. Mission 001 active. The hunt begins.")

    time.sleep(0.5)

    # Show mission briefing
    show_mission_briefing()

    input(f"\n{SHADOW}  ░ {ASH}Press ENTER to infiltrate...{RESET} ")

def main():
    """Main entry point"""

    # Intro sequence
    intro_sequence()

    # Main loop
    while True:
        clear_screen()

        # Compact header - SS_III style
        print(f"\n{SHADOW}░{RESET} {CRIMSON}{BOLD}忍 DEBT DESTROYER{RESET} {SHADOW}│{RESET} {BONE}MISSION 001{RESET} {SHADOW}░{RESET}")

        # Quick status - SS_III style
        mission = load_mission()
        progress = mission.get("progress", {})
        current_pnl = progress.get("paper_pnl", 0)
        target = 661.46
        pct = (current_pnl / target) * 100

        # Progress color: EMBER (high) -> CRIMSON (mid) -> BLOOD (low)
        color = BONE if pct >= 75 else ASH if pct >= 50 else CRIMSON if pct >= 25 else BLOOD
        bar_filled = int(20 * pct / 100)
        bar_empty = 20 - bar_filled
        progress_bar = f"{CRIMSON}{'█' * bar_filled}{SHADOW}{'░' * bar_empty}{RESET}"
        print(f"{SHADOW}░{RESET} [{progress_bar}] {color}${current_pnl:,.2f}{RESET} / {BONE}${target:,.2f}{RESET} {SHADOW}({pct:.1f}%){RESET}")

        show_menu()

        choice = input(f"\n{BOLD}Command:{RESET} ").strip()

        if choice == "1":
            aurora_speak("Initiating paper trading agent. Monitoring markets.")
            run_agent_watch()
        elif choice == "2":
            run_single_scan()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "3":
            run_status()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "4":
            run_manual_trade()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "5":
            run_close_trade()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "6":
            run_gateway_check()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "7":
            run_smart_signals()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "8":
            show_purge_menu()
        elif choice == "9":
            run_aurora_test()
            input(f"\n{DIM}Press ENTER to continue...{RESET}")
        elif choice == "0":
            clear_screen()
            # SS_III Exit Sequence - Ninja Vanish
            print(f"\n{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")
            print(f"{SHADOW}  ░{RESET}{CRIMSON}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{SHADOW}░{RESET}")
            print(f"{SHADOW}  ░{RESET}  {BONE}{BOLD}忍  THE SHADOW RETREATS  忍{RESET}                          {SHADOW}░{RESET}")
            print(f"{SHADOW}  ░{RESET}{BLOOD}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{SHADOW}░{RESET}")
            print(f"{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}")
            print(f"\n{SHADOW}  ┌{'─' * 54}┐{RESET}")
            print(f"{SHADOW}  │{RESET}  {ASH}\"The ninja vanishes. The debt remembers.\"{RESET}            {SHADOW}│{RESET}")
            print(f"{SHADOW}  │{RESET}                                                        {SHADOW}│{RESET}")
            print(f"{SHADOW}  │{RESET}  {SMOKE}Mission 001 paused. Re-engage when ready.{RESET}           {SHADOW}│{RESET}")
            print(f"{SHADOW}  │{RESET}  {CRIMSON}Every shadow leaves a mark.{RESET}                         {SHADOW}│{RESET}")
            print(f"{SHADOW}  └{'─' * 54}┘{RESET}")
            print(f"\n{SHADOW}  ░{RESET} {EMBER}忍{RESET} {BONE}SOVEREIGN SHADOW III - VANISHING{RESET} {EMBER}忍{RESET} {SHADOW}░{RESET}")
            print(f"{SHADOW}  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RESET}\n")
            aurora_speak("Shadow protocol suspended. Stay sovereign, Commander. The hunt continues.")
            time.sleep(0.5)
            sys.exit(0)
        else:
            print(f"{RED}Invalid command{RESET}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()

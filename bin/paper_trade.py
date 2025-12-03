#!/usr/bin/env python3
"""
PAPER TRADE LOGGER - Mission 001: DEBT_DESTROYER
Logs paper trades and tracks progress toward $661.46 target

Usage:
    python bin/paper_trade.py --log BTC long 97000 99000 50    # Log entry
    python bin/paper_trade.py --close T001 98500              # Close trade
    python bin/paper_trade.py --status                         # Mission status
    python bin/paper_trade.py --gateway                        # Check gateway unlock
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).parent.parent
MISSION_FILE = BASE_DIR / "data/missions/mission_001_aave_debt.json"
BRAIN_FILE = BASE_DIR / "BRAIN.json"

def load_mission():
    return json.loads(MISSION_FILE.read_text())

def save_mission(mission):
    MISSION_FILE.write_text(json.dumps(mission, indent=2))

def load_brain():
    return json.loads(BRAIN_FILE.read_text())

def save_brain(brain):
    BRAIN_FILE.write_text(json.dumps(brain, indent=2))

def log_paper_trade(symbol: str, direction: str, entry: float, stop_loss: float, position_size: float):
    """Log a new paper trade entry"""
    mission = load_mission()

    trade_id = f"PT{len(mission['paper_trades']) + 1:03d}"

    trade = {
        "id": trade_id,
        "symbol": symbol.upper(),
        "direction": direction.lower(),
        "entry_price": entry,
        "stop_loss": stop_loss,
        "position_size": position_size,
        "position_value": position_size,  # In USD
        "status": "open",
        "entry_time": datetime.now().isoformat(),
        "exit_price": None,
        "exit_time": None,
        "pnl": None,
        "pnl_pct": None
    }

    # Calculate risk
    if direction == "long":
        risk_pct = abs(entry - stop_loss) / entry * 100
    else:
        risk_pct = abs(stop_loss - entry) / entry * 100

    trade["risk_pct"] = round(risk_pct, 2)

    mission["paper_trades"].append(trade)
    save_mission(mission)

    print(f"{'=' * 60}")
    print(f"PAPER TRADE LOGGED: {trade_id}")
    print(f"{'=' * 60}")
    print(f"Symbol:    {symbol.upper()}")
    print(f"Direction: {direction.upper()}")
    print(f"Entry:     ${entry:,.2f}")
    print(f"Stop Loss: ${stop_loss:,.2f}")
    print(f"Size:      ${position_size:,.2f}")
    print(f"Risk:      {risk_pct:.1f}%")
    print(f"{'=' * 60}")

    return trade_id

def close_paper_trade(trade_id: str, exit_price: float):
    """Close a paper trade and calculate P&L"""
    mission = load_mission()

    trade = None
    for t in mission["paper_trades"]:
        if t["id"] == trade_id.upper() and t["status"] == "open":
            trade = t
            break

    if not trade:
        print(f"Trade {trade_id} not found or already closed")
        return

    # Calculate P&L
    entry = trade["entry_price"]
    size = trade["position_size"]

    if trade["direction"] == "long":
        pnl_pct = (exit_price - entry) / entry * 100
    else:
        pnl_pct = (entry - exit_price) / entry * 100

    pnl = size * (pnl_pct / 100)

    # Update trade
    trade["exit_price"] = exit_price
    trade["exit_time"] = datetime.now().isoformat()
    trade["pnl"] = round(pnl, 2)
    trade["pnl_pct"] = round(pnl_pct, 2)
    trade["status"] = "closed"

    # Update mission progress
    progress = mission["progress"]
    progress["paper_trades"] += 1
    progress["paper_pnl"] = round(progress["paper_pnl"] + pnl, 2)

    if pnl > 0:
        progress["paper_wins"] += 1
        if progress["best_trade"] is None or pnl > progress["best_trade"]:
            progress["best_trade"] = pnl
        # Update avg win
        wins = [t["pnl"] for t in mission["paper_trades"] if t["status"] == "closed" and t["pnl"] > 0]
        progress["avg_win"] = round(sum(wins) / len(wins), 2) if wins else 0
    else:
        progress["paper_losses"] += 1
        if progress["worst_trade"] is None or pnl < progress["worst_trade"]:
            progress["worst_trade"] = pnl
        # Update avg loss
        losses = [t["pnl"] for t in mission["paper_trades"] if t["status"] == "closed" and t["pnl"] < 0]
        progress["avg_loss"] = round(sum(losses) / len(losses), 2) if losses else 0

    # Calculate win rate
    if progress["paper_trades"] > 0:
        progress["paper_win_rate"] = round(progress["paper_wins"] / progress["paper_trades"] * 100, 1)

    save_mission(mission)

    # Update BRAIN.json
    brain = load_brain()
    brain["active_mission"]["current_profit"] = progress["paper_pnl"]
    brain["active_mission"]["progress_pct"] = round(progress["paper_pnl"] / mission["objective"]["target_profit"] * 100, 1)
    save_brain(brain)

    # Print result
    emoji = "" if pnl > 0 else ""
    print(f"{'=' * 60}")
    print(f"{emoji} TRADE CLOSED: {trade_id}")
    print(f"{'=' * 60}")
    print(f"Symbol:     {trade['symbol']}")
    print(f"Direction:  {trade['direction'].upper()}")
    print(f"Entry:      ${entry:,.2f}")
    print(f"Exit:       ${exit_price:,.2f}")
    print(f"P&L:        ${pnl:+,.2f} ({pnl_pct:+.1f}%)")
    print(f"{'=' * 60}")
    print(f"MISSION PROGRESS:")
    print(f"  Total Paper P&L: ${progress['paper_pnl']:+,.2f}")
    print(f"  Target:          ${mission['objective']['target_profit']:,.2f}")
    print(f"  Progress:        {progress['paper_pnl']/mission['objective']['target_profit']*100:.1f}%")
    print(f"  Win Rate:        {progress['paper_win_rate']:.1f}%")
    print(f"{'=' * 60}")

    return pnl

def show_status():
    """Show current mission status"""
    mission = load_mission()
    progress = mission["progress"]
    target = mission["objective"]["target_profit"]

    print(f"{'=' * 60}")
    print(f"MISSION 001: DEBT_DESTROYER")
    print(f"{'=' * 60}")
    print(f"Objective: Paper trade to ${target:,.2f}")
    print(f"Phase:     {mission['phase'].upper()}")
    print(f"{'=' * 60}")
    print(f"PROGRESS:")
    print(f"  Paper Trades: {progress['paper_trades']}")
    print(f"  Wins/Losses:  {progress['paper_wins']}/{progress['paper_losses']}")
    print(f"  Win Rate:     {progress['paper_win_rate']:.1f}%")
    print(f"  Paper P&L:    ${progress['paper_pnl']:+,.2f}")
    print(f"{'=' * 60}")

    # Progress bar
    pct = min(100, max(0, progress['paper_pnl'] / target * 100))
    bar_len = 40
    filled = int(bar_len * pct / 100)
    bar = '' * filled + '' * (bar_len - filled)
    print(f"[{bar}] {pct:.1f}%")
    print(f"{'=' * 60}")

    # Milestones
    print("MILESTONES:")
    for m in mission["milestones"]:
        status = "" if m["reached"] else ""
        print(f"  {status} {m['pct']}%: ${m['target']:,.2f}")

    print(f"{'=' * 60}")

    # Open trades
    open_trades = [t for t in mission["paper_trades"] if t["status"] == "open"]
    if open_trades:
        print("OPEN TRADES:")
        for t in open_trades:
            print(f"  {t['id']}: {t['symbol']} {t['direction'].upper()} @ ${t['entry_price']:,.2f}")

    print(f"{'=' * 60}")

def check_gateway():
    """Check if gateway to automation is unlocked"""
    mission = load_mission()
    progress = mission["progress"]
    req = mission["objective"]["success_criteria"]

    print(f"{'=' * 60}")
    print(f"GATEWAY CHECK: AUTOMATION UNLOCK STATUS")
    print(f"{'=' * 60}")

    checks = []

    # Check 1: Profit target
    profit_met = progress["paper_pnl"] >= req["paper_profit"]
    checks.append(profit_met)
    emoji = "" if profit_met else ""
    print(f"{emoji} Paper Profit: ${progress['paper_pnl']:,.2f} / ${req['paper_profit']:,.2f}")

    # Check 2: Win rate
    win_rate_met = progress["paper_win_rate"] >= req["win_rate_min"]
    checks.append(win_rate_met)
    emoji = "" if win_rate_met else ""
    print(f"{emoji} Win Rate:     {progress['paper_win_rate']:.1f}% / {req['win_rate_min']}%")

    # Check 3: Min trades
    trades_met = progress["paper_trades"] >= req["trades_min"]
    checks.append(trades_met)
    emoji = "" if trades_met else ""
    print(f"{emoji} Total Trades: {progress['paper_trades']} / {req['trades_min']}")

    print(f"{'=' * 60}")

    if all(checks):
        print(" GATEWAY UNLOCKED!")
        print("Heavy artillery ready for deployment:")
        print("  - LIVE_TRADING_ENABLED")
        print("  - AUTO_SIGNAL_EXECUTION")
        print("  - 24/7_SWARM_OPERATIONS")
        print("  - PROFIT_SIPHON_TO_COMMANDER")
        print("")
        print("Awaiting COMMANDER approval to proceed.")
    else:
        remaining = req["paper_profit"] - progress["paper_pnl"]
        print(f" GATEWAY LOCKED")
        print(f"Remaining to unlock: ${remaining:,.2f} paper profit")
        if progress["paper_trades"] < req["trades_min"]:
            print(f"Need {req['trades_min'] - progress['paper_trades']} more trades")
        if progress["paper_win_rate"] < req["win_rate_min"]:
            print(f"Win rate needs +{req['win_rate_min'] - progress['paper_win_rate']:.1f}%")

    print(f"{'=' * 60}")

def main():
    parser = argparse.ArgumentParser(description="Paper Trade Logger for Mission 001")
    parser.add_argument("--log", nargs=5, metavar=("SYMBOL", "DIR", "ENTRY", "SL", "SIZE"),
                       help="Log new trade: SYMBOL long/short ENTRY STOP_LOSS SIZE")
    parser.add_argument("--close", nargs=2, metavar=("ID", "PRICE"),
                       help="Close trade: TRADE_ID EXIT_PRICE")
    parser.add_argument("--status", action="store_true", help="Show mission status")
    parser.add_argument("--gateway", action="store_true", help="Check automation gateway")

    args = parser.parse_args()

    if args.log:
        symbol, direction, entry, stop_loss, size = args.log
        log_paper_trade(symbol, direction, float(entry), float(stop_loss), float(size))
    elif args.close:
        trade_id, exit_price = args.close
        close_paper_trade(trade_id, float(exit_price))
    elif args.status:
        show_status()
    elif args.gateway:
        check_gateway()
    else:
        show_status()

if __name__ == "__main__":
    main()

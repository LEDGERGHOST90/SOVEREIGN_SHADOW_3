#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Paper Trade Tracker
Local paper trading system (no external API calls)

Features:
- Manual trade entry
- P&L tracking
- JSON export/import for laptop sync
- December 2025 campaign rules

Usage:
    python scripts/paper_trade_tracker.py --status          # Show status
    python scripts/paper_trade_tracker.py --add BTC 95000 50  # Add trade: symbol, entry, size_usd
    python scripts/paper_trade_tracker.py --close 1 96000     # Close trade #1 at price
    python scripts/paper_trade_tracker.py --update BTC 96500  # Update current price
    python scripts/paper_trade_tracker.py --sync trades.json  # Import from laptop export
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

PROJECT_ROOT = Path(__file__).parent.parent
PAPER_TRADES_FILE = PROJECT_ROOT / "memory" / "paper_trades.json"

# December 2025 Campaign Rules
DECEMBER_RULES = {
    "starting_capital": 260.00,
    "max_position_usd": 50,
    "stop_loss_pct": 3,
    "take_profit_pct": 5,
    "max_concurrent_positions": 3,
    "target_win_rate": 60
}


def load_trades() -> Dict:
    """Load paper trades from file"""
    if PAPER_TRADES_FILE.exists():
        return json.loads(PAPER_TRADES_FILE.read_text())
    return create_new_campaign()


def save_trades(data: Dict):
    """Save paper trades to file"""
    PAPER_TRADES_FILE.parent.mkdir(exist_ok=True)
    PAPER_TRADES_FILE.write_text(json.dumps(data, indent=2))


def create_new_campaign() -> Dict:
    """Create new paper trading campaign"""
    return {
        "campaign": "December 2025 - Week 1 Paper Trading",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": "2025-12-07",
        "mode": "PAPER",
        "starting_capital": DECEMBER_RULES["starting_capital"],
        "current_capital": DECEMBER_RULES["starting_capital"],
        "rules": DECEMBER_RULES,
        "summary": {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "best_trade": None,
            "worst_trade": None
        },
        "trades": [],
        "signals_received": [],
        "notes": "Week 1 objective: Test signal generation, validate strategy before live trading"
    }


def add_trade(symbol: str, entry_price: float, position_size: float) -> Dict:
    """Add a new paper trade"""
    data = load_trades()

    # Check rules
    open_trades = [t for t in data["trades"] if t["status"] == "OPEN"]
    if len(open_trades) >= DECEMBER_RULES["max_concurrent_positions"]:
        print(f"Cannot add trade: Max {DECEMBER_RULES['max_concurrent_positions']} concurrent positions")
        return data

    if position_size > DECEMBER_RULES["max_position_usd"]:
        print(f"Warning: Position ${position_size} exceeds max ${DECEMBER_RULES['max_position_usd']}")
        position_size = DECEMBER_RULES["max_position_usd"]

    # Calculate stops
    stop_loss = entry_price * (1 - DECEMBER_RULES["stop_loss_pct"] / 100)
    take_profit = entry_price * (1 + DECEMBER_RULES["take_profit_pct"] / 100)
    quantity = position_size / entry_price

    trade = {
        "id": len(data["trades"]) + 1,
        "symbol": symbol.upper(),
        "side": "LONG",
        "entry_price": entry_price,
        "current_price": entry_price,
        "quantity": quantity,
        "position_size_usd": position_size,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "unrealized_pnl": 0,
        "unrealized_pnl_pct": 0,
        "status": "OPEN",
        "entry_time": datetime.now().isoformat(),
        "exit_time": None,
        "exit_price": None,
        "realized_pnl": None,
        "exit_reason": None
    }

    data["trades"].append(trade)
    data["summary"]["total_trades"] += 1
    save_trades(data)

    print(f"\n Trade #{trade['id']} OPENED")
    print(f"   Symbol: {trade['symbol']}")
    print(f"   Entry: ${entry_price:,.4f}")
    print(f"   Size: ${position_size:.2f} ({quantity:.6f} {symbol})")
    print(f"   Stop Loss: ${stop_loss:,.4f} (-{DECEMBER_RULES['stop_loss_pct']}%)")
    print(f"   Take Profit: ${take_profit:,.4f} (+{DECEMBER_RULES['take_profit_pct']}%)")

    return data


def close_trade(trade_id: int, exit_price: float, reason: str = "manual") -> Dict:
    """Close a paper trade"""
    data = load_trades()

    for trade in data["trades"]:
        if trade["id"] == trade_id and trade["status"] == "OPEN":
            trade["exit_price"] = exit_price
            trade["exit_time"] = datetime.now().isoformat()
            trade["exit_reason"] = reason

            # Calculate P&L
            pnl = (exit_price - trade["entry_price"]) * trade["quantity"]
            pnl_pct = ((exit_price / trade["entry_price"]) - 1) * 100

            trade["realized_pnl"] = round(pnl, 2)
            trade["status"] = "CLOSED"

            # Update summary
            data["summary"]["total_pnl"] += pnl
            data["current_capital"] += pnl

            if pnl > 0:
                data["summary"]["wins"] += 1
                if data["summary"]["best_trade"] is None or pnl > data["summary"]["best_trade"]:
                    data["summary"]["best_trade"] = round(pnl, 2)
            else:
                data["summary"]["losses"] += 1
                if data["summary"]["worst_trade"] is None or pnl < data["summary"]["worst_trade"]:
                    data["summary"]["worst_trade"] = round(pnl, 2)

            # Update win rate
            total_closed = data["summary"]["wins"] + data["summary"]["losses"]
            if total_closed > 0:
                data["summary"]["win_rate"] = round((data["summary"]["wins"] / total_closed) * 100, 1)

            save_trades(data)

            emoji = "" if pnl >= 0 else ""
            print(f"\n{emoji} Trade #{trade_id} CLOSED")
            print(f"   Symbol: {trade['symbol']}")
            print(f"   Entry: ${trade['entry_price']:,.4f}")
            print(f"   Exit: ${exit_price:,.4f}")
            print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
            print(f"   Reason: {reason}")

            return data

    print(f"Trade #{trade_id} not found or already closed")
    return data


def update_price(symbol: str, current_price: float) -> Dict:
    """Update current price for a symbol"""
    data = load_trades()
    updated = 0

    for trade in data["trades"]:
        if trade["symbol"] == symbol.upper() and trade["status"] == "OPEN":
            trade["current_price"] = current_price
            trade["unrealized_pnl"] = round((current_price - trade["entry_price"]) * trade["quantity"], 2)
            trade["unrealized_pnl_pct"] = round(((current_price / trade["entry_price"]) - 1) * 100, 2)
            updated += 1

            # Check stop loss / take profit
            if current_price <= trade["stop_loss"]:
                print(f" STOP LOSS HIT for {trade['symbol']}!")
            elif current_price >= trade["take_profit"]:
                print(f" TAKE PROFIT HIT for {trade['symbol']}!")

    if updated:
        save_trades(data)
        print(f"Updated {updated} {symbol} position(s) to ${current_price:,.4f}")
    else:
        print(f"No open positions for {symbol}")

    return data


def sync_from_file(filepath: str) -> Dict:
    """Import trades from laptop export"""
    try:
        import_data = json.loads(Path(filepath).read_text())
        data = load_trades()

        imported = 0
        for trade in import_data.get("trades", []):
            # Check if trade already exists (by entry_time)
            existing = [t for t in data["trades"] if t.get("entry_time") == trade.get("entry_time")]
            if not existing:
                trade["id"] = len(data["trades"]) + 1
                data["trades"].append(trade)
                imported += 1

        # Recalculate summary
        data["summary"]["total_trades"] = len(data["trades"])
        closed = [t for t in data["trades"] if t["status"] == "CLOSED"]
        data["summary"]["wins"] = len([t for t in closed if t.get("realized_pnl", 0) > 0])
        data["summary"]["losses"] = len([t for t in closed if t.get("realized_pnl", 0) <= 0])
        data["summary"]["total_pnl"] = sum(t.get("realized_pnl", 0) for t in closed)

        if closed:
            data["summary"]["win_rate"] = round((data["summary"]["wins"] / len(closed)) * 100, 1)

        save_trades(data)
        print(f"Imported {imported} trades from {filepath}")
        return data

    except Exception as e:
        print(f"Error importing: {e}")
        return load_trades()


def show_status():
    """Display paper trading status"""
    data = load_trades()

    print("\n" + "="*60)
    print("SOVEREIGN SHADOW - Paper Trade Tracker")
    print("="*60)

    print(f"\n[CAMPAIGN]")
    print(f"  {data['campaign']}")
    print(f"  Period: {data['start_date']} to {data['end_date']}")
    print(f"  Mode: {data['mode']}")

    print(f"\n[CAPITAL]")
    print(f"  Starting: ${data['starting_capital']:.2f}")
    print(f"  Current:  ${data['current_capital']:.2f}")
    pnl = data['current_capital'] - data['starting_capital']
    pnl_pct = (pnl / data['starting_capital']) * 100
    print(f"  P&L:      ${pnl:+.2f} ({pnl_pct:+.1f}%)")

    print(f"\n[RULES]")
    print(f"  Max Position: ${DECEMBER_RULES['max_position_usd']}")
    print(f"  Stop Loss: {DECEMBER_RULES['stop_loss_pct']}%")
    print(f"  Take Profit: {DECEMBER_RULES['take_profit_pct']}%")
    print(f"  Max Concurrent: {DECEMBER_RULES['max_concurrent_positions']}")

    print(f"\n[STATS]")
    s = data['summary']
    print(f"  Total Trades: {s['total_trades']}")
    print(f"  Wins: {s['wins']} | Losses: {s['losses']}")
    print(f"  Win Rate: {s['win_rate']}% (target: {DECEMBER_RULES['target_win_rate']}%)")
    print(f"  Total P&L: ${s['total_pnl']:+.2f}")
    print(f"  Best Trade: ${s['best_trade'] or 0:+.2f}")
    print(f"  Worst Trade: ${s['worst_trade'] or 0:+.2f}")

    # Open positions
    open_trades = [t for t in data["trades"] if t["status"] == "OPEN"]
    print(f"\n[OPEN POSITIONS] ({len(open_trades)}/{DECEMBER_RULES['max_concurrent_positions']})")
    if open_trades:
        for t in open_trades:
            emoji = "" if t['unrealized_pnl'] >= 0 else ""
            print(f"  {emoji} #{t['id']} {t['symbol']}: ${t['position_size_usd']:.2f} @ ${t['entry_price']:,.4f}")
            print(f"      Current: ${t['current_price']:,.4f} | P&L: ${t['unrealized_pnl']:+.2f} ({t['unrealized_pnl_pct']:+.1f}%)")
            print(f"      SL: ${t['stop_loss']:,.4f} | TP: ${t['take_profit']:,.4f}")
    else:
        print("  No open positions")

    # Recent closed trades
    closed_trades = [t for t in data["trades"] if t["status"] == "CLOSED"][-5:]
    if closed_trades:
        print(f"\n[RECENT CLOSED]")
        for t in closed_trades:
            emoji = "" if t['realized_pnl'] >= 0 else ""
            print(f"  {emoji} #{t['id']} {t['symbol']}: ${t['realized_pnl']:+.2f} ({t['exit_reason']})")

    print("\n" + "="*60)

    # Goal check
    if s['win_rate'] >= DECEMBER_RULES['target_win_rate'] and s['total_trades'] >= 5:
        print(" GOAL MET: Ready for live trading!")
    elif s['total_trades'] < 5:
        print(f" Need {5 - s['total_trades']} more trades before evaluating")
    else:
        print(f" Win rate {s['win_rate']}% below target {DECEMBER_RULES['target_win_rate']}%")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Paper Trade Tracker")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--add", nargs=3, metavar=("SYMBOL", "PRICE", "SIZE"), help="Add trade")
    parser.add_argument("--close", nargs=2, metavar=("ID", "PRICE"), help="Close trade")
    parser.add_argument("--update", nargs=2, metavar=("SYMBOL", "PRICE"), help="Update price")
    parser.add_argument("--sync", type=str, metavar="FILE", help="Import from file")
    parser.add_argument("--reset", action="store_true", help="Reset campaign")

    args = parser.parse_args()

    if args.add:
        symbol, price, size = args.add
        add_trade(symbol, float(price), float(size))
    elif args.close:
        trade_id, price = args.close
        close_trade(int(trade_id), float(price))
    elif args.update:
        symbol, price = args.update
        update_price(symbol, float(price))
    elif args.sync:
        sync_from_file(args.sync)
    elif args.reset:
        save_trades(create_new_campaign())
        print("Campaign reset!")
    else:
        show_status()


if __name__ == "__main__":
    main()

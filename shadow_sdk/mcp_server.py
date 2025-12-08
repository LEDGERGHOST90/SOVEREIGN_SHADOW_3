#!/usr/bin/env python3
"""
忍 Shadow SDK - MCP Server (SS_III)
Exposes full SOVEREIGN_SHADOW_3 functionality through Model Context Protocol

Tools:
  - mission_status: Get Mission 001 progress and stats
  - portfolio_balances: Get live portfolio from BRAIN.json
  - open_positions: View open paper trades
  - market_scan: Get smart signals and Fear & Greed
  - gateway_check: Check if gateway is unlocked
  - log_paper_trade: Log a new paper trade
  - close_paper_trade: Close an existing paper trade
  - my_capital: Legacy capital breakdown
  - can_i_trade: Check if trade amount is safe
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
import os
from pathlib import Path
from datetime import datetime

# Add SDK to path
sys.path.insert(0, os.path.dirname(__file__))
BASE_DIR = Path(__file__).parent.parent

# File paths
BRAIN_FILE = BASE_DIR / "BRAIN.json"
MISSION_FILE = BASE_DIR / "data/missions/mission_001_aave_debt.json"
SIGNALS_FILE = BASE_DIR / "logs/smart_signals.json"

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


# Helper functions
def load_brain() -> dict:
    """Load BRAIN.json"""
    if BRAIN_FILE.exists():
        return json.loads(BRAIN_FILE.read_text())
    return {}

def load_mission() -> dict:
    """Load mission file"""
    if MISSION_FILE.exists():
        return json.loads(MISSION_FILE.read_text())
    return {}

def save_mission(data: dict):
    """Save mission file"""
    MISSION_FILE.write_text(json.dumps(data, indent=2))

def load_signals() -> dict:
    """Load smart signals"""
    if SIGNALS_FILE.exists():
        return json.loads(SIGNALS_FILE.read_text())
    return {"signals": []}


# Initialize MCP server
app = Server("shadow-sdk")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available Shadow SDK tools"""
    return [
        # ===== MISSION 001 TOOLS =====
        types.Tool(
            name="mission_status",
            description="忍 Get Mission 001 DEBT_DESTROYER status - progress, trades, milestones, gateway status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="portfolio_balances",
            description="忍 Get current portfolio balances from BRAIN.json - Ledger, exchanges, AAVE debt, net worth",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="open_positions",
            description="忍 View all open paper trade positions with entry prices, SL/TP, and current P&L",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="market_scan",
            description="忍 Get smart signals - Fear & Greed index, trading signals, market recommendation",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="gateway_check",
            description="忍 Check if gateway is unlocked for live trading - requires profit target, win rate, and trade count",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="log_paper_trade",
            description="忍 Log a new paper trade entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading symbol (BTC, ETH, SOL, XRP)",
                    },
                    "direction": {
                        "type": "string",
                        "description": "Trade direction (long or short)",
                    },
                    "entry_price": {
                        "type": "number",
                        "description": "Entry price in USD",
                    },
                    "stop_loss": {
                        "type": "number",
                        "description": "Stop loss price in USD",
                    },
                    "position_size": {
                        "type": "number",
                        "description": "Position size in USD (default $50)",
                        "default": 50,
                    },
                },
                "required": ["symbol", "direction", "entry_price", "stop_loss"],
            },
        ),
        types.Tool(
            name="close_paper_trade",
            description="忍 Close an existing paper trade",
            inputSchema={
                "type": "object",
                "properties": {
                    "trade_id": {
                        "type": "string",
                        "description": "Trade ID (e.g., PT001)",
                    },
                    "exit_price": {
                        "type": "number",
                        "description": "Exit price in USD",
                    },
                },
                "required": ["trade_id", "exit_price"],
            },
        ),
        # ===== LEGACY TOOLS =====
        types.Tool(
            name="my_capital",
            description="Show total capital breakdown (Ledger + exchanges)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="can_i_trade",
            description="Check if I can safely trade this amount based on risk limits",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Trade amount in USD",
                    },
                },
                "required": ["amount"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    """Handle tool calls"""

    # ===== MISSION STATUS =====
    if name == "mission_status":
        mission = load_mission()
        progress = mission.get("progress", {})
        objective = mission.get("objective", {})
        milestones = mission.get("milestones", [])

        target = objective.get("target_profit", 661.46)
        current = progress.get("paper_pnl", 0)

        # Check gateway
        req = objective.get("success_criteria", {})
        profit_met = current >= req.get("paper_profit", 661.46)
        win_rate_met = progress.get("paper_win_rate", 0) >= req.get("win_rate_min", 60)
        trades_met = progress.get("paper_trades", 0) >= req.get("trades_min", 10)
        gateway = "🚀 UNLOCKED" if all([profit_met, win_rate_met, trades_met]) else "⛩ SEALED"

        result = {
            "忍 MISSION 001": "DEBT_DESTROYER",
            "status": mission.get("status", "active"),
            "phase": mission.get("phase", "paper_trading"),
            "target_profit": f"${target:,.2f}",
            "current_profit": f"${current:,.2f}",
            "progress_pct": f"{(current/target*100):.1f}%",
            "trades": progress.get("paper_trades", 0),
            "wins": progress.get("paper_wins", 0),
            "losses": progress.get("paper_losses", 0),
            "win_rate": f"{progress.get('paper_win_rate', 0):.1f}%",
            "gateway": gateway,
            "milestones": [
                f"{'✅' if m['reached'] else '⬜'} {m['pct']}%: ${m['target']:,.2f}"
                for m in milestones
            ]
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== PORTFOLIO BALANCES =====
    elif name == "portfolio_balances":
        brain = load_brain()
        portfolio = brain.get("portfolio", {})

        result = {
            "忍 PORTFOLIO STATUS": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "net_worth": f"${portfolio.get('net_worth', 0):,.2f}",
            "total_assets": f"${portfolio.get('ledger_total', 0) + portfolio.get('exchange_total', 0):,.2f}",
            "total_debt": f"${portfolio.get('aave_debt', 0):,.2f}",
            "ledger": portfolio.get("ledger", {}),
            "exchanges": portfolio.get("exchanges", {}),
            "aave": portfolio.get("aave", {}),
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== OPEN POSITIONS =====
    elif name == "open_positions":
        mission = load_mission()
        open_trades = [t for t in mission.get("paper_trades", []) if t.get("status") == "open"]

        if not open_trades:
            result = {"忍 OPEN POSITIONS": "None - Ready to strike"}
        else:
            result = {
                "忍 OPEN POSITIONS": len(open_trades),
                "positions": [
                    {
                        "id": t["id"],
                        "symbol": t["symbol"],
                        "direction": t["direction"],
                        "entry": f"${t['entry_price']:,.2f}",
                        "stop_loss": f"${t['stop_loss']:,.2f}",
                        "take_profit": f"${t.get('take_profit', 0):,.2f}",
                        "size": f"${t['position_size']}",
                        "entry_time": t["entry_time"]
                    }
                    for t in open_trades
                ]
            }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== MARKET SCAN =====
    elif name == "market_scan":
        signals_data = load_signals()
        market_state = signals_data.get("market_state", {})
        fg = market_state.get("fear_greed", {"value": 50, "classification": "Neutral"})
        signals = signals_data.get("signals", [])

        # Recommendation
        buy_signals = [s for s in signals if "BUY" in s.get("action", "")]
        if any(s.get("action") == "STRONG_BUY" for s in signals):
            recommendation = "🎯 STRONG BUY - Optimal entry zone"
        elif buy_signals:
            recommendation = f"📈 BUY - {len(buy_signals)} assets signaling entry"
        elif fg.get("value", 50) <= 25:
            recommendation = "💰 ACCUMULATE - Extreme fear = opportunity"
        else:
            recommendation = "⏸️ WAIT - No clear signals"

        result = {
            "忍 MARKET SCAN": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fear_greed": fg.get("value", 50),
            "classification": fg.get("classification", "Neutral"),
            "recommendation": recommendation,
            "signals": signals[:5]  # Top 5 signals
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== GATEWAY CHECK =====
    elif name == "gateway_check":
        mission = load_mission()
        progress = mission.get("progress", {})
        req = mission.get("objective", {}).get("success_criteria", {})

        profit_target = req.get("paper_profit", 661.46)
        win_rate_min = req.get("win_rate_min", 60)
        trades_min = req.get("trades_min", 10)

        current_profit = progress.get("paper_pnl", 0)
        current_win_rate = progress.get("paper_win_rate", 0)
        current_trades = progress.get("paper_trades", 0)

        profit_met = current_profit >= profit_target
        win_rate_met = current_win_rate >= win_rate_min
        trades_met = current_trades >= trades_min

        gateway_unlocked = all([profit_met, win_rate_met, trades_met])

        result = {
            "忍 GATEWAY STATUS": "🚀 UNLOCKED - Heavy artillery ready!" if gateway_unlocked else "⛩ SEALED",
            "requirements": {
                "profit": {
                    "required": f"${profit_target:,.2f}",
                    "current": f"${current_profit:,.2f}",
                    "met": "✅" if profit_met else "❌"
                },
                "win_rate": {
                    "required": f"{win_rate_min}%",
                    "current": f"{current_win_rate:.1f}%",
                    "met": "✅" if win_rate_met else "❌"
                },
                "trades": {
                    "required": trades_min,
                    "current": current_trades,
                    "met": "✅" if trades_met else "❌"
                }
            },
            "unlocks_on_success": [
                "LIVE_TRADING_ENABLED",
                "AUTO_SIGNAL_EXECUTION",
                "24/7_SWARM_OPERATIONS"
            ]
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== LOG PAPER TRADE =====
    elif name == "log_paper_trade":
        mission = load_mission()

        symbol = arguments.get("symbol", "").upper()
        direction = arguments.get("direction", "long").lower()
        entry_price = arguments.get("entry_price", 0)
        stop_loss = arguments.get("stop_loss", 0)
        position_size = arguments.get("position_size", 50)

        trade_id = f"PT{len(mission.get('paper_trades', [])) + 1:03d}"

        # Calculate take profit (5% for long, -5% for short)
        if direction == "long":
            take_profit = entry_price * 1.05
        else:
            take_profit = entry_price * 0.95

        trade = {
            "id": trade_id,
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": round(take_profit, 2),
            "position_size": position_size,
            "position_value": position_size,
            "status": "open",
            "entry_time": datetime.now().isoformat(),
            "exit_price": None,
            "exit_time": None,
            "pnl": None,
            "pnl_pct": None
        }

        if "paper_trades" not in mission:
            mission["paper_trades"] = []

        mission["paper_trades"].append(trade)
        save_mission(mission)

        result = {
            "忍 TRADE LOGGED": trade_id,
            "symbol": symbol,
            "direction": direction,
            "entry_price": f"${entry_price:,.2f}",
            "stop_loss": f"${stop_loss:,.2f}",
            "take_profit": f"${take_profit:,.2f}",
            "position_size": f"${position_size}",
            "status": "OPEN"
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== CLOSE PAPER TRADE =====
    elif name == "close_paper_trade":
        mission = load_mission()
        trade_id = arguments.get("trade_id", "").upper()
        exit_price = arguments.get("exit_price", 0)

        trade = None
        for t in mission.get("paper_trades", []):
            if t["id"] == trade_id and t["status"] == "open":
                trade = t
                break

        if not trade:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Trade {trade_id} not found or already closed"
            }, indent=2))]

        # Calculate P&L
        entry = trade["entry_price"]
        if trade["direction"] == "long":
            pnl_pct = (exit_price - entry) / entry * 100
        else:
            pnl_pct = (entry - exit_price) / entry * 100

        pnl = trade["position_size"] * (pnl_pct / 100)

        # Update trade
        trade["exit_price"] = exit_price
        trade["exit_time"] = datetime.now().isoformat()
        trade["pnl"] = round(pnl, 2)
        trade["pnl_pct"] = round(pnl_pct, 2)
        trade["status"] = "closed"

        # Update mission progress
        progress = mission.get("progress", {})
        progress["paper_trades"] = progress.get("paper_trades", 0) + 1
        progress["paper_pnl"] = round(progress.get("paper_pnl", 0) + pnl, 2)

        if pnl > 0:
            progress["paper_wins"] = progress.get("paper_wins", 0) + 1
        else:
            progress["paper_losses"] = progress.get("paper_losses", 0) + 1

        if progress["paper_trades"] > 0:
            progress["paper_win_rate"] = round(
                progress["paper_wins"] / progress["paper_trades"] * 100, 1
            )

        mission["progress"] = progress
        save_mission(mission)

        result = {
            "忍 TRADE CLOSED": trade_id,
            "symbol": trade["symbol"],
            "entry": f"${entry:,.2f}",
            "exit": f"${exit_price:,.2f}",
            "pnl": f"${pnl:+,.2f}",
            "pnl_pct": f"{pnl_pct:+.1f}%",
            "mission_progress": f"${progress['paper_pnl']:,.2f} / $661.46"
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== MY CAPITAL (LEGACY) =====
    elif name == "my_capital":
        brain = load_brain()
        portfolio = brain.get("portfolio", {})

        result = {
            "💰 Net Worth": f"${portfolio.get('net_worth', 0):,.2f}",
            "🔒 Ledger (Cold)": f"${portfolio.get('ledger_total', 0):,.2f}",
            "🔥 Exchanges (Hot)": f"${portfolio.get('exchange_total', 0):,.2f}",
            "⚠️ AAVE Debt": f"${portfolio.get('aave_debt', 0):,.2f}",
            "🎯 Mission Target": "$661.46 profit to clear debt"
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    # ===== CAN I TRADE =====
    elif name == "can_i_trade":
        amount = arguments.get("amount", 0)
        max_position = 50  # Mission 001 limit

        is_safe = amount <= max_position
        verdict = "✅ SAFE TO TRADE" if is_safe else "❌ TOO RISKY"

        result = {
            "verdict": verdict,
            "💵 Amount": f"${amount}",
            "🛡️ Mission Limit": f"${max_position}",
            "📋 Rule": "Max $50/position during paper trading phase"
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

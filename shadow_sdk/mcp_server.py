#!/usr/bin/env python3
"""
🏴 Shadow SDK - MCP Server
Exposes Shadow SDK functionality through Model Context Protocol
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
import os

# Add SDK to path
sys.path.insert(0, os.path.dirname(__file__))

from shadow_sdk import (
    ShadowScope, 
    EXCHANGES, 
    CAPITAL_TOTAL,
    CAPITAL_LEDGER,
    CAPITAL_COINBASE,
    TARGET_CAPITAL,
    MAX_DAILY_LOSS,
    MAX_POSITION_SIZE,
    PHILOSOPHY
)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


# Initialize MCP server
app = Server("shadow-sdk")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available Shadow SDK tools"""
    return [
        types.Tool(
            name="my_capital",
            description="Show my total capital breakdown (Ledger + Coinbase hot wallet)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="my_exchanges",
            description="Show which exchanges I'm trading on (Coinbase, OKX, Kraken)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="my_safety_rules",
            description="Show my trading safety rules and position limits",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="can_i_trade",
            description="Check if I can safely trade this amount based on my risk limits",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Trade amount in USD (e.g., 100, 250, 400)",
                    },
                },
                "required": ["amount"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if name == "my_capital":
        result = {
            "💰 Total Capital": f"${CAPITAL_TOTAL:,}",
            "🔒 Ledger (Cold Storage)": f"${CAPITAL_LEDGER:,}",
            "🔥 Coinbase (Hot Wallet)": f"${CAPITAL_COINBASE:,}",
            "🎯 Target Goal": f"${TARGET_CAPITAL:,}",
            "📈 Progress": f"{(CAPITAL_TOTAL/TARGET_CAPITAL)*100:.1f}%",
            "philosophy": PHILOSOPHY,
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "my_exchanges":
        result = {
            "✅ Active Exchanges": EXCHANGES,
            "📊 Exchange Count": len(EXCHANGES),
            "details": {
                "Coinbase": "🇺🇸 Primary US exchange - $1,660 hot wallet",
                "OKX": "🌍 Global exchange - Arbitrage opportunities",
                "Kraken": "🏰 Veteran exchange - High liquidity, working!",
            }
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "my_safety_rules":
        result = {
            "🛡️ Max Daily Loss": f"${MAX_DAILY_LOSS}",
            "💵 Max Position Size": f"${MAX_POSITION_SIZE}",
            "📊 Max Position %": f"{(MAX_POSITION_SIZE / CAPITAL_COINBASE) * 100:.1f}% of hot wallet",
            "🎯 Philosophy": "Safety first, profits second",
            "📜 Trading Rules": [
                "✅ Never risk more than $100/day",
                "✅ Max position: 25% of hot wallet ($415)",
                "✅ Paper trade before real money",
                "✅ Stop after 3 consecutive losses",
                "✅ Scale methodically, document everything"
            ]
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "can_i_trade":
        amount = arguments.get("amount", 0)
        is_safe = amount <= MAX_POSITION_SIZE
        percent_of_capital = (amount / CAPITAL_COINBASE) * 100
        
        verdict = "✅ SAFE TO TRADE" if is_safe else "❌ TOO RISKY"
        reason = f"Within safety limits" if is_safe else f"Exceeds max position of ${MAX_POSITION_SIZE}"
        
        result = {
            "verdict": verdict,
            "💵 Amount": f"${amount}",
            "📊 Percent of Hot Wallet": f"{percent_of_capital:.1f}%",
            "🛡️ Max Allowed": f"${MAX_POSITION_SIZE}",
            "💡 Reason": reason,
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


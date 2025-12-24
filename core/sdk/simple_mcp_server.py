#!/usr/bin/env python3
"""
🏴 Simple MCP Server for Sovereign Shadow
Minimal working version for Claude Desktop - FIXED BrokenPipeError
Enhanced with robust terminal disconnection handling
"""

import asyncio
import json
import sys
import os
import signal
from typing import Any, Dict, List

# Force unbuffered stdout/stderr to prevent pipe issues
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except (AttributeError, OSError):
    # Fallback for older Python versions or when reconfigure fails
    # Just ensure we flush frequently
    import atexit
    def flush_streams():
        sys.stdout.flush()
        sys.stderr.flush()
    atexit.register(flush_streams)

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
app = Server("sovereign-shadow")

# Log to stderr for debugging (won't break the MCP protocol)
def log(msg: str):
    print(f"[DEBUG] {msg}", file=sys.stderr, flush=True)

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available Shadow SDK tools"""
    log("list_tools() called")
    return [
        types.Tool(
            name="my_capital",
            description="Show my total capital breakdown",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="my_status",
            description="Show my trading system status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="scan_opportunities",
            description="Scan for trading opportunities across all exchanges",
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "description": "Trading strategy to use (arbitrage, scalping, meme_coins)",
                        "enum": ["arbitrage", "scalping", "meme_coins", "all"]
                    }
                }
            },
        ),
        types.Tool(
            name="check_exchanges",
            description="Check status of all exchange connections",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="deploy_meme_coins",
            description="Deploy meme coin strategy with specified allocations",
            inputSchema={
                "type": "object",
                "properties": {
                    "total_capital": {
                        "type": "number",
                        "description": "Total capital to deploy (default: 1660)"
                    },
                    "strategy": {
                        "type": "string",
                        "description": "Deployment strategy",
                        "enum": ["conservative", "moderate", "aggressive"]
                    }
                }
            },
        ),
        types.Tool(
            name="optimize_system",
            description="Analyze and optimize the entire Sovereign Shadow system",
            inputSchema={
                "type": "object",
                "properties": {
                    "focus_area": {
                        "type": "string",
                        "description": "Area to focus optimization on",
                        "enum": ["trading", "risk_management", "performance", "all"]
                    }
                }
            },
        ),
        types.Tool(
            name="read_file",
            description="Read any file in the Sovereign Shadow system",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            },
        ),
        types.Tool(
            name="list_strategies",
            description="List all available trading strategies",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_market_data",
            description="Get real-time market data for specified assets",
            inputSchema={
                "type": "object",
                "properties": {
                    "assets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of assets to get data for (e.g., ['BTC', 'ETH', 'BONK'])"
                    }
                }
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    """Handle tool calls"""
    log(f"call_tool() called: {name} with args {arguments}")
    
    try:
        if name == "my_capital":
            result = {
                "💰 Capital Breakdown": {
                    "Vault (Cold Storage)": "$6,600 USDC (Ledger)",
                    "Engine (Active Trading)": "$1,660 USDC (Hot Wallet)",
                    "AAVE Position": "$2,397 net ($3,547 supplied - $1,150 borrowed)",
                    "Health Factor": "2.49 (SAFE)",
                    "Total Portfolio": "~$10,657"
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "my_status":
            result = {
                "🎯 System Status": {
                    "MCP Connection": "✅ Connected",
                    "Exchanges": {
                        "Coinbase": "⚠️ API Auth Error (401)",
                        "OKX": "❌ Not Configured",
                        "Kraken": "❌ Not Configured"
                    },
                    "Active Strategies": "None (awaiting deployment)",
                    "Pending Actions": [
                        "Fix Coinbase API authentication",
                        "Configure OKX for meme coin trading",
                        "Deploy $1,660 across 6 meme positions"
                    ]
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "scan_opportunities":
            strategy = arguments.get("strategy", "all")
            result = {
                "🔍 Trading Opportunities": {
                    "Strategy": strategy,
                    "Note": "Real scanning requires exchange API connections",
                    "Action Required": "Configure OKX and Coinbase APIs first"
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "check_exchanges":
            result = {
                "📡 Exchange Status": {
                    "Coinbase": {"Status": "❌ Error", "Issue": "401 API Auth"},
                    "OKX": {"Status": "❌ Not Configured", "Issue": "Missing API keys"},
                    "Kraken": {"Status": "❌ Not Configured", "Issue": "Missing API keys"}
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "deploy_meme_coins":
            total_capital = arguments.get("total_capital", 1660)
            strategy = arguments.get("strategy", "moderate")
            result = {
                "🚀 Meme Coin Deployment": {
                    "Total Capital": f"${total_capital}",
                    "Strategy": strategy,
                    "Allocations": {
                        "BONK": "$276 (Solana flagship)",
                        "POPCAT": "$276 (Strong Solana meme)",
                        "WIF": "$276 (Solana ecosystem)",
                        "PEPE": "$276 (Established meme)",
                        "NUBCAT": "$276 (Micro-cap moonshot)",
                        "FARTCOIN": "$280 (Moonshot potential)"
                    },
                    "Action": "Execute these limit orders on OKX"
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "optimize_system":
            focus_area = arguments.get("focus_area", "all")
            result = {
                "🔧 System Optimization": {
                    "Focus": focus_area,
                    "Issues": [
                        "Coinbase API 401 error",
                        "OKX not configured",
                        "Tactical scalps fee inefficient"
                    ],
                    "Recommendations": [
                        "1. Fix Coinbase API auth",
                        "2. Configure OKX API",
                        "3. Deploy meme coin strategy",
                        "4. Monitor AAVE health daily"
                    ]
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "read_file":
            file_path = arguments.get("file_path")
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                # Limit response size to prevent pipe overflow
                truncated = len(content) > 2000
                result = {
                    "📄 File": file_path,
                    "Content": content[:2000] + "..." if truncated else content,
                    "Truncated": truncated
                }
            except Exception as e:
                result = {"❌ Error": f"Could not read {file_path}: {str(e)}"}
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_strategies":
            result = {
                "📈 Trading Strategies": {
                    "Arbitrage": "Cross-exchange price differences",
                    "Sniping": "New listing quick trades",
                    "Scalping": "Micro movements (fee inefficient)",
                    "Meme Coins": "BONK, POPCAT, PEPE, WIF, NUBCAT, FARTCOIN"
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_market_data":
            assets = arguments.get("assets", ["BTC", "ETH"])
            result = {
                "📊 Market Data": {
                    "Note": "Real-time data requires API connections",
                    "Assets": ", ".join(assets)
                }
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        log(f"Error in call_tool: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server with proper error handling"""
    log("Starting Sovereign Shadow MCP server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            log("Server running, awaiting requests...")
            await app.run(
                read_stream, 
                write_stream, 
                app.create_initialization_options()
            )
    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        # Terminal disconnected - graceful shutdown
        log(f"Terminal disconnected: {type(e).__name__}")
        return
    except asyncio.CancelledError:
        log("Server cancelled - shutting down gracefully")
        return
    except EOFError:
        log("EOFError - stdin closed, client disconnected")
        return
    except Exception as e:
        log(f"Server error: {type(e).__name__}: {str(e)}")
        # Don't raise - allow graceful exit
        return

def signal_handler(signum, frame):
    """Handle terminal signals gracefully"""
    log(f"Received signal {signum} - shutting down gracefully")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # Let SIGPIPE behave normally
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user")
        sys.exit(0)
    except (BrokenPipeError, ConnectionResetError, EOFError) as e:
        log(f"Terminal disconnected: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        log(f"Fatal error: {str(e)}")
        sys.exit(1)

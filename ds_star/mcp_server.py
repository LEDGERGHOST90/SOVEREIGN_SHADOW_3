#!/usr/bin/env python3
"""
DS-STAR MCP Server
Unified Model Context Protocol server exposing all DS-STAR modules

Tools:
- synoptic_core_assess: Smart Asset Score analysis
- architect_forge_build: Strategy generation
- oracle_query: Natural language market questions
- gatekeeper_clean: Data normalization
- transparent_analyst_explain: Step-by-step analysis
"""

import json
import sys
import asyncio
import os
import requests
from pathlib import Path
from typing import Any

# Add ds_star to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ds_star.synoptic_core import SynopticCore
from ds_star.architect_forge import ArchitectForge
from ds_star.oracle_interface import OracleInterface
from ds_star.gatekeeper import Gatekeeper
from ds_star.transparent_analyst import TransparentAnalyst


class DSStarMCPServer:
    """
    DS-STAR MCP Server

    Provides unified access to all DS-STAR analysis modules
    via the Model Context Protocol
    """

    def __init__(self):
        self.name = "ds-star"
        self.version = "1.0.0"

        # Initialize all modules
        self.synoptic = SynopticCore()
        self.architect = ArchitectForge()
        self.oracle = OracleInterface()
        self.gatekeeper = Gatekeeper()
        self.transparent = TransparentAnalyst()

        # Define available tools
        self.tools = {
            "synoptic_core_assess": {
                "description": "Get Smart Asset Score (0-100) with unified analysis across technical, on-chain, fundamental, and sentiment data",
                "parameters": {
                    "asset": {"type": "string", "description": "Asset symbol (e.g., BTC, ETH, SOL)"},
                    "timeframe": {"type": "string", "description": "Data timeframe (1h, 4h, 1d)", "default": "1d"},
                    "lookback_days": {"type": "integer", "description": "Days of history to analyze", "default": 30}
                },
                "handler": self._handle_synoptic
            },
            "architect_forge_build": {
                "description": "Build a verified trading strategy from natural language description",
                "parameters": {
                    "request": {"type": "string", "description": "Natural language strategy description"},
                    "symbols": {"type": "array", "description": "Assets to trade (default: ['BTC/USDT'])"},
                    "timeframe": {"type": "string", "description": "Trading timeframe", "default": "1d"},
                    "backtest_days": {"type": "integer", "description": "Days for backtest", "default": 90}
                },
                "handler": self._handle_architect
            },
            "oracle_query": {
                "description": "Ask market questions in natural language, get charts and metrics",
                "parameters": {
                    "question": {"type": "string", "description": "Natural language market question"}
                },
                "handler": self._handle_oracle
            },
            "gatekeeper_clean": {
                "description": "Normalize raw CEX/DEX/blockchain data to Sovereign Standard Schema",
                "parameters": {
                    "raw_data": {"type": "object", "description": "Raw JSON data to clean"},
                    "source_hint": {"type": "string", "description": "Optional source hint (binance, uniswap, etc.)"}
                },
                "handler": self._handle_gatekeeper
            },
            "transparent_analyst_explain": {
                "description": "Perform analysis with step-by-step process visibility",
                "parameters": {
                    "context": {"type": "object", "description": "Analysis context data"},
                    "description": {"type": "string", "description": "Description of analysis to perform"}
                },
                "handler": self._handle_transparent
            },
            "get_replit_sync": {
                "description": "Fetch live portfolio from Shadow.AI Replit - all exchanges, AAVE position, balances",
                "parameters": {},
                "handler": self._handle_replit_sync
            },
            "get_brain_state": {
                "description": "Read current BRAIN.json state - portfolio, wallets, mission, agents",
                "parameters": {},
                "handler": self._handle_brain_state
            }
        }

    def get_tools_schema(self) -> list:
        """Return MCP tools schema"""
        return [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": tool["parameters"],
                    "required": [k for k, v in tool["parameters"].items() if "default" not in v]
                }
            }
            for name, tool in self.tools.items()
        ]

    async def handle_tool_call(self, name: str, arguments: dict) -> Any:
        """Handle a tool call"""
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}

        handler = self.tools[name]["handler"]
        try:
            result = await handler(arguments)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def _handle_synoptic(self, args: dict) -> dict:
        """Handle synoptic_core_assess tool"""
        asset = args.get("asset", "BTC")
        timeframe = args.get("timeframe", "1d")
        days = args.get("lookback_days", 30)

        result = self.synoptic.assess(asset, timeframe, days)
        return result.to_dict()

    async def _handle_architect(self, args: dict) -> dict:
        """Handle architect_forge_build tool"""
        request = args.get("request", "")
        symbols = args.get("symbols", ["BTC/USDT"])
        timeframe = args.get("timeframe", "1d")
        days = args.get("backtest_days", 90)

        result = self.architect.build(request, symbols, timeframe, days)
        return result.to_dict()

    async def _handle_oracle(self, args: dict) -> dict:
        """Handle oracle_query tool"""
        question = args.get("question", "")
        result = self.oracle.query(question)

        # Don't include large chart data in response
        if result.get("chart"):
            result["chart"] = f"[Chart generated - {len(result['chart'])} bytes]"

        return result

    async def _handle_gatekeeper(self, args: dict) -> dict:
        """Handle gatekeeper_clean tool"""
        raw_data = args.get("raw_data", [])
        source_hint = args.get("source_hint")

        result = self.gatekeeper.clean(raw_data, source_hint)
        return result

    async def _handle_transparent(self, args: dict) -> dict:
        """Handle transparent_analyst_explain tool"""
        context = args.get("context", {})
        description = args.get("description", "Analysis")

        self.transparent.start_analysis(description)

        # Record context loading
        for key, value in context.items():
            self.transparent.record_step(f"Loaded {key}")

        # Generate analysis
        result = self.transparent.analyze_with_context(context)

        return self.transparent.format_for_ui(result)

    async def _handle_replit_sync(self, args: dict) -> dict:
        """Handle get_replit_sync tool - fetch live data from Shadow.AI Replit"""
        replit_url = os.getenv("REPLIT_API_URL", "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev")
        try:
            response = requests.get(f"{replit_url}/api/brain/sync", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to fetch from Replit: {str(e)}"}

    async def _handle_brain_state(self, args: dict) -> dict:
        """Handle get_brain_state tool - read local BRAIN.json"""
        brain_path = Path(__file__).parent.parent / "BRAIN.json"
        try:
            with open(brain_path) as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to read BRAIN.json: {str(e)}"}

    def run_stdio(self):
        """Run MCP server over stdio"""
        print(json.dumps({
            "name": self.name,
            "version": self.version,
            "tools": self.get_tools_schema()
        }), file=sys.stderr)

        for line in sys.stdin:
            try:
                request = json.loads(line)
                method = request.get("method")

                # MCP Protocol: initialize handshake
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {
                                "name": self.name,
                                "version": self.version
                            }
                        }
                    }

                # MCP Protocol: initialized notification (no response)
                elif method == "notifications/initialized":
                    continue

                elif method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"tools": self.get_tools_schema()}
                    }

                elif method == "tools/call":
                    params = request.get("params", {})
                    name = params.get("name")
                    arguments = params.get("arguments", {})

                    result = asyncio.run(self.handle_tool_call(name, arguments))

                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
                    }

                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }

                print(json.dumps(response))
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }))
                sys.stdout.flush()


# FastAPI integration for HTTP-based MCP
def create_fastapi_app():
    """Create FastAPI app for DS-STAR MCP"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import Optional, List, Dict

    app = FastAPI(
        title="DS-STAR MCP Server",
        description="Decision Support - Strategic Trading Analysis & Research",
        version="1.0.0"
    )

    server = DSStarMCPServer()

    class ToolCallRequest(BaseModel):
        name: str
        arguments: Dict[str, Any] = {}

    @app.get("/")
    async def root():
        return {
            "name": server.name,
            "version": server.version,
            "tools": [t["name"] for t in server.get_tools_schema()]
        }

    @app.get("/tools")
    async def list_tools():
        return {"tools": server.get_tools_schema()}

    @app.post("/tools/call")
    async def call_tool(request: ToolCallRequest):
        result = await server.handle_tool_call(request.name, request.arguments)
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    # Convenience endpoints for each tool
    @app.get("/synoptic/{asset}")
    async def synoptic_assess(asset: str, timeframe: str = "1d", days: int = 30):
        return await server._handle_synoptic({
            "asset": asset,
            "timeframe": timeframe,
            "lookback_days": days
        })

    @app.post("/architect")
    async def architect_build(request: str, symbols: List[str] = ["BTC/USDT"]):
        return await server._handle_architect({
            "request": request,
            "symbols": symbols
        })

    @app.get("/oracle")
    async def oracle_query(question: str):
        return await server._handle_oracle({"question": question})

    @app.post("/gatekeeper")
    async def gatekeeper_clean(raw_data: List[Dict], source_hint: Optional[str] = None):
        return await server._handle_gatekeeper({
            "raw_data": raw_data,
            "source_hint": source_hint
        })

    return app


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DS-STAR MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio",
                       help="Server mode (stdio for MCP, http for FastAPI)")
    parser.add_argument("--port", type=int, default=8001, help="HTTP port")
    parser.add_argument("--test", action="store_true", help="Run quick test")

    args = parser.parse_args()

    if args.test:
        # Quick test of all modules
        print("Testing DS-STAR modules...")

        server = DSStarMCPServer()

        # Test Synoptic Core
        print("\n1. Synoptic Core:")
        result = asyncio.run(server._handle_synoptic({"asset": "BTC"}))
        print(f"   Score: {result.get('smart_asset_score')}/100")

        # Test Oracle
        print("\n2. Oracle Interface:")
        result = asyncio.run(server._handle_oracle({"question": "BTC price 7 days"}))
        print(f"   Caption: {result.get('caption')}")

        # Test Gatekeeper
        print("\n3. Gatekeeper:")
        result = asyncio.run(server._handle_gatekeeper({
            "raw_data": [{"time": 1701388800000, "price": "95000", "qty": "1"}]
        }))
        print(f"   Cleaned: {result.get('success')}, Records: {len(result.get('records', []))}")

        # Test Transparent Analyst
        print("\n4. Transparent Analyst:")
        result = asyncio.run(server._handle_transparent({
            "context": {"score": 75, "trend": "bullish"},
            "description": "Test analysis"
        }))
        print(f"   Recommendation: {result.get('main_content', '')[:100]}...")

        print("\n✅ All modules operational!")

    elif args.mode == "http":
        import uvicorn
        app = create_fastapi_app()
        print(f"Starting DS-STAR HTTP server on port {args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)

    else:
        server = DSStarMCPServer()
        server.run_stdio()

#!/usr/bin/env python3
"""
SovereignShadow Unified API
Bridge between Gemini frontend and Python trading backend
Deploy to: sovereignnshadowii.abacusai.app/api
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing SovereignShadow modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="SovereignShadow API",
    description="Unified trading API for the Sovereign ecosystem",
    version="1.0.0"
)

# CORS - Allow Gemini frontend and Abacus domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "https://sovereignnshadowii.abacusai.app",
        "https://*.abacusai.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# DATA MODELS
# =============================================================================

class Strategy(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    category: str  # Vault, Sniper, Ladder, MENACE
    risk_level: str
    timeframe: str
    assets: List[str]
    buy_conditions: List[str]
    sell_conditions: List[str]
    stop_loss: str
    take_profit: str
    indicators: List[str]
    sentiment: int
    source: str = "manual"
    created_at: Optional[str] = None

class Trade(BaseModel):
    asset: str
    side: str  # buy/sell
    amount: float
    price: Optional[float] = None
    strategy_id: Optional[str] = None

class SessionState(BaseModel):
    date: str
    portfolio_snapshot: Dict[str, Any]
    active_strategies: List[str]
    notes: str

# =============================================================================
# DATA PERSISTENCE (File-based for now, upgrade to DB later)
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "memory" / "api_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename: str) -> List[Dict]:
    filepath = DATA_DIR / filename
    if filepath.exists():
        return json.loads(filepath.read_text())
    return []

def save_json(filename: str, data: List[Dict]):
    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(data, indent=2, default=str))

# =============================================================================
# PORTFOLIO ENDPOINTS
# =============================================================================

@app.get("/api/portfolio")
async def get_portfolio():
    """Get aggregated portfolio from all exchanges"""
    try:
        # Try to import and use existing connectors
        portfolio = {
            "timestamp": datetime.now().isoformat(),
            "total_value_usd": 0,
            "exchanges": {},
            "defi": {},
            "summary": {}
        }

        # Load from session state if available
        session_file = Path(__file__).parent.parent / "SESSION_STATE_2025-11-26.json"
        if session_file.exists():
            session = json.loads(session_file.read_text())
            if "portfolio" in session:
                portfolio.update(session["portfolio"])

        # Load from LIVE_STATUS if available
        live_status = Path(__file__).parent.parent / "memory" / "LIVE_STATUS.json"
        if live_status.exists():
            status = json.loads(live_status.read_text())
            portfolio["live_status"] = status

        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/aave")
async def get_aave_status():
    """Get AAVE health factor and debt status"""
    return {
        "health_factor": 3.71,
        "total_debt_usd": 660.94,
        "collateral_usd": 3040.25,
        "collateral_asset": "wstETH",
        "borrow_apy": 5.49,
        "annual_cost": 36.29,
        "status": "URGENT - Repay to stop bleed",
        "last_updated": datetime.now().isoformat()
    }

# =============================================================================
# STRATEGY ENDPOINTS
# =============================================================================

@app.get("/api/strategies")
async def list_strategies():
    """List all analyzed strategies"""
    strategies = load_json("strategies.json")
    return {"strategies": strategies, "count": len(strategies)}

@app.get("/api/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID"""
    strategies = load_json("strategies.json")
    for s in strategies:
        if s.get("id") == strategy_id:
            return s
    raise HTTPException(status_code=404, detail="Strategy not found")

@app.post("/api/strategies")
async def save_strategy(strategy: Strategy):
    """Save a new strategy from Gemini analysis"""
    strategies = load_json("strategies.json")

    # Generate ID if not provided
    if not strategy.id:
        strategy.id = f"strat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    strategy.created_at = datetime.now().isoformat()

    strategies.append(strategy.dict())
    save_json("strategies.json", strategies)

    return {"status": "saved", "strategy_id": strategy.id}

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    strategies = load_json("strategies.json")
    strategies = [s for s in strategies if s.get("id") != strategy_id]
    save_json("strategies.json", strategies)
    return {"status": "deleted"}

# =============================================================================
# SCANNER ENDPOINTS
# =============================================================================

@app.get("/api/scanner/breakout")
async def get_breakout_candidates():
    """Run meme_machine breakout scanner"""
    try:
        # Import meme_machine if available
        from meme_machine.breakout_scanner import BreakoutScanner
        scanner = BreakoutScanner()
        candidates = scanner.scan()
        return {"candidates": candidates, "scanned_at": datetime.now().isoformat()}
    except ImportError:
        # Return mock data if module not available
        return {
            "candidates": [],
            "scanned_at": datetime.now().isoformat(),
            "note": "meme_machine not configured"
        }

@app.get("/api/scanner/dex")
async def scan_dex_tokens():
    """Scan DexScreener for new tokens"""
    try:
        from meme_machine.dex_scanner import scan_new_tokens
        tokens = scan_new_tokens()
        return {"tokens": tokens, "scanned_at": datetime.now().isoformat()}
    except ImportError:
        return {
            "tokens": [],
            "scanned_at": datetime.now().isoformat(),
            "note": "Run: python -m meme_machine --dex"
        }

# =============================================================================
# TRADING ENDPOINTS
# =============================================================================

@app.post("/api/trades/execute")
async def execute_trade(trade: Trade):
    """Execute a trade via shade_agent"""
    try:
        # Log the trade request
        trades = load_json("trades.json")
        trade_record = {
            "id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **trade.dict(),
            "status": "pending",
            "requested_at": datetime.now().isoformat()
        }
        trades.append(trade_record)
        save_json("trades.json", trades)

        # In production, this would call shade_agent
        # from core.agents_highlevel.shade_agent import ShadeAgent
        # agent = ShadeAgent()
        # result = agent.execute_trade(trade.dict())

        return {
            "status": "queued",
            "trade_id": trade_record["id"],
            "message": "Trade queued for execution"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def list_trades():
    """List all trades"""
    trades = load_json("trades.json")
    return {"trades": trades, "count": len(trades)}

# =============================================================================
# SESSION ENDPOINTS
# =============================================================================

@app.get("/api/session")
async def get_current_session():
    """Get current session state"""
    today = datetime.now().strftime("%Y-%m-%d")
    session_file = Path(__file__).parent.parent / f"SESSION_STATE_{today.replace('-', '-')}.json"

    if session_file.exists():
        return json.loads(session_file.read_text())

    return {
        "date": today,
        "status": "no_session_file",
        "message": "Start a new session to create state"
    }

@app.post("/api/session")
async def save_session(state: SessionState):
    """Save session state"""
    session_file = Path(__file__).parent.parent / f"SESSION_STATE_{state.date}.json"
    session_file.write_text(json.dumps(state.dict(), indent=2))
    return {"status": "saved", "file": str(session_file)}

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "modules": {
            "portfolio": "ready",
            "strategies": "ready",
            "scanner": "ready",
            "trades": "ready",
            "session": "ready"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "SovereignShadow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": [
            "GET /api/portfolio",
            "GET /api/portfolio/aave",
            "GET /api/strategies",
            "POST /api/strategies",
            "GET /api/scanner/breakout",
            "GET /api/scanner/dex",
            "POST /api/trades/execute",
            "GET /api/session"
        ]
    }

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           SovereignShadow Unified API Server                  ║
║                                                               ║
║  Local:   http://localhost:8000                               ║
║  Docs:    http://localhost:8000/docs                          ║
║  Health:  http://localhost:8000/api/health                    ║
║                                                               ║
║  Connect Gemini app to: http://localhost:8000/api             ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)

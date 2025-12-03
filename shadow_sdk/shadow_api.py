#!/usr/bin/env python3
"""
忍 SHADOW API - SS_III Ninja Protocol
FastAPI endpoints for Shadow.AI integration

Endpoints:
  GET  /shadow/health      - System health check
  GET  /shadow/scan        - Market scanner
  GET  /shadow/balances    - Portfolio balances
  GET  /shadow/performance - Strategy performance
  POST /shadow/execute     - Paper trade execution
  POST /shadow/update      - Dashboard updates
  GET  /shadow/mission     - Mission 001 status

SS_III Color Scheme: Off-white, Matte Black, Crimson
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal
from dataclasses import dataclass, asdict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# SS_III Base paths
BASE_DIR = Path(__file__).parent.parent
BRAIN_FILE = BASE_DIR / "BRAIN.json"
MISSION_FILE = BASE_DIR / "data/missions/mission_001_aave_debt.json"
SIGNALS_FILE = BASE_DIR / "logs/smart_signals.json"

# Initialize FastAPI with SS_III branding
app = FastAPI(
    title="忍 SHADOW API",
    description="SS_III Ninja Protocol - Paper Trading & Mission Control",
    version="3.0.0",
    docs_url="/shadow/docs",
    redoc_url="/shadow/redoc"
)

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    mission: str
    phase: str
    uptime: str
    services: Dict[str, str]
    timestamp: str

class BalanceResponse(BaseModel):
    total_assets: float
    total_debt: float
    net_worth: float
    ledger: Dict[str, Any]
    exchanges: Dict[str, Any]
    aave: Dict[str, Any]
    timestamp: str

class ScanResponse(BaseModel):
    fear_greed: int
    classification: str
    signals: List[Dict[str, Any]]
    recommendation: str
    timestamp: str

class PerformanceResponse(BaseModel):
    mission_id: str
    codename: str
    target_profit: float
    current_profit: float
    progress_pct: float
    trades: int
    wins: int
    losses: int
    win_rate: float
    milestones: List[Dict[str, Any]]
    gateway_status: str
    timestamp: str

class ExecuteRequest(BaseModel):
    symbol: str
    direction: str  # long/short
    entry_price: float
    stop_loss: float
    position_size: float = 50.0

class ExecuteResponse(BaseModel):
    trade_id: str
    status: str
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timestamp: str

class UpdateRequest(BaseModel):
    trade_id: str
    action: str  # close, update_sl, update_tp
    value: Optional[float] = None

class MissionResponse(BaseModel):
    mission_id: str
    codename: str
    status: str
    phase: str
    objective: str
    target_profit: float
    current_profit: float
    progress_pct: float
    gateway_unlocked: bool
    open_trades: List[Dict[str, Any]]
    timestamp: str

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_brain() -> dict:
    """Load BRAIN.json"""
    if BRAIN_FILE.exists():
        return json.loads(BRAIN_FILE.read_text())
    return {}

def save_brain(data: dict):
    """Save BRAIN.json"""
    BRAIN_FILE.write_text(json.dumps(data, indent=2))

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

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/shadow/health", response_model=HealthResponse)
async def health_check():
    """
    忍 System Health Check
    Returns operational status of all SS_III services
    """
    brain = load_brain()
    mission = load_mission()

    services = {
        "neural_hub": "operational",
        "paper_trading": "operational",
        "smart_signals": "operational",
        "aurora_voice": "operational",
        "mission_tracker": "operational"
    }

    # Check if services are actually running
    try:
        import requests
        resp = requests.get("http://localhost:8000/health", timeout=2)
        services["neural_hub"] = "operational" if resp.status_code == 200 else "degraded"
    except:
        services["neural_hub"] = "offline"

    return HealthResponse(
        status="operational",
        mission=mission.get("codename", "DEBT_DESTROYER"),
        phase=mission.get("phase", "paper_trading"),
        uptime="active",
        services=services,
        timestamp=datetime.now().isoformat()
    )

@app.get("/shadow/balances", response_model=BalanceResponse)
async def get_balances():
    """
    忍 Portfolio Balances
    Returns current balances across all sources
    """
    brain = load_brain()
    portfolio = brain.get("portfolio", {})

    return BalanceResponse(
        total_assets=portfolio.get("ledger_total", 0) + portfolio.get("exchange_total", 0),
        total_debt=portfolio.get("aave_debt", 0),
        net_worth=portfolio.get("net_worth", 0),
        ledger=portfolio.get("ledger", {}),
        exchanges=portfolio.get("exchanges", {}),
        aave=portfolio.get("aave", {}),
        timestamp=datetime.now().isoformat()
    )

@app.get("/shadow/scan", response_model=ScanResponse)
async def market_scan():
    """
    忍 Market Scanner
    Returns smart signals and market conditions
    """
    signals_data = load_signals()

    # Get fear & greed from signals or fetch fresh
    market_state = signals_data.get("market_state", {})
    fg = market_state.get("fear_greed", {"value": 50, "classification": "Neutral"})

    signals = signals_data.get("signals", [])

    # Determine recommendation
    buy_signals = [s for s in signals if "BUY" in s.get("action", "")]
    if any(s.get("action") == "STRONG_BUY" for s in signals):
        recommendation = "STRONG BUY - Optimal entry zone"
    elif buy_signals:
        recommendation = f"BUY - {len(buy_signals)} assets signaling entry"
    elif fg.get("value", 50) <= 25:
        recommendation = "ACCUMULATE - Extreme fear = opportunity"
    else:
        recommendation = "WAIT - No clear signals"

    return ScanResponse(
        fear_greed=fg.get("value", 50),
        classification=fg.get("classification", "Neutral"),
        signals=signals,
        recommendation=recommendation,
        timestamp=datetime.now().isoformat()
    )

@app.get("/shadow/performance", response_model=PerformanceResponse)
async def get_performance():
    """
    忍 Strategy Performance
    Returns Mission 001 progress and stats
    """
    mission = load_mission()
    progress = mission.get("progress", {})
    objective = mission.get("objective", {})
    milestones = mission.get("milestones", [])

    target = objective.get("target_profit", 661.46)
    current = progress.get("paper_pnl", 0)
    req = objective.get("success_criteria", {})

    # Check gateway status
    profit_met = current >= req.get("paper_profit", 661.46)
    win_rate_met = progress.get("paper_win_rate", 0) >= req.get("win_rate_min", 60)
    trades_met = progress.get("paper_trades", 0) >= req.get("trades_min", 10)

    gateway_status = "UNLOCKED" if all([profit_met, win_rate_met, trades_met]) else "SEALED"

    return PerformanceResponse(
        mission_id=mission.get("mission_id", "MISSION_001"),
        codename=mission.get("codename", "DEBT_DESTROYER"),
        target_profit=target,
        current_profit=current,
        progress_pct=round((current / target) * 100, 1) if target > 0 else 0,
        trades=progress.get("paper_trades", 0),
        wins=progress.get("paper_wins", 0),
        losses=progress.get("paper_losses", 0),
        win_rate=progress.get("paper_win_rate", 0),
        milestones=milestones,
        gateway_status=gateway_status,
        timestamp=datetime.now().isoformat()
    )

@app.post("/shadow/execute", response_model=ExecuteResponse)
async def execute_paper_trade(request: ExecuteRequest):
    """
    忍 Paper Trade Execution
    Log a new paper trade entry
    """
    mission = load_mission()

    trade_id = f"PT{len(mission.get('paper_trades', [])) + 1:03d}"

    # Calculate take profit (5% for long, -5% for short)
    if request.direction == "long":
        take_profit = request.entry_price * 1.05
    else:
        take_profit = request.entry_price * 0.95

    trade = {
        "id": trade_id,
        "symbol": request.symbol.upper(),
        "direction": request.direction.lower(),
        "entry_price": request.entry_price,
        "stop_loss": request.stop_loss,
        "take_profit": round(take_profit, 2),
        "position_size": request.position_size,
        "position_value": request.position_size,
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

    return ExecuteResponse(
        trade_id=trade_id,
        status="open",
        symbol=trade["symbol"],
        direction=trade["direction"],
        entry_price=trade["entry_price"],
        stop_loss=trade["stop_loss"],
        take_profit=trade["take_profit"],
        position_size=trade["position_size"],
        timestamp=datetime.now().isoformat()
    )

@app.post("/shadow/update")
async def update_trade(request: UpdateRequest):
    """
    忍 Update/Close Trade
    Modify or close an existing paper trade
    """
    mission = load_mission()

    trade = None
    for t in mission.get("paper_trades", []):
        if t["id"] == request.trade_id:
            trade = t
            break

    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {request.trade_id} not found")

    if request.action == "close" and request.value:
        # Close the trade
        exit_price = request.value
        entry = trade["entry_price"]

        if trade["direction"] == "long":
            pnl_pct = (exit_price - entry) / entry * 100
        else:
            pnl_pct = (entry - exit_price) / entry * 100

        pnl = trade["position_size"] * (pnl_pct / 100)

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

    elif request.action == "update_sl" and request.value:
        trade["stop_loss"] = request.value

    elif request.action == "update_tp" and request.value:
        trade["take_profit"] = request.value

    save_mission(mission)

    return {"status": "success", "trade_id": request.trade_id, "action": request.action}

@app.get("/shadow/mission", response_model=MissionResponse)
async def get_mission():
    """
    忍 Mission Status
    Returns full Mission 001 status including open trades
    """
    mission = load_mission()
    progress = mission.get("progress", {})
    objective = mission.get("objective", {})
    req = objective.get("success_criteria", {})

    target = objective.get("target_profit", 661.46)
    current = progress.get("paper_pnl", 0)

    # Check gateway
    profit_met = current >= req.get("paper_profit", 661.46)
    win_rate_met = progress.get("paper_win_rate", 0) >= req.get("win_rate_min", 60)
    trades_met = progress.get("paper_trades", 0) >= req.get("trades_min", 10)

    gateway_unlocked = all([profit_met, win_rate_met, trades_met])

    # Get open trades
    open_trades = [t for t in mission.get("paper_trades", []) if t.get("status") == "open"]

    return MissionResponse(
        mission_id=mission.get("mission_id", "MISSION_001"),
        codename=mission.get("codename", "DEBT_DESTROYER"),
        status=mission.get("status", "active"),
        phase=mission.get("phase", "paper_trading"),
        objective=objective.get("description", "Paper trade to acquire $661.46"),
        target_profit=target,
        current_profit=current,
        progress_pct=round((current / target) * 100, 1) if target > 0 else 0,
        gateway_unlocked=gateway_unlocked,
        open_trades=open_trades,
        timestamp=datetime.now().isoformat()
    )

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Shadow API"""
    print("忍 SHADOW API - SS_III Ninja Protocol")
    print("=" * 50)
    print("Endpoints:")
    print("  GET  /shadow/health      - Health check")
    print("  GET  /shadow/scan        - Market scanner")
    print("  GET  /shadow/balances    - Portfolio")
    print("  GET  /shadow/performance - Mission stats")
    print("  POST /shadow/execute     - Paper trade")
    print("  POST /shadow/update      - Update trade")
    print("  GET  /shadow/mission     - Mission status")
    print("=" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)

#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Neural Hub API Server
FastAPI backend for the Neural Trading Hub

Features:
- REST API for portfolio, signals, positions
- WebSocket for real-time updates
- Gemini AI integration
- Full automation support
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from neural_hub.backend.gemini_agent import GeminiNeuralAgent, MarketData, create_market_data
from neural_hub.backend.services.market_data import MarketDataService
from neural_hub.backend.services.portfolio import PortfolioService
from neural_hub.backend.services.signals import SignalService

# =============================================================================
# LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🌅 Starting AURORA Command Center...")

    # Initialize services
    app.state.gemini = GeminiNeuralAgent()
    app.state.market = MarketDataService()
    app.state.portfolio = PortfolioService()
    app.state.signals = SignalService()
    app.state.websockets = []

    print("✅ AURORA online")

    yield

    print("👋 AURORA signing off...")

# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="AURORA Command Center",
    description="Claude-powered trade execution system for Sovereign Shadow",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class SignalRequest(BaseModel):
    symbol: str

class TradeRequest(BaseModel):
    symbol: str
    action: str  # BUY or SELL
    amount_usd: float
    signal_id: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class AutomationConfig(BaseModel):
    enabled: bool
    mode: str  # paper, signal, auto
    max_trades_per_day: int = 5
    min_confidence: int = 70
    require_approval: bool = True

# =============================================================================
# REST ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Sovereign Shadow Neural Hub",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/")
async def api_root():
    """API Health check (for frontend)"""
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# -----------------------------------------------------------------------------
# PORTFOLIO
# -----------------------------------------------------------------------------

@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio status"""
    try:
        portfolio = await app.state.portfolio.get_portfolio()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/history")
async def get_portfolio_history(days: int = 30):
    """Get portfolio history"""
    try:
        history = await app.state.portfolio.get_history(days)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# SIGNALS
# -----------------------------------------------------------------------------

@app.get("/api/signals")
async def get_signals(status: Optional[str] = None):
    """Get all signals, optionally filtered by status"""
    try:
        signals = await app.state.signals.get_signals(status)
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals/generate")
async def generate_signal(request: SignalRequest, background_tasks: BackgroundTasks):
    """Generate a new signal using Gemini"""
    try:
        # Get market data
        market_data = await app.state.market.get_market_data(request.symbol)

        # Generate signal
        signal = await app.state.gemini.generate_signal(market_data)

        # Save signal
        saved = await app.state.signals.save_signal(signal)

        # Broadcast to WebSocket clients
        background_tasks.add_task(broadcast_signal, signal)

        return {
            "status": "success",
            "signal": {
                "symbol": signal.symbol,
                "action": signal.action,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit_1": signal.take_profit_1,
                "take_profit_2": signal.take_profit_2,
                "risk_level": signal.risk_level,
                "timeframe": signal.timeframe,
                "timestamp": signal.timestamp
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals/{signal_id}/accept")
@app.post("/api/signals/{signal_id}/execute")  # Alias for frontend
async def accept_signal(signal_id: str):
    """Accept a signal and create a position"""
    try:
        result = await app.state.signals.accept_signal(signal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals/{signal_id}/reject")
async def reject_signal(signal_id: str):
    """Reject a signal"""
    try:
        result = await app.state.signals.reject_signal(signal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# POSITIONS
# -----------------------------------------------------------------------------

@app.get("/api/positions")
async def get_positions(status: Optional[str] = "open"):
    """Get positions"""
    try:
        # Import swing engine
        sys.path.insert(0, str(PROJECT_ROOT / "strategies"))
        from swing_trade_engine import SwingTradeEngine, SwingConfig, TradeMode

        config = SwingConfig(mode=TradeMode.PAPER)
        engine = SwingTradeEngine(config)
        positions = engine.position_mgr.get_open_positions()

        return {
            "positions": [
                {
                    "id": p.id,
                    "symbol": p.symbol,
                    "entry_price": p.entry_price,
                    "current_price": await app.state.market.get_price(p.symbol),
                    "quantity": p.quantity,
                    "position_value": p.position_value,
                    "stop_loss": p.stop_loss,
                    "take_profit_1": p.take_profit_1,
                    "take_profit_2": p.take_profit_2,
                    "status": p.status,
                    "tp1_hit": p.tp1_hit,
                    "entry_time": p.entry_time
                }
                for p in positions
            ],
            "count": len(positions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/positions/open")
async def open_position(request: TradeRequest):
    """Open a new position"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "strategies"))
        from swing_trade_engine import SwingTradeEngine, SwingConfig, TradeMode, TradeSignal

        config = SwingConfig(mode=TradeMode.PAPER)
        engine = SwingTradeEngine(config)

        # Get current price
        price = await app.state.market.get_price(request.symbol)

        # Create signal
        signal = TradeSignal(
            symbol=request.symbol,
            signal_type="entry",
            direction="long",
            strength=70,
            price=price,
            rsi=50,
            volume_ratio=1.5,
            ema_20=price,
            reasons=["Manual entry via API"],
            timestamp=datetime.now().isoformat()
        )

        position = engine.execute_paper_trade(signal)

        if position:
            return {
                "status": "success",
                "position": {
                    "id": position.id,
                    "symbol": position.symbol,
                    "entry_price": position.entry_price,
                    "position_value": position.position_value,
                    "stop_loss": position.stop_loss,
                    "take_profit_1": position.take_profit_1,
                    "take_profit_2": position.take_profit_2
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Could not open position")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/positions/{position_id}/close")
async def close_position(position_id: str):
    """Close a position"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "strategies"))
        from swing_trade_engine import SwingTradeEngine, SwingConfig, TradeMode

        config = SwingConfig(mode=TradeMode.PAPER)
        engine = SwingTradeEngine(config)

        positions = engine.position_mgr.get_open_positions()
        for pos in positions:
            if pos.id == position_id:
                price = await app.state.market.get_price(pos.symbol)
                engine.position_mgr.close_position(pos, price, "manual")
                return {
                    "status": "success",
                    "message": f"Closed {pos.symbol} at ${price:,.4f}"
                }

        raise HTTPException(status_code=404, detail="Position not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# NEURAL ANALYSIS
# -----------------------------------------------------------------------------

@app.get("/api/neural/analyze/{symbol}")
async def analyze_symbol(symbol: str):
    """Deep analysis of a symbol"""
    try:
        market_data = await app.state.market.get_market_data(symbol.upper())
        analysis = await app.state.gemini.deep_analyze(market_data)

        return {
            "symbol": analysis.symbol,
            "trend": analysis.trend,
            "strength": analysis.strength,
            "support_levels": analysis.support_levels,
            "resistance_levels": analysis.resistance_levels,
            "patterns_detected": analysis.patterns_detected,
            "key_insights": analysis.key_insights,
            "recommendation": analysis.recommendation,
            "timestamp": analysis.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/neural/chat")
async def neural_chat(request: ChatMessage):
    """Chat with the neural agent"""
    try:
        response = await app.state.gemini.chat(request.message, request.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/neural/strategy")
async def get_strategy_recommendation():
    """Get strategy recommendation based on market conditions"""
    try:
        # Get market conditions
        btc_data = await app.state.market.get_market_data("BTC")

        conditions = {
            "btc_trend": "bullish" if btc_data.change_24h > 2 else "bearish" if btc_data.change_24h < -2 else "neutral",
            "volatility": "high" if abs(btc_data.change_24h) > 5 else "medium" if abs(btc_data.change_24h) > 2 else "low",
            "fear_greed": 50,  # Would need external API
            "funding": "neutral"
        }

        strategy = await app.state.gemini.select_strategy(conditions)
        return strategy

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# SCANNER
# -----------------------------------------------------------------------------

@app.get("/api/scanner")
@app.get("/api/scanner/scan")
async def run_scanner(
    minVolume: int = 0,
    minChange: float = 0,
    sortBy: str = "volume_24h",
    signal: Optional[str] = None
):
    """Run the market scanner"""
    try:
        watchlist = ["BTC", "ETH", "SOL", "XRP", "RENDER", "SUI", "APT", "DOGE", "BONK", "PEPE"]
        results = []

        for symbol in watchlist:
            market_data = await app.state.market.get_market_data(symbol)
            signal = await app.state.gemini.generate_signal(market_data)

            if signal.confidence >= 60:
                results.append({
                    "symbol": symbol,
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning,
                    "price": market_data.price,
                    "rsi": market_data.rsi,
                    "change_24h": market_data.change_24h
                })

        # Apply filters
        if minVolume > 0:
            results = [r for r in results if r.get("volume_24h", 0) >= minVolume]
        if minChange > 0:
            results = [r for r in results if abs(r.get("change_24h", 0)) >= minChange]
        if signal and signal != "all":
            results = [r for r in results if r.get("signal_type") == signal]

        # Sort
        if sortBy == "change_24h":
            results.sort(key=lambda x: abs(x.get("change_24h", 0)), reverse=True)
        elif sortBy == "rsi":
            results.sort(key=lambda x: x.get("rsi", 50))
        else:
            results.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        return {
            "scan_time": datetime.now().isoformat(),
            "symbols_scanned": len(watchlist),
            "signals_found": len(results),
            "tokens": results  # Frontend expects 'tokens'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# AUTOMATION
# -----------------------------------------------------------------------------

@app.get("/api/automation/status")
async def get_automation_status():
    """Get automation status"""
    return {
        "enabled": False,
        "mode": "paper",
        "trades_today": 1,
        "max_trades": 5,
        "min_confidence": 70,
        "last_scan": datetime.now().isoformat()
    }

@app.post("/api/automation/config")
async def update_automation(config: AutomationConfig):
    """Update automation configuration"""
    return {"status": "updated", "config": config.dict()}

# =============================================================================
# COUNCIL SYNC - GIO <-> AURORA Bridge
# =============================================================================

class CouncilMotion(BaseModel):
    """Motion from a Council member (GIO/AURORA/ARCHITECT)"""
    source: str  # "GIO", "AURORA", "ARCHITECT_PRIME"
    type: str  # "trade_proposal", "strategy_change", "risk_alert", "market_analysis"
    content: str
    confidence: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class CouncilVote(BaseModel):
    """Vote on a motion"""
    motion_id: str
    voter: str
    vote: str  # "approve", "reject", "abstain"
    reason: Optional[str] = None

@app.get("/api/council/state")
async def get_council_state():
    """Get current Council state from BRAIN.json"""
    try:
        brain_file = PROJECT_ROOT / "BRAIN.json"
        if brain_file.exists():
            with open(brain_file) as f:
                brain = json.load(f)

            return {
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "council": brain.get("ai_council", {}),
                "last_trade": brain.get("trading", {}).get("last_trade", {}),
                "portfolio_snapshot": {
                    "net_worth": brain.get("portfolio", {}).get("net_worth"),
                    "debt": brain.get("portfolio", {}).get("aave", {}).get("debt"),
                    "health_factor": brain.get("portfolio", {}).get("aave", {}).get("health_factor")
                },
                "december_campaign": brain.get("december_campaign", {}),
                "active_motions": brain.get("council_motions", [])
            }
        else:
            return {"status": "offline", "error": "BRAIN.json not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/council/sync")
async def sync_council(motion: CouncilMotion, background_tasks: BackgroundTasks):
    """Receive a motion from a Council member and sync to BRAIN.json"""
    try:
        brain_file = PROJECT_ROOT / "BRAIN.json"

        # Load current brain
        if brain_file.exists():
            with open(brain_file) as f:
                brain = json.load(f)
        else:
            brain = {}

        # Create motion record
        motion_record = {
            "id": f"M{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "source": motion.source,
            "type": motion.type,
            "content": motion.content,
            "confidence": motion.confidence,
            "data": motion.data,
            "timestamp": motion.timestamp or datetime.now().isoformat(),
            "status": "pending",
            "votes": []
        }

        # Initialize council_motions if not exists
        if "council_motions" not in brain:
            brain["council_motions"] = []

        # Add motion
        brain["council_motions"].append(motion_record)

        # Keep only last 50 motions
        brain["council_motions"] = brain["council_motions"][-50:]

        # Update last_updated
        brain["last_updated"] = datetime.now().isoformat()

        # Save brain
        with open(brain_file, "w") as f:
            json.dump(brain, f, indent=2)

        # Broadcast to WebSocket clients
        background_tasks.add_task(broadcast_council_motion, motion_record)

        # If it's a trade proposal, consult AURORA (Gemini agent)
        response = None
        if motion.type == "trade_proposal" and motion.data:
            try:
                analysis = await app.state.gemini.chat(
                    f"Council Motion from {motion.source}: {motion.content}",
                    {"motion_data": motion.data}
                )
                response = {
                    "aurora_analysis": analysis,
                    "aurora_timestamp": datetime.now().isoformat()
                }
            except:
                pass

        return {
            "status": "received",
            "motion_id": motion_record["id"],
            "message": f"Motion from {motion.source} logged to BRAIN.json",
            "aurora_response": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/council/vote")
async def vote_on_motion(vote: CouncilVote):
    """Cast a vote on a Council motion"""
    try:
        brain_file = PROJECT_ROOT / "BRAIN.json"

        with open(brain_file) as f:
            brain = json.load(f)

        # Find motion
        for motion in brain.get("council_motions", []):
            if motion["id"] == vote.motion_id:
                motion["votes"].append({
                    "voter": vote.voter,
                    "vote": vote.vote,
                    "reason": vote.reason,
                    "timestamp": datetime.now().isoformat()
                })

                # Check for consensus (2/3 votes)
                votes = motion["votes"]
                if len(votes) >= 2:
                    approvals = sum(1 for v in votes if v["vote"] == "approve")
                    if approvals >= 2:
                        motion["status"] = "approved"
                    elif len(votes) - approvals >= 2:
                        motion["status"] = "rejected"

                # Save
                with open(brain_file, "w") as f:
                    json.dump(brain, f, indent=2)

                return {
                    "status": "voted",
                    "motion_id": vote.motion_id,
                    "current_status": motion["status"],
                    "votes_count": len(votes)
                }

        raise HTTPException(status_code=404, detail="Motion not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def broadcast_council_motion(motion: dict):
    """Broadcast council motion to all WebSocket clients"""
    message = {
        "type": "council_motion",
        "data": motion
    }
    for ws in app.state.websockets:
        try:
            await ws.send_json(message)
        except:
            pass

# =============================================================================
# WEBSOCKET
# =============================================================================

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    app.state.websockets.append(websocket)

    try:
        while True:
            # Send heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })

            # Get prices
            prices = await app.state.market.get_prices(["BTC", "ETH", "SOL", "XRP"])
            await websocket.send_json({
                "type": "prices",
                "data": prices
            })

            await asyncio.sleep(5)

    except WebSocketDisconnect:
        app.state.websockets.remove(websocket)

async def broadcast_signal(signal):
    """Broadcast signal to all WebSocket clients"""
    message = {
        "type": "signal",
        "data": {
            "symbol": signal.symbol,
            "action": signal.action,
            "confidence": signal.confidence,
            "timestamp": signal.timestamp
        }
    }

    for ws in app.state.websockets:
        try:
            await ws.send_json(message)
        except:
            pass

# =============================================================================
# UNIFIED SOVEREIGN ENDPOINT (For AbacusAI Dashboard)
# =============================================================================

@app.get("/api/sovereign/unified")
async def get_unified_state():
    """
    Single endpoint that returns EVERYTHING for external dashboards.
    AbacusAI, Replit, or any dashboard can pull all data with one call.

    Returns: BRAIN.json + live prices + positions + signals + system status
    """
    try:
        # Load BRAIN.json
        brain_path = PROJECT_ROOT / "BRAIN.json"
        brain_data = {}
        if brain_path.exists():
            brain_data = json.loads(brain_path.read_text())

        # Get live prices
        prices = {}
        try:
            prices = await app.state.market.get_prices(["BTC", "ETH", "SOL", "XRP", "DOGE", "PEPE"])
        except:
            prices = brain_data.get("prices", {})

        # Get active signals
        signals = []
        try:
            signals = await app.state.signals.get_signals("pending")
        except:
            pass

        # Get positions
        positions = []
        try:
            sys.path.insert(0, str(PROJECT_ROOT / "strategies"))
            from swing_trade_engine import SwingTradeEngine, SwingConfig, TradeMode
            config = SwingConfig(mode=TradeMode.PAPER)
            engine = SwingTradeEngine(config)
            open_positions = engine.position_mgr.get_open_positions()
            positions = [
                {
                    "id": p.id,
                    "symbol": p.symbol,
                    "entry_price": p.entry_price,
                    "quantity": p.quantity,
                    "stop_loss": p.stop_loss,
                    "take_profit_1": p.take_profit_1,
                    "status": p.status
                }
                for p in open_positions
            ]
        except:
            pass

        # Load pending strategies from content ingestion
        pending_strategies = []
        strategies_dir = PROJECT_ROOT / "content_ingestion" / "strategies"
        if strategies_dir.exists():
            for f in strategies_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text())
                    if data.get("requires_review"):
                        pending_strategies.append({
                            "file": f.name,
                            "source": data.get("source", "unknown"),
                            "confidence": data.get("confidence", 0),
                            "indicators": data.get("indicators", [])
                        })
                except:
                    pass

        # December campaign status
        campaign = brain_data.get("december_campaign", {
            "status": "ACTIVE",
            "mode": "paper",
            "capital": 260,
            "max_position": 50,
            "stop_loss_pct": 3,
            "win_rate_target": 60
        })

        return {
            "timestamp": datetime.now().isoformat(),
            "status": "online",
            "version": "3.0.0",

            # Portfolio
            "portfolio": {
                "net_worth": brain_data.get("portfolio", {}).get("net_worth", 0),
                "ledger_total": brain_data.get("portfolio", {}).get("ledger_total", 0),
                "exchange_total": brain_data.get("portfolio", {}).get("exchange_total", 0),
                "aave_debt": brain_data.get("portfolio", {}).get("aave_debt", 0),
                "health_factor": brain_data.get("portfolio", {}).get("aave", {}).get("health_factor", 0),
                "allocation": brain_data.get("portfolio", {}).get("allocation", {})
            },

            # Live prices
            "prices": prices,

            # Trading
            "signals": {
                "pending": len(signals) if isinstance(signals, list) else 0,
                "items": signals[:5] if isinstance(signals, list) else []
            },
            "positions": {
                "open": len(positions),
                "items": positions
            },

            # Strategy pipeline
            "strategies": {
                "pending_review": len(pending_strategies),
                "items": pending_strategies[:5]
            },

            # Campaign
            "campaign": campaign,

            # System health
            "system": {
                "neural_hub": "online",
                "market_scanner": "scheduled",
                "state_updater": "scheduled",
                "last_brain_update": brain_data.get("last_updated", "unknown")
            }
        }

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }


@app.get("/api/sovereign/brain")
async def get_brain():
    """Direct access to BRAIN.json"""
    brain_path = PROJECT_ROOT / "BRAIN.json"
    if brain_path.exists():
        return json.loads(brain_path.read_text())
    return {"error": "BRAIN.json not found"}


@app.post("/api/sovereign/ingest")
async def ingest_content(url: str, content_type: str = "youtube"):
    """
    Ingest content from external sources
    Triggers content pipeline for strategy extraction
    """
    try:
        if content_type == "youtube":
            sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
            from youtube_transcriptor import YouTubeTranscriptor

            transcriptor = YouTubeTranscriptor()
            strategy = transcriptor.process_video(url)

            if strategy:
                return {
                    "status": "success",
                    "message": "Content processed and strategy extracted",
                    "strategy": strategy
                }
            else:
                return {
                    "status": "partial",
                    "message": "Downloaded but extraction failed"
                }
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/sovereign/github")
async def get_github_status():
    """
    Get GitHub repository status via git CLI
    Returns recent commits, uncommitted changes, and repo info
    """
    import subprocess

    try:
        # Recent commits
        commits_result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        commits = []
        if commits_result.returncode == 0:
            for line in commits_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1] if len(parts) > 1 else ""
                    })

        # Uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        changes = []
        if status_result.returncode == 0:
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status = line[:2].strip()
                    filepath = line[3:]
                    changes.append({
                        "status": status,
                        "file": filepath
                    })

        # Remote info
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        remote_url = ""
        if remote_result.returncode == 0:
            # Strip credentials from URL for display
            url = remote_result.stdout.strip()
            if "@" in url:
                url = "https://github.com/" + url.split("@github.com/")[1] if "@github.com/" in url else url
            remote_url = url

        # Branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        return {
            "repository": "LEDGERGHOST90/SOVEREIGN_SHADOW_3",
            "url": remote_url.replace(".git", ""),
            "branch": branch,
            "recent_commits": commits[:5],
            "uncommitted_changes": len(changes),
            "changes": changes[:10],
            "last_commit": commits[0] if commits else None
        }

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# ALPHA SOURCES (Sentiment + On-Chain + Sniper)
# =============================================================================

@app.get("/api/alpha/sentiment")
async def get_sentiment(symbols: str = "BTC,ETH,SOL,XRP"):
    """
    Get social sentiment for symbols
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
        from sentiment_scanner import SentimentScanner

        scanner = SentimentScanner()
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        results = scanner.scan_watchlist(symbol_list)

        return results

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/alpha/sentiment/signals")
async def get_sentiment_signals():
    """
    Get trading signals from sentiment
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
        from sentiment_scanner import SentimentScanner

        scanner = SentimentScanner()
        return {"signals": scanner.get_trading_signals()}

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/alpha/onchain")
async def get_onchain():
    """
    Get on-chain analytics (DEX volume, TVL flows)
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
        from onchain_monitor import OnChainMonitor

        monitor = OnChainMonitor()
        return monitor.run_full_scan()

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/alpha/onchain/signals")
async def get_onchain_signals():
    """
    Get trading signals from on-chain data
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
        from onchain_monitor import OnChainMonitor

        monitor = OnChainMonitor()
        return monitor.get_onchain_signals()

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/alpha/sniper/{chain}")
async def get_sniper_targets(chain: str = "solana", min_liquidity: float = 5000):
    """
    Get snipeable new token launches

    Args:
        chain: solana, ethereum, bsc
        min_liquidity: Minimum liquidity in USD
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))
        from onchain_monitor import OnChainMonitor

        monitor = OnChainMonitor()
        tokens = monitor.scan_new_tokens(chain, min_liquidity)

        # Convert to dict
        from dataclasses import asdict
        return {
            "chain": chain,
            "min_liquidity": min_liquidity,
            "count": len(tokens),
            "snipeable": len([t for t in tokens if t.snipe_eligible]),
            "tokens": [asdict(t) for t in tokens[:20]]
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/alpha/combined")
async def get_combined_alpha():
    """
    Get ALL alpha signals in one call
    Sentiment + On-Chain + Sniper opportunities
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "content_ingestion"))

        results = {
            "timestamp": datetime.now().isoformat(),
            "sentiment": {},
            "onchain": {},
            "sniper": {}
        }

        # Sentiment
        try:
            from sentiment_scanner import SentimentScanner
            scanner = SentimentScanner()
            results["sentiment"] = {
                "data": scanner.scan_watchlist(['BTC', 'ETH', 'SOL', 'XRP']),
                "signals": scanner.get_trading_signals()
            }
        except Exception as e:
            results["sentiment"] = {"error": str(e)}

        # On-chain
        try:
            from onchain_monitor import OnChainMonitor
            monitor = OnChainMonitor()
            results["onchain"] = monitor.get_onchain_signals()
        except Exception as e:
            results["onchain"] = {"error": str(e)}

        # Sniper (Solana by default)
        try:
            from onchain_monitor import OnChainMonitor
            from dataclasses import asdict
            monitor = OnChainMonitor()
            tokens = monitor.scan_new_tokens('solana', 5000)
            snipeable = [t for t in tokens if t.snipe_eligible]
            results["sniper"] = {
                "chain": "solana",
                "opportunities": len(snipeable),
                "top_5": [asdict(t) for t in snipeable[:5]]
            }
        except Exception as e:
            results["sniper"] = {"error": str(e)}

        return results

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

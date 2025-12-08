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
# HYBRID SYSTEM - Siphon Protocol, Profit Tracker, Ladder, Sniper Bridge
# =============================================================================

HYBRID_SYSTEM_PATH = PROJECT_ROOT / "hybrid_system"


@app.get("/api/sovereign/siphon")
async def get_siphon_status():
    """
    Get Cold Storage Siphon status
    Shows profit tracking and 30% withdrawal status
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from cold_storage_siphon import ColdStorageSiphon

        siphon = ColdStorageSiphon()

        # Get profit calculations from each exchange
        exchange_status = {}
        for exchange_name in ['coinbase', 'kraken']:
            try:
                profit_data = siphon.calculate_profits(exchange_name)
                exchange_status[exchange_name] = profit_data
            except Exception as e:
                exchange_status[exchange_name] = {"error": str(e)}

        return {
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "siphon_percentage": 30,
            "min_withdrawal_threshold": siphon.MIN_PROFIT_TO_WITHDRAW,
            "daily_limit": siphon.DAILY_WITHDRAWAL_LIMIT,
            "daily_used": siphon.daily_withdrawal_total,
            "ledger_addresses": {
                k: f"{v[:10]}...{v[-6:]}" for k, v in siphon.LEDGER_ADDRESSES.items()
            },
            "exchanges": exchange_status,
            "withdrawal_history": siphon.get_withdrawal_history()[-10:]
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/sovereign/siphon/dry-run")
async def run_siphon_dry_run():
    """
    Run siphon in dry-run mode (simulate withdrawals)
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from cold_storage_siphon import ColdStorageSiphon

        siphon = ColdStorageSiphon()
        results = siphon.auto_siphon_profits(dry_run=True)

        return {
            "status": "dry_run_complete",
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/sovereign/siphon/execute")
async def execute_siphon(confirm: bool = False):
    """
    Execute LIVE siphon (requires confirmation)
    WARNING: This will initiate real withdrawals to Ledger
    """
    if not confirm:
        return {
            "status": "blocked",
            "message": "Must pass confirm=true to execute live withdrawal",
            "warning": "This will withdraw real funds to your Ledger!"
        }

    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from cold_storage_siphon import ColdStorageSiphon

        siphon = ColdStorageSiphon()
        results = siphon.auto_siphon_profits(dry_run=False)

        return {
            "status": "executed",
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/sovereign/profit")
async def get_profit_status():
    """
    Get profit tracking status
    Shows P&L across all exchanges and 30% cold storage allocation
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from profit_tracker import ProfitTracker

        tracker = ProfitTracker()
        balances = tracker.fetch_exchange_balances()
        report = tracker.calculate_profits(balances)

        return {
            "timestamp": datetime.now().isoformat(),
            "report": report
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/sovereign/profit/recommendations")
async def get_profit_recommendations():
    """
    Get cold storage withdrawal recommendations
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from profit_tracker import ProfitTracker

        tracker = ProfitTracker()
        balances = tracker.fetch_exchange_balances()
        report = tracker.calculate_profits(balances)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_profit": report["totals"]["total_profit"],
            "cold_storage_allocation": report["totals"]["cold_storage_allocation"],
            "recommendations": report["recommendations"]
        }

    except Exception as e:
        return {"error": str(e)}


class LadderSignal(BaseModel):
    """Signal for ladder deployment"""
    symbol: str
    entry_price: float
    entry_low: Optional[float] = None
    entry_high: Optional[float] = None
    tp1_price: float
    tp2_price: Optional[float] = None
    tp3_price: Optional[float] = None
    sl_price: Optional[float] = None


@app.get("/api/sovereign/ladder")
async def get_ladder_status():
    """
    Get Unified Ladder System status
    Shows active ladders and their execution state
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from unified_ladder_system import UnifiedLadderSystem

        ladder = UnifiedLadderSystem()
        active = ladder.get_active_ladders()

        return {
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "min_ray_score": ladder.min_ray_score,
            "min_tp1_roi": ladder.min_tp1_roi,
            "max_drawdown": ladder.max_drawdown,
            "active_ladders": active
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/sovereign/ladder/validate")
async def validate_ladder_signal(signal: LadderSignal):
    """
    Validate a signal for ladder deployment
    Returns ray score and validation status
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from unified_ladder_system import UnifiedLadderSystem

        ladder = UnifiedLadderSystem()

        signal_dict = {
            "symbol": signal.symbol,
            "entry_price": signal.entry_price,
            "entry_low": signal.entry_low or signal.entry_price * 0.995,
            "entry_high": signal.entry_high or signal.entry_price * 1.005,
            "tp1_price": signal.tp1_price,
            "tp2_price": signal.tp2_price or signal.tp1_price * 1.10,
            "tp3_price": signal.tp3_price or signal.tp1_price * 1.25,
            "sl_price": signal.sl_price or signal.entry_price * 0.93
        }

        is_valid, rejection_reasons = ladder.validate_signal(signal_dict)
        ray_score = ladder.calculate_ray_score(signal_dict)

        return {
            "valid": is_valid,
            "ray_score": ray_score,
            "rejection_reasons": rejection_reasons,
            "signal_with_validation": signal_dict.get("validation", {})
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/sovereign/ladder/deploy")
async def deploy_ladder(signal: LadderSignal, capital: float = 100, mode: str = "paper"):
    """
    Deploy a ladder for a signal

    Args:
        signal: The trade signal
        capital: Capital to allocate (default $100)
        mode: 'paper' or 'live'
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from unified_ladder_system import UnifiedLadderSystem

        ladder = UnifiedLadderSystem()

        signal_dict = {
            "symbol": signal.symbol,
            "entry_price": signal.entry_price,
            "entry_low": signal.entry_low or signal.entry_price * 0.995,
            "entry_high": signal.entry_high or signal.entry_price * 1.005,
            "tp1_price": signal.tp1_price,
            "tp2_price": signal.tp2_price or signal.tp1_price * 1.10,
            "tp3_price": signal.tp3_price or signal.tp1_price * 1.25,
            "sl_price": signal.sl_price or signal.entry_price * 0.93
        }

        result = ladder.deploy_ladder(signal_dict, capital, mode)

        return result

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/sovereign/sniper-bridge")
async def get_sniper_bridge_status():
    """
    Get Shadow Sniper Bridge status
    Shows connection to desktop sniper system
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from shadow_sniper_bridge import ShadowSniperBridge

        bridge = ShadowSniperBridge()
        status = bridge.check_shadow_sniper_status()
        pnl = bridge.read_shadow_sniper_pnl()

        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "pnl_data": pnl
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/sovereign/sniper-bridge/sync")
async def sync_sniper_bridge():
    """
    Sync Shadow Sniper data to profit tracker
    """
    try:
        sys.path.insert(0, str(HYBRID_SYSTEM_PATH))
        from shadow_sniper_bridge import ShadowSniperBridge

        bridge = ShadowSniperBridge()
        success = bridge.sync_to_profit_tracker()

        return {
            "status": "synced" if success else "failed",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# TRADING SWARM ENDPOINTS
# =============================================================================

SWARM_CONFIG_PATH = PROJECT_ROOT / "config" / "swarm_config.json"
BIN_PATH = PROJECT_ROOT / "bin"

@app.get("/api/swarm/status")
async def get_swarm_status():
    """
    Get Trading Swarm status
    Shows swarm config, psychology state, recent scans
    """
    try:
        result = {
            "timestamp": datetime.now().isoformat(),
            "swarm_type": "trading_swarm"
        }

        # Load swarm config
        if SWARM_CONFIG_PATH.exists():
            with open(SWARM_CONFIG_PATH) as f:
                config = json.load(f)
            result["config"] = {
                "mode": config.get("mode"),
                "risk_rules": config.get("risk_rules", {}).get("position_sizing", {}),
                "december_targets": config.get("december_targets", {})
            }
        else:
            result["config"] = {"error": "Config not found"}

        # Check psychology/strikes
        loss_log = PROJECT_ROOT / "logs" / "psychology" / "loss_streak.json"
        if loss_log.exists():
            with open(loss_log) as f:
                psych_data = json.load(f)
            today = datetime.now().strftime("%Y-%m-%d")
            strikes = psych_data.get("count", 0) if psych_data.get("date") == today else 0
        else:
            strikes = 0

        result["psychology"] = {
            "strikes": strikes,
            "max_strikes": 3,
            "trading_allowed": strikes < 3,
            "status": "CLEAR" if strikes < 3 else "LOCKED"
        }

        # Recent scan logs
        log_dir = PROJECT_ROOT / "logs" / "swarm"
        if log_dir.exists():
            scans = sorted(log_dir.glob("scan_*.json"), reverse=True)[:5]
            result["recent_scans"] = [s.name for s in scans]
        else:
            result["recent_scans"] = []

        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/swarm/scan")
async def run_swarm_scan(scan_type: str = "breakout"):
    """
    Trigger a swarm scan cycle

    Scan types:
    - breakout: High momentum plays
    - kings: Top performers
    - trending: Trending tokens
    - smart-buys: Value opportunities
    - full: All scan types
    """
    import subprocess

    try:
        if scan_type == "full":
            cmd = ["python3", str(BIN_PATH / "trading_swarm.py"), "--scan"]
        else:
            cmd = ["python3", "-m", "meme_machine", f"--{scan_type}", "--min-score", "70"]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "status": "completed",
            "scan_type": scan_type,
            "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "timestamp": datetime.now().isoformat()
        }

    except subprocess.TimeoutExpired:
        return {"status": "timeout", "scan_type": scan_type}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/swarm/intelligence")
async def get_swarm_intelligence():
    """
    Get Swarm Intelligence Bridge data
    Shows AI swarm P&L aggregation (Agent Swarm, Shadow Army, Hive Mind)
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "hybrid_system"))
        from swarm_intelligence_bridge import SwarmIntelligenceBridge

        bridge = SwarmIntelligenceBridge()
        status = bridge.check_swarm_systems_status()
        aggregated = bridge.aggregate_swarm_pnl()

        return {
            "timestamp": datetime.now().isoformat(),
            "systems_status": status,
            "aggregated_pnl": aggregated
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/swarm/intelligence/sync")
async def sync_swarm_intelligence():
    """
    Sync Swarm Intelligence data to profit tracker
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "hybrid_system"))
        from swarm_intelligence_bridge import SwarmIntelligenceBridge

        bridge = SwarmIntelligenceBridge()
        success = bridge.sync_to_profit_tracker()

        return {
            "status": "synced" if success else "failed",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/swarm/smart-signals")
async def get_smart_signals():
    """
    Get latest smart signals (proven alpha sources)
    Fear & Greed + Funding Rates + DEX Volume + Sentiment
    """
    try:
        signals_file = PROJECT_ROOT / "logs" / "smart_signals.json"

        if signals_file.exists():
            with open(signals_file) as f:
                signals = json.load(f)
            return signals
        else:
            return {
                "error": "No smart signals found",
                "hint": "Run: python3 bin/smart_signals.py"
            }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/swarm/smart-signals/generate")
async def generate_smart_signals():
    """
    Generate fresh smart signals from proven alpha sources
    """
    import subprocess

    try:
        result = subprocess.run(
            ["python3", str(BIN_PATH / "smart_signals.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )

        # Read the generated signals
        signals_file = PROJECT_ROOT / "logs" / "smart_signals.json"
        if signals_file.exists():
            with open(signals_file) as f:
                signals = json.load(f)
            return {
                "status": "generated",
                "signals": signals
            }
        else:
            return {
                "status": "error",
                "output": result.stdout
            }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/swarm/best-signals")
async def get_best_signals():
    """
    Get latest best signals scan (70 assets)
    """
    try:
        signals_file = PROJECT_ROOT / "logs" / "best_signals.json"

        if signals_file.exists():
            with open(signals_file) as f:
                signals = json.load(f)
            return signals
        else:
            return {
                "error": "No best signals found",
                "hint": "Run: python3 bin/best_signals.py"
            }

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# MARKET TICKER ENDPOINTS
# =============================================================================

@app.get("/api/ticker/prices")
async def get_market_ticker():
    """
    Get real-time prices for all watched assets
    Similar to birdeye.io heat map data
    """
    import requests

    try:
        # Watchlist
        symbols = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX",
                   "LINK", "DOT", "SHIB", "LTC", "UNI", "AAVE", "MATIC", "ATOM"]

        # CoinGecko IDs
        cg_ids = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple",
            "BNB": "binancecoin", "DOGE": "dogecoin", "ADA": "cardano", "AVAX": "avalanche-2",
            "LINK": "chainlink", "DOT": "polkadot", "SHIB": "shiba-inu", "LTC": "litecoin",
            "UNI": "uniswap", "AAVE": "aave", "MATIC": "matic-network", "ATOM": "cosmos"
        }

        ids = [cg_ids[s] for s in symbols if s in cg_ids]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"

        resp = requests.get(url, timeout=10)
        data = resp.json()

        # Format response
        prices = {}
        for symbol in symbols:
            cg_id = cg_ids.get(symbol)
            if cg_id and cg_id in data:
                change = data[cg_id].get("usd_24h_change", 0)
                prices[symbol] = {
                    "price": data[cg_id].get("usd", 0),
                    "change_24h": change,
                    "heat": "hot" if change > 5 else "warm" if change > 0 else "cool" if change > -5 else "cold"
                }

        return {
            "timestamp": datetime.now().isoformat(),
            "prices": prices
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/ticker/portfolio")
async def get_portfolio_ticker():
    """
    Get portfolio values with real-time prices
    Includes Ledger cold storage
    """
    import requests

    try:
        # Load BRAIN.json for holdings
        brain_path = PROJECT_ROOT / "BRAIN.json"
        if brain_path.exists():
            with open(brain_path) as f:
                brain = json.load(f)
        else:
            brain = {}

        # Ledger holdings
        ledger = brain.get("ledger_holdings", {
            "BTC": 0.0157,
            "wstETH": 0.897,
            "XRP": 456.0,
            "USDC": 53.61
        })

        # Get prices
        cg_ids = {
            "BTC": "bitcoin", "ETH": "ethereum", "wstETH": "wrapped-steth",
            "XRP": "ripple", "SOL": "solana"
        }

        ids = [cg_ids[s] for s in ledger.keys() if s in cg_ids]
        if ids:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
            resp = requests.get(url, timeout=10)
            prices = resp.json()
        else:
            prices = {}

        # Calculate values
        portfolio = {}
        total_value = 0

        for symbol, amount in ledger.items():
            cg_id = cg_ids.get(symbol)
            if cg_id and cg_id in prices:
                price = prices[cg_id].get("usd", 0)
                change = prices[cg_id].get("usd_24h_change", 0)
            elif symbol == "USDC":
                price = 1.0
                change = 0
            else:
                price = 0
                change = 0

            value = amount * price
            total_value += value

            portfolio[symbol] = {
                "amount": amount,
                "price": price,
                "value": value,
                "change_24h": change
            }

        # AAVE debt
        aave_debt = brain.get("aave_debt", 360.94)

        return {
            "timestamp": datetime.now().isoformat(),
            "holdings": portfolio,
            "total_value": total_value,
            "aave_debt": aave_debt,
            "net_worth": total_value - aave_debt
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/sovereign/complete")
async def get_complete_system_status():
    """
    MASTER ENDPOINT - Get ENTIRE system status in one call

    Includes:
    - Portfolio (BRAIN.json)
    - Prices
    - Signals
    - Positions
    - Alpha sources (sentiment, on-chain, sniper)
    - Siphon protocol
    - Profit tracker
    - Ladder system
    - Sniper bridge
    - Trading Swarm
    - Market Ticker
    - System health
    """
    try:
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.1.0-complete-with-swarm",
            "status": "online"
        }

        # Base unified state
        try:
            unified = await get_unified_state()
            result["unified"] = unified
        except Exception as e:
            result["unified"] = {"error": str(e)}

        # Siphon Protocol
        try:
            siphon = await get_siphon_status()
            result["siphon"] = siphon
        except Exception as e:
            result["siphon"] = {"error": str(e)}

        # Profit Tracker
        try:
            profit = await get_profit_status()
            result["profit"] = profit
        except Exception as e:
            result["profit"] = {"error": str(e)}

        # Ladder System
        try:
            ladder = await get_ladder_status()
            result["ladder"] = ladder
        except Exception as e:
            result["ladder"] = {"error": str(e)}

        # Sniper Bridge
        try:
            sniper = await get_sniper_bridge_status()
            result["sniper_bridge"] = sniper
        except Exception as e:
            result["sniper_bridge"] = {"error": str(e)}

        # Alpha Sources
        try:
            alpha = await get_combined_alpha()
            result["alpha"] = alpha
        except Exception as e:
            result["alpha"] = {"error": str(e)}

        # Trading Swarm
        try:
            swarm = await get_swarm_status()
            result["swarm"] = swarm
        except Exception as e:
            result["swarm"] = {"error": str(e)}

        # Smart Signals
        try:
            signals = await get_smart_signals()
            result["smart_signals"] = signals
        except Exception as e:
            result["smart_signals"] = {"error": str(e)}

        # Market Ticker
        try:
            ticker = await get_market_ticker()
            result["ticker"] = ticker
        except Exception as e:
            result["ticker"] = {"error": str(e)}

        # Portfolio Ticker
        try:
            portfolio = await get_portfolio_ticker()
            result["portfolio_ticker"] = portfolio
        except Exception as e:
            result["portfolio_ticker"] = {"error": str(e)}

        return result

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# AURORA NOTIFICATION ENDPOINTS
# =============================================================================

NTFY_TOPIC = "ntfy.sh/sovereignshadow_dc4d2fa1"

class NotificationRequest(BaseModel):
    message: str
    title: Optional[str] = "Sovereign Shadow"
    priority: Optional[str] = "default"
    tags: Optional[List[str]] = None


@app.post("/api/aurora/push")
async def send_push_notification(notification: NotificationRequest):
    """
    Send push notification via ntfy.sh
    """
    import requests as req

    try:
        headers = {
            "Title": notification.title,
            "Priority": notification.priority
        }

        if notification.tags:
            headers["Tags"] = ",".join(notification.tags)

        resp = req.post(
            f"https://{NTFY_TOPIC}",
            data=notification.message,
            headers=headers,
            timeout=10
        )

        return {
            "status": "sent" if resp.status_code == 200 else "failed",
            "code": resp.status_code,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/aurora/speak")
async def aurora_speak(message: str):
    """
    Make Aurora speak (macOS text-to-speech)
    Falls back to system voice if ElevenLabs not configured
    """
    import subprocess

    try:
        # Use macOS say command
        subprocess.run(["say", "-v", "Samantha", message], check=True, timeout=30)
        return {
            "status": "spoken",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/aurora/alert")
async def aurora_alert(symbol: str, action: str, confidence: int, reason: str = ""):
    """
    Send full alert (push + voice) for trading signal
    """
    import requests as req
    import subprocess

    try:
        # Push notification
        title = f"{action} Signal: {symbol}"
        message = f"{symbol} {action} ({confidence}%)"
        if reason:
            message += f"\n{reason}"

        tags = ["chart_with_upwards_trend", "money_mouth_face"] if "BUY" in action else ["warning"]
        priority = "high" if confidence >= 80 else "default"

        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": ",".join(tags)
        }

        push_resp = req.post(
            f"https://{NTFY_TOPIC}",
            data=message,
            headers=headers,
            timeout=10
        )

        # Voice alert for high confidence
        voice_status = "skipped"
        if confidence >= 80:
            try:
                speech = f"Alert! High confidence {action.lower()} signal on {symbol}. {confidence} percent confidence."
                subprocess.run(["say", "-v", "Samantha", speech], check=True, timeout=30)
                voice_status = "spoken"
            except:
                voice_status = "failed"

        return {
            "push_status": "sent" if push_resp.status_code == 200 else "failed",
            "voice_status": voice_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/aurora/watch/start")
async def start_aurora_watch(background_tasks: BackgroundTasks):
    """
    Start Aurora signal watching in background
    Monitors for high-confidence signals and sends alerts
    """
    async def watch_loop():
        import time
        import requests as req

        while True:
            try:
                # Get smart signals
                resp = req.get(f"http://localhost:8000/api/swarm/smart-signals", timeout=15)
                data = resp.json()

                if "market_state" in data:
                    fng = data["market_state"]["fear_greed"]["value"]

                    # Alert at extremes
                    if fng <= 25 or fng >= 75:
                        title = "EXTREME FEAR" if fng <= 25 else "EXTREME GREED"
                        msg = f"Fear & Greed at {fng}"
                        req.post(
                            f"https://{NTFY_TOPIC}",
                            data=msg,
                            headers={"Title": title, "Priority": "urgent"},
                            timeout=10
                        )

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                time.sleep(60)

    background_tasks.add_task(watch_loop)
    return {"status": "Aurora watching started"}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

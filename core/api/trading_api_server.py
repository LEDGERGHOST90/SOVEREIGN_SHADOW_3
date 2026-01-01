#!/usr/bin/env python3
"""
🌐 Sovereign Shadow Trading API Server

RESTful API + WebSocket interface for neural consciousness integration.

Endpoints:
- GET  /api/strategy/performance  - Strategy metrics and performance
- POST /api/trade/execute         - Execute trades with validation
- POST /api/dashboard/update      - Dashboard event updates
- WS   /ws/dashboard              - Real-time dashboard stream

Part of the Sovereign Shadow Trading System
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    print("⚠️ FastAPI not installed. Run: pip install fastapi uvicorn websockets")
    sys.exit(1)

from core.trading.tactical_risk_gate import TacticalRiskGate, TradeRequest, ValidationResult
from strategy_knowledge_base import StrategyKnowledgeBase

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class StrategyPerformance(BaseModel):
    """Strategy performance metrics"""
    name: str
    type: str
    total_trades: int
    total_profit: float
    success_rate: float
    avg_execution_time: float
    last_trade: Optional[str] = None
    status: str = "active"


class PerformanceResponse(BaseModel):
    """GET /api/strategy/performance response"""
    strategies: List[StrategyPerformance]
    total_profit: float
    total_trades: int
    session_start: str


class TradeExecutionRequest(BaseModel):
    """POST /api/trade/execute request"""
    strategy: str
    pair: str
    amount: float
    exchanges: Optional[List[str]] = None
    side: Optional[str] = "auto"  # auto, long, short
    mode: Optional[str] = "paper"  # paper, test, live


class TradeExecutionResponse(BaseModel):
    """POST /api/trade/execute response"""
    trade_id: str
    status: str
    profit: Optional[float] = None
    execution_time: Optional[float] = None
    timestamp: str
    validation_warnings: List[str] = []
    risk_adjustments: Dict = {}


class DashboardUpdateRequest(BaseModel):
    """POST /api/dashboard/update request"""
    event: str
    data: Dict


class DashboardUpdateResponse(BaseModel):
    """POST /api/dashboard/update response"""
    success: bool
    dashboard_updated: bool
    timestamp: str


class HealthCheckResponse(BaseModel):
    """GET /api/health response"""
    status: str
    uptime_seconds: float
    active_strategies: int
    risk_gate_status: str
    aave_health_factor: Optional[float] = None
    session_pnl: float


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.reconnect_attempts: Dict[WebSocket, int] = {}
        self.max_reconnect_attempts = 3
    
    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.reconnect_attempts[websocket] = 0
            logger.info(f"🔌 WebSocket connected ({len(self.active_connections)} active)")
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}")
            raise
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.reconnect_attempts:
            del self.reconnect_attempts[websocket]
        logger.info(f"🔌 WebSocket disconnected ({len(self.active_connections)} active)")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients with reconnection handling"""
        dead_connections = []
        for connection in self.active_connections[:]:  # Copy list to avoid modification during iteration
            try:
                await connection.send_json(message)
                # Reset reconnect attempts on successful send
                if connection in self.reconnect_attempts:
                    self.reconnect_attempts[connection] = 0
            except (WebSocketDisconnect, ConnectionResetError, BrokenPipeError) as e:
                logger.warning(f"WebSocket disconnected during broadcast: {type(e).__name__}")
                dead_connections.append(connection)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                # Track failed attempts
                if connection in self.reconnect_attempts:
                    self.reconnect_attempts[connection] += 1
                    if self.reconnect_attempts[connection] >= self.max_reconnect_attempts:
                        dead_connections.append(connection)
                else:
                    self.reconnect_attempts[connection] = 1
        
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client with error handling"""
        try:
            await websocket.send_json(message)
            # Reset reconnect attempts on successful send
            if websocket in self.reconnect_attempts:
                self.reconnect_attempts[websocket] = 0
        except (WebSocketDisconnect, ConnectionResetError, BrokenPipeError) as e:
            logger.warning(f"WebSocket disconnected: {type(e).__name__}")
            self.disconnect(websocket)
            raise
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            raise


# ============================================================================
# Trading API Server
# ============================================================================

class TradingAPIServer:
    """Main API server for Sovereign Shadow trading system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.app = FastAPI(
            title="Sovereign Shadow Trading API",
            description="🏴 Neural consciousness bridge for the Sovereign Shadow trading system",
            version="1.0.0"
        )
        
        # CORS for external access
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://shadow-ai-alpharunner-33906555678.us-west1.run.app", "http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.config_path = config_path or "/Volumes/LegacySafe/SovereignShadow/config/tactical_scalp_config.json"
        self.risk_gate = TacticalRiskGate(config_path=self.config_path)
        self.strategy_kb = StrategyKnowledgeBase()
        self.ws_manager = ConnectionManager()
        
        # Session tracking
        self.server_start_time = datetime.now()
        self.trade_history: List[Dict] = []
        self.strategy_performance: Dict[str, Dict] = {}
        
        # Initialize strategy performance from knowledge base
        self._initialize_strategy_performance()
        
        # Register routes
        self._register_routes()
        
        logger.info("🌐 Trading API Server initialized")
    
    def _initialize_strategy_performance(self):
        """Initialize strategy performance tracking"""
        strategies = self.strategy_kb.get_all_strategies()
        
        # strategies is a Dict[str, TradingStrategy]
        for strategy_key, strategy in strategies.items():
            self.strategy_performance[strategy.name] = {
                "type": strategy.type,
                "total_trades": 0,
                "total_profit": 0.0,
                "successful_trades": 0,
                "failed_trades": 0,
                "execution_times": [],
                "last_trade": None
            }
        
        logger.info(f"📊 Initialized tracking for {len(strategies)} strategies")
    
    def _register_routes(self):
        """Register all API routes"""
        
        @self.app.get("/", tags=["info"])
        async def root():
            return {
                "service": "Sovereign Shadow Trading API",
                "version": "1.0.0",
                "status": "operational",
                "endpoints": [
                    "/api/health",
                    "/api/strategy/performance",
                    "/api/trade/execute",
                    "/api/dashboard/update",
                    "/ws/dashboard"
                ]
            }
        
        @self.app.get("/api/health", response_model=HealthCheckResponse, tags=["monitoring"])
        async def health_check():
            """Health check endpoint"""
            uptime = (datetime.now() - self.server_start_time).total_seconds()
            stats = self.risk_gate.get_session_stats()
            
            return HealthCheckResponse(
                status="healthy",
                uptime_seconds=uptime,
                active_strategies=len([k for k, v in self.strategy_performance.items() if v["total_trades"] > 0]),
                risk_gate_status="operational",
                aave_health_factor=stats.get("aave_health_factor"),
                session_pnl=stats.get("session_pnl_usd", 0.0)
            )
        
        @self.app.get("/api/strategy/performance", response_model=PerformanceResponse, tags=["strategy"])
        async def get_strategy_performance():
            """Get performance metrics for all strategies"""
            
            strategies = []
            total_profit = 0.0
            total_trades = 0
            
            for name, perf in self.strategy_performance.items():
                if perf["total_trades"] == 0:
                    success_rate = 0.0
                    avg_exec_time = 0.0
                else:
                    success_rate = perf["successful_trades"] / perf["total_trades"]
                    avg_exec_time = sum(perf["execution_times"]) / len(perf["execution_times"]) if perf["execution_times"] else 0.0
                
                strategies.append(StrategyPerformance(
                    name=name,
                    type=perf["type"],
                    total_trades=perf["total_trades"],
                    total_profit=perf["total_profit"],
                    success_rate=success_rate,
                    avg_execution_time=avg_exec_time,
                    last_trade=perf["last_trade"],
                    status="active" if perf["total_trades"] > 0 else "idle"
                ))
                
                total_profit += perf["total_profit"]
                total_trades += perf["total_trades"]
            
            return PerformanceResponse(
                strategies=strategies,
                total_profit=total_profit,
                total_trades=total_trades,
                session_start=self.server_start_time.isoformat()
            )
        
        @self.app.post("/api/trade/execute", response_model=TradeExecutionResponse, tags=["trading"])
        async def execute_trade(request: TradeExecutionRequest, background_tasks: BackgroundTasks):
            """Execute a trade with full risk validation"""
            
            logger.info(f"🎯 Trade execution request: {request.strategy} | {request.pair} | ${request.amount}")
            
            # Parse pair (e.g., "BTC/USD" -> "BTC")
            asset = request.pair.split("/")[0]
            
            # Determine side based on strategy type
            if request.side == "auto":
                # Try to find strategy by display name or key
                strategy_info = None
                for key, strat in self.strategy_kb.get_all_strategies().items():
                    if strat.name == request.strategy or key == request.strategy:
                        strategy_info = strat
                        break
                
                if not strategy_info:
                    raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy}' not found")
                
                # For arbitrage, always "long" (buy low, sell high)
                # For other strategies, would need more context
                side = "long" if "arbitrage" in strategy_info.type.lower() else "long"
            else:
                side = request.side
            
            # Create trade request for validation
            trade_request = TradeRequest(
                strategy_name=request.strategy,
                asset=asset,
                side=side,
                notional_usd=request.amount,
                stop_loss_bps=28,  # Default from tactical config
                entry_price=0.0,  # Would get current market price
                conditions_met={"api_request": True},
                timestamp=datetime.now()
            )
            
            # Validate through risk gate
            validation = self.risk_gate.validate_trade(trade_request)
            
            if not validation.approved:
                logger.warning(f"❌ Trade rejected: {validation.reason}")
                raise HTTPException(status_code=400, detail={
                    "error": "Trade rejected by risk gate",
                    "reason": validation.reason,
                    "warnings": validation.warnings
                })
            
            # Adjust amount based on risk gate
            adjusted_amount = request.amount * validation.size_adjustment
            
            # Generate trade ID
            trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Execute trade (in production, this would call actual exchange APIs)
            if request.mode == "paper":
                logger.info(f"📝 Paper trade: {trade_id}")
                execution_time = 0.5
                profit = adjusted_amount * 0.005  # Simulated 0.5% profit
                status = "completed"
            elif request.mode == "test":
                logger.info(f"🧪 Test trade: {trade_id}")
                execution_time = 0.8
                profit = adjusted_amount * 0.003  # Simulated 0.3% profit
                status = "completed"
            else:
                logger.warning(f"🔴 Live trade requested: {trade_id}")
                # In production, would execute real trade here
                execution_time = 0.0
                profit = 0.0
                status = "pending"
            
            # Record trade
            self.risk_gate.add_trade_to_session(trade_id, trade_request)
            
            # Update strategy performance
            if request.strategy in self.strategy_performance:
                perf = self.strategy_performance[request.strategy]
                perf["total_trades"] += 1
                perf["total_profit"] += profit
                if profit > 0:
                    perf["successful_trades"] += 1
                else:
                    perf["failed_trades"] += 1
                perf["execution_times"].append(execution_time)
                perf["last_trade"] = datetime.now().isoformat()
            
            # Broadcast to WebSocket clients
            background_tasks.add_task(
                self.ws_manager.broadcast,
                {
                    "event": "trade_completed",
                    "data": {
                        "trade_id": trade_id,
                        "strategy": request.strategy,
                        "pair": request.pair,
                        "amount": adjusted_amount,
                        "profit": profit,
                        "execution_time": execution_time,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            
            return TradeExecutionResponse(
                trade_id=trade_id,
                status=status,
                profit=profit,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
                validation_warnings=validation.warnings,
                risk_adjustments={
                    "original_amount": request.amount,
                    "adjusted_amount": adjusted_amount,
                    "size_multiplier": validation.size_adjustment,
                    "stop_loss_bps": validation.stop_adjustment_bps
                }
            )
        
        @self.app.post("/api/dashboard/update", response_model=DashboardUpdateResponse, tags=["dashboard"])
        async def dashboard_update(request: DashboardUpdateRequest, background_tasks: BackgroundTasks):
            """Process dashboard update events"""
            
            logger.info(f"📊 Dashboard update: {request.event}")
            
            # Handle different event types
            if request.event == "trade_completed":
                data = request.data
                trade_id = data.get("trade_id")
                profit = data.get("profit", 0.0)
                
                # Record trade result
                self.risk_gate.record_trade_result(
                    trade_id=trade_id,
                    pnl_usd=profit,
                    was_loss=(profit < 0)
                )
                
                logger.info(f"✅ Trade {trade_id} recorded: ${profit:+.2f}")
            
            elif request.event == "market_update":
                # Update market data in risk gate
                data = request.data
                if "positioning" in data:
                    pos = data["positioning"]
                    self.risk_gate.update_positioning(
                        asset=pos.get("asset", "BTC"),
                        long_pct=pos.get("long_pct", 50.0),
                        short_pct=pos.get("short_pct", 50.0)
                    )
            
            elif request.event == "health_factor_update":
                hf = request.data.get("health_factor")
                if hf:
                    self.risk_gate.update_aave_health_factor(hf)
            
            # Broadcast to all connected clients
            background_tasks.add_task(
                self.ws_manager.broadcast,
                {
                    "event": request.event,
                    "data": request.data,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return DashboardUpdateResponse(
                success=True,
                dashboard_updated=True,
                timestamp=datetime.now().isoformat()
            )
        
        @self.app.websocket("/ws/dashboard")
        async def websocket_dashboard(websocket: WebSocket):
            """WebSocket endpoint for real-time dashboard updates"""
            
            await self.ws_manager.connect(websocket)
            
            try:
                # Send initial state
                await websocket.send_json({
                    "event": "connected",
                    "data": {
                        "session_start": self.server_start_time.isoformat(),
                        "active_strategies": len(self.strategy_performance),
                        "status": "operational"
                    }
                })
                
                # Keep connection alive and handle incoming messages
                while True:
                    data = await websocket.receive_json()
                    
                    # Handle ping/pong
                    if data.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    
                    # Handle data requests
                    elif data.get("type") == "request_stats":
                        stats = self.risk_gate.get_session_stats()
                        await websocket.send_json({
                            "event": "stats_update",
                            "data": stats
                        })
            
            except (WebSocketDisconnect, ConnectionResetError, BrokenPipeError) as e:
                logger.info(f"WebSocket disconnected: {type(e).__name__}")
                self.ws_manager.disconnect(websocket)
            except asyncio.CancelledError:
                logger.info("WebSocket connection cancelled")
                self.ws_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.ws_manager.disconnect(websocket)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the API server"""
        logger.info(f"🚀 Starting Sovereign Shadow Trading API on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🏴 Sovereign Shadow Trading API Server"
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to tactical scalp config'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # Create and run server
    server = TradingAPIServer(config_path=args.config)
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()


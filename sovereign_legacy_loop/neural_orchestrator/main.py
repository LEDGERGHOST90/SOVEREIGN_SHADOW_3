#!/usr/bin/env python3
"""
🧠 Neural Orchestrator - Backend for The Legacy Loop
===================================================

Powers the glassmorphic neural consciousness dashboard at:
https://legacyloopshadowai.abacusai.app/dashboard

Coordinates all 7 trading systems and provides real-time data aggregation.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    ConsciousnessValue, TierAData, TierBData, ShadowAIStatus,
    MigrationStatus, SystemHealth, TradeSignal, ExecutionResult
)
from services.neural_aggregator import NeuralAggregator
from services.system_coordinator import SystemCoordinator
from services.websocket_manager import WebSocketManager
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
neural_aggregator: Optional[NeuralAggregator] = None
system_coordinator: Optional[SystemCoordinator] = None
websocket_manager: Optional[WebSocketManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    global neural_aggregator, system_coordinator, websocket_manager
    
    logger.info("🧠 Initializing Neural Orchestrator...")
    
    # Initialize services
    neural_aggregator = NeuralAggregator()
    system_coordinator = SystemCoordinator()
    websocket_manager = WebSocketManager()
    
    # Start background tasks
    asyncio.create_task(periodic_consciousness_update())
    asyncio.create_task(system_health_monitor())
    
    logger.info("✅ Neural Orchestrator initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Neural Orchestrator...")
    if websocket_manager:
        await websocket_manager.disconnect_all()


# Create FastAPI app
app = FastAPI(
    title="Neural Orchestrator",
    description="Backend for The Legacy Loop neural consciousness dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for website integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://legacyloopshadowai.abacusai.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - system status."""
    return {
        "status": "online",
        "service": "Neural Orchestrator",
        "timestamp": datetime.utcnow().isoformat(),
        "website": "https://legacyloopshadowai.abacusai.app/dashboard"
    }


@app.get("/api/neural/consciousness-value", response_model=ConsciousnessValue)
async def get_consciousness_value():
    """Get total consciousness value for the main dashboard display."""
    try:
        value = await neural_aggregator.get_total_consciousness_value()
        return value
    except Exception as e:
        logger.error(f"Error getting consciousness value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neural/tier-a", response_model=TierAData)
async def get_tier_a():
    """Get Tier A (Preservation) data - Ledger Live + Coinbase."""
    try:
        tier_a = await neural_aggregator.get_tier_a_data()
        return tier_a
    except Exception as e:
        logger.error(f"Error getting Tier A data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neural/tier-b", response_model=TierBData)
async def get_tier_b():
    """Get Tier B (Flip Engine) data - ONDO + USDT."""
    try:
        tier_b = await neural_aggregator.get_tier_b_data()
        return tier_b
    except Exception as e:
        logger.error(f"Error getting Tier B data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neural/shadow-ai-status", response_model=ShadowAIStatus)
async def get_shadow_ai_status():
    """Get SHADOW.AI status and neural ganglion state."""
    try:
        status = await neural_aggregator.get_shadow_ai_status()
        return status
    except Exception as e:
        logger.error(f"Error getting SHADOW.AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neural/migration-status", response_model=MigrationStatus)
async def get_migration_status():
    """Get migration status (e.g., Binance.US → Ledger Live)."""
    try:
        migration = await neural_aggregator.get_migration_status()
        return migration
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/neural/system-health", response_model=SystemHealth)
async def get_system_health():
    """Get health status of all 7 trading systems."""
    try:
        health = await system_coordinator.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/neural/execute-signal", response_model=ExecutionResult)
async def execute_signal(signal: TradeSignal):
    """Execute a coordinated trade signal across systems."""
    try:
        result = await system_coordinator.execute_signal(signal)
        
        # Broadcast update to all connected clients
        await websocket_manager.broadcast_consciousness_update()
        
        return result
    except Exception as e:
        logger.error(f"Error executing signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/neural/emergency-stop")
async def emergency_stop():
    """Emergency stop all trading systems."""
    try:
        result = await system_coordinator.emergency_stop_all()
        
        # Broadcast emergency status
        await websocket_manager.broadcast_emergency_status()
        
        return {"status": "emergency_stop_executed", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates to the website."""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Could handle client commands here if needed
            logger.debug(f"Received WebSocket message: {data}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def periodic_consciousness_update():
    """Periodically update consciousness value and broadcast to clients."""
    while True:
        try:
            # Update consciousness value
            await neural_aggregator.refresh_consciousness_data()
            
            # Broadcast to all connected clients
            await websocket_manager.broadcast_consciousness_update()
            
            # Wait 30 seconds before next update
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in periodic consciousness update: {e}")
            await asyncio.sleep(60)  # Wait longer on error


async def system_health_monitor():
    """Monitor system health and broadcast alerts."""
    while True:
        try:
            # Check system health
            health = await system_coordinator.check_all_systems()
            
            # Broadcast health updates
            await websocket_manager.broadcast_health_update(health)
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in system health monitor: {e}")
            await asyncio.sleep(120)  # Wait longer on error


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Neural Orchestrator...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

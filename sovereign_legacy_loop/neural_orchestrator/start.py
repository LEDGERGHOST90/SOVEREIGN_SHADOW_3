#!/usr/bin/env python3
"""
🚀 Neural Orchestrator - Startup Script
=======================================

Quick startup script for the Neural Orchestrator backend.
This script handles environment setup and starts the FastAPI server.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the neural_orchestrator directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import app
from utils.logger import setup_logging

def main():
    """Start the Neural Orchestrator."""
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    # Print startup banner
    print("""
🧠 ╔══════════════════════════════════════════════════════════════════╗ 🧠
   ║                 NEURAL ORCHESTRATOR STARTUP                     ║
   ║              Backend for The Legacy Loop Dashboard              ║
   ║                                                                  ║
   ║  🌐 Website: https://legacyloopshadowai.abacusai.app/dashboard  ║
   ║  🔌 API: http://localhost:8000                                  ║
   ║  📡 WebSocket: ws://localhost:8000/ws                          ║
   ║                                                                  ║
   ║  🎯 Coordinating 7 Trading Systems:                            ║
   ║     • Sovereign Shadow AI (Primary)                            ║
   ║     • Omega AI Ecosystem (Orchestration)                       ║
   ║     • Nexus Protocol (Autonomous AI)                           ║
   ║     • Scout Watch (Bot Army)                                   ║
   ║     • Ledger Ghost90 (Execution)                               ║
   ║     • Toshi Trading System (Dashboard)                         ║
   ║     • Ledger Hardware Vault (Cold Storage)                     ║
   ║                                                                  ║
   ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("🚀 Starting Neural Orchestrator...")
    logger.info(f"📊 Log level: {log_level}")
    logger.info("🌐 Website integration: https://legacyloopshadowai.abacusai.app/dashboard")
    
    # Start the server
    import uvicorn
    
    uvicorn.run(
        "main:app",  # Import string for reload to work
        host="0.0.0.0",
        port=8000,
        log_level=log_level.lower(),
        reload=True,  # Enable auto-reload in development
        reload_dirs=[str(Path(__file__).parent)],  # Watch for changes
        access_log=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Neural Orchestrator stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed to start Neural Orchestrator: {e}")
        sys.exit(1)

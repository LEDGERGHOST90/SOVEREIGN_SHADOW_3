#!/bin/bash

##############################################################################
# 🌐 START SOVEREIGN SHADOW API SERVER
#
# Launches the REST API + WebSocket server for neural consciousness bridge
#
# Usage:
#   ./bin/START_API_SERVER.sh [port]
#
# Examples:
#   ./bin/START_API_SERVER.sh          # Default port 8000
#   ./bin/START_API_SERVER.sh 8080     # Custom port
#
# Endpoints:
#   GET  http://localhost:8000/api/strategy/performance
#   POST http://localhost:8000/api/trade/execute
#   POST http://localhost:8000/api/dashboard/update
#   WS   ws://localhost:8000/ws/dashboard
#
# Part of the Sovereign Shadow Trading System
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${PURPLE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           🏴 SOVEREIGN SHADOW API SERVER 🏴                   ║"
echo "║                                                                ║"
echo "║        Neural Consciousness Bridge - Trading API              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Port configuration
PORT="${1:-8000}"

echo -e "${CYAN}📋 Configuration:${NC}"
echo "  Project Root: $PROJECT_ROOT"
echo "  Port: $PORT"
echo "  Host: 0.0.0.0 (all interfaces)"
echo ""

# Check Python
echo -e "${CYAN}🐍 Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"

# Check dependencies
echo -e "${CYAN}📦 Checking dependencies...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  FastAPI not found. Installing...${NC}"
    pip install fastapi uvicorn websockets pydantic
fi
echo -e "${GREEN}✅ Dependencies OK${NC}"

# Check tactical config
echo -e "${CYAN}📝 Checking tactical config...${NC}"
CONFIG_FILE="$PROJECT_ROOT/config/tactical_scalp_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Tactical config not found: $CONFIG_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Config found${NC}"

# Check strategy knowledge base
echo -e "${CYAN}🧠 Checking strategy knowledge base...${NC}"
if [ ! -f "$PROJECT_ROOT/strategy_knowledge_base.py" ]; then
    echo -e "${RED}❌ Strategy knowledge base not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Strategy KB found${NC}"

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs/api"
mkdir -p "$LOG_DIR"

# Start server
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🚀 Starting API Server                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📡 API Endpoints:${NC}"
echo "  Health:       http://localhost:$PORT/api/health"
echo "  Strategies:   http://localhost:$PORT/api/strategy/performance"
echo "  Execute:      http://localhost:$PORT/api/trade/execute"
echo "  Dashboard:    http://localhost:$PORT/api/dashboard/update"
echo "  WebSocket:    ws://localhost:$PORT/ws/dashboard"
echo "  Docs:         http://localhost:$PORT/docs (interactive)"
echo ""
echo -e "${YELLOW}⚡ Press Ctrl+C to stop${NC}"
echo ""

# Launch server
python3 "$PROJECT_ROOT/core/api/trading_api_server.py" \
    --host 0.0.0.0 \
    --port "$PORT" \
    --log-level INFO \
    2>&1 | tee "$LOG_DIR/api_server_$(date +%Y%m%d_%H%M%S).log"


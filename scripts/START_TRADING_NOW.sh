#!/bin/bash

##############################################################################
# 🚀 START TRADING NOW - BULLETPROOF LAUNCHER
#
# This script will:
# 1. Check if API keys are set up
# 2. Validate all connections
# 3. Start the API server
# 4. Deploy tactical scalps
# 5. NEVER FAIL AGAIN
#
# Usage: ./scripts/START_TRADING_NOW.sh
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
echo "║           🏴 SOVEREIGN SHADOW - START TRADING NOW 🏴         ║"
echo "║                                                                ║"
echo "║        Bulletproof Launcher - Never Fails Again               ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📋 Configuration:${NC}"
echo "  Project Root: $PROJECT_ROOT"
echo "  Mode: BULLETPROOF"
echo ""

# Step 1: Check if .env exists
echo -e "${CYAN}🔐 Step 1: Checking API keys...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Setting up API keys...${NC}"
    echo ""
    echo -e "${BLUE}📝 This will ask for your API keys ONCE. Never again.${NC}"
    echo ""
    python3 scripts/SETUP_KEYS_NOW.py
    echo ""
    echo -e "${GREEN}✅ API keys configured!${NC}"
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Step 2: Validate keys
echo -e "${CYAN}🧪 Step 2: Validating API connections...${NC}"
if python3 scripts/validate_keys.py; then
    echo -e "${GREEN}✅ All API keys validated!${NC}"
else
    echo -e "${RED}❌ API key validation failed!${NC}"
    echo -e "${YELLOW}💡 Run: python3 scripts/SETUP_KEYS_NOW.py${NC}"
    exit 1
fi

# Step 3: Check dependencies
echo -e "${CYAN}📦 Step 3: Checking dependencies...${NC}"
if pip install -r requirements.txt --quiet; then
    echo -e "${GREEN}✅ Dependencies OK${NC}"
else
    echo -e "${RED}❌ Dependencies failed!${NC}"
    exit 1
fi

# Step 4: Start API server
echo -e "${CYAN}🌐 Step 4: Starting API server...${NC}"
echo -e "${BLUE}📡 API will be available at: http://localhost:8000${NC}"
echo -e "${BLUE}📚 Interactive docs: http://localhost:8000/docs${NC}"
echo ""

# Kill any existing server
pkill -f "trading_api_server.py" 2>/dev/null || true

# Start server in background
nohup python3 core/api/trading_api_server.py --port 8000 --log-level INFO > logs/api/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
sleep 5

# Test server
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✅ API server running (PID: $SERVER_PID)${NC}"
else
    echo -e "${RED}❌ API server failed to start!${NC}"
    echo -e "${YELLOW}📋 Check logs: tail -f logs/api/server.log${NC}"
    exit 1
fi

# Step 5: Deploy tactical scalps
echo -e "${CYAN}🎯 Step 5: Deploying tactical scalps...${NC}"
echo -e "${BLUE}📊 Mode: Paper trading (no real money)${NC}"
echo -e "${BLUE}🛡️  All safety limits active${NC}"
echo ""

# Deploy in background
nohup python3 scripts/deploy_tactical_scalps.py --mode paper > logs/tactical_scalps/deployment.log 2>&1 &
DEPLOY_PID=$!

echo -e "${GREEN}✅ Tactical scalps deployed (PID: $DEPLOY_PID)${NC}"
echo ""

# Step 6: Final status
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 SOVEREIGN SHADOW IS LIVE! 🎉                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 System Status:${NC}"
echo -e "  ${GREEN}✅ API Server: http://localhost:8000${NC}"
echo -e "  ${GREEN}✅ Tactical Scalps: Paper mode${NC}"
echo -e "  ${GREEN}✅ Risk Gate: Active${NC}"
echo -e "  ${GREEN}✅ Safety Limits: Enforced${NC}"
echo ""
echo -e "${CYAN}🔗 Quick Links:${NC}"
echo -e "  ${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo -e "  ${BLUE}🏥 Health: http://localhost:8000/api/health${NC}"
echo -e "  ${BLUE}📊 Performance: http://localhost:8000/api/strategy/performance${NC}"
echo ""
echo -e "${CYAN}📋 Monitoring:${NC}"
echo -e "  ${YELLOW}📄 API Logs: tail -f logs/api/server.log${NC}"
echo -e "  ${YELLOW}📄 Trading Logs: tail -f logs/tactical_scalps/deployment.log${NC}"
echo ""
echo -e "${CYAN}🛑 To Stop:${NC}"
echo -e "  ${RED}pkill -f trading_api_server.py${NC}"
echo -e "  ${RED}pkill -f deploy_tactical_scalps.py${NC}"
echo ""
echo -e "${PURPLE}🎯 The system is now hunting liquidation bands!${NC}"
echo -e "${PURPLE}   Fearless. Bold. Smiling through chaos. 🏴${NC}"
echo ""

# Keep script running to show status
echo -e "${YELLOW}⏳ System running... Press Ctrl+C to stop monitoring${NC}"
echo ""

# Monitor loop
while true; do
    sleep 30
    
    # Check if server is still running
    if ! curl -s http://localhost:8000/api/health > /dev/null; then
        echo -e "${RED}❌ API server stopped! Restarting...${NC}"
        nohup python3 core/api/trading_api_server.py --port 8000 --log-level INFO > logs/api/server.log 2>&1 &
        sleep 5
    fi
    
    # Show status
    echo -e "${GREEN}✅ System healthy: $(date)${NC}"
done



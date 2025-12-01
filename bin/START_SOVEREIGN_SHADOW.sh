#!/bin/bash

# =============================================================================
# 🏴 SOVEREIGN SHADOW - ONE-COMMAND DEPLOYMENT
# =============================================================================
# Philosophy: "Fearless. Bold. Smiling through chaos."
# Usage: ./START_SOVEREIGN_SHADOW.sh [mode]
# Modes: paper | test | live
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_PATH="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
MODE="${1:-paper}"  # Default to paper trading

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "   🏴 SOVEREIGN SHADOW - DEPLOYMENT SYSTEM"
echo "   'Fearless. Bold. Smiling through chaos.'"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Validate mode
if [[ ! "$MODE" =~ ^(paper|test|live)$ ]]; then
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo "   Valid modes: paper | test | live"
    exit 1
fi

echo -e "${YELLOW}⚙️  Mode: $MODE${NC}"
echo ""

# ====================
# PREFLIGHT CHECKS
# ====================
echo "🔍 Running Preflight Checks..."

# Check if we're in the right directory
cd "$BASE_PATH" || {
    echo -e "${RED}❌ Failed to navigate to $BASE_PATH${NC}"
    exit 1
}

# Check for .env file
if [ ! -f ".env" ] && [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ No .env file found${NC}"
    echo "   Run: cp .env.template .env"
    echo "   Then add your API keys"
    exit 1
fi

# Use .env.production if it exists, otherwise .env
ENV_FILE=".env"
if [ -f ".env.production" ]; then
    ENV_FILE=".env.production"
    echo -e "${GREEN}✅ Using .env.production${NC}"
else
    echo -e "${YELLOW}⚠️  Using .env (not .env.production)${NC}"
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q python-dotenv requests ccxt pandas numpy 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Some packages may need manual installation${NC}"
}

echo -e "${GREEN}✅ Environment ready${NC}"
echo ""

# ====================
# API VALIDATION
# ====================
echo "🔐 Validating API Connections..."

if python3 scripts/validate_api_connections.py; then
    echo -e "${GREEN}✅ API connections validated${NC}"
else
    echo -e "${RED}❌ API validation failed${NC}"
    echo "   Check your API keys in $ENV_FILE"
    exit 1
fi

echo ""

# ====================
# MODE-SPECIFIC SETUP
# ====================

case "$MODE" in
    paper)
        echo -e "${BLUE}📝 PAPER TRADING MODE${NC}"
        echo "   No real money at risk"
        echo "   Simulating trades with $8,260 capital"
        
        TRADING_MODE="paper"
        MAX_POSITION=1000
        RISK_LEVEL="safe"
        ;;
        
    test)
        echo -e "${YELLOW}🧪 TEST MODE${NC}"
        echo "   Real money - SMALL POSITIONS"
        echo "   Max position: $100"
        echo "   Testing with live APIs"
        
        TRADING_MODE="live"
        MAX_POSITION=100
        RISK_LEVEL="minimal"
        
        read -p "⚠️  This uses real money. Continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Cancelled"
            exit 0
        fi
        ;;
        
    live)
        echo -e "${RED}🔥 LIVE TRADING MODE${NC}"
        echo "   Real money - FULL POSITIONS"
        echo "   Max position: $415 (25% of hot wallet)"
        echo "   This is your $1,660 Coinbase account"
        
        TRADING_MODE="live"
        MAX_POSITION=415
        RISK_LEVEL="production"
        
        echo ""
        echo -e "${RED}WARNING: This mode trades with your real $1,660!${NC}"
        read -p "Type 'EXECUTE' to confirm: " confirm
        if [ "$confirm" != "EXECUTE" ]; then
            echo "Cancelled"
            exit 0
        fi
        ;;
esac

echo ""

# ====================
# NEURAL BRIDGE CHECK
# ====================
echo "🧠 Testing Neural Consciousness Bridge..."

if python3 scripts/neural_bridge.py; then
    echo -e "${GREEN}✅ Neural bridge operational${NC}"
else
    echo -e "${YELLOW}⚠️  Neural bridge offline (optional)${NC}"
fi

echo ""

# ====================
# DEPLOYMENT
# ====================

echo "🚀 Deploying Sovereign Shadow..."
echo ""

# Export environment variables
export TRADING_MODE="$TRADING_MODE"
export MAX_POSITION_SIZE="$MAX_POSITION"
export RISK_LEVEL="$RISK_LEVEL"

# Create logs directory
mkdir -p logs/trading

# Start timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/trading/deployment_${TIMESTAMP}.log"

echo -e "${GREEN}✅ Deployment Configuration:${NC}"
echo "   Mode: $MODE"
echo "   Trading: $TRADING_MODE"
echo "   Max Position: \$$MAX_POSITION"
echo "   Risk Level: $RISK_LEVEL"
echo "   Log File: $LOG_FILE"
echo ""

# ====================
# EXECUTION OPTIONS
# ====================

echo "═══════════════════════════════════════════════════════════════"
echo "   EXECUTION OPTIONS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Select trading strategy:"
echo ""
echo "  1) Arbitrage Scanner (Cross-exchange opportunities)"
echo "  2) Sniping (New listing detector)"
echo "  3) Scalping (High-frequency trades)"
echo "  4) Laddering (DCA accumulation)"
echo "  5) All Strategies (Full autonomous mode)"
echo "  6) Monitor Only (No trading)"
echo ""
read -p "Select option (1-6): " strategy

case "$strategy" in
    1)
        echo -e "${GREEN}Starting Arbitrage Scanner...${NC}"
        python3 scripts/claude_arbitrage_trader.py \
            --mode "$TRADING_MODE" \
            --max-position "$MAX_POSITION" \
            | tee "$LOG_FILE"
        ;;
    2)
        echo -e "${GREEN}Starting Sniping Bot...${NC}"
        python3 scripts/token_sniper.py \
            --mode "$TRADING_MODE" \
            --max-position "$MAX_POSITION" \
            | tee "$LOG_FILE" 2>/dev/null || echo "Sniper not yet implemented"
        ;;
    3)
        echo -e "${GREEN}Starting Scalping Engine...${NC}"
        python3 scripts/scalp_trader.py \
            --mode "$TRADING_MODE" \
            --max-position "$MAX_POSITION" \
            | tee "$LOG_FILE" 2>/dev/null || echo "Scalper not yet implemented"
        ;;
    4)
        echo -e "${GREEN}Starting Ladder Strategy...${NC}"
        python3 scripts/ladder_accumulator.py \
            --mode "$TRADING_MODE" \
            | tee "$LOG_FILE" 2>/dev/null || echo "Ladder not yet implemented"
        ;;
    5)
        echo -e "${GREEN}Starting Full Autonomous Mode...${NC}"
        python3 sovereign_legacy_loop/sovereign_shadow_unified.py \
            --mode "$TRADING_MODE" \
            --autonomy \
            --max-position "$MAX_POSITION" \
            | tee "$LOG_FILE" 2>/dev/null || echo "Unified system needs integration"
        ;;
    6)
        echo -e "${BLUE}Starting Monitor Only...${NC}"
        python3 monitoring/live_dashboard.py \
            | tee "$LOG_FILE" 2>/dev/null || echo "Monitor needs setup"
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

# ====================
# POST-EXECUTION
# ====================

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   EXECUTION COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Session Summary:"
echo "   Log: $LOG_FILE"
echo "   Mode: $MODE ($TRADING_MODE)"
echo "   Strategy: Option $strategy"
echo ""
echo "💎 Philosophy: Fearless. Bold. Smiling through chaos."
echo "🎯 Target: \$8,260 → \$50,000"
echo ""
echo "═══════════════════════════════════════════════════════════════"


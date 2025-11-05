#!/bin/bash
# =============================================================================
# 🏴 SOVEREIGN SHADOW - DESKTOP LAUNCHER
# =============================================================================
# Double-click this file to launch your trading system
# =============================================================================

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "   🏴 SOVEREIGN SHADOW TRADING SYSTEM"
echo "   'Fearless. Bold. Smiling through chaos.'"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""

# Navigate to the correct directory
cd "/Volumes/LegacySafe/SovereignShadow_II" || {
    echo -e "${RED}❌ Failed to find SovereignShadow_II directory${NC}"
    echo "Make sure your LegacySafe drive is connected"
    read -p "Press Enter to exit..."
    exit 1
}

echo -e "${GREEN}✅ Found SovereignShadow_II${NC}"
echo -e "${YELLOW}📂 Working directory: $(pwd)${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Copying from config/.env.CORRECTED..."
    cp config/.env.CORRECTED .env
fi

echo -e "${GREEN}✅ Configuration loaded${NC}"
echo ""

# Show menu
echo "═══════════════════════════════════════════════════════════════════"
echo "   LAUNCH OPTIONS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  1) Start Trading System (Paper Mode - Safe)"
echo "  2) Monitor AAVE Position"
echo "  3) Check Portfolio Balance"
echo "  4) Open Claude Code"
echo "  5) Full System Launch (Advanced)"
echo ""
echo "  9) Exit"
echo ""
read -p "Select option (1-5, 9): " choice

case "$choice" in
    1)
        echo ""
        echo -e "${GREEN}🚀 Launching Trading System in Paper Mode...${NC}"
        ./bin/START_SOVEREIGN_SHADOW.sh paper
        ;;
    2)
        echo ""
        echo -e "${GREEN}🏦 Checking AAVE Position...${NC}"
        python3 modules/safety/aave_monitor.py
        ;;
    3)
        echo ""
        echo -e "${GREEN}💰 Checking Portfolio Balance...${NC}"
        python3 sovereign_legacy_loop/core/portfolio/metamask_monitor.py
        ;;
    4)
        echo ""
        echo -e "${GREEN}💻 Opening Claude Code...${NC}"
        cd /Volumes/LegacySafe/SovereignShadow_II
        claude
        ;;
    5)
        echo ""
        echo -e "${GREEN}🚀 Full System Launch...${NC}"
        ./bin/LAUNCH_LEGACY_LOOP.sh
        ;;
    9)
        echo ""
        echo "👋 Goodbye"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${YELLOW}Invalid option${NC}"
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "   Session Complete"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
read -p "Press Enter to exit..."

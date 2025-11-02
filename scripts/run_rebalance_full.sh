#!/bin/bash
# Sovereign Shadow - Full Rebalancing Workflow
# Runs from terminal to completion (simulation → execution)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 Sovereign Shadow - Full Rebalancing Workflow${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REBALANCE_DIR="$BASE_DIR/core/rebalancing"

cd "$BASE_DIR"

# Load environment
if [ -f "$BASE_DIR/.env" ]; then
    set -a
    source "$BASE_DIR/.env"
    set +a
    echo -e "${GREEN}✅ Loaded .env configuration${NC}"
else
    echo -e "${RED}❌ No .env file found at $BASE_DIR/.env${NC}"
    exit 1
fi

# Show current mode
echo ""
echo -e "${YELLOW}📊 Current Configuration:${NC}"
echo "   ENV: ${ENV:-not set}"
echo "   DISABLE_REAL_EXCHANGES: ${DISABLE_REAL_EXCHANGES:-not set}"
echo "   ALLOW_LIVE_EXCHANGE: ${ALLOW_LIVE_EXCHANGE:-0}"

# Safety check
if [ "$DISABLE_REAL_EXCHANGES" != "1" ] && [ "$ENV" = "prod" ]; then
    echo ""
    echo -e "${RED}⚠️  WARNING: REAL TRADING MODE DETECTED${NC}"
    echo -e "${RED}   DISABLE_REAL_EXCHANGES is NOT set to 1${NC}"
    read -p "   Type 'LIVE TRADING' to continue: " confirm
    if [ "$confirm" != "LIVE TRADING" ]; then
        echo -e "${YELLOW}❌ Aborted by user${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✅ Paper mode enabled - safe to proceed${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Running Preflight Checks${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

cd "$REBALANCE_DIR"
python3 preflight_check.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Preflight checks failed - aborting${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Running Daily Health Check${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

cd "$BASE_DIR"
./scripts/daily_check.sh

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Running Rebalance Simulation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

cd "$REBALANCE_DIR"
python3 rebalance_sim.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Simulation failed - aborting${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Simulation complete - results saved to logs/rebalance_sim_result.json${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Review Simulation Results${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Parse and display simulation results
python3 << 'PYTHON_EOF'
import json
from pathlib import Path

sim_file = Path(__file__).parent.parent / "logs" / "rebalance_sim_result.json"
if sim_file.exists():
    with open(sim_file) as f:
        data = json.load(f)

    print("📊 Simulated Targets:")
    for asset, weight in sorted(data.get("targets", {}).items()):
        print(f"   • {asset}: {weight:.1%}")

    print(f"\n💰 Estimated Fees: ${data.get('total_fees', 0):.2f}")
    print(f"📈 Simulated Sharpe: {data.get('sharpe_estimate', 0):.2f}")
else:
    print("⚠️  Simulation results not found")
PYTHON_EOF

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 5: Execution Confirmation${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$DISABLE_REAL_EXCHANGES" = "1" ]; then
    echo -e "${GREEN}Running in PAPER MODE - no real trades will execute${NC}"
    read -p "Press ENTER to execute paper rebalance, or Ctrl+C to cancel: "
else
    echo -e "${RED}⚠️  LIVE TRADING MODE - REAL MONEY WILL BE TRADED${NC}"
    read -p "Type 'EXECUTE LIVE' to proceed: " confirm
    if [ "$confirm" != "EXECUTE LIVE" ]; then
        echo -e "${YELLOW}❌ Execution cancelled${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 6: Executing Rebalance${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Execute rebalance with auto-confirmation
cd "$REBALANCE_DIR"
echo "EXECUTE" | python3 rebalance_run.py

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Rebalance workflow complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📄 Check logs at: $BASE_DIR/logs/"
echo "💾 Session saved to: $BASE_DIR/memory/"

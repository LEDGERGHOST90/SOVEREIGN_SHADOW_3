#!/bin/bash
# 🏴 LAUNCH LEGACY LOOP - The CORRECT Master System
# SOVEREIGN LEGACY LOOP is the master, not empire!
# Your $8,260 connects to Legacy Loop, which orchestrates everything

echo "═══════════════════════════════════════════════════════════════════"
echo "🏴 SOVEREIGN LEGACY LOOP - MASTER SYSTEM LAUNCHER"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🎯 CORRECT HIERARCHY:"
echo "   SOVEREIGN LEGACY LOOP (MASTER)"
echo "   ├─ Empire (55,000 files) - INSIDE Legacy Loop"
echo "   ├─ ClaudeSDK (5,000 files) - INSIDE Legacy Loop"
echo "   ├─ Trading System (1,000 files) - INSIDE Legacy Loop"
echo "   └─ All Components - INSIDE Legacy Loop"
echo ""

# Check if we're in the right directory
if [ ! -d "sovereign_legacy_loop" ]; then
    echo "❌ Error: sovereign_legacy_loop directory not found"
    echo "Please run this script from the SovereignShadow directory"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 not found"
    echo "Please install Python3 to run Legacy Loop"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo "🔍 Validating Sovereign Legacy Loop Structure..."
echo ""

# Check Legacy Loop components
cd sovereign_legacy_loop

legacy_components=("ClaudeSDK" "app" "Legacy-Loop-Secret" "monitoring" "data" "scripts")

for component in "${legacy_components[@]}"; do
    if [ -d "$component" ]; then
        echo "✅ $component/ - FOUND"
    else
        echo "❌ $component/ - MISSING"
    fi
done

echo ""
echo "🏗️ Checking Legacy Loop Files..."

# Check key Legacy Loop files
legacy_files=("sovereign_shadow_unified.py" "market_intelligence_system.py" "auto_market_alerts.py" "whale_dump_analysis.py" "SOVEREIGN_LEGACY_LOOP_MASTER.py")

for file in "${legacy_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - READY"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "💰 Your Capital Connection to Legacy Loop:"
echo "   🔒 Ledger: $6,600 → Legacy Loop Monitoring"
echo "   ⚡ Coinbase: $1,660 → Legacy Loop Trading"
echo "   🔄 OKX: $0 → Legacy Loop Arbitrage"
echo "   🔄 Kraken: $0 → Legacy Loop Arbitrage"
echo "   📊 TOTAL: $8,260"
echo ""

echo "🎯 Mission: Legacy Loop orchestrates your $8,260 through the empire"
echo "🛡️ Safety: Ledger protected, Coinbase limited to 25% max risk"
echo ""

echo "🚀 Launching Sovereign Legacy Loop Master..."
echo ""

# Launch the Legacy Loop master
python3 SOVEREIGN_LEGACY_LOOP_MASTER.py

echo ""
echo "👋 Legacy Loop session complete."
echo "Remember: LEGACY LOOP is the master system!"
echo "Your $8,260 connects to Legacy Loop, which orchestrates the empire."
echo ""
echo "🏴 Legacy Loop > Empire > All Components"
echo ""

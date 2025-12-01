#!/bin/bash
# START CLAUDE SESSION - Ensures 100% Live Data
# Usage: ./start_claude_session.sh

cd /Volumes/LegacySafe/SOVEREIGN_SHADOW_3

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏴 SovereignShadow II - Session Starter"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Live System Check
echo "🔍 Running Live System Check..."
python3 scripts/live_system_check.py
echo ""

# 2. AAVE Health (if needed)
if command -v python3 &> /dev/null; then
    echo "💚 AAVE Health Factor Check..."
    python3 hybrid_system/aave_monitor.py 2>/dev/null | grep -A 5 "Health Factor" || echo "   ⚠️  AAVE monitor needs .env setup"
    echo ""
fi

# 3. Git Status
echo "📝 Git Status..."
git_changes=$(git status --porcelain 2>/dev/null | wc -l | xargs)
if [ "$git_changes" -gt 0 ]; then
    echo "   ⚠️  $git_changes uncommitted changes"
else
    echo "   ✅ Clean working tree"
fi
echo ""

# 4. Market Scanner Status
echo "📊 Market Scanner Status..."
if launchctl list 2>/dev/null | grep -q "market-scanner"; then
    echo "   ✅ Scanner running"
    latest_log=$(ls -t logs/market_scanner/*.jsonl 2>/dev/null | head -1)
    if [ -n "$latest_log" ]; then
        echo "   📍 Latest scan: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$latest_log")"
    fi
else
    echo "   ⚠️  Scanner not running"
fi
echo ""

# 5. Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Live data ready at: memory/LIVE_STATUS.json"
echo "📂 Working directory: $(pwd)"
echo "⏰ Session started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🤖 Claude: Read these files FIRST:"
echo "   1. memory/LIVE_STATUS.json"
echo "   2. PERSISTENT_STATE.json"
echo "   3. memory/LIVE_UPDATE_PROTOCOL_MEMORY.md"
echo "   4. memory/CONSOLIDATED_SYSTEM_MEMORY_2025-11-25.md"
echo ""

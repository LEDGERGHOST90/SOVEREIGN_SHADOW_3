#!/bin/bash
# Quick status check for 24-hour autonomy test

echo "🏰 Sovereign Shadow AI - Autonomy Test Status"
echo "=============================================="
echo ""

# Check if process is running
if ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" > /dev/null; then
    PID=$(ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" | awk '{print $2}')
    UPTIME=$(ps -p $PID -o etime= | xargs)
    CPU=$(ps -p $PID -o %cpu= | xargs)
    MEM=$(ps -p $PID -o %mem= | xargs)
    
    echo "✅ Status: RUNNING"
    echo "📊 PID: $PID"
    echo "⏱️  Uptime: $UPTIME"
    echo "💻 CPU: ${CPU}%"
    echo "🧠 Memory: ${MEM}%"
else
    echo "❌ Status: NOT RUNNING"
    echo ""
    echo "To start: make autonomy"
    exit 1
fi

echo ""
echo "📄 Recent Activity:"
echo "-------------------"
tail -20 logs/ai_enhanced/autonomy_24h_test.log | grep -E "(Heartbeat|💓|ERROR|✅|❌)" || echo "No recent activity logged"

echo ""
echo "📊 Latest Report:"
echo "----------------"
if [ -f "logs/ai_enhanced/sovereign_shadow_unified_report.json" ]; then
    python3 -c "
import json
from datetime import datetime
with open('logs/ai_enhanced/sovereign_shadow_unified_report.json') as f:
    r = json.load(f)
    print(f\"Timestamp: {r['timestamp']}\")
    print(f\"Mode: {r['guardrails']['effective_mode']}\")
    print(f\"Status: {r['summary']['system_status']}\")
    print(f\"Opportunities: {r['summary']['total_opportunities']}\")
    print(f\"Exchanges: {r['summary']['total_exchanges']}\")
"
else
    echo "No report found yet"
fi

echo ""
echo "🎯 Commands:"
echo "  ./check_autonomy.sh       - Check status"
echo "  ./stop_autonomy.sh        - Stop test"
echo "  tail -f logs/ai_enhanced/autonomy_24h_test.log  - Watch live"


#!/bin/bash
# Stop the 24-hour autonomy test

echo "🛑 Stopping Sovereign Shadow AI Autonomy Test"
echo "============================================="

if ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" > /dev/null; then
    PID=$(ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" | awk '{print $2}')
    echo "Found process: PID $PID"
    echo "Sending SIGTERM..."
    kill $PID
    sleep 2
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "Process still running, sending SIGKILL..."
        kill -9 $PID
        sleep 1
    fi
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Failed to stop process"
        exit 1
    else
        echo "✅ Process stopped successfully"
        echo ""
        echo "📊 Final Statistics:"
        if [ -f "logs/ai_enhanced/sovereign_shadow_unified_report.json" ]; then
            python3 -c "
import json
with open('logs/ai_enhanced/sovereign_shadow_unified_report.json') as f:
    r = json.load(f)
    print(f\"  Last update: {r['timestamp']}\")
    print(f\"  Total opportunities detected: {r['summary']['total_opportunities']}\")
    print(f\"  System status: {r['summary']['system_status']}\")
"
        fi
        echo ""
        echo "📄 Logs saved to: logs/ai_enhanced/autonomy_24h_test.log"
    fi
else
    echo "❌ No autonomy process found"
    exit 1
fi


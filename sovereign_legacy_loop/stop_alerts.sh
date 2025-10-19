#!/bin/bash
# 🛑 STOP MARKET ALERT SYSTEM

echo "════════════════════════════════════════════════════════════════"
echo "🛑 STOPPING MARKET ALERT SYSTEM"
echo "════════════════════════════════════════════════════════════════"

# Find and kill the process
if pgrep -f "auto_market_alerts.py" > /dev/null; then
    pkill -f "auto_market_alerts.py"
    echo "✅ Alert system stopped"
else
    echo "⚠️  Alert system is not running"
fi

echo "════════════════════════════════════════════════════════════════"


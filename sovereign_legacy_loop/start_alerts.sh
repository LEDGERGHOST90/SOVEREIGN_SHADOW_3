#!/bin/bash
# 🚨 START MARKET ALERT SYSTEM
# Run this to start automated market monitoring

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════════════"
echo "🚨 STARTING AUTOMATED MARKET ALERT SYSTEM"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will monitor:"
echo "  • Whale movements (big money dumps)"
echo "  • Market conditions (prices, sentiment)"
echo "  • Your portfolio risk"
echo ""
echo "Alerts will appear as Mac notifications when:"
echo "  🔴 Whale threat is high (DO NOT BUY)"
echo "  💎 Support levels are hit (BUY opportunity)"
echo "  ⚠️  Your portfolio is at risk"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if already running
if pgrep -f "auto_market_alerts.py" > /dev/null; then
    echo "⚠️  Alert system is already running!"
    echo ""
    echo "To stop it, run: ./stop_alerts.sh"
    exit 1
fi

# Default: Check every hour
INTERVAL=${1:-60}

echo "Starting with ${INTERVAL}-minute intervals..."
echo "Press Ctrl+C to stop (or run ./stop_alerts.sh)"
echo ""

# Run in foreground for now (user can see logs)
python3 auto_market_alerts.py --interval "$INTERVAL"


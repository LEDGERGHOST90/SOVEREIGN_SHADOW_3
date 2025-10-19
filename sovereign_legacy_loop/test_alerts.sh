#!/bin/bash
# 🧪 TEST ALERT SYSTEM
# Run this to test if notifications work

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════════════"
echo "🧪 TESTING MARKET ALERT SYSTEM"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will:"
echo "  1. Run ONE market scan"
echo "  2. Send test notifications"
echo "  3. Show you what alerts look like"
echo ""
echo "Watch for Mac notifications in top-right corner!"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 auto_market_alerts.py --once

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Test complete!"
echo ""
echo "If you saw notifications, the system is working."
echo "To start continuous monitoring, run: ./start_alerts.sh"
echo "════════════════════════════════════════════════════════════════"


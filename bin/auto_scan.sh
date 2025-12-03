#!/bin/bash
# Auto-scan watchlist for signals
# Run: ./auto_scan.sh or add to cron

WATCHLIST="BTC ETH SOL XRP"
API="http://localhost:8000"

echo "$(date): Starting watchlist scan..."

for symbol in $WATCHLIST; do
    result=$(curl -s -X POST "$API/api/signals/generate" \
        -H "Content-Type: application/json" \
        -d "{\"symbol\": \"$symbol\"}")
    
    action=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('signal',{}).get('action','ERROR'))" 2>/dev/null)
    conf=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('signal',{}).get('confidence',0))" 2>/dev/null)
    
    # Alert on high-confidence BUY/SELL
    if [[ "$action" == "BUY" && "$conf" -ge 70 ]]; then
        echo "🟢 HIGH SIGNAL: $symbol BUY ($conf%)"
        # Uncomment to send push notification:
        # curl -d "$symbol BUY signal ($conf%)" ntfy.sh/sovereignshadow_dc4d2fa1
    elif [[ "$action" == "SELL" && "$conf" -ge 80 ]]; then
        echo "🔴 HIGH SIGNAL: $symbol SELL ($conf%)"
    else
        echo "⚪ $symbol: $action ($conf%)"
    fi
done

echo "$(date): Scan complete"

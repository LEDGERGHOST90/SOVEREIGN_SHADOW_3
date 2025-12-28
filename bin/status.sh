#!/usr/bin/env bash
# Quick system status - run: ./bin/status.sh

SS3="/Volumes/LegacySafe/SS_III"
cd "$SS3"

echo "═══════════════════════════════════════════════════"
echo " SOVEREIGN SHADOW III - SYSTEM STATUS"
echo "═══════════════════════════════════════════════════"
echo ""

# Service status
echo "▸ OVERNIGHT RUNNER"
if pgrep -f "overnight_runner.py" > /dev/null; then
    PID=$(pgrep -f "overnight_runner.py" | head -1)
    echo "  Status: ✓ RUNNING (PID $PID)"
    if launchctl list com.sovereign.overnight &>/dev/null; then
        echo "  Manager: launchd (auto-restart ON)"
    else
        echo "  Manager: nohup (no auto-restart)"
    fi
else
    echo "  Status: ✗ STOPPED"
fi
echo ""

# API Keys
echo "▸ API KEYS"
if [[ -f "$SS3/.env" ]]; then
    [[ $(grep -c "BINANCE_US_API_KEY=." "$SS3/.env") -gt 0 ]] && echo "  Binance.US: ✓ (6000 req/min)" || echo "  Binance.US: ✗ (1200 req/min)"
    [[ $(grep -c "KRAKEN_API_KEY=." "$SS3/.env") -gt 0 ]] && echo "  Kraken:     ✓ (60 req/sec)" || echo "  Kraken:     ✗ (15 req/sec)"
    [[ $(grep -c "COINBASE_API_KEY=." "$SS3/.env") -gt 0 ]] && echo "  Coinbase:   ✓ (30 req/sec)" || echo "  Coinbase:   ✗ (10 req/sec)"
else
    echo "  ✗ No .env file found"
fi
echo ""

# Latest cycle
echo "▸ LATEST CYCLE"
LATEST=$(ls -t "$SS3/data/overnight_results/"*.json 2>/dev/null | head -1)
if [[ -n "$LATEST" ]]; then
    echo "  File: $(basename "$LATEST")"
    echo "  Time: $(stat -f '%Sm' "$LATEST")"
    python3 -c "
import json
d = json.load(open('$LATEST'))
shorts = len(d.get('summary',{}).get('short',[]))
longs = len(d.get('summary',{}).get('long',[]))
neutral = len(d.get('summary',{}).get('neutral',[]))
opps = len(d.get('opportunities',[]))
print(f'  Signals: {longs} LONG | {shorts} SHORT | {neutral} NEUTRAL')
print(f'  Opportunities: {opps}')
" 2>/dev/null || echo "  (parse error)"
else
    echo "  No cycles yet"
fi
echo ""

# Git status
echo "▸ GIT"
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
echo "  Branch: $(git branch --show-current)"
echo "  Commits: $AHEAD ahead, $BEHIND behind origin"
echo ""

echo "═══════════════════════════════════════════════════"
echo " Run: ./bin/overnight_service.sh logs   (live logs)"
echo " Run: ./bin/status.sh                   (this check)"
echo "═══════════════════════════════════════════════════"

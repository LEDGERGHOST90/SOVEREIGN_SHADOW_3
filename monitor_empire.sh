#!/bin/bash
# 🏴 SOVEREIGN SHADOW EMPIRE MONITOR

while true; do
    clear
    echo "🏴 SOVEREIGN SHADOW EMPIRE - LIVE STATUS"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    
    # Check if process is running
    if pgrep -f "claude_arbitrage_trader" > /dev/null; then
        echo "✅ Arbitrage Engine: RUNNING"
    else
        echo "❌ Arbitrage Engine: STOPPED"
    fi
    
    # Show latest log entries
    echo ""
    echo "📊 Latest Activity:"
    if [ -f "/Volumes/LegacySafe/SovereignShadow/logs/ai_enhanced/sovereign_shadow_unified.log" ]; then
        tail -5 /Volumes/LegacySafe/SovereignShadow/logs/ai_enhanced/sovereign_shadow_unified.log
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "Press Ctrl+C to exit monitor"
    
    sleep 10
done


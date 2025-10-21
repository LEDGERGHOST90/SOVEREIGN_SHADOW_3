#!/bin/bash
# 🏴 SOVEREIGN SHADOW - CLEAN RESTART
# Kills all old processes and starts fresh

echo "🧹 Cleaning up old processes..."
killall -9 python3 2>/dev/null
killall -9 tail 2>/dev/null
sleep 2

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "🏴 SOVEREIGN SHADOW - READY TO TRADE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "💰 Portfolio: \$8,260 total"
echo "   🔒 Ledger: \$6,600 (protected)"
echo "   ⚡ Coinbase: \$1,660 (active trading)"
echo ""
echo "🔥 All safety limits: DISABLED"
echo "⚡ Exchange connections: LIVE (Coinbase, OKX, Kraken)"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Choose your action:"
echo ""
echo "1) 🔍 Scan for arbitrage opportunities (5 min)"
echo "2) 📊 Check real balances across all exchanges"
echo "3) 💹 View market intelligence (prices, volatility)"
echo "4) 🚀 Execute manual trade"
echo "5) ❌ Exit"
echo ""
read -p "Enter choice (1-5): " choice

cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate

case $choice in
    1)
        echo ""
        echo "🔍 Starting arbitrage scanner..."
        python3 scripts/claude_arbitrage_trader.py
        ;;
    2)
        echo ""
        echo "💰 Fetching real balances..."
        python3 scripts/get_real_balances.py
        ;;
    3)
        echo ""
        echo "📊 Market Intelligence Dashboard..."
        python3 shadow_scope.py
        ;;
    4)
        echo ""
        echo "🚀 Manual Trade Execution..."
        python3 EXECUTE_MANUAL_TRADE.py
        ;;
    5)
        echo "👋 Goodbye"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🏴 Session complete"
echo "═══════════════════════════════════════════════════════════════════"


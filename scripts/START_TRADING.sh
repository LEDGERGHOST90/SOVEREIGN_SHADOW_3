#!/bin/bash
# 🏴 SOVEREIGN SHADOW - CLEAN TRADING INTERFACE
# One command to rule them all

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "🏴 SOVEREIGN SHADOW TRADING SYSTEM"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "💰 Capital: \$8,260 (\$6,600 Ledger + \$1,660 Coinbase)"
echo "🔥 Safety: DISABLED - Full access enabled"
echo "⚡ Mode: REAL EXCHANGE CONNECTIONS"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""

cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate

echo "🔧 Connecting to exchanges..."
python3 scripts/claude_arbitrage_trader.py

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🏴 Trading session complete"
echo "═══════════════════════════════════════════════════════════════════"


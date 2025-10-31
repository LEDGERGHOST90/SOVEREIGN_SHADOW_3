#!/bin/bash

clear
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🔥          SOVEREIGN SHADOW - QUICK STATUS CHECK         🔥"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Capital
echo "💎 CAPITAL ALLOCATION:"
echo "   Total Portfolio: \$10,811"
echo "   Active Trading:  \$1,660 (ready to deploy)"
echo "   Cold Storage:    \$6,600 (Ledger)"
echo "   DeFi (AAVE):     \$2,397 (Health: 2.49 ✅)"
echo ""

# Exchange Status
echo "🔌 EXCHANGE STATUS:"
if grep -q 'organizations/' .env 2>/dev/null; then
    echo "   Coinbase: ⚠️  Configured (401 - add IP to allowlist)"
else
    echo "   Coinbase: ❌ Not configured"
fi

if grep -q '^OKX_API_KEY="[^"]*[a-zA-Z0-9]' .env 2>/dev/null; then
    echo "   OKX:      ✅ Configured"
else
    echo "   OKX:      ❌ Empty (need API keys)"
fi

if grep -q '^KRAKEN_API_KEY="[^"]*[a-zA-Z0-9]' .env 2>/dev/null; then
    echo "   Kraken:   ✅ Configured"
else
    echo "   Kraken:   ❌ Empty (need API keys)"
fi
echo ""

# Trading Mode
if grep -q '^ALLOW_LIVE_EXCHANGE=1' .env 2>/dev/null; then
    echo "⚙️  MODE: 🔴 LIVE TRADING (REAL MONEY)"
else
    echo "⚙️  MODE: 📄 PAPER TRADING (SAFE)"
fi
echo ""

# Available Scripts
echo "🎯 AVAILABLE COMMANDS:"
echo "   python3 setup_exchanges.py    - Fix API configuration"
echo "   python3 meme_coin_scanner.py  - Find opportunities"
echo "   python3 master_control.py     - Interactive menu"
echo "   python3 live_dashboard.py     - Real-time monitoring"
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check what's blocking
BLOCKERS=0
if ! grep -q 'organizations/' .env 2>/dev/null; then
    BLOCKERS=$((BLOCKERS + 1))
fi
if ! grep -q '^OKX_API_KEY="[^"]*[a-zA-Z0-9]' .env 2>/dev/null; then
    BLOCKERS=$((BLOCKERS + 1))
fi

if [ $BLOCKERS -gt 0 ]; then
    echo "🚨 BLOCKERS FOUND: $BLOCKERS"
    echo ""
    echo "👉 ACTION REQUIRED:"
    if ! grep -q 'organizations/' .env 2>/dev/null; then
        echo "   1. Fix Coinbase: Add IP to allowlist at portal.cdp.coinbase.com"
    fi
    if ! grep -q '^OKX_API_KEY="[^"]*[a-zA-Z0-9]' .env 2>/dev/null; then
        echo "   2. Add OKX keys: Get from OKX → Account → API Management"
        echo "      Then update .env with: OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
    fi
    echo ""
else
    echo "✅ ALL CLEAR! Ready to trade!"
    echo ""
    echo "🚀 RUN: python3 meme_coin_scanner.py 100"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════════"
echo ""

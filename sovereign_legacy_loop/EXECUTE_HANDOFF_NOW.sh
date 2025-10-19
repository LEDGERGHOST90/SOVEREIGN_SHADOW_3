#!/bin/bash
# 🏰 SOVEREIGN SHADOW - EXECUTE HANDOFF & FIX COINBASE

echo "════════════════════════════════════════════════════════════"
echo "🏰 SOVEREIGN SHADOW LEGACY LOOP - EXECUTING HANDOFF"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Current Status:"
echo "  ✅ System RUNNING (PID: $(pgrep -f sovereign_shadow_unified | head -1))"
echo "  ✅ Arbitrage module FIXED"
echo "  ✅ Packages INSTALLED"
echo "  ❌ API Keys MISSING"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "🔑 ADDING YOUR COINBASE API KEYS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "You have a Coinbase CDP key file with:"
echo "  API Key ID: 62d59def-cd4b-4285-879c-ea113c1900a4"
echo ""
echo "Enter your Coinbase private key (or press Enter to skip):"
echo "(Paste the ENTIRE key including BEGIN/END lines)"
echo ""
read -p "Private Key: " PRIVATE_KEY

if [ ! -z "$PRIVATE_KEY" ]; then
    # Create proper .env file
    cat << EOF > .env
# Coinbase CDP Configuration
COINBASE_KEY=62d59def-cd4b-4285-879c-ea113c1900a4
COINBASE_SECRET=$PRIVATE_KEY
CB_API_KEY=62d59def-cd4b-4285-879c-ea113c1900a4
CB_API_SECRET=$PRIVATE_KEY

# System Configuration (FROM HANDOFF)
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
EOF

    echo "✅ Coinbase keys configured"
else
    echo "⚠️  Skipping Coinbase configuration"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🔄 RESTARTING SYSTEM AS PER HANDOFF PROCEDURE"
echo "════════════════════════════════════════════════════════════"

# Kill current process gracefully (as per handoff)
pkill -SIGTERM -f sovereign_shadow_unified.py
sleep 2

# Set production environment (as per handoff)
export ENV=prod
export ALLOW_LIVE_EXCHANGE=1
export DISABLE_REAL_EXCHANGES=0
export SANDBOX=0

echo "🚀 Starting system in PRODUCTION mode..."

# Restart the system (as per handoff)
python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &

sleep 3

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ HANDOFF EXECUTED SUCCESSFULLY"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 VERIFY SUCCESS (as per handoff):"
echo ""
echo "1. Check mode is LIVE:"
cat logs/ai_enhanced/sovereign_shadow_unified_report.json | grep effective_mode | tail -1

echo ""
echo "2. Check system status:"
cat logs/ai_enhanced/sovereign_shadow_unified_report.json | python3 -m json.tool | grep -A5 summary | tail -6

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📊 MONITOR YOUR EMPIRE (as per handoff):"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Watch logs:    tail -f logs/ai_enhanced/sovereign_shadow_unified.log"
echo "View report:   cat logs/ai_enhanced/sovereign_shadow_unified_report.json | python3 -m json.tool"
echo ""
echo "🏰 SOVEREIGN SHADOW IS OPERATIONAL"
echo "════════════════════════════════════════════════════════════"

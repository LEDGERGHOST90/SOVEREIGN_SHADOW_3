#!/bin/bash
# CONNECT COINBASE IMMEDIATELY

echo "🔑 CONNECTING COINBASE TO YOUR SYSTEM"
echo "======================================"
echo ""
echo "You need your Coinbase API credentials."
echo "Get them from: https://www.coinbase.com/settings/api"
echo ""
read -p "Enter Coinbase API Key: " CB_KEY
read -s -p "Enter Coinbase API Secret: " CB_SECRET
echo ""

# Save to .env
cat << EOL > .env
# Coinbase Production Keys
COINBASE_KEY=$CB_KEY
COINBASE_SECRET=$CB_SECRET
CB_API_KEY=$CB_KEY
CB_API_SECRET=$CB_SECRET

# System Mode
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
EOL

echo "✅ Keys saved to .env"
echo ""
echo "🔄 Restarting system with Coinbase..."

# Kill old process
pkill -f sovereign_shadow_unified.py
sleep 2

# Start with keys loaded
export $(cat .env | grep -v '^#' | xargs)
python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &

echo ""
echo "✅ SYSTEM RESTARTED WITH COINBASE!"
echo ""
echo "📊 Watch it connect:"
echo "   tail -f logs/ai_enhanced/sovereign_shadow_unified.log"
echo ""
echo "Look for: \"coinbase\": \"connected\""

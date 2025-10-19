#!/bin/bash
# ADD YOUR REAL COINBASE PRIVATE KEY

echo "🔑 ADD YOUR REAL COINBASE CDP PRIVATE KEY"
echo "=========================================="
echo ""
echo "Your private key looks like:"
echo "-----BEGIN EC PRIVATE KEY-----"
echo "MHcCAQEE....(long string)...."
echo "-----END EC PRIVATE KEY-----"
echo ""
echo "Paste your ENTIRE private key (including BEGIN/END lines):"
echo "Press Ctrl+D when done"
echo ""

# Read multi-line private key
PRIVATE_KEY=$(cat)

# Update the JSON file
cat << EOF > CBase_api_key.json
{
   "name": "organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/62d59def-cd4b-4285-879c-ea113c1900a4",
   "privateKey": "$PRIVATE_KEY"
}
EOF

echo ""
echo "✅ Private key saved to CBase_api_key.json"

# Create .env
cat << EOF > .env
# Coinbase CDP Configuration
COINBASE_CDP_API_KEY=62d59def-cd4b-4285-879c-ea113c1900a4
COINBASE_CDP_PRIVATE_KEY="$PRIVATE_KEY"

# System Mode
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
EOF

echo "✅ Configuration saved to .env"
echo ""
echo "🔄 Restarting system with real Coinbase connection..."

pkill -f sovereign_shadow_unified.py
sleep 2

export $(cat .env | grep -v '^#' | xargs)
python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &

echo ""
echo "🚀 SYSTEM RUNNING WITH COINBASE!"
echo ""
echo "Check status: tail -f logs/ai_enhanced/sovereign_shadow_unified.log"

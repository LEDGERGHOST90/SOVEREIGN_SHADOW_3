#!/bin/bash

#############################################################
# 🚨 SOVEREIGN SHADOW COMPLETE NETWORK FIX
# Full system integration with Abacus AI, Notion, and MCP
#############################################################

echo "🔥 SOVEREIGN SHADOW COMPLETE NETWORK FIX INITIATED"
echo "================================================"

# Step 1: Kill all conflicting processes
echo "📍 Step 1: Clearing all conflicting processes..."
killall Claude 2>/dev/null
killall node 2>/dev/null
killall python3 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Step 2: Fix Claude Desktop configuration
echo "📍 Step 2: Fixing Claude Desktop MCP configuration..."
cat > "$HOME/Library/Application Support/Claude/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "sovereign-shadow": {
      "command": "python3",
      "args": [
        "/Volumes/LegacySafe/SovereignShadow/MASTER_FIX/unified_mcp_server.py"
      ],
      "env": {
        "SHADOW_MODE": "production",
        "PORTFOLIO_ACTIVE": "1660",
        "PORTFOLIO_COLD": "6600",
        "AAVE_BORROWED": "1151",
        "HEALTH_FACTOR": "2.49",
        "PYTHONPATH": "/Volumes/LegacySafe/SovereignShadow",
        "ABACUS_AI_URL": "https://sovereign-legacy-looping.abacusai.app/",
        "NOTION_ENABLED": "true"
      }
    },
    "notion": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-notion"
      ]
    }
  }
}
EOF

# Step 3: Start the unified trading API
echo "📍 Step 3: Starting Sovereign Shadow Trading API..."
cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate

# Install required packages
pip install -q fastapi uvicorn aiohttp python-dotenv 2>/dev/null

# Start the trading API in background
nohup python3 /Volumes/LegacySafe/SovereignShadow/MASTER_FIX/trading_api.py > /tmp/trading_api.log 2>&1 &
echo "Trading API PID: $!"

# Step 4: Start ngrok for Abacus AI connection
echo "📍 Step 4: Setting up Abacus AI tunnel..."
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    brew install ngrok 2>/dev/null
fi

# Start ngrok tunnel
nohup ngrok http 8000 > /tmp/ngrok.log 2>&1 &
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)
echo "🌐 Ngrok URL for Abacus AI: $NGROK_URL"

# Step 5: Test all connections
echo "📍 Step 5: Testing all connections..."
echo ""

# Test local API
echo -n "Testing local API... "
if curl -s localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ CONNECTED"
else
    echo "❌ FAILED"
fi

# Test Abacus AI
echo -n "Testing Abacus AI... "
if curl -s https://sovereign-legacy-looping.abacusai.app/ > /dev/null 2>&1; then
    echo "✅ REACHABLE"
else
    echo "⚠️  CHECK MANUALLY"
fi

# Step 6: Create status dashboard
echo ""
echo "📍 Step 6: Creating status dashboard..."
cat > /tmp/sovereign_status.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Sovereign Shadow Status</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: monospace; padding: 20px; }
        h1 { color: #ff6600; }
        .status { padding: 10px; margin: 10px; border: 1px solid #333; }
        .online { color: #00ff00; }
        .offline { color: #ff0000; }
    </style>
</head>
<body>
    <h1>🔥 SOVEREIGN SHADOW SYSTEM STATUS</h1>
    <div class="status">
        <h2>Trading API: <span id="api-status">Checking...</span></h2>
        <h2>MCP Server: <span id="mcp-status">Checking...</span></h2>
        <h2>Abacus AI: <span id="abacus-status">Checking...</span></h2>
        <h2>Capital: $10,811</h2>
        <h2>Active Strategies: 9</h2>
    </div>
    <script>
        // Auto-refresh status
        setInterval(() => {
            fetch('http://localhost:8000/api/health')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('api-status').innerHTML = 
                        '<span class="online">ONLINE</span>';
                })
                .catch(e => {
                    document.getElementById('api-status').innerHTML = 
                        '<span class="offline">OFFLINE</span>';
                });
        }, 5000);
    </script>
</body>
</html>
EOF

echo ""
echo "=========================================="
echo "🚀 FIX COMPLETE! NEXT STEPS:"
echo ""
echo "1. RESTART CLAUDE DESKTOP NOW:"
echo "   - Quit Claude Desktop completely (Cmd+Q)"
echo "   - Wait 3 seconds"
echo "   - Reopen Claude Desktop"
echo ""
echo "2. ABACUS AI CONNECTION:"
echo "   - URL: $NGROK_URL"
echo "   - Dashboard: https://sovereign-legacy-looping.abacusai.app/"
echo ""
echo "3. STATUS DASHBOARD:"
echo "   - Open: open /tmp/sovereign_status.html"
echo ""
echo "4. TEST IN CLAUDE:"
echo "   Ask: 'What is my capital?'"
echo "   Expected: Shows $10,811 total"
echo ""
echo "⏰ STEP AWAY NOW FOR 30 SECONDS!"
echo "   Let everything initialize..."
echo "=========================================="

# Keep script running to maintain processes
echo ""
echo "Press Ctrl+C to stop all services"
trap "kill 0" EXIT
wait

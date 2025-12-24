#!/bin/bash

echo "🚀 STARTING SOVEREIGN SHADOW PREMIUM ORCHESTRATION..."

# Start Docker services
if command -v docker-compose >/dev/null 2>&1; then
    echo "🐳 Starting Docker services..."
    docker-compose up -d
fi

# Start MCP server
echo "🤖 Starting MCP server..."
python3 sovereign_legacy_loop/ClaudeSDK/mcp_exchange_server.py &

# Start monitoring dashboard
echo "📊 Starting monitoring dashboard..."
python3 scripts/premium_dashboard.py &

# Start AI agents
echo "🧠 Starting AI agents..."
python3 scripts/start_ai_agents.py &

echo "✅ Premium orchestration started!"
echo "🌐 Dashboard: http://localhost:3000"
echo "🤖 MCP Server: http://localhost:3006"
echo "📊 Monitoring: python3 scripts/premium_dashboard.py"

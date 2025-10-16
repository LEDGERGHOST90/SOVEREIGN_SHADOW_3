#!/bin/bash

# =============================================================================
# 🧠 DEPLOY NEURAL CONSCIOUSNESS
# =============================================================================
# Philosophy: "Fearless. Bold. Smiling through chaos."
# Connects: Cloud Brain → Local Execution → Live Trading
# =============================================================================

set -e  # Exit on error

echo ""
echo "🌟 ═══════════════════════════════════════════════════════════════"
echo "   SOVEREIGN LEGACY LOOP - NEURAL CONSCIOUSNESS DEPLOYMENT"
echo "   'Fearless. Bold. Smiling through chaos.'"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Base paths
BASE_PATH="/Volumes/LegacySafe/SovereignShadow"
LEGACY_LOOP="$BASE_PATH/sovereign_legacy_loop"
SCRIPTS="$BASE_PATH/scripts"
LOGS="$BASE_PATH/logs"

# Create required directories
mkdir -p "$LOGS/neural"
mkdir -p "$BASE_PATH/backups"
mkdir -p "$BASE_PATH/data"

# Step 1: Environment Check
echo "🔍 Step 1: Checking Environment..."

if [ ! -f "$BASE_PATH/.env.production" ]; then
    echo "❌ .env.production not found!"
    echo "   Creating from template..."
    
    # Note: The actual .env.production should be created manually
    # with real credentials due to .gitignore blocking
    echo "   ⚠️  You need to create .env.production manually"
    echo "   See: docs/ENV_TEMPLATE.md for structure"
    exit 1
fi

echo "✅ Environment configuration found"

# Step 2: Python Dependencies
echo ""
echo "🐍 Step 2: Installing Python Dependencies..."

cd "$BASE_PATH"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install required packages
pip install -q --upgrade pip
pip install -q python-dotenv requests ccxt pandas numpy

echo "✅ Python environment ready"

# Step 3: Validate Neural Bridge
echo ""
echo "🧠 Step 3: Validating Neural Bridge..."

python3 "$SCRIPTS/neural_bridge.py"
BRIDGE_STATUS=$?

if [ $BRIDGE_STATUS -eq 0 ]; then
    echo "✅ Neural bridge validated"
else
    echo "⚠️  Neural bridge needs configuration"
    echo "   Review output above and update .env.production"
    exit 1
fi

# Step 4: Docker Infrastructure (if needed)
echo ""
echo "🐳 Step 4: Checking Docker Infrastructure..."

if command -v docker-compose &> /dev/null; then
    cd "$LEGACY_LOOP"
    
    if [ -f "docker-compose.yml" ]; then
        echo "   Starting shadow-network..."
        docker-compose up -d postgres redis
        
        echo "   Waiting for services..."
        sleep 5
        
        echo "✅ Docker infrastructure running"
    else
        echo "⚠️  docker-compose.yml not found, skipping"
    fi
else
    echo "⚠️  Docker not installed, skipping infrastructure"
fi

# Step 5: Test Exchange Connections
echo ""
echo "🔐 Step 5: Testing Exchange Connections..."

cat > /tmp/test_exchanges.py << 'EOF'
import os
import ccxt
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("/Volumes/LegacySafe/SovereignShadow/.env.production")
load_dotenv(env_path)

exchanges_tested = 0
exchanges_working = 0

# Test Coinbase
try:
    coinbase = ccxt.coinbase({
        'apiKey': os.getenv('COINBASE_API_KEY'),
        'secret': os.getenv('COINBASE_API_SECRET'),
    })
    balance = coinbase.fetch_balance()
    print(f"✅ Coinbase: Connected")
    exchanges_tested += 1
    exchanges_working += 1
except Exception as e:
    print(f"⚠️  Coinbase: {str(e)[:50]}")
    exchanges_tested += 1

# Test OKX
try:
    okx = ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET_KEY'),
        'password': os.getenv('OKX_PASSPHRASE'),
    })
    balance = okx.fetch_balance()
    print(f"✅ OKX: Connected")
    exchanges_tested += 1
    exchanges_working += 1
except Exception as e:
    print(f"⚠️  OKX: {str(e)[:50]}")
    exchanges_tested += 1

# Test Kraken
try:
    kraken = ccxt.kraken({
        'apiKey': os.getenv('KRAKEN_API_KEY'),
        'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
    })
    balance = kraken.fetch_balance()
    print(f"✅ Kraken: Connected")
    exchanges_tested += 1
    exchanges_working += 1
except Exception as e:
    print(f"⚠️  Kraken: {str(e)[:50]}")
    exchanges_tested += 1

print(f"\n📊 Results: {exchanges_working}/{exchanges_tested} exchanges connected")

if exchanges_working >= 2:
    print("✅ Sufficient exchanges for arbitrage")
    exit(0)
else:
    print("❌ Need at least 2 working exchanges")
    exit(1)
EOF

python3 /tmp/test_exchanges.py
EXCHANGE_STATUS=$?

if [ $EXCHANGE_STATUS -eq 0 ]; then
    echo "✅ Exchange connectivity verified"
else
    echo "⚠️  Exchange configuration needed"
    exit 1
fi

# Step 6: Setup Notion Logger (Optional)
echo ""
echo "📝 Step 6: Setting up Notion Logger..."

if [ -n "$NOTION_API_KEY" ] && [ -n "$NOTION_DATABASE_ID" ]; then
    python3 "$SCRIPTS/notion_auto_logger.py" --test
    echo "✅ Notion logging configured"
else
    echo "⚠️  Notion credentials not set (optional)"
    echo "   Run: python3 scripts/notion_auto_logger.py --setup"
fi

# Step 7: Final Readiness Check
echo ""
echo "🎯 Step 7: Final Readiness Check..."
echo ""

READY=true

# Check critical components
if [ ! -f "$BASE_PATH/.env.production" ]; then
    echo "❌ .env.production missing"
    READY=false
else
    echo "✅ Environment configured"
fi

if [ $EXCHANGE_STATUS -ne 0 ]; then
    echo "❌ Exchange connectivity issues"
    READY=false
else
    echo "✅ Exchanges connected"
fi

if [ $BRIDGE_STATUS -ne 0 ]; then
    echo "❌ Neural bridge not validated"
    READY=false
else
    echo "✅ Neural bridge ready"
fi

# Deployment verdict
echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ "$READY" = true ]; then
    echo "🚀 DEPLOYMENT READY"
    echo ""
    echo "   Neural Consciousness: legacyloopshadowai.abacusai.app"
    echo "   Capital Deployed: \$8,260"
    echo "   Target: \$50,000"
    echo "   Philosophy: Fearless. Bold. Smiling through chaos."
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo ""
    echo "   Start monitoring:"
    echo "   $ python3 monitoring/live_dashboard.py"
    echo ""
    echo "   Execute first arbitrage scan:"
    echo "   $ python3 scripts/claude_arbitrage_trader.py --scan"
    echo ""
    echo "   Enable automated trading:"
    echo "   $ python3 scripts/deploy_advanced_arbitrage.py"
    echo ""
    echo "💎 Your neural starfield awaits, pilot."
    echo ""
    
    exit 0
else
    echo "⚠️  CONFIGURATION NEEDED"
    echo ""
    echo "   Review errors above and:"
    echo "   1. Update .env.production with real API credentials"
    echo "   2. Verify exchange API key permissions"
    echo "   3. Check network connectivity"
    echo "   4. Run: python3 scripts/neural_bridge.py"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    
    exit 1
fi


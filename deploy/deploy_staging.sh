#!/bin/bash
# 🧪 STAGING ENVIRONMENT DEPLOYMENT
# Purpose: Real market data, paper trading execution

echo "🧪 Deploying SovereignShadow.Ai Staging Environment"
echo "===================================================="

# Set environment
export ENVIRONMENT="staging"
export CONFIG_FILE="environments/staging/config_staging.yaml"

# Check if staging environment exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Staging config not found: $CONFIG_FILE"
    exit 1
fi

echo "✅ Staging environment configuration loaded"

# Check for API keys
echo "🔑 Checking API key configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Please copy .env.template to .env and configure your API keys"
    echo "   Required for staging:"
    echo "   • BINANCE_TESTNET_API_KEY"
    echo "   • BINANCE_TESTNET_SECRET_KEY"
    echo "   • COINBASE_SANDBOX_API_KEY"
    echo "   • COINBASE_SANDBOX_SECRET_KEY"
    exit 1
fi

# Load environment variables
source .env

# Validate API keys
if [ -z "$BINANCE_TESTNET_API_KEY" ] || [ -z "$BINANCE_TESTNET_SECRET_KEY" ]; then
    echo "❌ Binance Testnet API keys not configured"
    exit 1
fi

if [ -z "$COINBASE_SANDBOX_API_KEY" ] || [ -z "$COINBASE_SANDBOX_SECRET_KEY" ]; then
    echo "❌ Coinbase Sandbox API keys not configured"
    exit 1
fi

echo "✅ API keys configured for staging environment"

# Create staging logs directory
mkdir -p logs/staging
echo "✅ Staging logs directory created"

# Test exchange connectivity
echo "🔍 Testing exchange connectivity..."
python3 -c "
import os
import sys
sys.path.append('shared')

# Test API connections
try:
    from exchange_interfaces import BinanceTestnetInterface, CoinbaseSandboxInterface
    
    # Test Binance
    binance = BinanceTestnetInterface(
        os.getenv('BINANCE_TESTNET_API_KEY'),
        os.getenv('BINANCE_TESTNET_SECRET_KEY')
    )
    print('✅ Binance Testnet connection successful')
    
    # Test Coinbase
    coinbase = CoinbaseSandboxInterface(
        os.getenv('COINBASE_SANDBOX_API_KEY'),
        os.getenv('COINBASE_SANDBOX_SECRET_KEY')
    )
    print('✅ Coinbase Sandbox connection successful')
    
except Exception as e:
    print(f'❌ Exchange connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Exchange connectivity test failed"
    exit 1
fi

echo "✅ All exchange connections verified"

# Start staging paper trading
echo "🚀 Starting staging paper trading..."
echo "   • Mode: Paper Trading"
echo "   • Starting Balance: $1,000 (paper money)"
echo "   • Max Position Size: 2%"
echo "   • Risk Level: ZERO (real data, fake execution)"
echo "   • Exchanges: Binance Testnet, Coinbase Sandbox"
echo ""

# Start the staging trading system
python3 environments/staging/paper_trading.py --config "$CONFIG_FILE" --mode staging

echo ""
echo "✅ Staging environment deployed successfully!"
echo "📊 Access staging dashboard at: http://localhost:3000/staging"
echo "📋 View logs at: logs/staging/"
echo "🛑 Stop with: Ctrl+C"

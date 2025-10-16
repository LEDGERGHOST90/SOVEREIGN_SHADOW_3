#!/bin/bash
# 🚀 SOVEREIGNSHADOW.AI - REAL TRADING STARTUP

echo "🚀 Starting SovereignShadow.Ai Real Trading System"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.template to .env and configure your API keys"
    exit 1
fi

# Load environment variables
source .env

# Check if API keys are configured
if [ -z "$BINANCE_TESTNET_API_KEY" ]; then
    echo "⚠️  BINANCE_TESTNET_API_KEY not configured"
fi

if [ -z "$COINBASE_SANDBOX_API_KEY" ]; then
    echo "⚠️  COINBASE_SANDBOX_API_KEY not configured"
fi

# Start real trading system
echo "🎯 Starting real exchange integration..."
python3 real_exchange_integration.py

echo "✅ Real trading system started"

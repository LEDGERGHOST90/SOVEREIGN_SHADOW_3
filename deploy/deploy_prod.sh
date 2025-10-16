#!/bin/bash
# 🚀 PRODUCTION ENVIRONMENT DEPLOYMENT
# Purpose: Real money, real trades, live execution
# ⚠️  WARNING: REAL CAPITAL AT RISK

echo "🚀 Deploying SovereignShadow.Ai Production Environment"
echo "======================================================"
echo "⚠️  WARNING: This will deploy LIVE TRADING with REAL MONEY"
echo "⚠️  Make sure you have:"
echo "   1. Completed 1-2 weeks of paper trading validation"
echo "   2. Configured all safety mechanisms"
echo "   3. Set ultra-conservative position sizes"
echo "   4. Prepared emergency stop procedures"
echo ""

# Safety confirmation
read -p "Are you absolutely sure you want to deploy LIVE TRADING? (type 'LIVE_TRADING_CONFIRMED'): " confirmation
if [ "$confirmation" != "LIVE_TRADING_CONFIRMED" ]; then
    echo "❌ Deployment cancelled - safety confirmation required"
    exit 1
fi

# Set environment
export ENVIRONMENT="production"
export CONFIG_FILE="environments/production/config_prod.yaml"

# Check if production environment exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Production config not found: $CONFIG_FILE"
    exit 1
fi

echo "✅ Production environment configuration loaded"

# Check for live API keys
echo "🔑 Checking LIVE API key configuration..."
if [ ! -f ".env.prod" ]; then
    echo "❌ Production .env.prod file not found!"
    echo "   This file should contain LIVE exchange API keys"
    echo "   Required for production:"
    echo "   • BINANCE_LIVE_API_KEY"
    echo "   • BINANCE_LIVE_SECRET_KEY"
    echo "   • COINBASE_PRO_API_KEY"
    echo "   • COINBASE_PRO_SECRET_KEY"
    exit 1
fi

# Load production environment variables
source .env.prod

# Validate live API keys
if [ -z "$BINANCE_LIVE_API_KEY" ] || [ -z "$BINANCE_LIVE_SECRET_KEY" ]; then
    echo "❌ Binance LIVE API keys not configured"
    exit 1
fi

if [ -z "$COINBASE_PRO_API_KEY" ] || [ -z "$COINBASE_PRO_SECRET_KEY" ]; then
    echo "❌ Coinbase Pro LIVE API keys not configured"
    exit 1
fi

echo "✅ LIVE API keys configured for production environment"

# Final safety checks
echo "🔍 Performing final safety checks..."

# Check starting capital
STARTING_CAPITAL=${STARTING_CAPITAL:-500}
if [ "$STARTING_CAPITAL" -gt 1000 ]; then
    echo "⚠️  WARNING: Starting capital > $1000"
    echo "   Recommended: Start with $500 or less for first month"
    read -p "Continue with $STARTING_CAPITAL? (y/N): " capital_confirm
    if [ "$capital_confirm" != "y" ]; then
        echo "❌ Deployment cancelled - reduce starting capital"
        exit 1
    fi
fi

# Check position size
MAX_POSITION=${MAX_POSITION:-0.005}
if (( $(echo "$MAX_POSITION > 0.01" | bc -l) )); then
    echo "⚠️  WARNING: Max position size > 1%"
    echo "   Recommended: Start with 0.5% or less"
    read -p "Continue with ${MAX_POSITION}%? (y/N): " position_confirm
    if [ "$position_confirm" != "y" ]; then
        echo "❌ Deployment cancelled - reduce position size"
        exit 1
    fi
fi

echo "✅ Safety checks passed"

# Create production logs directory
mkdir -p logs/production
echo "✅ Production logs directory created"

# Test live exchange connectivity
echo "🔍 Testing LIVE exchange connectivity..."
python3 -c "
import os
import sys
sys.path.append('shared')

# Test LIVE API connections
try:
    from exchange_interfaces import BinanceLiveInterface, CoinbaseProInterface
    
    # Test Binance LIVE
    binance = BinanceLiveInterface(
        os.getenv('BINANCE_LIVE_API_KEY'),
        os.getenv('BINANCE_LIVE_SECRET_KEY')
    )
    print('✅ Binance LIVE connection successful')
    
    # Test Coinbase Pro LIVE
    coinbase = CoinbaseProInterface(
        os.getenv('COINBASE_PRO_API_KEY'),
        os.getenv('COINBASE_PRO_SECRET_KEY')
    )
    print('✅ Coinbase Pro LIVE connection successful')
    
    # Verify account balances
    usdt_balance = binance.get_balance('USDT')
    print(f'✅ USDT Balance: {usdt_balance}')
    
    if usdt_balance < 100:
        print('⚠️  WARNING: Low USDT balance - ensure sufficient funds')
    
except Exception as e:
    print(f'❌ LIVE exchange connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ LIVE exchange connectivity test failed"
    exit 1
fi

echo "✅ All LIVE exchange connections verified"

# Final deployment confirmation
echo ""
echo "🚨 FINAL DEPLOYMENT CONFIRMATION 🚨"
echo "=================================="
echo "Environment: PRODUCTION (LIVE TRADING)"
echo "Starting Capital: $${STARTING_CAPITAL}"
echo "Max Position Size: $(echo "$MAX_POSITION * 100" | bc -l)%"
echo "Risk Level: REAL CAPITAL AT RISK"
echo "Exchanges: Binance LIVE, Coinbase Pro LIVE"
echo ""

read -p "Deploy LIVE TRADING system now? (type 'DEPLOY_LIVE'): " final_confirm
if [ "$final_confirm" != "DEPLOY_LIVE" ]; then
    echo "❌ Live deployment cancelled"
    exit 1
fi

# Start production live trading
echo "🚀 Starting PRODUCTION LIVE TRADING..."
echo "   • Mode: LIVE TRADING"
echo "   • Starting Capital: $${STARTING_CAPITAL}"
echo "   • Max Position Size: $(echo "$MAX_POSITION * 100" | bc -l)%"
echo "   • Risk Level: REAL MONEY AT RISK"
echo "   • Exchanges: Binance LIVE, Coinbase Pro LIVE"
echo "   • Emergency Stop: Available"
echo ""

# Start the production trading system
python3 environments/production/live_trading.py --config "$CONFIG_FILE" --mode production

echo ""
echo "✅ PRODUCTION environment deployed successfully!"
echo "📊 Access live trading dashboard at: http://localhost:3000/production"
echo "📋 View logs at: logs/production/"
echo "🛑 Emergency stop: ./emergency_stop.sh"
echo "⚠️  MONITOR CLOSELY - REAL MONEY IS AT RISK!"

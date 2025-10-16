#!/bin/bash
# 🏗️ DEVELOPMENT ENVIRONMENT DEPLOYMENT
# Purpose: Code development & algorithm testing

echo "🏗️ Deploying SovereignShadow.Ai Development Environment"
echo "========================================================"

# Set environment
export ENVIRONMENT="dev"
export CONFIG_FILE="environments/dev/config_dev.yaml"

# Check if development environment exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Development config not found: $CONFIG_FILE"
    exit 1
fi

echo "✅ Development environment configuration loaded"

# Create development logs directory
mkdir -p logs/dev
echo "✅ Development logs directory created"

# Install development dependencies
echo "📦 Installing development dependencies..."
pip3 install -r requirements-dev.txt 2>/dev/null || echo "⚠️  requirements-dev.txt not found, using base requirements"

# Run development simulation
echo "🚀 Starting development simulation..."
echo "   • Mode: Simulation"
echo "   • Starting Balance: $10,000 (fake money)"
echo "   • Max Position Size: 5%"
echo "   • Risk Level: ZERO"
echo ""

# Start the development trading system
python3 environments/dev/simulate_trading.py --config "$CONFIG_FILE" --mode dev

echo ""
echo "✅ Development environment deployed successfully!"
echo "📊 Access development dashboard at: http://localhost:3000/dev"
echo "📋 View logs at: logs/dev/"
echo "🛑 Stop with: Ctrl+C"

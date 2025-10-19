#!/bin/bash

# 🏴 Sovereign Shadow Dev Container - Post-Creation Setup
# This script runs once after the container is created

set -e

echo "🏴 Initializing Sovereign Shadow Development Environment..."

# 🎨 Configure shell
echo ""
echo "📝 Configuring shell..."
cat >> ~/.zshrc <<'EOF'

# 🏴 Sovereign Shadow Configuration
export PYTHONPATH="/workspace:$PYTHONPATH"
export WORKSPACE=/workspace

# Aliases
alias python=python3
alias pip=pip3
alias ss='cd /workspace'
alias trade='python3 /workspace/sovereign_shadow_orchestrator.py'
alias balance='python3 /workspace/scripts/get_real_balances.py'
alias monitor='python3 /workspace/scripts/live_trading_monitor.py'

# Trading shortcuts
alias paper='cd /workspace && ./START_SOVEREIGN_SHADOW.sh paper'
alias live='cd /workspace && ./START_SOVEREIGN_SHADOW.sh live'

# Development
alias logs='tail -f /workspace/logs/*.log'
alias status='python3 /workspace/FINAL_API_STATUS.py'

echo "🏴 Sovereign Shadow Development Environment Ready"
echo "💰 Capital: \$8,260 | Target: \$50,000"
echo ""
echo "Quick Commands:"
echo "  ss          - Go to workspace"
echo "  balance     - Check real balances"
echo "  status      - API status check"
echo "  paper       - Start paper trading"
echo "  live        - Start live trading"
echo ""
EOF

# 📦 Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "/workspace/requirements.txt" ]; then
    pip install --user -r /workspace/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping..."
fi

# 🔍 Check for .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ -f "/workspace/.env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file not found!"
    echo "   Create one based on .env.template if available"
fi

# 📁 Create necessary directories
echo ""
echo "📁 Setting up directories..."
mkdir -p /workspace/logs
mkdir -p /workspace/logs/dev
mkdir -p /workspace/logs/ai_enhanced
mkdir -p /workspace/.cache
echo "✅ Directories ready"

# 🧪 Verify Python environment
echo ""
echo "🧪 Verifying Python environment..."
python3 --version
pip --version
echo "✅ Python environment verified"

# 📊 Display system info
echo ""
echo "📊 Container System Info:"
echo "   Python: $(python3 --version)"
echo "   Pip: $(pip --version | cut -d' ' -f2)"
echo "   Workspace: /workspace"
echo "   User: $(whoami)"
echo ""

# 🎯 Final message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Sovereign Shadow Dev Container Ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Next Steps:"
echo "   1. Verify API connections: python3 scripts/validate_api_connections.py"
echo "   2. Check balances: balance"
echo "   3. Start paper trading: paper"
echo ""
echo "📚 Documentation: /workspace/Master_LOOP_Creation/README_START_HERE.md"
echo "🔧 Dev Container Guide: /workspace/DEV_CONTAINERS_GUIDE.md"
echo ""
echo "Fearless. Bold. Smiling through chaos. 🏴"
echo ""


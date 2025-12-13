#!/bin/bash
# 🏴 SOVEREIGN SHADOW II - INSTALLATION SCRIPT

echo "======================================================================="
echo "🏴 SOVEREIGN SHADOW II - INSTALLATION"
echo "======================================================================="

# Check Python version
echo ""
echo "📍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install pandas numpy python-dotenv || {
    echo "❌ Failed to install dependencies"
    exit 1
}

echo "✅ Core dependencies installed"

# Try to install Coinbase SDK
echo ""
echo "📦 Installing Coinbase Advanced Trade SDK..."
pip3 install coinbase-advanced-py || {
    echo "⚠️  Coinbase SDK installation failed (may need to install manually)"
}

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p data logs
echo "✅ Directories created"

# Copy environment template
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "✅ Created .env file (please edit with your credentials)"
else
    echo "ℹ️  .env file already exists"
fi

# Test imports
echo ""
echo "🧪 Testing imports..."
python3 -c "import pandas; import numpy; print('✅ pandas and numpy working')" || {
    echo "❌ Import test failed"
    exit 1
}

echo ""
echo "======================================================================="
echo "✅ INSTALLATION COMPLETE"
echo "======================================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit configuration:"
echo "   nano .env"
echo ""
echo "2. Add your Coinbase API credentials:"
echo "   COINBASE_API_KEY=your_key_here"
echo "   COINBASE_API_SECRET=your_secret_here"
echo ""
echo "3. Test the system:"
echo "   python3 test_system.py"
echo ""
echo "4. Run the orchestrator:"
echo "   python3 core/orchestrator.py"
echo ""
echo "📖 Read DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "======================================================================="

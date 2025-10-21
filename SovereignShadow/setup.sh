#!/bin/bash

# SovereignShadow VES System Setup Script
# Run this to initialize your environment

echo "🏰 SovereignShadow VES System Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/{vault,engine,siphon}
mkdir -p logs
mkdir -p backups
mkdir -p tmp
echo "✅ Directories created"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API credentials before running!"
    echo "   Run: nano .env"
else
    echo "✅ .env file exists"
fi
echo ""

# Test imports
echo "Testing module imports..."
python3 -c "
try:
    from modules.vault_manager import VaultManager
    from modules.engine_manager import EngineManager
    from modules.siphon_distributor import SiphonDistributor
    print('✅ All modules imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Module import test failed"
    exit 1
fi
echo ""

# Check for API keys
echo "Checking configuration..."
if grep -q "your_.*_here" .env; then
    echo "⚠️  WARNING: Default placeholder values found in .env"
    echo "   Please update with your actual API credentials"
else
    echo "✅ .env file appears to be configured"
fi
echo ""

# Display next steps
echo "📋 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Configure your API keys in .env file:"
echo "   nano .env"
echo ""
echo "2. Test the system with a single cycle:"
echo "   python main.py --mode single"
echo ""
echo "3. Check system status:"
echo "   python main.py --mode status"
echo ""
echo "4. Run continuous mode (15-minute cycles):"
echo "   python main.py --mode continuous --interval 15"
echo ""
echo "5. View logs:"
echo "   tail -f logs/system.log"
echo ""
echo "6. Emergency stop (if needed):"
echo "   python main.py --mode emergency"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "🚀 Happy trading!"
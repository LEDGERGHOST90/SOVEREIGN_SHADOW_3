#!/bin/bash
# Replit Setup Script for SovereignShadow.Ai

echo "🏰 Setting up SovereignShadow.Ai Trading Platform on Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional trading dependencies
echo "📊 Installing trading libraries..."
pip install ccxt python-dotenv aiohttp websocket-client

# Install Node.js dependencies (if package.json exists)
if [ -f "app/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd app
    npm install
    cd ..
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p logs/ai_enhanced
mkdir -p data
mkdir -p environments/{dev,staging,production}

# Set up environment files from templates
echo "⚙️ Setting up environment templates..."
if [ -f "env_template.txt" ] && [ ! -f ".env" ]; then
    cp env_template.txt .env
    echo "✅ Created .env from template"
fi

echo "✅ Setup complete!"
echo ""
echo "🔑 NEXT STEPS:"
echo "1. Go to Secrets (🔒 icon in left sidebar)"
echo "2. Add your API keys:"
echo "   - COINBASE_API_KEY"
echo "   - COINBASE_API_SECRET"
echo "   - OKX_API_KEY"
echo "   - OKX_API_SECRET"
echo "   - KRAKEN_API_KEY"
echo "   - KRAKEN_API_SECRET"
echo ""
echo "3. Click 'Run' button to start!"
echo ""
echo "🛡️ SAFETY: System starts in SANDBOX mode by default"
echo "   Real trading is DISABLED until you explicitly enable it"









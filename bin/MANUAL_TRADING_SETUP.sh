#!/bin/bash
# 🏴 SOVEREIGN SHADOW - MANUAL TRADING SETUP
# RUN THIS NOW TO ENABLE MANUAL TRADING

echo "🚀 SETTING UP MANUAL TRADING ENVIRONMENT..."
echo "============================================"

# Create .env file with your credentials
cat > .env << 'EOL'
# 🏴 SOVEREIGN SHADOW - EXCHANGE API CREDENTIALS

# OKX EXCHANGE (ALREADY CONFIGURED)
OKX_API_KEY=9c0aa605-e38f-4388-b65d-da5ac01081ec
OKX_SECRET_KEY=115A249DF5534DE7F42ABB847F9CA617
OKX_PASSPHRASE=okx_Shadow

# COINBASE - REPLACE WITH YOUR REAL KEYS!
# Get from: https://www.coinbase.com/settings/api
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_secret_here

# KRAKEN (OPTIONAL)
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_PRIVATE_KEY=your_kraken_secret_here
EOL

echo "✅ .env file created"
echo ""
echo "⚠️  IMPORTANT: Edit .env and add your REAL Coinbase API keys!"
echo "   Run: nano .env"
echo ""
echo "Then test your connections:"
echo "   python scripts/validate_api_connections.py"
echo ""
echo "============================================"



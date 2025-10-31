#!/bin/bash

echo ""
echo "========================================"
echo "🔥 SOVEREIGN SHADOW EMPIRE QUICK START"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ No .env file found!"
    echo ""
    echo "Creating .env from template..."
    cp .env.template .env
    echo ""
    echo "✅ .env created. NOW ADD YOUR API KEYS:"
    echo "   nano .env"
    echo ""
    echo "GET YOUR KEYS FROM:"
    echo "   Coinbase: https://portal.cdp.coinbase.com/access/api"
    echo "   OKX: https://www.okx.com/account/my-api"
    echo "   Kraken: https://www.kraken.com/u/security/api"
    echo ""
    exit 1
fi

echo "✅ .env file found"
echo ""
echo "🚀 LAUNCHING UNIFIED EMPIRE COMMAND CENTER..."
echo ""

python3 sovereign_empire_core.py


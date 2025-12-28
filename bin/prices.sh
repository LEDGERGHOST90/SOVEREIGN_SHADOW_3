#!/usr/bin/env bash
# Quick price check for locked watchlist
# Usage: ./bin/prices.sh

SS3="/Volumes/LegacySafe/SS_III"
cd "$SS3"

PYTHONPATH="$SS3" python3 << 'EOF'
import ccxt
import json
import os
from pathlib import Path

# Load API keys
env_file = Path("/Volumes/LegacySafe/SS_III/.env")
for line in env_file.read_text().splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k] = v

# Load watchlist
with open("/Volumes/LegacySafe/SS_III/config/watchlist.json") as f:
    config = json.load(f)

# Setup exchanges
binance = ccxt.binanceus({
    'apiKey': os.environ.get('BINANCE_US_API_KEY'),
    'secret': os.environ.get('BINANCE_US_API_SECRET') or os.environ.get('BINANCE_US_SECRET_KEY'),
    'enableRateLimit': True,
})

kraken = ccxt.kraken({
    'apiKey': os.environ.get('KRAKEN_API_KEY'),
    'secret': os.environ.get('KRAKEN_PRIVATE_KEY'),
    'enableRateLimit': True,
})

print("═" * 60)
print(" SOVEREIGN SHADOW III - LOCKED WATCHLIST")
print("═" * 60)
print(f"{'Asset':<8} {'Price':>12} {'24h':>8} {'15m':>8} {'4h':>8}")
print("-" * 60)

for asset in config['primary_watchlist']['assets']:
    sym = asset['symbol']
    exc = asset['exchange']
    tier = asset['tier']

    try:
        if exc == 'binanceus':
            exchange = binance
            pair = f"{sym}/USDT"
        else:
            exchange = kraken
            pair = f"{sym}/USD"

        ticker = exchange.fetch_ticker(pair)
        price = ticker['last']
        pct_24h = ticker.get('percentage', 0) or 0

        # Get trends
        try:
            ohlcv_15m = exchange.fetch_ohlcv(pair, '15m', limit=4)
            ohlcv_4h = exchange.fetch_ohlcv(pair, '4h', limit=4)
            pct_15m = ((ohlcv_15m[-1][4] - ohlcv_15m[0][1]) / ohlcv_15m[0][1]) * 100 if len(ohlcv_15m) >= 4 else 0
            pct_4h = ((ohlcv_4h[-1][4] - ohlcv_4h[0][1]) / ohlcv_4h[0][1]) * 100 if len(ohlcv_4h) >= 4 else 0
        except:
            pct_15m = 0
            pct_4h = 0

        # Format price
        if price >= 1000:
            price_str = f"${price:>10,.0f}"
        elif price >= 1:
            price_str = f"${price:>10.2f}"
        else:
            price_str = f"${price:>10.4f}"

        flag = " 🔥" if pct_4h > 2 or pct_4h < -2 else ""
        print(f"{sym:<8} {price_str} {pct_24h:>+7.2f}% {pct_15m:>+7.2f}% {pct_4h:>+7.2f}%{flag}")

    except Exception as e:
        print(f"{sym:<8} {'--':>12} {str(e)[:25]}")

print("═" * 60)
print(" Locked: 2025-12-28 | Foresight Stack integrated")
print("═" * 60)
EOF

#!/bin/bash
# ==============================================
# SOVEREIGN SHADOW III - FreqTrade Launcher
# ==============================================
# DynamicCrossfire Strategy on Coinbase Advanced
# INJ/USDC, LINK/USDC | 15m Timeframe
# ==============================================

cd /Volumes/LegacySafe/SS_III/freqtrade

MODE=${1:-"dry-run"}

echo "=========================================="
echo "  SOVEREIGN SHADOW III - FreqTrade"
echo "=========================================="
echo "  Strategy: DynamicCrossfire"
echo "  Pairs: INJ/USDC, LINK/USDC"
echo "  Mode: $MODE"
echo "=========================================="

if [ "$MODE" == "live" ]; then
    echo "⚠️  LIVE MODE - Real money at risk!"
    echo "Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
    freqtrade trade -c config.json --strategy DynamicCrossfire
elif [ "$MODE" == "dry-run" ]; then
    echo "🧪 DRY RUN MODE - Paper trading"
    freqtrade trade --dry-run -c config.json --strategy DynamicCrossfire
elif [ "$MODE" == "backtest" ]; then
    echo "📊 BACKTEST MODE"
    freqtrade backtesting -c config.json --strategy DynamicCrossfire --timeframe 15m
else
    echo "Usage: ./start_bot.sh [dry-run|live|backtest]"
fi

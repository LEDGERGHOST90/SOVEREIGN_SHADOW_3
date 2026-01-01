#!/bin/bash
# Start the Sovereign Shadow III Trading System
# Usage: ./bin/start_system.sh [--live]

MODE="--paper"
if [ "$1" == "--live" ]; then
    MODE="--live"
    echo "⚠️  WARNING: LIVE TRADING MODE ENABLED"
    echo "   Real orders will be placed on Coinbase"
    sleep 3
fi

echo "Starting SS3 Trading System..."
echo "Mode: $MODE"
echo "Interval: 15 minutes"
echo "Logs: logs/overnight_*.log"
echo "Press Ctrl+C to stop"
echo "==================================================="

# Ensure we are in project root
cd "$(dirname "$0")/.."

# Export path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run loop
python3 bin/overnight_runner.py --interval 15 --duration 24 $MODE

#!/bin/bash
# 🏴 SOVEREIGN SHADOW - Install 24/7 Market Scanner
# Runs every 15 minutes using macOS launchd

set -e

PROJECT_ROOT="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
PLIST_NAME="com.sovereignshadow.market-scanner.plist"
PLIST_SOURCE="$PROJECT_ROOT/config/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"
LOG_DIR="$PROJECT_ROOT/logs/market_scanner"

echo "============================================="
echo "🏴 SOVEREIGN SHADOW 24/7 Market Scanner"
echo "   Installation Script"
echo "============================================="
echo

# Create log directory
echo "📁 Creating log directory..."
mkdir -p "$LOG_DIR"
echo "   ✅ $LOG_DIR"
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found in PATH"
    echo "   Please install Python 3 first"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo

# Check if requests library is installed
echo "📦 Checking for required Python libraries..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  'requests' library not found"
    echo "   Installing..."
    pip3 install requests
fi
echo "   ✅ All required libraries installed"
echo

# Unload existing job if running
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "🔄 Unloading existing scanner job..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    echo "   ✅ Unloaded"
    echo
fi

# Copy plist to LaunchAgents
echo "📋 Installing launchd configuration..."
cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "   ✅ Copied to $PLIST_DEST"
echo

# Load the job
echo "🚀 Loading market scanner job..."
launchctl load "$PLIST_DEST"
echo "   ✅ Loaded successfully"
echo

# Verify it's running
sleep 2
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "✅ Market scanner is now active!"
    echo
    echo "============================================="
    echo "📊 CONFIGURATION"
    echo "============================================="
    echo "   Interval: Every 15 minutes (900 seconds)"
    echo "   Script: $PROJECT_ROOT/bin/market_scanner_15min.py"
    echo "   Logs: $LOG_DIR/"
    echo "   Status: RUNNING"
    echo
    echo "============================================="
    echo "💡 COMMANDS"
    echo "============================================="
    echo "   Check status:"
    echo "     launchctl list | grep market-scanner"
    echo
    echo "   Stop scanner:"
    echo "     launchctl unload $PLIST_DEST"
    echo
    echo "   Restart scanner:"
    echo "     launchctl unload $PLIST_DEST"
    echo "     launchctl load $PLIST_DEST"
    echo
    echo "   View logs:"
    echo "     tail -f $LOG_DIR/stdout.log"
    echo "     tail -f $LOG_DIR/stderr.log"
    echo
    echo "   View latest scan:"
    echo "     cat $LOG_DIR/latest_scan.json | python3 -m json.tool"
    echo
    echo "   View scan history:"
    echo "     tail -20 $LOG_DIR/scan_history.jsonl"
    echo
    echo "============================================="
    echo "🏴 Scanner installed and running!"
    echo "   First scan will run immediately"
    echo "   Then every 15 minutes thereafter"
    echo "============================================="
    echo
else
    echo "❌ ERROR: Scanner did not load successfully"
    echo "   Check logs at: $LOG_DIR/stderr.log"
    exit 1
fi

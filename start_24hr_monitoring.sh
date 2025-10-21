#!/bin/bash

# 🏴 SOVEREIGN SHADOW - 24 HOUR MONITORING TEST

echo "🏴 SOVEREIGN SHADOW - 24 HOUR MONITORING TEST"
echo "=============================================="
echo ""
echo "📅 Start Time: $(date)"
echo "⏱️  Duration: 24 hours"
echo "📊 Mode: Market monitoring + data collection"
echo ""

# Create test directories
mkdir -p logs/24hr_test
mkdir -p monitoring/24hr_test/data

# Save start config
cat > monitoring/24hr_test/config.json << CONFIG
{
  "test_name": "24hr_monitoring_test",
  "start_time": "$(date -Iseconds)",
  "end_time": "$(date -v+24H -Iseconds)",
  "mode": "monitoring",
  "exchanges": ["binance_us", "kraken", "okx"],
  "status": "running"
}
CONFIG

echo "✅ Configuration saved"
echo ""
echo "📡 What we're monitoring:"
echo "   • Exchange prices (3 exchanges)"
echo "   • Market opportunities"
echo "   • System health"
echo "   • Performance metrics"
echo ""
echo "📁 Data will be saved to:"
echo "   logs/24hr_test/"
echo "   monitoring/24hr_test/data/"
echo ""
echo "🚀 Starting monitoring processes..."
echo ""

# Run dashboard in foreground
python3 scripts/premium_dashboard.py

echo ""
echo "✅ 24-hour test started!"
echo "🛑 Press Ctrl+C to stop"

#!/bin/bash
# ==============================================
# POSITION MONITOR - Auto TP/SL Execution
# ==============================================

cd /Volumes/LegacySafe/SS_III

MODE=${1:-"check"}

echo "=========================================="
echo "  POSITION MONITOR - SS_III"
echo "=========================================="

case $MODE in
    "check")
        echo "  Mode: Single Check"
        /Users/memphis/.pyenv/versions/3.11.9/bin/python3 bin/position_monitor.py
        ;;
    "dry")
        echo "  Mode: Dry Run (no execution)"
        /Users/memphis/.pyenv/versions/3.11.9/bin/python3 bin/position_monitor.py --dry-run
        ;;
    "daemon")
        echo "  Mode: Daemon (continuous monitoring)"
        echo "  Interval: 60 seconds"
        # Kill any existing daemon first (use exact match to avoid hitting system processes)
        pkill -f "python3 bin/position_monitor.py" 2>/dev/null || true
        sleep 1
        # Launch in background with nohup
        nohup /Users/memphis/.pyenv/versions/3.11.9/bin/python3 bin/position_monitor.py --daemon >> logs/position_monitor.log 2>&1 &
        DAEMON_PID=$!
        echo "  Started with PID: $DAEMON_PID"
        echo "  Log: logs/position_monitor.log"
        echo "  Stop: ./bin/start_position_monitor.sh stop"
        # Save PID for later
        echo $DAEMON_PID > /tmp/position_monitor.pid
        ;;
    "daemon-fast")
        echo "  Mode: Daemon (30s interval)"
        pkill -f "python3 bin/position_monitor.py" 2>/dev/null || true
        sleep 1
        nohup /Users/memphis/.pyenv/versions/3.11.9/bin/python3 bin/position_monitor.py --daemon --interval 30 >> logs/position_monitor.log 2>&1 &
        DAEMON_PID=$!
        echo "  Started with PID: $DAEMON_PID"
        echo $DAEMON_PID > /tmp/position_monitor.pid
        ;;
    "stop")
        echo "  Stopping daemon..."
        pkill -f "python3 bin/position_monitor.py" 2>/dev/null && echo "  Stopped." || echo "  No daemon running."
        rm -f /tmp/position_monitor.pid
        ;;
    *)
        echo "Usage: ./start_position_monitor.sh [check|dry|daemon|daemon-fast|stop]"
        echo ""
        echo "  check       - Run once, execute if TP/SL hit"
        echo "  dry         - Run once, no execution"
        echo "  daemon      - Run continuously in background (60s interval)"
        echo "  daemon-fast - Run continuously in background (30s interval)"
        echo "  stop        - Stop running daemon"
        ;;
esac

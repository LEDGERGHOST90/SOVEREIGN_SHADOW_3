#!/bin/bash
#
# SOVEREIGN SHADOW - Real-Time Alert Daemon Launcher
# Starts continuous monitoring of classified assets
#
# Usage:
#   ./bin/start_realtime_alerts.sh           # Start daemon
#   ./bin/start_realtime_alerts.sh stop      # Stop daemon
#   ./bin/start_realtime_alerts.sh status    # Check status
#

PROJECT_ROOT="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
PID_FILE="${PROJECT_ROOT}/logs/realtime_alerts.pid"
LOG_FILE="${PROJECT_ROOT}/logs/realtime_alerts.log"

cd "$PROJECT_ROOT"

# Activate venv if exists
if [ -f "${PROJECT_ROOT}/venv/bin/activate" ]; then
    source "${PROJECT_ROOT}/venv/bin/activate"
fi

start_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Daemon already running (PID: $PID)"
            return
        fi
    fi

    mkdir -p "$(dirname "$LOG_FILE")"

    echo "Starting Real-Time Alert Daemon..."
    nohup python3 scanners/realtime_alerts.py --daemon --interval 60 >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Daemon started (PID: $(cat $PID_FILE))"
    echo "Log file: $LOG_FILE"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping daemon (PID: $PID)..."
            kill $PID
            rm -f "$PID_FILE"
            echo "Daemon stopped."
        else
            echo "Daemon not running (stale PID file removed)"
            rm -f "$PID_FILE"
        fi
    else
        echo "No daemon running."
    fi
}

status_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Daemon RUNNING (PID: $PID)"
            echo ""
            echo "Last 10 log lines:"
            tail -10 "$LOG_FILE" 2>/dev/null || echo "(no logs yet)"
        else
            echo "Daemon NOT RUNNING (stale PID file)"
        fi
    else
        echo "Daemon NOT RUNNING"
    fi
}

case "${1:-start}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        status_daemon
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac

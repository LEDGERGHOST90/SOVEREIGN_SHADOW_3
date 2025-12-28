#!/usr/bin/env bash
#
# OVERNIGHT RUNNER SERVICE CONTROLLER
# Usage: ./overnight_service.sh [start|stop|status|logs|cycle]
#
set -euo pipefail

SS3_ROOT="/Volumes/LegacySafe/SS_III"
PLIST_NAME="com.sovereign.overnight"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LOG_DIR="$SS3_ROOT/logs"
PID_FILE="$SS3_ROOT/.overnight.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

create_plist() {
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${SS3_ROOT}/bin/overnight_runner.py</string>
        <string>--interval</string>
        <string>15</string>
        <string>--duration</string>
        <string>24</string>
        <string>--paper</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${SS3_ROOT}</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>${SS3_ROOT}</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/overnight_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/overnight_stderr.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>ThrottleInterval</key>
    <integer>60</integer>
</dict>
</plist>
EOF
    echo -e "${GREEN}Created launchd plist${NC}"
}

cmd_start() {
    echo -e "${YELLOW}Starting Overnight Runner...${NC}"

    # Ensure log directory exists
    mkdir -p "$LOG_DIR"

    # Check if already running via launchctl
    if launchctl list "$PLIST_NAME" &>/dev/null; then
        echo -e "${YELLOW}Already running via launchd${NC}"
        cmd_status
        return 0
    fi

    # Create/update plist
    create_plist

    # Load and start via launchd (auto-restarts on crash)
    launchctl load "$PLIST_PATH"
    launchctl start "$PLIST_NAME"

    sleep 2

    if launchctl list "$PLIST_NAME" &>/dev/null; then
        # Get PID from launchctl
        NEW_PID=$(launchctl list "$PLIST_NAME" 2>/dev/null | awk 'NR==2 {print $1}')
        [[ -n "$NEW_PID" && "$NEW_PID" != "-" ]] && echo "$NEW_PID" > "$PID_FILE"

        echo -e "${GREEN}Overnight Runner STARTED (launchd managed)${NC}"
        echo -e "${GREEN}Auto-restart on crash: ENABLED${NC}"
        echo ""
        echo "Monitoring: BTC, ETH, SOL, ENA, PENDLE, LDO"
        echo "Interval: Every 15 minutes"
        echo "Mode: Paper trading"
        echo ""
        echo "Commands:"
        echo "  ./bin/overnight_service.sh status  - Check status"
        echo "  ./bin/overnight_service.sh logs    - View live logs"
        echo "  ./bin/overnight_service.sh stop    - Stop service"
    else
        echo -e "${RED}Failed to start. Check logs:${NC}"
        echo "  tail -f $LOG_DIR/overnight_stderr.log"
    fi
}

cmd_stop() {
    echo -e "${YELLOW}Stopping Overnight Runner...${NC}"

    # Stop via launchd first (primary method)
    if launchctl list "$PLIST_NAME" &>/dev/null; then
        launchctl stop "$PLIST_NAME" 2>/dev/null || true
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
        echo -e "${GREEN}Overnight Runner STOPPED (launchd unloaded)${NC}"
    fi

    # Also kill any orphaned process
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID" 2>/dev/null || true
            sleep 1
            if ps -p "$PID" > /dev/null 2>&1; then
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi

    echo -e "${GREEN}Service fully stopped${NC}"
}

cmd_status() {
    echo "=== OVERNIGHT RUNNER STATUS ==="
    echo ""

    RUNNING=false

    # Check launchd first
    if launchctl list "$PLIST_NAME" &>/dev/null; then
        # Get PID from running process
        PID=$(pgrep -f "overnight_runner.py" | head -1)
        if [[ -n "$PID" ]]; then
            RUNNING=true
            echo -e "Service: ${GREEN}RUNNING${NC}"
            echo -e "Manager: ${GREEN}launchd (auto-restart on crash)${NC}"
            echo "PID: $PID"
            STARTED=$(ps -p "$PID" -o lstart= 2>/dev/null || echo "unknown")
            echo "Started: $STARTED"
        fi
    fi

    # Fallback to PID file check
    if [[ "$RUNNING" == "false" && -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            RUNNING=true
            echo -e "Service: ${GREEN}RUNNING${NC}"
            echo -e "Manager: ${YELLOW}nohup (no auto-restart)${NC}"
            echo "PID: $PID"
            STARTED=$(ps -p "$PID" -o lstart= 2>/dev/null || echo "unknown")
            echo "Started: $STARTED"
        fi
    fi

    if [[ "$RUNNING" == "false" ]]; then
        echo -e "Service: ${RED}STOPPED${NC}"
    fi

    echo ""

    # Show latest cycle
    LATEST_CYCLE=$(ls -t "$SS3_ROOT/data/overnight_results/"*.json 2>/dev/null | head -1)
    if [[ -n "$LATEST_CYCLE" ]]; then
        echo "Latest Cycle: $(basename "$LATEST_CYCLE")"
        echo "Time: $(stat -f '%Sm' "$LATEST_CYCLE")"

        # Extract key info
        if command -v jq &>/dev/null; then
            echo ""
            echo "Signals:"
            jq -r '.moondev_signals | to_entries[] | "  \(.key): \(.value.action)"' "$LATEST_CYCLE" 2>/dev/null || echo "  (parsing error)"
        fi
    else
        echo "No cycles run yet"
    fi

    echo ""
    echo "Log files:"
    echo "  $LOG_DIR/overnight_$(date +%Y%m%d).log"
}

cmd_logs() {
    LOG_FILE="$LOG_DIR/overnight_$(date +%Y%m%d).log"

    if [[ -f "$LOG_FILE" ]]; then
        echo "=== LIVE LOGS (Ctrl+C to exit) ==="
        tail -f "$LOG_FILE"
    else
        echo "No log file for today. Checking stdout..."
        tail -f "$LOG_DIR/overnight_stdout.log" 2>/dev/null || echo "No logs available"
    fi
}

cmd_cycle() {
    echo -e "${YELLOW}Running single cycle...${NC}"
    echo ""

    cd "$SS3_ROOT"
    PYTHONPATH="$SS3_ROOT" python3 bin/overnight_runner.py --once
}

cmd_help() {
    echo "OVERNIGHT RUNNER SERVICE"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start   - Start the background service"
    echo "  stop    - Stop the background service"
    echo "  status  - Show current status and latest cycle"
    echo "  logs    - Follow live log output"
    echo "  cycle   - Run a single cycle manually"
    echo "  help    - Show this help"
    echo ""
    echo "The service monitors markets every 15 minutes and:"
    echo "  1. Fetches OHLCV data from Binance.US, Kraken, Coinbase"
    echo "  2. Runs MoonDev strategies (3 verified)"
    echo "  3. Applies Manus research bias"
    echo "  4. Generates paper trades when signals align"
    echo ""
    echo "Results saved to: $SS3_ROOT/data/overnight_results/"
}

# Main
case "${1:-help}" in
    start)  cmd_start ;;
    stop)   cmd_stop ;;
    status) cmd_status ;;
    logs)   cmd_logs ;;
    cycle)  cmd_cycle ;;
    help)   cmd_help ;;
    *)      cmd_help ;;
esac

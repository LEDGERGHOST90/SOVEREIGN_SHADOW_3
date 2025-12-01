#!/bin/bash
# 🏴 MASTER LOOP CONTROL - Easy start/stop/monitor for the eternal heartbeat

set -e

REPO_ROOT="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
MASTER_LOOP="$REPO_ROOT/MASTER_TRADING_LOOP.py"
PID_FILE="$REPO_ROOT/logs/master_loop/master_loop.pid"
LOG_DIR="$REPO_ROOT/logs/master_loop"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOG_DIR"

print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}🏴  MASTER TRADING LOOP CONTROL${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Master Loop is RUNNING (PID: $PID)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  PID file exists but process is not running${NC}"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${RED}❌ Master Loop is NOT running${NC}"
        return 1
    fi
}

start_loop() {
    MODE=${1:-paper}
    INTERVAL=${2:-60}

    print_header
    echo ""

    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Master Loop is already running!${NC}"
        echo "Use 'stop' to stop it first, or 'restart' to restart."
        exit 1
    fi

    echo -e "${BLUE}🚀 Starting Master Trading Loop...${NC}"
    echo -e "   Mode: ${GREEN}$MODE${NC}"
    echo -e "   Scan Interval: ${GREEN}${INTERVAL}s${NC}"
    echo ""

    # Start the loop in background
    cd "$REPO_ROOT"
    nohup python3 "$MASTER_LOOP" --mode "$MODE" --interval "$INTERVAL" \
        > "$LOG_DIR/master_loop.out" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"

    sleep 2

    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Master Loop started successfully!${NC}"
        echo -e "   PID: $PID"
        echo -e "   Logs: $LOG_DIR"
        echo -e "   Output: $LOG_DIR/master_loop.out"
        echo ""
        echo -e "${BLUE}💡 Use './bin/MASTER_LOOP_CONTROL.sh status' to check status${NC}"
        echo -e "${BLUE}💡 Use './bin/MASTER_LOOP_CONTROL.sh logs' to tail logs${NC}"
        echo -e "${BLUE}💡 Use './bin/MASTER_LOOP_CONTROL.sh stop' to stop${NC}"
    else
        echo -e "${RED}❌ Failed to start Master Loop${NC}"
        echo "Check logs at: $LOG_DIR/master_loop.out"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_loop() {
    print_header
    echo ""

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")

        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 Stopping Master Loop (PID: $PID)...${NC}"
            kill $PID

            # Wait for process to stop (max 10 seconds)
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ Master Loop stopped successfully${NC}"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done

            # Force kill if still running
            echo -e "${YELLOW}⚠️  Process didn't stop gracefully, forcing...${NC}"
            kill -9 $PID 2>/dev/null || true
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ Master Loop force stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  PID file exists but process is not running${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${RED}❌ Master Loop is not running${NC}"
    fi
}

restart_loop() {
    MODE=${1:-paper}
    INTERVAL=${2:-60}

    print_header
    echo ""
    echo -e "${BLUE}🔄 Restarting Master Loop...${NC}"
    echo ""

    stop_loop
    sleep 2
    start_loop "$MODE" "$INTERVAL"
}

show_status() {
    print_header
    echo ""
    check_status
    echo ""

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            # Show process details
            echo -e "${BLUE}📊 Process Details:${NC}"
            ps aux | grep $PID | grep -v grep || true
            echo ""

            # Show recent stats
            LATEST_LOG=$(ls -t "$LOG_DIR"/master_loop_*.log 2>/dev/null | head -1)
            if [ -n "$LATEST_LOG" ]; then
                echo -e "${BLUE}📈 Recent Activity:${NC}"
                tail -n 5 "$LATEST_LOG"
            fi
        fi
    fi
}

show_logs() {
    LINES=${1:-50}

    print_header
    echo ""

    LATEST_LOG=$(ls -t "$LOG_DIR"/master_loop_*.log 2>/dev/null | head -1)

    if [ -n "$LATEST_LOG" ]; then
        echo -e "${BLUE}📜 Showing last $LINES lines from: $LATEST_LOG${NC}"
        echo ""
        tail -n $LINES "$LATEST_LOG"
    else
        echo -e "${RED}❌ No log files found${NC}"
    fi
}

tail_logs() {
    print_header
    echo ""

    LATEST_LOG=$(ls -t "$LOG_DIR"/master_loop_*.log 2>/dev/null | head -1)

    if [ -n "$LATEST_LOG" ]; then
        echo -e "${BLUE}📜 Tailing: $LATEST_LOG${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        tail -f "$LATEST_LOG"
    else
        echo -e "${RED}❌ No log files found${NC}"
    fi
}

show_stats() {
    print_header
    echo ""

    LATEST_EVENTS=$(ls -t "$LOG_DIR"/events_*.json 2>/dev/null | head -1)

    if [ -n "$LATEST_EVENTS" ]; then
        echo -e "${BLUE}📊 Statistics from: $LATEST_EVENTS${NC}"
        echo ""

        # Count events
        TOTAL_TRADES=$(grep -c '"event": "TRADE_EXECUTION_COMPLETE"' "$LATEST_EVENTS" 2>/dev/null || echo 0)
        SUCCESSFUL=$(grep '"success": true' "$LATEST_EVENTS" 2>/dev/null | wc -l | xargs)

        echo -e "Total Trades: ${GREEN}$TOTAL_TRADES${NC}"
        echo -e "Successful: ${GREEN}$SUCCESSFUL${NC}"
        echo ""

        # Show recent events
        echo -e "${BLUE}Recent Events:${NC}"
        tail -n 10 "$LATEST_EVENTS" | jq -r '.event + " - " + .timestamp' 2>/dev/null || tail -n 10 "$LATEST_EVENTS"
    else
        echo -e "${RED}❌ No event logs found${NC}"
    fi
}

show_help() {
    print_header
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh <command> [options]"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  start [mode] [interval]  - Start the master loop"
    echo "                             mode: paper (default), live, monitor"
    echo "                             interval: seconds between scans (default: 60)"
    echo "  stop                     - Stop the master loop"
    echo "  restart [mode] [interval]- Restart the master loop"
    echo "  status                   - Show current status"
    echo "  logs [lines]             - Show recent logs (default: 50 lines)"
    echo "  tail                     - Follow logs in real-time"
    echo "  stats                    - Show trading statistics"
    echo "  help                     - Show this help message"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh start paper 60"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh start live 30"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh stop"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh restart paper"
    echo "  ./bin/MASTER_LOOP_CONTROL.sh tail"
    echo ""
    echo -e "${YELLOW}⚠️  SAFETY REMINDER:${NC}"
    echo "  - Always start in PAPER mode first!"
    echo "  - Test for 24 hours minimum before live trading"
    echo "  - Your Ledger ($6,514.65) is always protected"
    echo "  - Active capital: $1,638.49 (Coinbase hot wallet)"
    echo ""
}

# Main command router
case "${1:-help}" in
    start)
        start_loop "${2:-paper}" "${3:-60}"
        ;;
    stop)
        stop_loop
        ;;
    restart)
        restart_loop "${2:-paper}" "${3:-60}"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "${2:-50}"
        ;;
    tail)
        tail_logs
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

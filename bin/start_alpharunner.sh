#!/usr/bin/env bash
#
# start_alpharunner.sh - Launch AlphaRunner + SS_III Backend
#
# Features:
# - Kills existing listeners on target ports
# - Verifies health before claiming ONLINE
# - Clean shutdown on Ctrl+C (kills only what we started)
# - Logs to ./.logs for debugging
# - Forces Vite port with --strictPort (no surprise 3000)
#

set -euo pipefail

SS3_ROOT="${SS3_ROOT:-/Volumes/LegacySafe/SS_III}"
API_PORT="${API_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

API_PID=""
FRONTEND_PID=""

LOG_DIR="${SS3_ROOT}/.logs"
API_LOG="${LOG_DIR}/api_${API_PORT}.log"
FE_LOG="${LOG_DIR}/frontend_${FRONTEND_PORT}.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

cleanup() {
  echo ""
  echo -e "${YELLOW}Shutting down...${NC}"

  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
    echo "  Killed Frontend (PID ${FRONTEND_PID})"
  fi

  if [[ -n "${API_PID}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" 2>/dev/null || true
    echo "  Killed API (PID ${API_PID})"
  fi

  exit 0
}

trap cleanup SIGINT SIGTERM

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo -e "  ${YELLOW}Port $port is in use → killing listener(s)${NC}"
    # Try graceful first
    echo "$pids" | xargs kill 2>/dev/null || true
    sleep 1
    # Force if still alive
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      echo "$pids" | xargs kill -9 2>/dev/null || true
      sleep 1
    fi
  fi
}

wait_for_health() {
  local url="$1"
  local max_attempts="${2:-25}"
  local sleep_s="${3:-0.5}"
  local attempt=0

  while (( attempt < max_attempts )); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    attempt=$((attempt + 1))
    sleep "$sleep_s"
  done
  return 1
}

echo ""
echo "========================================"
echo "  AlphaRunner + SS_III Backend"
echo "========================================"
echo ""

# === Step 1: Start API Backend ===
echo -e "[1/2] ${YELLOW}Starting API Backend...${NC}"
kill_port "$API_PORT"

cd "$SS3_ROOT"
: > "$API_LOG"

# Export port for Python server
export API_PORT

python3 web_api/shadow_api_server.py >"$API_LOG" 2>&1 &
API_PID=$!
echo "     PID: $API_PID"
echo "     Log: $API_LOG"

if wait_for_health "http://localhost:${API_PORT}/api/" 30 0.5; then
  echo -e "     Status: ${GREEN}ONLINE${NC}"
else
  echo -e "     Status: ${RED}FAILED${NC}"
  echo "     Last 80 lines of API log:"
  tail -n 80 "$API_LOG" || true
  kill "$API_PID" 2>/dev/null || true
  exit 1
fi

# === Step 2: Start Frontend ===
echo ""
echo -e "[2/2] ${YELLOW}Starting Frontend...${NC}"
kill_port "$FRONTEND_PORT"

cd "$SS3_ROOT/shadow.ai_-alpharunner"
: > "$FE_LOG"

# Force port + strictPort so banner is always truthful
npm run dev -- --port "$FRONTEND_PORT" --strictPort >"$FE_LOG" 2>&1 &
FRONTEND_PID=$!
echo "     PID: $FRONTEND_PID"
echo "     Log: $FE_LOG"

# Vite can take a moment; this checks actual HTTP availability.
if wait_for_health "http://localhost:${FRONTEND_PORT}/" 60 0.5; then
  echo -e "     Status: ${GREEN}ONLINE${NC}"
else
  # If process died, show log.
  if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo -e "     Status: ${RED}FAILED${NC}"
    echo "     Last 120 lines of Frontend log:"
    tail -n 120 "$FE_LOG" || true
    cleanup
  else
    echo -e "     Status: ${YELLOW}STARTING${NC} (Vite still compiling...)"
  fi
fi

# === Summary ===
echo ""
echo "========================================"
echo -e "  ${GREEN}Services Running${NC}"
echo "========================================"
echo ""
echo "  API:      http://localhost:${API_PORT}/api/"
echo "  Frontend: http://localhost:${FRONTEND_PORT}/"
echo ""
echo "  Logs:"
echo "    API:      $API_LOG"
echo "    Frontend: $FE_LOG"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

wait

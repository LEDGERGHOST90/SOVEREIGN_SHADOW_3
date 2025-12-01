#!/bin/bash
# =============================================================================
# SOVEREIGN SHADOW - Neural Hub Startup Script
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           SOVEREIGN SHADOW - NEURAL HUB                      ║"
echo "║                  Starting System...                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Gemini API Key
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    fi
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}ERROR: GEMINI_API_KEY not set!${NC}"
    echo "Set it with: export GEMINI_API_KEY=your_key"
    echo "Or add to $PROJECT_ROOT/.env"
    exit 1
fi

echo -e "${GREEN}✓ Gemini API Key found${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down Neural Hub...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo -e "${GREEN}Shutdown complete${NC}"
}

trap cleanup EXIT

# Start Backend
echo -e "\n${CYAN}[1/2] Starting Backend Server...${NC}"
cd "$SCRIPT_DIR/backend"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip3 install -q -r requirements.txt
fi

# Start uvicorn in background
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started on http://localhost:8000${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend...${NC}"
sleep 3

# Start Frontend
echo -e "\n${CYAN}[2/2] Starting Frontend Dev Server...${NC}"
cd "$SCRIPT_DIR/frontend"

# Install node dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start Vite dev server
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started on http://localhost:5173${NC}"

# Success message
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              NEURAL HUB IS NOW ONLINE                        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Frontend:  http://localhost:5173                            ║"
echo "║  Backend:   http://localhost:8000                            ║"
echo "║  API Docs:  http://localhost:8000/docs                       ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Keep script running
wait

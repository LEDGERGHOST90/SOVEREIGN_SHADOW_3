#!/bin/bash
#
# SovereignShadow Unified Startup
# Starts both the API backend and Gemini frontend
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗      ║
║       ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝      ║
║       ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗        ║
║       ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝        ║
║       ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗      ║
║       ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝      ║
║                                                               ║
║                  UNIFIED TRADING SYSTEM                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.10+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "npm not found. Please install Node.js"
    exit 1
fi

# Check for required Python packages
echo -e "${YELLOW}Checking Python packages...${NC}"
pip3 install -q fastapi uvicorn pydantic 2>/dev/null || true

# Create data directory
mkdir -p memory/api_data

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start API backend
echo -e "${GREEN}Starting API backend on http://localhost:8000${NC}"
python3 api/sovereign_api.py &
API_PID=$!

# Wait for API to be ready
sleep 2
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${YELLOW}Waiting for API to start...${NC}"
    sleep 3
fi

# Start Gemini frontend
echo -e "${GREEN}Starting Gemini frontend on http://localhost:5173${NC}"
cd "Sov.Shade{11:21:25}-GeminiAi"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!

cd ..

echo -e "${GREEN}"
cat << 'EOF'

╔═══════════════════════════════════════════════════════════════╗
║                    SYSTEM RUNNING                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  API Backend:    http://localhost:8000                        ║
║  API Docs:       http://localhost:8000/docs                   ║
║  Gemini App:     http://localhost:5173                        ║
║                                                               ║
║  Press Ctrl+C to stop all services                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

# Wait for processes
wait

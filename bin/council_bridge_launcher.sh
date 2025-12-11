#!/bin/bash
# ============================================================================
# Council Bridge Launcher - Loads .env and starts the backend
# ============================================================================

SS3_ROOT="/Volumes/LegacySafe/Shadow-3-Legacy-Loop-Platform"
BACKEND_DIR="$SS3_ROOT/neural_hub/backend"

# Load environment from .env
if [ -f "$SS3_ROOT/.env" ]; then
    export $(grep -v '^#' "$SS3_ROOT/.env" | grep -v '^$' | xargs)
fi

# Activate venv if exists
if [ -f "$SS3_ROOT/venv/bin/activate" ]; then
    source "$SS3_ROOT/venv/bin/activate"
fi

# Start the server
cd "$BACKEND_DIR"
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000


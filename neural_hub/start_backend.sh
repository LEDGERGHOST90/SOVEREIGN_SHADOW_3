#!/bin/bash
# Start only the backend server
cd "$(dirname "$0")/backend"
source ../../venv/bin/activate 2>/dev/null || true
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

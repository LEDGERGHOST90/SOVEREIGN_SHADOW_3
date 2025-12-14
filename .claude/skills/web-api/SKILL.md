---
name: web-api
description: Flask API server for portfolio, GIO integration, system access. 4 API modules.
---

# web_api - API Server

**Location:** `/Volumes/LegacySafe/SS_III/web_api/`

## What It Does

REST API for system access:

- **Flask Server** - Main API endpoint
- **GIO API** - Gemini integration endpoints
- **Portfolio API** - Portfolio data access
- **System Monitoring** - Health checks and status

## Key Modules

```
app.py           - Flask server (289 lines)
gio_api.py       - Gemini endpoints (222 lines)
portfolio_api.py - Portfolio access (246 lines)
start.sh         - Startup script
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/web_api

# Start API server
./start.sh

# Or run directly
python app.py
```

## Endpoints

- `GET /portfolio` - Portfolio data
- `GET /gio/analyze` - Gemini analysis
- `GET /health` - System health

## Status

- Files: 4 API modules
- Purpose: REST API for system access and monitoring

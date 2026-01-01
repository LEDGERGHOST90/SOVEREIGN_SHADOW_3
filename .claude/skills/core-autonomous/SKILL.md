---
name: core-autonomous
description: 24/7 autonomous trading loops. Master trading loop, daily status, terminal interface. 8 automation modules. (project)
---

# core/autonomous - 24/7 Trading Loops

**Location:** `/Volumes/LegacySafe/SS_III/core/autonomous/`

## What It Does

Autonomous trading and monitoring systems that run 24/7:

- **MASTER_TRADING_LOOP.py** - Main autonomous trading engine
- **autonomous_trading_loop.py** - Secondary trading automation
- **DAILY_STATUS_SYSTEM.py** - Daily portfolio/status reports
- **SHADOW_SYSTEM_LAUNCHER.py** - System startup orchestration

## Key Modules

```
MASTER_TRADING_LOOP.py       - Main 24/7 trading engine (25K+ lines)
autonomous_trading_loop.py   - Autonomous trade execution
DAILY_STATUS_SYSTEM.py       - Daily status reports
SHADOW_SYSTEM_LAUNCHER.py    - System launcher
JANE_STREET_DEPLOYMENT.py    - Advanced strategy deployment
CLAUDE_TERMINAL.py           - Claude Code terminal interface
TERMINAL_INTERFACE.py        - CLI interface
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/core/autonomous

# Start master trading loop
python MASTER_TRADING_LOOP.py

# Run daily status check
python DAILY_STATUS_SYSTEM.py

# Launch full system
python SHADOW_SYSTEM_LAUNCHER.py
```

## Status

- Files: 8 Python modules
- Purpose: 24/7 autonomous trading, monitoring, status reporting

---
name: core-autonomous
description: 24/7 trading loops - MASTER_TRADING_LOOP, JANE_STREET_DEPLOYMENT. 8 autonomous systems that never sleep.
---

# core/autonomous - 24/7 Trading Loops

**Location:** `/Volumes/LegacySafe/SS_III/core/autonomous/`

## What It Does

Continuous autonomous trading systems:

- **MASTER_TRADING_LOOP** - Main 24/7 orchestrator
- **JANE_STREET_DEPLOYMENT** - HFT-style execution
- **CLAUDE_TERMINAL** - AI terminal interface
- **SHADOW_SYSTEM_LAUNCHER** - System bootstrap
- **DAILY_STATUS_SYSTEM** - Daily reporting
- **RAY_AUTOMATED_TRADING** - Distributed trading

## Key Modules

```
MASTER_TRADING_LOOP.py         - 24/7 orchestrator
JANE_STREET_DEPLOYMENT.py      - HFT execution
CLAUDE_TERMINAL.py             - AI interface
SHADOW_SYSTEM_LAUNCHER.py      - System startup
DAILY_STATUS_SYSTEM.py         - Status reports
RAY_AUTOMATED_TRADING.py       - Distributed ops
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/core/autonomous

# Start 24/7 loop
python MASTER_TRADING_LOOP.py

# Run HFT deployment
python JANE_STREET_DEPLOYMENT.py

# Launch full system
python SHADOW_SYSTEM_LAUNCHER.py
```

## Status

- Files: 8 autonomous loops
- Purpose: 24/7 trading, HFT execution, system orchestration

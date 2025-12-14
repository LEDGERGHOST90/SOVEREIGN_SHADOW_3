---
name: eco-system
description: ECO_SYSTEM_4 - 6-stage autonomous trading pipeline. Research → Signal → Consensus → Approval → Execute → Learn. 4,878 Python files.
---

# ECO_SYSTEM_4 - Autonomous Trading Pipeline

**Location:** `/Volumes/LegacySafe/SS_III/ECO_SYSTEM_4/`

## What It Does

Complete autonomous trading ecosystem that runs every 15 minutes:

1. **Research** - Market scanning and data collection
2. **Signal** - Generate trading signals from data
3. **Consensus** - Multi-agent agreement on signals
4. **Approval** - Human-in-loop or auto-approval
5. **Execute** - Paper or live trading execution
6. **Learn** - Analyze results and improve

## Key Components

- **Risk Agent** - Pre-trade risk validation
- **Swarm Agent** - Multi-AI consensus
- **Approval Agent** - Decision gateway
- **Paper Trader** - Execution engine
- **Session Closer** - Post-trade analysis

## How to Use

```bash
# Run the full pipeline
cd /Volumes/LegacySafe/SS_III/ECO_SYSTEM_4
python main.py

# Check configuration
cat .env
```

## Entry Points

- `main.py` - Primary entry point for full pipeline
- `agents/research/` - Market research modules
- `agents/execution/paper_trader.py` - Trade execution

## Status

- Files: 4,878 Python files
- Credentials: ECO_SYSTEM_4/.env
- Mode: Paper trading

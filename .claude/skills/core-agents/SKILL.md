---
name: core-agents
description: 12 specialized trading agents - whale tracking, swarm coordination, RBI, funding arbitrage, liquidation hunting.
---

# core/agents - Trading Agents

**Location:** `/Volumes/LegacySafe/SS_III/core/agents/`

## What It Does

Specialized autonomous trading agents:

- **Whale Agent** - Track large wallet movements
- **Swarm Agent** - Multi-agent coordination
- **Trading Agent** - Core trading logic
- **RBI Agent** - Risk-based investing
- **Wealth Agents** - Portfolio management
- **Funding Agent** - Funding rate arbitrage
- **Liquidation Agent** - Liquidation hunting
- **Chart Analysis Agent** - Technical analysis

## Key Modules

```
whale_agent.py        - Whale tracking
swarm_agent.py        - Swarm coordination
trading_agent.py      - Core trading
rbi_agent.py          - Risk-based investing
wealth_agents.py      - Portfolio management
funding_agent.py      - Funding arb
liquidation_agent.py  - Liq hunting
chartanalysis_agent.py - TA
backtest_runner.py    - Backtesting
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/core/agents

# Run whale tracker
python whale_agent.py

# Execute swarm coordination
python swarm_agent.py

# Start trading agent
python trading_agent.py
```

## Status

- Files: 12 agent modules
- Purpose: Specialized trading strategies, whale tracking, arbitrage

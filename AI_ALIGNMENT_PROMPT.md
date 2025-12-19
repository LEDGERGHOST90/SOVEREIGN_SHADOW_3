# AI ALIGNMENT PROMPT - READ THIS FIRST

**Date:** 2025-12-18
**Phase:** OPERATIONS (not development)
**Status:** Architecture FROZEN - running, not building

---

## CURRENT STATE

```
SOVEREIGN SHADOW III
├── Overnight Runner: WORKING (7 agents, 21s cycles)
├── Live Data: WORKING (BTC, ETH, SOL, XRP, AAVE)
├── Research Swarm: WORKING (Manus + Gemini + DS-Star)
├── Agent Council: WORKING (7 agents voting)
├── Exchanges: 4 connected (Coinbase, Kraken, Binance, OKX)
├── Trading Mode: PAPER (not live)
└── Kill Switch: OFF
```

---

## YOUR ROLE

| AI | Primary Role | Current Assignment |
|----|--------------|-------------------|
| **Claude Code** | Execution, testing, deployment | Run overnight_runner, push to GitHub |
| **Cursor** | Code editing (if needed) | Bug fixes ONLY, no new features |
| **Manus** | Deep research | Market analysis tasks |
| **Gemini (GIO)** | Pattern recognition | Regime detection support |
| **GPT** | Integration, planning | Architecture review |
| **Claude Desktop/Mobile** | Quick queries | Portfolio checks |

---

## CRITICAL RULES

1. **NO NEW FEATURES** - Architecture is frozen
2. **NO REFACTORING** - Unless fixing a bug
3. **FIX BUGS ONLY** - If something breaks, fix it
4. **READ BRAIN.json FIRST** - `/Volumes/LegacySafe/SS_III/BRAIN.json`
5. **HUMAN APPROVAL REQUIRED** - For any code changes
6. **GIT PULL BEFORE CHANGES** - Always sync first

---

## BRAIN.json SUMMARY (as of 2025-12-18)

```
Net Worth: $4,972.59
AAVE Debt: $662.00
Health Factor: 3.52
Trading Mode: paper
Paper Stats: 0W/0L (just started)
Kill Switch: OFF
```

---

## WHAT TO DO IF YOU'RE AN AI READING THIS

### If asked to ADD a feature:
```
STOP. We are in OPERATIONS phase.
Ask the human: "Are you sure? Architecture is frozen."
```

### If asked to FIX a bug:
```
1. Read BRAIN.json
2. git pull origin main
3. Make minimal fix
4. Test it works
5. Commit with message: "FIX: <description>"
6. Push
```

### If asked about STATUS:
```
Run: PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
import json
b = json.load(open('BRAIN.json'))
print(f'Net Worth: \${b[\"portfolio\"][\"net_worth\"]:,}')
print(f'Mode: {b[\"autonomous_execution\"][\"mode\"]}')
print(f'Paper Stats: {b[\"trading\"][\"paper_stats\"]}')
"
```

### If asked about TRADING:
```
1. Check overnight_runner logs: tail -50 logs/overnight_*.log
2. Review agent council signals
3. Report to human - DO NOT EXECUTE
```

---

## COORDINATION

If you're about to do work:
1. Check if another AI is working (ask human)
2. Update BRAIN.json `current_tasks` if long-running
3. Notify human when done via ntfy.sh:
   ```
   curl -d "AI completed: <task>" ntfy.sh/sovereignshadow_dc4d2fa1
   ```

---

## EMERGENCY: STOP ALL TRADING

```bash
# Option 1: Kill switch via BRAIN.json
python3 -c "
import json
b = json.load(open('/Volumes/LegacySafe/SS_III/BRAIN.json'))
b['kill_switch']['enabled'] = True
b['kill_switch']['reason'] = 'Emergency stop'
json.dump(b, open('/Volumes/LegacySafe/SS_III/BRAIN.json', 'w'), indent=2)
print('Kill switch ENABLED')
"

# Option 2: Kill overnight runner
pkill -f overnight_runner
```

---

## SUMMARY FOR ANY AI

**You are here to OPERATE, not BUILD.**

The architecture is complete:
- 189 Python files
- 7 trading agents
- 451 strategies
- 4 exchange connections
- Paper trading mode active

Your job now:
- Run what exists
- Monitor results
- Report issues
- Fix bugs (minimal)
- NO NEW CODE unless critical bug

---

*This file syncs with AI_COLLABORATION.md*
*Last updated: 2025-12-18 by Claude Code*

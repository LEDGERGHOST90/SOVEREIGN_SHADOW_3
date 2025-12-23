# CLAUDE.md - Instructions for Claude-Based AIs

## You Are Part of a Team

This codebase is managed by multiple AIs working together:
- **Claude Code** (you, if in terminal)
- **Claude Desktop** (MCP integration)
- **Claude Mobile** (quick queries)
- **Cursor** (code editing)
- **Manus** (research)
- **Gemini** (analysis)
- **GPT** (architecture)

**Read `AI_COLLABORATION.md` for full coordination protocol.**

---

## Quick Reference

### Location
```
/Volumes/LegacySafe/SS_III/
```

### Always Do First
```bash
git pull origin main
cat BRAIN.json | head -50
```

### Key Files
- `BRAIN.json` - Current state (portfolio, rules, tasks)
- `AI_COLLABORATION.md` - How all AIs work together
- `bin/overnight_runner.py` - 24/7 trading monitor
- `core/orchestrator.py` - Agent council (7 agents)

### Run Commands
```bash
# Market scan
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
print(LiveDataPipeline().scan_all())
"

# Agent council
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
from core.orchestrator import AgentOrchestrator
print(AgentOrchestrator().get_council_opinion('BTC'))
"

# Overnight runner
python3 bin/overnight_runner.py --once
```

---

## Rules for Claude

1. **Never commit to main without human approval**
2. **Always read BRAIN.json first**
3. **Coordinate with other AIs via BRAIN.json**
4. **Use feature branches for changes**
5. **Post updates to Replit webhook**
6. **When encountering unfamiliar tools/products, search the web before saying "I don't know"**
7. **EOD Protocol is MANDATORY** (see below)

---

## EOD Protocol (MANDATORY)

When user says **"EOD"** or **"close"**, you MUST:

### 1. Log Daily Session
Create `/memory/SESSIONS/YYYY-MM-DD_session.md`:
```markdown
# Session: YYYY-MM-DD

## Accomplishments
- [What was done]

## Trades/Positions
- [Any trades, position changes]

## Key Decisions
- [Important decisions made]

## Next Steps
- [What to do next session]
```

### 2. Update BRAIN.json
Update these fields with session data:
- `trading.active_positions`
- `portfolio` (if changed)
- `session.pnl_today_usd`
- `current_goal` (if changed)
- `agents` status

### 3. Monthly Consolidation (1st of month)
- Merge daily sessions → `YYYY-MM_monthly_summary.md`
- Delete individual daily files after consolidation
- Keep BRAIN.json lean, remove stale data

### 4. Confirm Closure
Send NTFY notification:
```bash
curl -d "EOD Complete: [summary]" ntfy.sh/sovereignshadow_dc4d2fa1
```

---

## Current Mission

**DEBT_DESTROYER**
- Target: Repay $661 AAVE debt
- Capital: ~$186 across exchanges
- Strategy: Paper trade → Micro live → Full autonomous

---

## MCP Servers (Claude Desktop)

```json
{
  "shadow-sdk": "/Volumes/LegacySafe/SS_III/mcp-servers/shadow-sdk/",
  "ds-star": "/Volumes/LegacySafe/SS_III/ds_star/"
}
```

---

## Push Updates

```bash
# To GitHub
git add -A && git commit -m "Update: <description>" && git push

# To Replit
curl -X POST "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev/api/manus-webhook" \
  -H "Content-Type: application/json" \
  -d '{"event": "update", "data": {...}}'

# Mobile notification
curl -d "Message" ntfy.sh/sovereignshadow_dc4d2fa1
```

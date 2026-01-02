# CLAUDE.md - Instructions for Claude-Based AIs

## You Are Part of a Team

This codebase is managed by multiple AIs working together:
- **Claude Code** (you, if in terminal)
- **Claude Desktop** (MCP integration)
- **Claude Mobile** (quick queries)
- **Antigravity** (Google IDE)
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

---

## ⚠️ CRITICAL RULE: SEARCH BEFORE BUILD ⚠️

**This rule is MANDATORY. Violations waste the user's time and fragment the codebase.**

### Before Creating ANY New File or Function:

```bash
# 1. Search for existing implementation
grep -r "keyword" /Volumes/LegacySafe/SS_III --include="*.py" | head -20

# 2. Check existing modules
ls /Volumes/LegacySafe/SS_III/core/
ls /Volumes/LegacySafe/SS_III/.claude/skills/

# 3. Read related files before proposing changes
```

### The Rule:
1. **SEARCH FIRST** - Always grep/find before building
2. **INTEGRATE** - Add to existing modules, don't create standalone files
3. **CONNECT** - New code must import from and connect to existing SS_III systems
4. **ASK** - If unsure whether something exists, ASK the user
5. **NEVER** build a "new standalone" when the feature exists somewhere

### Why This Matters:
- SS_III has 150+ core modules, 15 skills, 75+ strategies
- Previous Claude sessions built duplicates without searching
- User has rebuilt the same features multiple times unknowingly
- The codebase became fragmented instead of unified

### Examples of WRONG Behavior:
❌ "Let me build a position monitor" → Creates `bin/position_monitor.py`
❌ "I'll create a new TP/SL system" → Ignores existing `core/trading/tactical_risk_gate.py`
❌ "Let me write a regime detector" → Doesn't know `core/regime/hmm_regime_detector.py` exists

### Examples of CORRECT Behavior:
✅ "Let me search for existing position monitoring..." → Finds `core/autonomous/MASTER_TRADING_LOOP.py`
✅ "I found TP/SL logic in 75 files. Which should I extend?" → Asks user
✅ "Adding CoinGlass to existing `core/integrations/live_data_pipeline.py`" → Integrates

### Before Every Session:
```bash
# Understand what exists
find /Volumes/LegacySafe/SS_III/core -name "*.py" | wc -l
ls /Volumes/LegacySafe/SS_III/.claude/skills/
```

**If you skip this step and build something that already exists, you are wasting the user's time and money.**

---

### Key Files
- `BRAIN.json` - Current state (portfolio, rules, tasks)
- `AI_COLLABORATION.md` - How all AIs work together
- `bin/overnight_runner.py` - 24/7 trading monitor
- `core/orchestrator.py` - Agent council (7 agents)

### Active Web Endpoints
```
Replit Dashboard: https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev/
AlphaRunner (GCP): https://shadow-ai-alpharunner-33906555678.us-west1.run.app/
DEPRECATED: sovereignnshadowii.abacusai.app, legacyloopshadowai.abacusai.app
```

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

## ACC Protocol (Auto-Compact Call) - MANDATORY

**When context reaches ~80% or you sense compaction is imminent, IMMEDIATELY run:**

```python
from core.session.auto_save import emergency_save

emergency_save(
    summary="Brief summary of session",
    accomplishments=["What was done", "Files created"],
    issues_found=["Problems discovered"],
    files_created=["path/to/new/file.py"],
    files_modified=["path/to/changed/file.py"],
    next_steps=["What to do next"],
    brain_updates={"key": "value"}  # Optional BRAIN.json updates
)
```

**Or via CLI:**
```bash
python3 core/session/auto_save.py "Summary of what we accomplished"
```

### What ACC Does:
1. Saves session to `memory/SESSIONS/{date}_{time}_ACC.md`
2. Updates BRAIN.json with session record
3. Pushes summary to Replit
4. Sends NTFY notification
5. Preserves work BEFORE compaction destroys it

### Signs Compaction is Coming:
- Long conversation with many file reads
- Multiple tool calls accumulating
- Complex multi-step tasks
- You've been working for 30+ minutes

### Rule: SAVE EARLY, SAVE OFTEN
If in doubt, run ACC. Better to have duplicate saves than lost work.

---

## Current Mission

**PORTFOLIO_GROWTH** (AAVE = Strategic Good Debt)
- AAVE debt (~$609) is KEPT as strategic leverage
- Health Factor: 3.96 (min threshold: 2.5)
- Focus: Grow exchange holdings, capture swing opportunities

**Portfolio (2026-01-01):**
- Net Worth: ~$5,438
- Ledger Cold Storage: ~$5,000
- Exchange Capital: ~$950 (Coinbase $764, Binance US $111, Kraken $73)

**AAVE Rules (HARDCODED):**
- DO NOT repay debt unless HF < 2.5
- Collateral: wstETH (~$2,979)
- Debt: ~$609 (LOCKED IN as good debt)

**Active AI Basket (Coinbase):**
- LINK: 16.21 @ $12.43 = $201
- FET: 916.1 @ $0.21 = $192
- RENDER: 123.8 @ $1.35 = $167
- SUI: 90.7 @ $1.44 = $131

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

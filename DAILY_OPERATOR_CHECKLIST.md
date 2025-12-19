# DAILY OPERATOR CHECKLIST

> **You are an OPERATOR, not a developer.**
> If something breaks, FIX it. Don't ADD features.

---

## MORNING (6-8 AM)

### System Health
- [ ] Check overnight_runner.py logs: `tail -100 /Volumes/LegacySafe/SS_III/logs/overnight_*.log`
- [ ] Any errors? Fix them. Don't refactor.
- [ ] ntfy.sh alerts overnight? Review on phone.

### Portfolio Check
- [ ] Open Replit dashboard (or run: `python3 core/orchestrator.py --status`)
- [ ] Verify balances match reality:
  - Coinbase: ~$553
  - Kraken: ~$2.65
  - Binance: ~$73
  - OKX: ~$107
  - AAVE: HF > 2.0

### BRAIN.json Sync
- [ ] `cat /Volumes/LegacySafe/SS_III/BRAIN.json | jq '.portfolio'`
- [ ] Does it match Replit? If not, sync.

---

## MIDDAY (12-2 PM)

### Research (Optional)
- [ ] ONE Manus task max (research only)
- [ ] Review yesterday's Manus results if pending
- [ ] Update BRAIN.json `notes` field with insights

### Market Pulse
- [ ] Check Replit live data (top movers)
- [ ] Any regime change? (ADX/ATR shift)
- [ ] Note in BRAIN.json if significant

---

## EVENING (6-8 PM)

### Agent Council
- [ ] Run orchestrator: `PYTHONPATH=/Volumes/LegacySafe/SS_III python3 core/orchestrator.py`
- [ ] Watch agent votes (should see 7 agents)
- [ ] Record consensus: BUY / SELL / HOLD

### Paper Trade Decision
- [ ] If consensus is actionable:
  - Asset: ________
  - Direction: ________
  - Entry: ________
  - Stop: 3%
  - Target: 5%
- [ ] Log in BRAIN.json under `trading.paper_trades`

### Result Logging
- [ ] Update paper trade if closed:
  - PnL: ________
  - Win/Loss: ________
  - Update `trading.paper_stats.wins` or `losses`

---

## EOD (10 PM)

### Codebase Check
```bash
cd /Volumes/LegacySafe/SS_III
git status
```
- [ ] **NO NEW FILES** (if there are, you broke the rule)
- [ ] **NO FEATURE COMMITS** (fixes only)

### Session Log
- [ ] Update `/Volumes/LegacySafe/SS_III/memory/SESSIONS/SESSION_YYYY-MM-DD.md`
- [ ] What happened today?
- [ ] Any paper trades?
- [ ] System health?

### Overnight Setup
- [ ] Verify overnight_runner.py will run
- [ ] Check cron or launchd if automated
- [ ] Or run manually: `nohup python3 bin/overnight_runner.py &`

### Sleep
- [ ] Close laptop
- [ ] Trust the system

---

## FORBIDDEN ACTIONS

```
✗ "Let me add a new feature"
✗ "I should refactor this module"
✗ "What if we also integrated..."
✗ "I found another tool/API"
✗ "Let me reorganize the folder structure"
✗ "This needs a new agent"
```

---

## ALLOWED ACTIONS

```
✓ Fix a bug that prevents operation
✓ Update BRAIN.json with real data
✓ Log paper trade results
✓ Review Manus research (don't implement)
✓ Run existing scripts
✓ Monitor dashboards
```

---

## WEEKLY REVIEW (Sundays)

- [ ] Total paper trades this week: ____
- [ ] Wins: ____ Losses: ____
- [ ] Win rate: ____%
- [ ] Overnight runner uptime: ____/7 nights
- [ ] Code changes made: ____ (should be 0-2 fixes max)

### Graduation Criteria
```
□ 7 days paper trading logged
□ Win rate > 50%
□ No critical bugs
□ Overnight runner stable 7 nights
□ Zero feature additions
□ BRAIN.json accurate
```

When all boxes checked → Move to TIER 3 (Micro Live: $25 max)

---

## QUICK COMMANDS

```bash
# Morning status
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
import json
with open('BRAIN.json') as f:
    b = json.load(f)
print(f'Net Worth: \${b[\"portfolio\"][\"net_worth\"]:,.2f}')
print(f'Paper Stats: {b[\"trading\"][\"paper_stats\"]}')
"

# Run orchestrator
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 core/orchestrator.py

# Check overnight logs
ls -la /Volumes/LegacySafe/SS_III/logs/

# Push to GitHub (EOD)
cd /Volumes/LegacySafe/SS_III && git add -A && git commit -m "EOD: $(date +%Y-%m-%d)" && git push
```

---

*Created: 2025-12-18*
*Phase: OPERATIONS (not development)*

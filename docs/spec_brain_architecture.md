# SOVEREIGN BRAIN - Architecture Specification

**Version:** 1.0
**Created:** 2025-11-26
**Purpose:** Central automation layer connecting all three tiers

---

## Overview

One Python script (`sovereign_brain.py`) that runs every 15 minutes and:
1. Executes automated tasks (Tier 1)
2. Detects opportunities and queues them (Tier 2)
3. Monitors conditions and logs alerts (Tier 3)

All state is stored in one JSON file (`brain_state.json`).

---

## File Structure

```
/Volumes/LegacySafe/SovereignShadow_II/
├── sovereign_brain.py      # The brain (NEW)
├── brain_state.json        # State file (NEW)
├── sovereign.sh            # Updated to read brain state
├── DAILY_AUTOPILOT.py      # Existing - called by brain
└── agents/
    └── shade_agent.py      # Existing - called by brain
```

---

## TIER 1: Fully Automated (No Human Needed)

These run automatically every cycle:

| Task | Frequency | What It Does |
|------|-----------|--------------|
| Fetch balances | Every 15 min | Coinbase, Binance US |
| Snapshot portfolio | Every 4 hours | Save to history |
| Generate daily report | Once/day at 7 AM | DAILY_AUTOPILOT.py |
| Reset loss streak | Once/day at midnight | New day = clean slate |
| Sync prices | Every 15 min | BTC, ETH, SOL, XRP |

**Output:** Updates `brain_state.json` with latest data

---

## TIER 2: Opportunity Detection (Human Approves)

Brain detects these conditions and queues for your approval:

| Condition | Trigger | Action Queued |
|-----------|---------|---------------|
| Asset +50% from cost | XRP > $3.48 | "TRIM: Sell 25% XRP" |
| Asset underweight >10% | BTC at 26% (target 40%) | "REBALANCE: Buy BTC" |
| Asset overweight >10% | ETH at 53% (target 30%) | "REBALANCE: Sell ETH" |
| Quarterly rebalance | Jan/Apr/Jul/Oct 1-7 | "REBALANCE: Full review" |
| SHADE setup valid | All criteria met | "TRADE: [details]" |

**Output:** Adds to `pending_actions` array in state file

**You approve by:**
```bash
python3 sovereign_brain.py --approve 1   # Approve action #1
python3 sovereign_brain.py --reject 1    # Reject action #1
python3 sovereign_brain.py --list        # See all pending
```

---

## TIER 3: Monitor & Alert (Passive Watching)

Brain watches these conditions and logs alerts:

| Condition | Threshold | Alert Level |
|-----------|-----------|-------------|
| AAVE health factor | < 2.5 | WARNING |
| AAVE health factor | < 2.0 | CRITICAL |
| AAVE health factor | < 1.5 | EMERGENCY |
| BTC price drop | > 10% in 24h | WARNING |
| ETH price drop | > 10% in 24h | WARNING |
| Portfolio drop | > 15% in 24h | WARNING |
| No check-in | > 48 hours | REMINDER |

**Output:** Adds to `alerts` array in state file

**Alert Levels:**
- `INFO` - FYI, no action needed
- `WARNING` - Pay attention
- `CRITICAL` - Action needed soon
- `EMERGENCY` - Act NOW

---

## State File Structure

```json
{
  "last_run": "2025-11-26T14:30:00",
  "last_human_checkin": "2025-11-26T08:00:00",

  "balances": {
    "coinbase": {"ETH": 0.000007, "USD": 33.03, "USDC": 58.90},
    "binance_us": {"USDC": 73.16, "PEPE": 372.32, "RENDER": 0.009434},
    "total_usd": 165.11
  },

  "prices": {
    "BTC": 87607.40,
    "ETH": 2950.56,
    "SOL": 137.77,
    "XRP": 2.19
  },

  "portfolio": {
    "total_value": 4900,
    "allocation": {
      "BTC": {"percent": 26, "target": 40, "status": "UNDER"},
      "ETH": {"percent": 53, "target": 30, "status": "OVER"},
      "SOL": {"percent": 0, "target": 20, "status": "UNDER"},
      "XRP": {"percent": 20, "target": 10, "status": "OVER"}
    }
  },

  "pending_actions": [
    {
      "id": 1,
      "created": "2025-11-26T14:30:00",
      "type": "TRIM",
      "asset": "XRP",
      "reason": "Up 50% from cost basis ($2.32 -> $3.48)",
      "suggested_action": "Sell 25% of XRP position",
      "status": "pending"
    }
  ],

  "alerts": [
    {
      "timestamp": "2025-11-26T14:30:00",
      "level": "WARNING",
      "message": "AAVE health factor at 2.3 - watch closely",
      "acknowledged": false
    }
  ],

  "history": {
    "snapshots": [
      {"date": "2025-11-26", "total": 4900},
      {"date": "2025-11-25", "total": 4850}
    ]
  },

  "psychology": {
    "losses_today": 0,
    "last_loss_date": null,
    "trading_allowed": true
  }
}
```

---

## Daily Workflow

**Morning (automatic):**
1. Brain ran overnight, generated report
2. You run `./sovereign.sh`
3. See: Report + Pending Actions + Alerts

**If pending actions exist:**
```bash
# Review what brain found
python3 sovereign_brain.py --list

# Output:
# PENDING ACTIONS:
# [1] TRIM: Sell 25% XRP (up 50% from cost)
# [2] REBALANCE: Buy BTC (26% vs 40% target)
#
# ALERTS:
# [!] WARNING: AAVE health at 2.3

# Approve or reject
python3 sovereign_brain.py --approve 1
python3 sovereign_brain.py --reject 2
```

**If no pending actions:**
```bash
./sovereign.sh
# Output: "No action required. Close terminal."
```

---

## Cron Schedule

```bash
# Run brain every 15 minutes
*/15 * * * * cd /Volumes/LegacySafe/SovereignShadow_II && python3 sovereign_brain.py --auto

# Generate daily report at 7 AM
0 7 * * * cd /Volumes/LegacySafe/SovereignShadow_II && python3 DAILY_AUTOPILOT.py
```

---

## Commands

| Command | What It Does |
|---------|--------------|
| `./sovereign.sh` | Daily check-in (shows everything) |
| `python3 sovereign_brain.py --auto` | Run automation cycle |
| `python3 sovereign_brain.py --list` | Show pending actions & alerts |
| `python3 sovereign_brain.py --approve N` | Approve action #N |
| `python3 sovereign_brain.py --reject N` | Reject action #N |
| `python3 sovereign_brain.py --status` | Quick status check |
| `python3 sovereign_brain.py --history` | Show portfolio history |

---

## Integration with Existing Tools

| Existing Tool | How Brain Uses It |
|---------------|-------------------|
| `DAILY_AUTOPILOT.py` | Brain triggers at 7 AM |
| `agents/shade_agent.py` | Brain calls for trade validation |
| `logs/psychology/loss_streak.json` | Brain reads/writes |
| `exchanges/coinbase_connector.py` | Brain fetches balances |
| `exchanges/binance_us_connector.py` | Brain fetches balances |

---

## What Brain Does NOT Do

- Execute trades automatically (always needs approval)
- Access AAVE directly (you check Ledger Live / debank)
- Send push notifications (future: add Telegram/Discord)
- Make decisions for you (only suggests)

---

## Future Enhancements (Not Now)

- [ ] Telegram bot for mobile alerts
- [ ] AAVE direct integration via web3
- [ ] Auto-execute approved trades
- [ ] Backtesting integration
- [ ] NotebookLM daily digest

---

## Questions Before Building

1. **AAVE monitoring:** Since we can't check directly, should brain just remind you to check manually when market drops >5%?

2. **Cost basis:** Where should I pull your entry prices from? SESSION_STATE files?

3. **Approval timeout:** If you don't approve/reject in 48 hours, should actions auto-expire?

Review this and let me know. Building now.

# SOVEREIGN SHADOW II - OPERATIONAL PLAYBOOK

**Owner:** Raymond (LedgerGhost90)
**Created:** 2025-11-26
**Purpose:** Use what you already built. Stop improvising.

---

## YOUR EXISTING TOOLS (Use These)

| Tool | Location | What It Does |
|------|----------|--------------|
| Daily Autopilot | `python3 DAILY_AUTOPILOT.py` | Pulls Coinbase/Kraken balances, shows prices |
| SHADE Agent | `python3 agents/shade_agent.py` | Validates trades, enforces risk rules |
| Psychology Tracker | `agents/psychology_tracker.py` | Tracks emotions, 3-strike rule |
| Trade Journal | `agents/trade_journal.py` | Logs all trades with analysis |
| Live Market Scan | `python3 LIVE_MARKET_SCAN.py` | Quick price check |
| Coinbase Connector | `exchanges/coinbase_connector.py` | Execute trades on Coinbase |
| Preflight Check | `core/rebalancing/preflight_check.py` | 21-point validation |

---

## DAILY ROUTINE (5 minutes)

### Morning (When you wake up)

```bash
cd /Volumes/LegacySafe/SovereignShadow_II

# Step 1: Check the autopilot report (already ran at 7AM)
cat daily_reports/LATEST.txt
```

**What to look for:**
- BTC/ETH/SOL/XRP prices
- Coinbase balance
- Any dramatic overnight moves (>5%)

**Decision:**
- Nothing unusual? → Done. Close terminal.
- Something moved big? → Go to "SCENARIO RESPONSES" below

---

## SCENARIO RESPONSES

### SCENARIO A: Market Down 10%+

**Step 1: Check AAVE health (DO THIS FIRST)**
```bash
# Open Ledger Live or check debank.com
# Look at health factor
```

| Health Factor | Action |
|---------------|--------|
| > 3.0 | Do nothing. You're safe. |
| 2.0 - 3.0 | Watch closely. Check every 4 hours. |
| 1.5 - 2.0 | Prepare $200 USDC to repay debt |
| < 1.5 | EMERGENCY: Repay debt NOW |

**Step 2: If health factor is fine**
```
CLOSE ALL APPS.
DO NOT TRADE.
Check back in 24-48 hours.
```

---

### SCENARIO B: Want to Make a Trade

**Step 1: Wait 24 hours**
- Write down the trade idea
- Sleep on it
- Still want to do it tomorrow? Continue.

**Step 2: Run SHADE validation**
```bash
cd /Volumes/LegacySafe/SovereignShadow_II
python3 agents/shade_agent.py
```

**Step 3: Fill out trade details**
```python
trade = {
    'symbol': 'BTC/USD',           # What asset
    'direction': 'LONG',            # LONG or SHORT
    'entry': 87000,                 # Entry price
    'stop': 85000,                  # Stop loss (REQUIRED)
    'target_1': 92000,              # Take profit
    '4h_trend': 'bullish',          # What's the 4h trend?
    '4h_rsi': 55,                   # 4h RSI value
    '4h_at_sr': True,               # At support/resistance?
    '15m_at_level': True,           # 15m at key level?
    '15m_candle_pattern': True,     # Confirmation candle?
    '15m_volume_spike': True,       # Volume confirmation?
    '15m_rsi': 45                   # 15m RSI
}
```

**Step 4: Check result**
- SHADE APPROVED? → Proceed to execution
- SHADE REJECTED? → NO TRADE. Walk away.

---

### SCENARIO C: XRP or Single Asset Moons (50%+)

**Rule:** If any single asset goes up 50%+ from your average cost:
1. TRIM 25% of position
2. Move proceeds to underweight asset (SOL)

**How to check:**
```bash
cat SESSION_STATE_2025-11-25.json | grep -A5 "xrp"
```

Your XRP avg cost: $2.32
Trim trigger: $3.48 (50% above cost)

---

### SCENARIO D: Quarterly Rebalance (Jan 1, Apr 1, Jul 1, Oct 1)

**Target Allocation:**
| Asset | Target | Current |
|-------|--------|---------|
| BTC | 40% | 26% |
| ETH | 30% | 53% |
| SOL | 20% | 0% |
| XRP | 10% | 20% |

**Rebalance Steps:**
1. Run preflight check
2. Calculate trades needed
3. Execute sells first (ETH, XRP)
4. Execute buys second (BTC, SOL)
5. Log in trade journal

```bash
# Check current allocation
cat SESSION_STATE_*.json | grep allocation
```

---

### SCENARIO E: AAVE Emergency (Health Factor < 1.5)

**STOP EVERYTHING. DO THIS:**

```bash
# Option 1: Repay debt from USDC in Coinbase
# Transfer USDC to Ledger → Repay on AAVE

# Option 2: Add collateral
# Move more ETH to AAVE as collateral
```

**How much to repay:**
- Current debt: ~$660
- To get health factor from 1.5 → 3.0: Repay ~$300
- To eliminate debt entirely: Repay $660

---

## WHAT NOT TO DO

| Situation | Wrong Response | Right Response |
|-----------|----------------|----------------|
| Market down 10% | Panic sell | Check health factor, then wait |
| Saw a "hot tip" | FOMO buy immediately | Wait 24h, run SHADE |
| Lost a trade | Revenge trade to recover | Log it, accept 1 strike, stop for day if 3 |
| Bored | Look for trades | Touch grass |
| Up 20% | "Let it ride" forever | Trim 10%, take some profit |

---

## PSYCHOLOGY RULES (Already Built)

**3-Strike Rule:**
- Loss 1: Risk reduced to 1.5%
- Loss 2: Risk reduced to 1%
- Loss 3: STOP TRADING FOR THE DAY

**Check your strike count:**
```bash
cat logs/psychology/loss_streak.json
```

**Log emotion before trading:**
```bash
python3 -c "
from agents.psychology_tracker import PsychologyTracker
pt = PsychologyTracker()
pt.log_emotion('confident', 5, 'pre_trade', 'Feeling good about setup')
"
```

---

## EMERGENCY CONTACTS (Your Tools)

| I need to... | Use this |
|--------------|----------|
| See current prices | `python3 LIVE_MARKET_SCAN.py` |
| Check daily report | `cat daily_reports/LATEST.txt` |
| Validate a trade idea | `python3 agents/shade_agent.py` |
| Check my psychology state | `cat logs/psychology/loss_streak.json` |
| See portfolio state | `cat SESSION_STATE_*.json` |
| Execute on Coinbase | Use `exchanges/coinbase_connector.py` |

---

## THE ONLY COMMANDS YOU NEED

```bash
# Morning check
cat /Volumes/LegacySafe/SovereignShadow_II/daily_reports/LATEST.txt

# Before any trade
cd /Volumes/LegacySafe/SovereignShadow_II && python3 agents/shade_agent.py

# Price check
cd /Volumes/LegacySafe/SovereignShadow_II && python3 LIVE_MARKET_SCAN.py

# Psychology check
cat /Volumes/LegacySafe/SovereignShadow_II/logs/psychology/loss_streak.json
```

---

## SUMMARY: DECISION TREE

```
Wake up
    │
    ▼
Check daily_reports/LATEST.txt
    │
    ├── Nothing unusual? → Done for the day
    │
    ├── Market crashed? → Check AAVE health
    │   │
    │   ├── Health > 2.0 → Do nothing, wait 48h
    │   └── Health < 2.0 → Repay debt
    │
    └── Want to trade?
        │
        ▼
    Wait 24 hours
        │
        ▼
    Run SHADE validation
        │
        ├── Rejected → No trade
        └── Approved → Execute, log in journal
```

---

## TAPE THIS TO YOUR MONITOR

```
Before ANY action, ask:

1. Did I check AAVE health? □
2. Did I wait 24 hours? □
3. Did SHADE approve it? □

All three = YES → Trade
Any = NO → Stop
```

---

*This playbook uses YOUR tools. Not new ones. Use it.*

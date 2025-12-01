# DECEMBER 2025 BATTLE PLAN
## Autonomous Trading Operations

---

## CURRENT INFRASTRUCTURE

### Active Automation (launchd)
| Service | Interval | Function | Status |
|---------|----------|----------|--------|
| market-scanner | 15 min | BTC/ETH/SOL/XRP price tracking | ACTIVE |
| state-updater | ? | System state updates | ACTIVE |
| daily-report | Daily | Council briefings | ACTIVE |

### Available Tools
| Tool | Purpose | Cost |
|------|---------|------|
| meme_machine | Solana meme scanner | FREE (DexScreener) |
| Strategy Scout | Strategy builder from audio/video | AbacusAI hosted |
| Breakout Analyzer | Score tokens 0-100 | FREE |
| Smart Money Tracker | Track winning wallets | FREE |

---

## DECEMBER MISSION

**Objective:** Generate trading income through automated meme scanning + strategy execution

**Capital Allocation:**
- Starting Cash: $2,188
- December Expenses: $515
- AAVE Debt: $661 (manual repay when ready)
- Remaining for Deployment: $1,012

---

## AUTOMATION SCHEDULE

### TIER 1: ALWAYS RUNNING (Background)
```
[ACTIVE] Market Scanner - every 15 min
  - Tracks Core 4 prices (BTC, ETH, SOL, XRP)
  - Logs to: logs/market_scanner/
  - Alerts on price drops
```

### TIER 2: MEME MACHINE SCANS (To Be Scheduled)

#### Morning Scan (8:00 AM PST)
```bash
# Find overnight movers
python -m meme_machine --breakout --min-score 70
python -m meme_machine --smart-buys
python -m meme_machine --graduating
```

#### Midday Scan (12:00 PM PST)
```bash
# Catch momentum plays
python -m meme_machine --kings
python -m meme_machine --trending
```

#### Evening Scan (6:00 PM PST)
```bash
# Asian market prep
python -m meme_machine --pumpfun
python -m meme_machine --whales
```

### TIER 3: STRATEGY SCOUT (Manual/On-Demand)
```
URL: https://sovereignnshadowii.abacusai.app

WORKFLOW:
1. Drop audio/video of trading strategy
2. Extract strategy JSON
3. Apply Sovereign Protocol filter (Sniper/Vault/Ladder/MENACE)
4. Export to meme_machine watchlist
```

---

## DECISION FRAMEWORK

### When meme_machine finds a candidate:

```
STEP 1: Initial Scan
  └── --breakout returns token with score > 70

STEP 2: Deep Analysis
  └── python -m meme_machine --score <address>
  └── python -m meme_machine --holders <address>

STEP 3: Smart Money Check
  └── python -m meme_machine --wallet <top_holder>
  └── Look for: win rate > 60%, classification = SMART_MONEY

STEP 4: Final Decision
  └── python -m meme_machine --snipe <address>
  └── Returns: YES/NO with reasoning

STEP 5: Execute (if YES)
  └── Use Phantom wallet
  └── Position size: MAX $50 per trade
  └── Set stop loss: -20%
  └── Take profit: +50% (scale out)
```

---

## ALERT THRESHOLDS

### Price Alerts (Core 4)
| Asset | Buy Signal | Sell Signal |
|-------|------------|-------------|
| BTC | < $90,000 | > $105,000 |
| ETH | < $3,000 | > $4,000 |
| SOL | < $140 | > $200 |
| XRP | < $2.00 | > $3.00 |

### Meme Token Alerts
| Metric | Threshold | Action |
|--------|-----------|--------|
| Breakout Score | > 70 | ANALYZE |
| Breakout Score | > 85 | PRIORITY |
| Smart Money % | > 20% | BULLISH |
| Top 5 Concentration | > 50% | AVOID |
| Liquidity | < $10k | SKIP |

---

## DAILY ROUTINE

### Morning (8:00 AM)
- [ ] Check overnight alerts in logs/market_scanner/
- [ ] Run meme_machine --breakout
- [ ] Review any score > 70 tokens
- [ ] Check Strategy Scout for new strategies

### Midday (12:00 PM)
- [ ] Run --kings and --trending
- [ ] Monitor any open positions
- [ ] Update BRAIN.json if trades executed

### Evening (6:00 PM)
- [ ] Run --pumpfun for new launches
- [ ] Run --whales for whale activity
- [ ] Set overnight alerts

### Weekly (Sunday)
- [ ] Review trade journal
- [ ] Calculate weekly P&L
- [ ] Adjust thresholds if needed
- [ ] Update smart money database

---

## EXECUTION PROTOCOL

### ~~CONSERVATIVE MODE~~ (Original)
> Superseded by DECEMBER AGGRESSIVE mode below

### DECEMBER AGGRESSIVE MODE (Active)
*Goal: $500 → $1000-1500 by Dec 31*
*Config: /config/swarm_config.json*

### Entry Rules
1. Only enter tokens with breakout score > 70
2. Smart money presence required (> 3 tracked wallets)
3. Liquidity minimum: $10,000
4. Market cap maximum: $1,000,000 (early stage)
5. **Max position size: $100** (was $50)

### Exit Rules
1. **Stop loss: -15%** (tighter than before)
2. **First take profit: +30%** (sell 50% of position)
3. **Second take profit: +75%** (sell remaining)
4. Time stop: Exit after 24h if no movement
5. Trailing stop: Activates at +20%, trails by 10%

### Risk Management
- **Max daily loss: $150** (was $100)
- **Max weekly loss: $300** (was $200)
- **Max concurrent positions: 5** (was 3)
- **Daily trade limit: 10 trades** (was 5)
- Cooldown after loss: 30 minutes

---

## LAUNCHD SETUP ✅ COMPLETE

### Active Automation:
| Agent | Schedule | Status |
|-------|----------|--------|
| market-scanner | Every 15 min | ACTIVE |
| state-updater | Background | ACTIVE |
| dailyreport | Daily | ACTIVE |
| **meme-scanner** | 8AM/12PM/6PM | **ACTIVE** |

### Meme Scanner Files:
```
Plist: ~/Library/LaunchAgents/com.sovereignshadow.meme-scanner.plist
Script: bin/meme_scanner_scheduled.sh
Logs: logs/meme_machine/LATEST_SCAN.log
```

### Trading Swarm:
```bash
# Manual swarm scan
python bin/trading_swarm.py --scan

# Check swarm status
python bin/trading_swarm.py --status

# Config: config/swarm_config.json
```

---

## DECEMBER TARGETS

| Week | Target | Strategy |
|------|--------|----------|
| Week 1 (Dec 1-7) | Setup + paper trade | Test automation, no real money |
| Week 2 (Dec 8-14) | Small live trades | Max $25/trade, prove system |
| Week 3 (Dec 15-21) | Scale if profitable | Increase to $50/trade |
| Week 4 (Dec 22-31) | Maintain + review | Holiday volatility, stay cautious |

### Success Metrics
- Win rate target: > 50%
- Monthly P&L target: +$200
- Max drawdown: -$200
- Trades per week: 5-10

---

## NEXT STEPS

1. [x] Create meme_scanner_scheduled.sh script
2. [x] Create launchd plist for scheduled scans
3. [x] Create trading swarm orchestrator
4. [x] Update risk rules to DECEMBER AGGRESSIVE mode
5. [ ] Set up Phantom wallet for meme trades
6. [ ] Fund Phantom with initial $100 SOL
7. [ ] Deploy $500 USDC on Coinbase (TURBO/SOL)
8. [ ] Run first swarm scan: `python bin/trading_swarm.py --scan`
9. [ ] Paper trade first 5 signals
10. [ ] Go live Dec 1 if paper trades profitable

---

*Last Updated: 2025-11-28*
*System: LegacyLoop // MemeMachine // StrategyScount*

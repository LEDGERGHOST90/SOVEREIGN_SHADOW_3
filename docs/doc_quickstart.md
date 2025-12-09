# SOVEREIGN SHADOW II - START HERE

**Owner:** Raymond (LedgerGhost90)  
**Last Updated:** 2025-11-24  
**Status:** OPERATIONAL (Manual Trading + Daily Autopilot)

---

## WHAT ACTUALLY WORKS RIGHT NOW

### 1. Daily Autopilot (AUTOMATED)
- **Runs:** Every day at 7:00 AM automatically
- **Output:** `/Volumes/legacysafe/sovereignshadow_II/daily_reports/LATEST.txt`
- **What it does:** Pulls real balances from Coinbase + Kraken, shows prices
- **To run manually:** `python3 DAILY_AUTOPILOT.py`

### 2. Live Market Scan (MANUAL)
- **File:** `LIVE_MARKET_SCAN.py`
- **What it does:** Shows current prices and momentum signals
- **To run:** `python3 LIVE_MARKET_SCAN.py`

### 3. Emergency Position Check (MANUAL)
- **File:** `emergency_check_positions.py`
- **What it does:** Quick view of exchange positions

---

## PORTFOLIO LOCATIONS

| Location | What's There | Approximate Value |
|----------|--------------|-------------------|
| Ledger (Cold) | Staked ETH via AAVE | ~$2,800 |
| Ledger (Cold) | BTC | ~$1,400 |
| Ledger (Cold) | XRP | ~$1,000 |
| Coinbase | USDC + small amounts | ~$100 |
| Kraken | Dust amounts | <$10 |

**AAVE Position:**
- Health Factor: ~4.0 (SAFE)
- Debt: ~$659
- Collateral: ~$3,330

---

## WHAT TO DO DAILY

1. Check `daily_reports/LATEST.txt` (auto-generated)
2. If AAVE health < 2.0 → Add collateral or repay debt
3. Otherwise → Do nothing unless you have a specific trade idea

---

## WHAT NOT TO DO

- Don't build more infrastructure
- Don't switch tools (no Manus, no new frameworks)
- Don't try to automate everything at once
- Don't trade without a specific reason

---

## API KEYS CONFIGURED

- ✅ Coinbase (working)
- ✅ Kraken (working)
- ⚠️ OKX (configured, not tested)
- ⚠️ Binance US (configured, not tested)

---

## IF AI LOSES CONTEXT

Tell it to read this file first:
```
cat /Volumes/legacysafe/sovereignshadow_II/README_START_HERE.md
```

This is the single source of truth.

---

## FILES THAT MATTER

| File | Purpose |
|------|---------|
| `DAILY_AUTOPILOT.py` | Auto-runs daily, saves reports |
| `LIVE_MARKET_SCAN.py` | Manual market check |
| `.env` | All API keys |
| `daily_reports/LATEST.txt` | Most recent auto-report |
| `PERSISTENT_STATE.json` | Portfolio state |
| `MY_HOLDINGS_REPORT.md` | Detailed holdings breakdown |

Everything else is legacy/experimental. Ignore it.

---

*This file is the truth. Everything else is noise.*

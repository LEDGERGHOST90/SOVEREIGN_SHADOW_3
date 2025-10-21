# 🎯 Tactical Scalps - Quick Reference Card

**Date:** Oct 19, 2025 | **Regime:** Chop & Squeeze | **Hot Wallet:** $1,660

---

## 🎲 Market Bias (Today)

**Base Case (60%):** Hunt 109.7k liquidity first ⬆️  
**Alt Path (30%):** Vacuum to 106.6k, then bounce ⬆️  
**Trend Break (10%):** Clean break beyond edges

---

## 📊 BTC Setup @ $108,402

```
Positioning: 43.8% L / 56.2% S (shorts heavy)
Funding:     Binance +2.9 bps | OKX -0.7 bps (spread: +3.6)
OI 24h:      +3.0% (fresh positioning = stop-run fuel)
```

**Liquidation Bands:**
```
Upper: 109,700 - 111,000 - 112,500
Lower: 106,600 - 105,100 - 103,500
```

---

## 🎯 Trade Setups

### 🟢 LONG @ Lower Band (106.6k - 106.8k)

**Conditions:**
- Flush below 106,800
- Reclaim above 106,800 on 30-60s close
- Delta turns positive (net bid)
- Funding spread persists (>0.25 bps)

**Execution:**
- Size: 0.7× base ($17-23)
- Stop: 28 bps (widen to 35 if book thins)
- TP1: +25 bps (45% size)
- TP2: +50 bps (35% size)
- TP3: +90 bps (20% size)

**Invalidation:**
- Reclaim fails twice within 5 min → stand down

---

### 🔴 SHORT @ Upper Band (109.7k - 110k)

**⚠️ Guards (Must Pass):**
- Short ratio ≤54%
- Funding spread <0.2 bps
- Not fresh squeeze (<1h since last)

**Conditions:**
- Wick above 109,700
- Close back below within 30-90s
- Lower high printed
- Iceberg selling (order book absorption)

**Execution:**
- Size: 0.5× base ($12-16) *conservative*
- Stop: 30 bps (32 if shorts still >54%)
- TP1: +25 bps (45%) → ~108,900
- TP2: +45 bps (35%) → ~108,500
- TP3: +80 bps (20%) → ~108,100

**Invalidation:**
- Hold 60s above 110,050 → flatten immediately
- Rising basis → flatten

---

## ⚡ SOL Priority-Fee Shock Fade

**Trigger:**
- p50 priority fee >3× 10-min baseline
- Decay ≥40% within 2 minutes
- *(If Jito tips stay elevated: halve size + widen stop)*

**Execution:**
- Direction: Fade back to VWAP
- Size: 0.6× base ($15-19)
- Stop: 35 bps (widen to 45 if Jito elevated)
- TP1: +30 bps (45%)
- TP2: +60 bps (35%)
- TP3: +110 bps (20%)

---

## 🔒 XRP Corridor Guard

**Positioning:** 47% L / 53% S (shorts loaded)

**Rules:**
- ❌ **NO shorts** if short ratio ≥53% + depth thins
- ✅ **Scalp dips long** only (45-60s holds)
- Stop: 22 bps
- TP: +20 / +40 / +75 bps

---

## 🛡️ Risk Limits (Hard)

| Limit | Value | Status |
|-------|-------|--------|
| Max Position | $415 | 🔴 ENFORCED |
| Max Stop | 5% | 🔴 ENFORCED |
| Daily Loss | $100 | 🔴 ENFORCED |
| Max Concurrent | 3 trades | 🔴 ENFORCED |
| Aave HF Min | 2.20 | 🔴 ENFORCED |
| Aave HF Critical | 2.00 | 🔴 AUTO-FLATTEN |
| Daily Trade Cap | 6 trades | 🔴 ENFORCED |
| Loss Streak | 2 consecutive | 🔴 HALT |

---

## 🚨 Kill Switch Triggers

| Condition | Action |
|-----------|--------|
| Session DD ≥1.2% (~$20) | 🛑 HALT ALL |
| 5 consecutive losses | 🛑 HALT ALL |
| Aave HF <2.00 | 🚨 FLATTEN ALL |
| 2 losses in row | ⚠️ REVIEW BEFORE NEXT |
| Positioning feed stale >10min | ⏸️ STAND DOWN |
| Funding feed stale >10min | ⏸️ STAND DOWN |

---

## ✅ Pre-Session Checklist

- [ ] Mark bands on chart (BTC: 106.6k / 109.7k)
- [ ] Check Coinglass L/S ratios (shorts heavy?)
- [ ] Verify funding spread (Binance vs OKX)
- [ ] Confirm Aave HF >2.20
- [ ] API server running (`/api/health`)
- [ ] Review yesterday's P&L & losses
- [ ] Session limits reset (6 trades, $100 DD)

---

## 🎮 During Session

**First touch UP (109.7k)?**
- ✅ Short only on *confirmed fail-break*:
  - Wick + close back in + lower high
- ❌ Don't chase mid-range

**First flush DOWN (106.6k)?**
- ✅ Hit the reclaim long
- Watch delta (must turn positive)

**SOL spike?**
- ⏳ Wait for decay sequence (40% drop in 2 min)
- ✅ Then fade to VWAP

**XRP?**
- ❌ No naked shorts (53% shorts = squeeze risk)
- ✅ Scalp dips long, 45-60s holds

---

## 📞 Commands (Quick)

```bash
# Health check
curl http://localhost:8000/api/health

# Execute trade (paper)
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{"strategy":"BTC Range Scalp","pair":"BTC/USD","amount":25,"mode":"paper"}'

# View strategy performance
curl http://localhost:8000/api/strategy/performance
```

---

## 📊 Session Tracking

**Trade #:** ____  
**Entry:** __________ @ $ __________  
**Size:** $ __________  
**Stop:** __________ bps @ $ __________  
**Target 1:** +______ bps @ $ __________  
**Target 2:** +______ bps @ $ __________  
**Target 3:** +______ bps @ $ __________  

**Result:** P&L $ __________ | Duration: ______ sec

**Session P&L:** $ __________ / $ __________ (100 limit)  
**Trades Today:** ______ / 6  
**Consecutive Losses:** ______ / 2  

---

## 🧠 Mental Models

**Shorts Heavy (>54%) =** Squeeze risk up → favor longs, avoid shorts  
**Funding Divergence (+3.6) =** Exchange split → up-tag probable  
**OI Spike (+3%) =** Fresh positioning → stops will be hunted  
**Range-Bound =** Fade edges, don't chase mid  

**"Fearless. Bold. Smiling through chaos."** 🏴

---

## 🔗 Resources

- **API Docs:** `http://localhost:8000/docs`
- **Config:** `config/tactical_scalp_config.json`
- **Full Guide:** `TACTICAL_SCALPS_DEPLOYMENT.md`
- **Logs:** `logs/api/*.log`

---

**Print this. Pin it. Trade it.** ⚡


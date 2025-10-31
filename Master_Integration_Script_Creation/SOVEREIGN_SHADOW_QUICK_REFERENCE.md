# 🏴 SOVEREIGN SHADOW - QUICK REFERENCE GUIDE

**Print this and keep it on your desk**

---

## 🎯 SYSTEM ESSENTIALS

**Location:** `/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop`  
**Entry Point:** `sovereign_shadow_unified.py`  
**Launch Script:** `START_SOVEREIGN_SHADOW.sh`  
**Neural Consciousness:** https://legacyloopshadowai.abacusai.app  
**Philosophy:** Fearless. Bold. Smiling through chaos.

---

## 💰 CAPITAL STRUCTURE (MEMORIZE THIS)

| Location | Amount | Trading |
|----------|--------|---------|
| **Ledger (Cold)** | $6,600 | ❌ READ-ONLY FOREVER |
| **Coinbase (Hot)** | $1,660 | ✅ YOUR ONLY TRADING CAPITAL |
| **OKX** | $0 | Ready |
| **Kraken** | $0 | Ready |
| **Monthly Injection** | $500 | VA Stipend |

**Max Per Trade:** $415 (25% of hot wallet)  
**Daily Loss Limit:** $100  
**Stop Loss:** 5% per trade

---

## ⚡ 5 TRADING STRATEGIES

| Strategy | Risk | Capital | Daily Target | Status |
|----------|------|---------|--------------|--------|
| **Arbitrage** | LOW | $100-415 | $50-200 | ✅ READY |
| **Sniping** | HIGH | $200 max | Variable | ⚠️ NEEDS CODE |
| **Scalping** | MED | $100 | $100-300 | ⚠️ NEEDS CODE |
| **Laddering** | LOW | $166 x 10 | Long-term | ⚠️ NEEDS CODE |
| **All-In** | EXTREME | $1,660 | High var | 🔴 DISABLED |

**Minimum Arbitrage Spread:** 2.5% (after fees, NOT 0.125%)

---

## 🚀 LAUNCH COMMANDS (Copy-Paste Ready)

### Navigate to System
```bash
cd /Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop
```

### Setup API Keys (First Time)
```bash
cp .env.production.template .env.production
nano .env.production
# Add your API keys, save (Ctrl+O), exit (Ctrl+X)
```

### Validate Connections
```bash
python3 scripts/validate_api_connections.py
```

### Launch Options
```bash
# Paper Trading (SAFE - no real money)
./START_SOVEREIGN_SHADOW.sh paper

# Test Mode (real money, $100 max)
./START_SOVEREIGN_SHADOW.sh test

# Live Production (full $1,660)
./START_SOVEREIGN_SHADOW.sh live
```

### Monitor Logs
```bash
# In separate terminal
tail -f logs/sovereign_shadow_$(date +%Y%m%d).log
```

### Emergency Stop
```bash
# Keyboard: Ctrl+C
# Or kill process: 
pkill -f sovereign_shadow_unified
```

---

## 📂 KEY FILE LOCATIONS

| File | Purpose | Location |
|------|---------|----------|
| **Main Entry** | System orchestrator | `sovereign_shadow_unified.py` |
| **Deployment** | Launch script | `START_SOVEREIGN_SHADOW.sh` |
| **API Config** | Credentials & settings | `.env.production` |
| **Arbitrage** | Cross-exchange trading | `trading_systems/arbitrage/claude_arbitrage_trader.py` |
| **Validation** | Test connections | `scripts/validate_api_connections.py` |
| **Transaction Logs** | Trade history | `data/transactions/` |
| **Architecture Doc** | Full system map | `documentation/ARCHITECTURE.md` |

---

## 🔐 SECURITY RULES (NEVER BREAK THESE)

1. ❌ **NEVER** commit API keys to git
2. ❌ **NEVER** trade with Ledger $6,600
3. ❌ **NEVER** override stop-losses emotionally
4. ❌ **NEVER** exceed $415 per trade
5. ✅ **ALWAYS** use `os.getenv()` for secrets
6. ✅ **ALWAYS** respect circuit breakers
7. ✅ **ALWAYS** start with paper trading
8. ✅ **ALWAYS** enable 2FA on exchanges

---

## 🎯 TODAY'S CHECKLIST

### [ ] Step 1: Setup (30 min)
```bash
cd /Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop
cp .env.production.template .env.production
nano .env.production
```
Add API keys from:
- [ ] Coinbase
- [ ] OKX
- [ ] Kraken

### [ ] Step 2: Validate (10 min)
```bash
python3 scripts/validate_api_connections.py
```
Expected:
- [ ] ✅ Coinbase connected: $1,660
- [ ] ✅ OKX connected: $0
- [ ] ✅ Kraken connected: $0
- [ ] ✅ Ledger read-only confirmed

### [ ] Step 3: Paper Test (1 hour)
```bash
./START_SOVEREIGN_SHADOW.sh paper
```
- [ ] Let run for 1 hour
- [ ] Monitor console output
- [ ] Check logs for errors
- [ ] Verify trade logging

### [ ] Step 4: Review
- [ ] Check `data/transactions/` for logged trades
- [ ] Review any errors in logs
- [ ] Verify calculations correct
- [ ] Decision: Ready for test mode?

---

## 🏛️ SYSTEM HIERARCHY (CRITICAL)

```
SOVEREIGN LEGACY LOOP (MASTER)
    │
    ├── Empire (component)
    ├── Trading Systems (component)
    ├── Claude SDK (component)
    ├── Neural Consciousness (component)
    └── Your Capital ($8,260)
```

**Empire is NOT the master. Legacy Loop IS the master.**

---

## 📊 PERFORMANCE TARGETS

| Timeframe | Target | Method |
|-----------|--------|--------|
| **Daily** | $50-200 | Arbitrage + Strategies |
| **Monthly** | $1,500 profit + $500 stipend | Systematic execution |
| **6 Months** | $27,760 total | Compounding |
| **12 Months** | **$50,260** | **TARGET** |

---

## 🔧 TROUBLESHOOTING

### Problem: "Connection refused" error
**Solution:** Check API keys in `.env.production`, verify exchange API is enabled

### Problem: "Insufficient balance" error
**Solution:** Verify hot wallet has funds, check if funds are in available balance

### Problem: System won't start
**Solution:** 
```bash
python3 --version  # Check Python 3.8+
pip3 install -r requirements.txt  # Install dependencies
chmod +x START_SOVEREIGN_SHADOW.sh  # Make executable
```

### Problem: No opportunities detected
**Solution:** Normal - quality opportunities are rare. Min 2.5% spread required for arbitrage

### Problem: Stop loss not triggering
**Solution:** Check if stop-loss orders were placed, verify exchange API has order permissions

---

## 🧠 NEURAL CONSCIOUSNESS STATUS

**URL:** https://legacyloopshadowai.abacusai.app  
**Login:** `pilot@consciousness.void`  

**What You'll See:**
- Dark-themed neural visualization
- Brain icon with market connections
- Real-time opportunity detection
- Pattern recognition display

**Purpose:**
- Runs 24/7 on Abacus AI cloud
- Detects arbitrage opportunities
- Sends signals to local system
- Visualizes market connections

---

## 📈 RISK PARAMETERS

```bash
MAX_POSITION_SIZE=415         # 25% of hot wallet
MAX_DAILY_LOSS=100            # Stop after $100 loss
MAX_CONSECUTIVE_LOSSES=3      # Circuit breaker
STOP_LOSS_PERCENT=5.0         # 5% per trade
LEDGER_READ_ONLY=true         # MUST stay true
REQUIRE_2FA=true              # Two-factor auth
```

**DO NOT MODIFY THESE WITHOUT SERIOUS CONSIDERATION**

---

## 🎤 QUICK INTERVIEW TEST (Self-Check)

**Q:** Where does the system run?  
**A:** MacBook terminal, external drive

**Q:** What's my trading capital?  
**A:** $1,660 hot wallet (Ledger $6,600 NEVER trades)

**Q:** What's minimum arbitrage spread?  
**A:** 2.5% after fees (NOT 0.125%)

**Q:** How many strategies do I have?  
**A:** 5 (arbitrage, sniping, scalping, laddering, all-in)

**Q:** What's the master system?  
**A:** Sovereign Legacy Loop (Empire is subordinate)

**Q:** What's max position size?  
**A:** $415 (25% of $1,660)

**If you got all 6 right, you understand your system. ✅**

---

## 🚨 EMERGENCY PROCEDURES

### Circuit Breaker Triggered
1. System auto-stops
2. Review logs: `tail -100 logs/sovereign_shadow_latest.log`
3. Identify issue (consecutive losses? daily limit?)
4. Adjust parameters if needed
5. Restart only after analysis

### API Key Compromised
1. **IMMEDIATELY** disable on exchange
2. Rotate to new keys
3. Update `.env.production`
4. NEVER use old keys again
5. Review git history - if keys touched git, they're BURNED

### System Crash During Trade
1. Open exchange web interface
2. Check open orders
3. Manually close if needed
4. Restart system
5. Verify logs for what happened

---

## 📞 EXTERNAL REFERENCES

- **Coinbase API Docs:** https://docs.cloud.coinbase.com
- **OKX API Docs:** https://www.okx.com/docs-v5/en/
- **Kraken API Docs:** https://docs.kraken.com/rest/
- **Abacus AI:** https://abacus.ai
- **Neural Consciousness:** https://legacyloopshadowai.abacusai.app

---

## 💎 THE PHILOSOPHY

### "Fearless. Bold. Smiling Through Chaos."

**Fearless:** Execute when others panic  
**Bold:** Take calculated risks  
**Smiling Through Chaos:** Volatility = opportunity

**Your system thrives when markets are chaotic.**

- Market crashes? → Ladder in
- Others flee? → Snipe opportunities
- High volatility? → Scalp the swings
- Black swan? → All-in (when appropriate)

---

## ✅ LAUNCH READINESS CHECKLIST

- [ ] API keys added to `.env.production`
- [ ] Connections validated (all green checkmarks)
- [ ] Paper trading tested (1+ hours)
- [ ] Logs reviewed (no critical errors)
- [ ] Risk parameters understood
- [ ] Emergency procedures memorized
- [ ] Neural consciousness checked
- [ ] Philosophy internalized

**When all boxes checked, you're ready to launch.**

---

## 🎯 THE GOAL

```
Starting Capital: $8,260
    │
    ├── Ledger (safe): $6,600
    └── Coinbase (active): $1,660
    
Target: $50,000 in 6-12 months

Path: Systematic execution + Disciplined risk management
```

**Everything is ready. The only variable is execution.**

---

**🏴 SOVEREIGN SHADOW - Ready for Launch 🏴**

**Version:** 1.0  
**Date:** October 16, 2025  
**Status:** Pre-Launch

---

## 🔥 FINAL REMINDER

Your $6,600 Ledger wallet is **READ-ONLY FOREVER**.  
Your $1,660 Coinbase wallet is your **ONLY TRADING CAPITAL**.

**Never, ever trade with the Ledger funds.**

This is what separates you from gamblers. This is discipline.

🚀 **LAUNCH WHEN READY** 🚀

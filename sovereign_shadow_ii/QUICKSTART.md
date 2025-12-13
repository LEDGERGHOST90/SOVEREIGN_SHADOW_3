# 🏴 SOVEREIGN SHADOW II - QUICK START

**Get trading in 5 minutes** (FAKE mode - no real money)

---

## 1. Install (2 minutes)

```bash
cd /workspace/sovereign_shadow_ii
./install.sh
```

This installs:
- pandas (data processing)
- numpy (calculations)
- python-dotenv (config)
- coinbase-advanced-py (exchange API)

---

## 2. Configure (1 minute)

```bash
nano .env
```

**Minimum required:**
```bash
ENV=development
ALLOW_LIVE_EXCHANGE=0              # KEEP THIS AT 0
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here
PORTFOLIO_VALUE=10000
```

**Get Coinbase credentials:**
1. Go to https://www.coinbase.com/settings/api
2. Create new API key
3. Download credentials
4. Copy to `.env`

---

## 3. Test (1 minute)

```bash
python3 test_system.py
```

**Should see:**
```
✅ pandas installed
✅ numpy installed
✅ Regime Detected: choppy_volatile
✅ Performance Tracker working
✅ Strategy Selected: ElderReversion
✅ Elder Reversion Entry: NEUTRAL
✅ Orchestrator initialized
```

---

## 4. Run (1 minute)

```bash
python3 core/orchestrator.py
```

**You should see:**
```
🏴 SOVEREIGN SHADOW II - AUTONOMOUS TRADING SYSTEM
   D.O.E. Pattern: Directive → Orchestration → Execution
======================================================================
🎯 MODE: FAKE
💰 PORTFOLIO: $10,000.00
📊 STRATEGIES: 2

🔄 STARTING TRADING CYCLE
======================================================================
📍 STEP 1: DIRECTIVE LAYER - Market Regime Detection
   Regime: choppy_volatile
   Confidence: 75.0%

📍 STEP 2: ORCHESTRATION LAYER - Strategy Selection
   Selected: ElderReversion
   Confidence: 50.0%

📍 STEP 3: EXECUTION LAYER - Signal Generation
   🟢 ENTRY signal for BTC/USDT
      Confidence: 65.0%
      Position: $1,000.00

✅ CYCLE COMPLETE
```

**That's it!** The system is now running in paper trading mode.

---

## 5. Monitor

### Check Logs
```bash
tail -f logs/sovereign_shadow.log
```

### Check Database
```bash
sqlite3 data/performance.db
```

```sql
SELECT strategy_name, regime, total_trades, win_rate, total_pnl 
FROM strategy_performance;
```

### Check Active Positions
In Python:
```python
from core.orchestrator import SovereignShadowOrchestrator

orch = SovereignShadowOrchestrator()
print(orch.active_positions)
```

---

## 🎯 What Now?

### Week 1: Learn the System
- Run orchestrator multiple times
- Watch how it detects regimes
- See how it selects strategies
- Observe performance tracking

### Week 2: Add Strategies
- Copy `elder_reversion/` folder
- Modify entry/exit logic
- Test new strategy
- Compare performance

### Week 3: Backtest
- Load historical data
- Run strategies on past data
- Validate performance
- Optimize parameters

### Week 4: Prepare for Live
- Run 24/7 in FAKE mode
- Fix any bugs
- Verify stability
- Build confidence

### Month 2+: Gradual Live Deployment
- Start with $10 positions
- Monitor closely
- Scale slowly
- Stay disciplined

---

## 🚨 Emergency Stop

```bash
# Kill the process
pkill -f orchestrator.py

# Or set in .env
ALLOW_LIVE_EXCHANGE=0
```

---

## 📖 Learn More

- **Full Guide:** `DEPLOYMENT_GUIDE.md`
- **System Summary:** `SYSTEM_SUMMARY.md`
- **Code Docs:** Comments in each `.py` file

---

## ❓ Troubleshooting

**"Module not found"**
```bash
./install.sh
```

**"API authentication failed"**
- Check `.env` credentials
- Verify API key format
- Test: `python3 core/exchange_connectors/coinbase_connector.py`

**"Strategy not found"**
- Check `ls strategies/modularized/`
- Verify entry.py, exit.py, risk.py exist

**"Database locked"**
```bash
rm data/performance.db
python3 test_system.py
```

---

## 🎉 You're Ready!

The system is:
- ✅ Installed
- ✅ Configured
- ✅ Tested
- ✅ Running

**Happy trading!** (in FAKE mode first 😉)

---

*"System over emotion. Every single time."*

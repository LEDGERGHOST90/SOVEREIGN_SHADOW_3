# 🏴 SOVEREIGN SHADOW II - DEPLOYMENT GUIDE

**⚠️  READ THIS ENTIRE GUIDE BEFORE DEPLOYMENT**

---

## 🎯 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd /workspace/sovereign_shadow_ii
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your credentials
nano .env
```

**Required settings:**
```bash
ENV=development
ALLOW_LIVE_EXCHANGE=0              # MUST be 0 for testing
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here
PORTFOLIO_VALUE=10000
```

### 3. Test Connection

```bash
# Test Coinbase API connection
python core/exchange_connectors/coinbase_connector.py
```

Expected output:
```
✅ CONNECTION SUCCESSFUL
💰 Account Balances:
   USD: 1660.00
   BTC: 0.00500000
📊 BTC/USD Price: $99,050.00
```

### 4. Run in FAKE Mode

```bash
# Run orchestrator in paper trading mode
python core/orchestrator.py
```

---

## 🔐 Safety Guardrails

### FAKE Mode (Default)

**FAKE mode = Paper trading. No real money at risk.**

Settings:
```bash
ENV=development
ALLOW_LIVE_EXCHANGE=0
```

- All trades simulated
- Portfolio updates virtual
- Safe for testing strategies
- **USE THIS MODE FOR AT LEAST 1 MONTH**

### LIVE Mode (Danger Zone)

**LIVE mode = Real money. Real risk.**

⚠️ **DO NOT ENABLE UNTIL:**
1. ✅ 1+ months of successful FAKE mode operation
2. ✅ Backtesting shows positive results
3. ✅ You understand every line of code
4. ✅ You've tested with minimum position sizes
5. ✅ Stop losses working correctly

To enable:
```bash
ENV=production
ALLOW_LIVE_EXCHANGE=1              # DANGER: Real money mode
MAX_POSITION_SIZE_USD=100          # Start SMALL
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│         DIRECTIVE LAYER                  │
│      Market Regime Detector              │
│  (trending, choppy, breakout, etc)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      ORCHESTRATION LAYER                 │
│      AI Strategy Selector                │
│  (picks best strategy for regime)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        EXECUTION LAYER                   │
│       Strategy Engine                    │
│    (executes trades via API)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        LEARNING LAYER                    │
│     Performance Tracker                  │
│  (updates strategy performance)          │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

Before going live, verify:

### Phase 1: Component Testing (Week 1)

- [ ] **Coinbase Connection**
  ```bash
  python core/exchange_connectors/coinbase_connector.py
  ```
  - Verify balance fetch works
  - Verify price fetch works
  - NO errors

- [ ] **Regime Detection**
  ```bash
  python core/intelligence/regime_detector.py
  ```
  - Verify ADX calculation
  - Verify regime classification
  - Test with different market conditions

- [ ] **Strategy Selection**
  ```bash
  python core/intelligence/strategy_selector.py
  ```
  - Verify strategy ranking
  - Verify fallback logic

- [ ] **Performance Tracking**
  ```bash
  python core/intelligence/performance_tracker.py
  ```
  - Verify database creation
  - Verify trade logging
  - Verify metrics calculation

### Phase 2: Strategy Testing (Week 2-3)

- [ ] **Elder Reversion Strategy**
  ```bash
  python strategies/modularized/elder_reversion/entry.py
  python strategies/modularized/elder_reversion/exit.py
  python strategies/modularized/elder_reversion/risk.py
  ```

- [ ] **RSI Reversion Strategy**
  ```bash
  python strategies/modularized/rsi_reversion/entry.py
  python strategies/modularized/rsi_reversion/exit.py
  python strategies/modularized/rsi_reversion/risk.py
  ```

### Phase 3: Integration Testing (Week 4)

- [ ] **Full Orchestrator**
  ```bash
  python core/orchestrator.py
  ```
  - Run 100+ cycles in FAKE mode
  - Monitor for errors
  - Verify trades logged correctly

- [ ] **Performance Analysis**
  - Check win rate > 50%
  - Check profit factor > 1.5
  - Check max drawdown < 10%

### Phase 4: Live Deployment (After 1 Month)

- [ ] **Minimum Position Test**
  - Set MAX_POSITION_SIZE_USD=10
  - Run for 1 week
  - Verify everything works

- [ ] **Gradual Scale Up**
  - Week 1: $10 positions
  - Week 2: $25 positions
  - Week 3: $50 positions
  - Week 4: $100 positions

---

## 🚨 Emergency Procedures

### Stop Trading Immediately

```bash
# Set in .env
ALLOW_LIVE_EXCHANGE=0

# Or kill process
pkill -f orchestrator.py
```

### Close All Positions

```python
from core.orchestrator import SovereignShadowOrchestrator

orchestrator = SovereignShadowOrchestrator(mode="LIVE")

# Close all positions at market
for symbol in orchestrator.active_positions:
    # Close position logic here
    pass
```

### Check Logs

```bash
tail -f logs/sovereign_shadow.log
```

---

## 📈 Performance Monitoring

### Daily Checks

```bash
# View performance database
sqlite3 data/performance.db

# Query win rate
SELECT 
    strategy_name,
    regime,
    total_trades,
    win_rate,
    total_pnl
FROM strategy_performance
ORDER BY sharpe_ratio DESC;
```

### Key Metrics to Monitor

- **Win Rate**: Should be > 50%
- **Profit Factor**: Gross profit / Gross loss (target > 1.5)
- **Sharpe Ratio**: Risk-adjusted returns (target > 1.0)
- **Max Drawdown**: Largest peak-to-trough loss (keep < 10%)

---

## 🛠️ Troubleshooting

### Coinbase API Errors

**Error: "Invalid API key format"**
```bash
# Verify key format
echo $COINBASE_API_KEY
# Should be: organizations/{org_id}/apiKeys/{key_id}
```

**Error: "Invalid signature"**
```bash
# Verify secret is PEM format
cat .env | grep COINBASE_API_SECRET
# Should start with: -----BEGIN EC PRIVATE KEY-----
```

### Strategy Not Found

**Error: "Strategy not available"**
```bash
# List available strategies
ls -la strategies/modularized/

# Verify strategy has all files
ls -la strategies/modularized/elder_reversion/
# Should have: entry.py, exit.py, risk.py, metadata.json
```

### Database Errors

**Error: "Database locked"**
```bash
# Close any open connections
pkill -f python

# Reset database
rm data/performance.db
python core/intelligence/performance_tracker.py
```

---

## 📞 Support

**Issues?** Check logs first:
```bash
tail -100 logs/sovereign_shadow.log
```

**Need help?** Review:
1. This deployment guide
2. README.md
3. Code comments in each module

---

## ⚖️ Legal Disclaimer

**USE AT YOUR OWN RISK**

- This is experimental software
- No warranties or guarantees
- You are responsible for all losses
- Trading crypto is highly risky
- Past performance ≠ future results
- Always start with small position sizes
- Never trade with money you can't afford to lose

**By using this system, you acknowledge:**
- You understand the risks
- You've tested thoroughly in FAKE mode
- You accept full responsibility for all trades
- You will not hold the developers liable for any losses

---

## 🎯 Recommended Deployment Path

### Month 1: Paper Trading
- Run FAKE mode 24/7
- Monitor performance daily
- Fix any bugs immediately
- Target: 100+ trades, >50% win rate

### Month 2: Backtesting
- Backtest on historical data
- Validate strategy performance
- Optimize parameters
- Target: Sharpe > 1.0, Max DD < 10%

### Month 3: Minimum Live Test
- $10 positions only
- Monitor closely
- Verify everything works
- Target: Break even or better

### Month 4+: Gradual Scale
- Increase position sizes slowly
- Never exceed 10% of portfolio per trade
- Keep 3-strike rule active
- Target: Consistent profitability

---

**Remember:** The goal isn't to get rich quick. The goal is to build a reliable, sustainable trading system that works consistently over years, not days.

**"System over emotion. Every single time."**

---

*Last updated: 2024-12-13*

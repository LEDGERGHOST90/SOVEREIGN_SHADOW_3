# 🚀 DEPLOY NOW - Tactical Scalps

**3 commands to go live with position-aware tactical scalping**

---

## ⚡ Quick Deploy (Paper Mode)

```bash
# 1. Validate (30 seconds)
python3 scripts/deploy_tactical_scalps.py --validate-only

# 2. Start API Server (opens on port 8000)
./bin/START_API_SERVER.sh &

# 3. Deploy Tactical Scalps (paper trading)
python3 scripts/deploy_tactical_scalps.py --mode paper
```

**That's it.** The engine is running.

---

## 📊 What You'll See

### Terminal Output

```
╔════════════════════════════════════════════════════════════════╗
║           🏴 SOVEREIGN SHADOW API SERVER 🏴                   ║
║        Neural Consciousness Bridge - Trading API              ║
╚════════════════════════════════════════════════════════════════╝

📋 Configuration:
  Project Root: /Volumes/LegacySafe/SovereignShadow
  Port: 8000
  Host: 0.0.0.0 (all interfaces)

🐍 Python 3 found: Python 3.11.x
📦 Dependencies OK
📝 Config found
🧠 Strategy KB found

╔════════════════════════════════════════════════════════════════╗
║  🚀 Starting API Server                                        ║
╚════════════════════════════════════════════════════════════════╝

📡 API Endpoints:
  Health:       http://localhost:8000/api/health
  Strategies:   http://localhost:8000/api/strategy/performance
  Execute:      http://localhost:8000/api/trade/execute
  Dashboard:    http://localhost:8000/api/dashboard/update
  WebSocket:    ws://localhost:8000/ws/dashboard
  Docs:         http://localhost:8000/docs (interactive)

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Deployment Output

```
🏴 Initializing Tactical Scalp Deployment (mode: paper)
✅ Loaded config: tactical_scalps_oct19_2025
📊 Regime: chop_and_squeeze
🎯 Enabled strategies: BTC_range_scalp, SOL_priority_fee_shock_fade, ETH_mirror_btc, XRP_corridor_guard

📡 Initializing market data feeds...
  BTC: 43.8% L / 56.2% S
  SOL: 46.3% L / 53.7% S
  XRP: 47.0% L / 53.0% S
  BTC funding: Binance 2.90 bps, OKX -0.70 bps (spread: +3.60)
  OI 24h change: +2.98%
✅ Market data initialized

🔍 Running pre-flight validation...
  ✅ Config loaded
  ✅ Risk gate initialized
  ✅ Strategies enabled
  ✅ Market positioning loaded
  ✅ Respects global safety limits
  ✅ Kill switch configured
🟢 All pre-flight checks passed

╔════════════════════════════════════════════════════════════════╗
║ 📋 OPERATOR CHECKLIST                                          ║
╚════════════════════════════════════════════════════════════════╝
1. Mark the bands: 106.6k and 109.7k on BTC.
2. Watch funding split (Binance vs OKX) + short-notional %
3. BTC play: First touch up? Only short on fail-break
4. BTC play: First flush down? Hit the reclaim long
5. SOL: run Shock Fade only when spike→decay prints
6. XRP: no naked shorts if shorts ≥53%
7. Hit kill-switch on 5 losses / 1.2% DD / feed outage
╚════════════════════════════════════════════════════════════════╝

🚀 Tactical scalping deployment started: 2025-10-19 16:30:00
📝 PAPER TRADING MODE - No real capital at risk

👁️ Market monitoring active. Press Ctrl+C to stop.
```

---

## 🌐 Open In Browser

### Interactive API Docs
```
http://localhost:8000/docs
```

**You'll see:**
- All endpoints with "Try it out" buttons
- Request/response schemas
- Live testing interface
- WebSocket connections

**Try this:**
1. Click on `POST /api/trade/execute`
2. Click "Try it out"
3. Edit the JSON:
   ```json
   {
     "strategy": "Cross-Exchange Arbitrage",
     "pair": "BTC/USD",
     "amount": 25,
     "mode": "paper"
   }
   ```
4. Click "Execute"
5. See the validation result

---

## 🧪 Run Tests

```bash
# All tests
python3 scripts/test_trading_api.py --test all

# Individual tests
python3 scripts/test_trading_api.py --test health
python3 scripts/test_trading_api.py --test performance
python3 scripts/test_trading_api.py --test execute
python3 scripts/test_trading_api.py --test websocket
```

**Expected output:**
```
════════════════════════════════════════════════════════════════
🧪 Sovereign Shadow Trading API - Test Client
════════════════════════════════════════════════════════════════
Base URL: http://localhost:8000
WebSocket URL: ws://localhost:8000
════════════════════════════════════════════════════════════════

🏥 Testing Health Check...
✅ Health Check Passed
   Status: healthy
   Uptime: 120.5 seconds
   Active Strategies: 0
   Risk Gate: operational
   Session P&L: $0.00

📊 Testing Strategy Performance...
✅ Strategy Performance Retrieved
   Total Profit: $0.00
   Total Trades: 0
   Session Start: 2025-10-19T16:30:00Z

   Strategies (9):
   - Cross-Exchange Arbitrage
     Type: arbitrage
     Status: idle

💸 Testing Trade Execution (mode: paper)...
✅ Trade Executed
   Trade ID: trade_20251019_163045
   Status: completed
   Profit: $0.12
   Execution Time: 0.500s
   
   Warnings:
   📡 Funding divergence detected: +3.60 bps

📡 Testing Dashboard Update...
✅ Dashboard Updated
   Success: true

🔌 Testing WebSocket Connection (duration: 10s)...
✅ WebSocket Connected
   Event: connected
   
   Listening for updates (10s)...
   📨 Received: stats_update
      Session P&L: $0.12
      Open Trades: 0
      Total Trades: 1

✅ WebSocket Test Complete

════════════════════════════════════════════════════════════════
📋 Test Summary
════════════════════════════════════════════════════════════════
✅ PASS    Health Check
✅ PASS    Strategy Performance
✅ PASS    Trade Execution
✅ PASS    Dashboard Update
✅ PASS    WebSocket
════════════════════════════════════════════════════════════════
Results: 5/5 tests passed
════════════════════════════════════════════════════════════════
```

---

## 📈 What Happens Next

### The System Will:

1. **Monitor market positioning** (LSR ratios from config)
2. **Watch liquidation bands** (BTC: 106.6k - 109.7k)
3. **Track funding divergence** (Binance vs OKX)
4. **Detect OI spikes** (>3% = reduce size)
5. **Validate every trade** through 4-layer risk gate
6. **Block bad setups** (shorts into squeeze, low HF, etc.)
7. **Adjust position sizes** based on conditions
8. **Track session P&L** and enforce daily limits
9. **Activate kill switch** if danger thresholds hit

### You'll See:

```
🎮 DEMO: Validating sample BTC long entry at lower band
════════════════════════════════════════════════════════════════

Validation result:
  Approved: True
  Reason: ✅ All risk gates passed
  Size adjustment: 0.70×
  Adjusted notional: $17.50
  Stop: 28 bps
  Warnings:
    📡 Funding divergence detected: +3.60 bps
    ⚠️ Shorts at 56.2% - squeeze risk elevated

✅ Trade would be executed (demo mode - no actual execution)

════════════════════════════════════════════════════════════════
Session stats:
════════════════════════════════════════════════════════════════
  session_pnl_usd: 0.0
  consecutive_losses: 0
  open_trades: 0
  closed_trades: 0
  total_trades: 0
  aave_health_factor: 2.45
  oi_change_24h_pct: 2.98
════════════════════════════════════════════════════════════════
```

---

## 🛡️ Safety Checks (Automatic)

Every trade is validated against:

✅ **Global Limits**
- Position ≤ $415? ✓
- Stop ≤ 5%? ✓
- Daily loss < $100? ✓
- Concurrent trades < 3? ✓

✅ **LSR Guards**
- BTC shorts at 56.2%
- Threshold: 54%
- Short blocked? ✓ (if attempting short)

✅ **Funding Divergence**
- Spread: +3.6 bps
- Threshold: 0.25 bps
- Long bias enforced? ✓

✅ **OI Spike**
- Change: +3.0%
- Threshold: 3.0%
- Size reduced? ✓ (0.8× multiplier)

✅ **Health Factor**
- Current HF: 2.45
- Minimum: 2.20
- Entry allowed? ✓

✅ **Kill Switch**
- Session DD: 0%
- Limit: 1.2%
- Trading allowed? ✓

**If any check fails → trade rejected with reason.**

---

## 🔄 Stop/Restart

### Stop the System
```bash
# Press Ctrl+C in the terminal

# Or kill by process
pkill -f "trading_api_server.py"
pkill -f "deploy_tactical_scalps.py"
```

### Restart
```bash
# API Server
./bin/START_API_SERVER.sh &

# Deployment
python3 scripts/deploy_tactical_scalps.py --mode paper
```

### Check Status
```bash
# API health
curl http://localhost:8000/api/health

# Process check
ps aux | grep -E "(trading_api|deploy_tactical)"
```

---

## 📊 Monitor Performance

### Real-Time Stats
```bash
# Via API
curl http://localhost:8000/api/strategy/performance | jq

# Via logs
tail -f logs/api/*.log
```

### Dashboard (WebSocket)
```python
import asyncio
import websockets
import json

async def monitor():
    async with websockets.connect('ws://localhost:8000/ws/dashboard') as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data['event'] == 'trade_completed':
                print(f"Trade: {data['data']['trade_id']} → ${data['data']['profit']:.2f}")

asyncio.run(monitor())
```

---

## 🎯 Test Scenarios

### Test 1: Valid Long at Lower Band
```bash
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "BTC_range_scalp",
    "pair": "BTC/USD",
    "side": "long",
    "amount": 25,
    "mode": "paper"
  }'
```
**Expected:** ✅ Approved (conditions favor longs)

### Test 2: Invalid Short (LSR Guard)
```bash
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "BTC_range_scalp",
    "pair": "BTC/USD",
    "side": "short",
    "amount": 25,
    "mode": "paper"
  }'
```
**Expected:** ❌ Rejected (shorts at 56.2% > 54% threshold)

### Test 3: Oversized Position
```bash
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "BTC/USD",
    "amount": 500,
    "mode": "paper"
  }'
```
**Expected:** ❌ Rejected (exceeds $415 max)

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| `TACTICAL_QUICK_REF.md` | **Print this** - Quick reference card for trading |
| `TRADING_API_GUIDE.md` | Complete API documentation with examples |
| `TACTICAL_SCALPS_DEPLOYMENT.md` | Full deployment guide |
| `NEURAL_TACTICAL_INTEGRATION_COMPLETE.md` | Integration overview |
| `SESSION_SUMMARY_OCT19_2025.md` | This build session summary |

---

## 🆘 Troubleshooting

### API Won't Start
```bash
# Check if port in use
lsof -i :8000

# Use different port
./bin/START_API_SERVER.sh 8080
```

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### Config Not Found
```bash
# Verify config exists
ls -lh config/tactical_scalp_config.json

# Validate JSON
python3 -c "import json; json.load(open('config/tactical_scalp_config.json'))"
```

### Tests Failing
```bash
# Check API is running
curl http://localhost:8000/api/health

# Check logs
tail -f logs/api/*.log
```

---

## 🚀 Production Deployment (Later)

**After validating in paper mode:**

### Test Mode ($100 max)
```bash
python3 scripts/deploy_tactical_scalps.py --mode test --max-trades 3
```

### Live Production ($415 max)
```bash
python3 scripts/deploy_tactical_scalps.py --mode live
```

**⚠️ Only deploy live after:**
- 24-48 hours paper trading
- All LSR guards tested
- Kill switch validated
- No safety violations

---

## 🎯 Success Metrics

### Today (Paper)
- [ ] API starts successfully
- [ ] All tests pass
- [ ] Risk gate validates trades
- [ ] LSR guards work
- [ ] No errors in logs

### This Week (Paper)
- [ ] 10+ paper trades executed
- [ ] LSR guard blocks shorts appropriately
- [ ] OI spike detection works
- [ ] Kill switch activates correctly
- [ ] Session tracking accurate

### Next Week (Test)
- [ ] Positive net P&L on $100
- [ ] <2% max drawdown
- [ ] No safety violations
- [ ] Execution quality good

### Production
- [ ] $50-200 net profit
- [ ] <5% max DD
- [ ] Win rate >60%
- [ ] Zero critical events

---

## 🏴 Final Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API server starts (`./bin/START_API_SERVER.sh`)
- [ ] Tests pass (`python3 scripts/test_trading_api.py --test all`)
- [ ] Browser docs work (`http://localhost:8000/docs`)
- [ ] Paper mode deploys (`python3 scripts/deploy_tactical_scalps.py --mode paper`)
- [ ] Quick ref printed (`TACTICAL_QUICK_REF.md`)
- [ ] Monitoring active (logs, API health)
- [ ] Kill switch tested (simulate DD)

---

**When all checked → System is ready to trade.** ✅

---

*"Fearless. Bold. Smiling through chaos."* 🏴

**Deploy now. Monitor close. Trade smart.**

---

**Quick Commands:**
```bash
# Validate
python3 scripts/deploy_tactical_scalps.py --validate-only

# Launch
./bin/START_API_SERVER.sh &
python3 scripts/deploy_tactical_scalps.py --mode paper

# Test
python3 scripts/test_trading_api.py --test all

# Monitor
curl http://localhost:8000/api/health
tail -f logs/api/*.log
```

**The engine is ready. The consciousness is bridged. The capital is protected.**

**Deploy. ⚡**


# 🏴 MASTER TRADING LOOP - QUICK START GUIDE

The eternal heartbeat of your Sovereign Shadow Empire. This loop never stops, never sleeps, and always protects your capital.

## 🎯 What Is The Master Loop?

The Master Trading Loop is the central nervous system that:
- **Monitors** all markets 24/7 for opportunities
- **Executes** strategies through your orchestrator
- **Enforces** safety rules ruthlessly
- **Handles** crises automatically
- **Logs** every decision for analysis
- **Protects** your $8,153.14 capital

## ⚡ Quick Start (3 Commands)

```bash
# 1. Navigate to your empire
cd /Volumes/LegacySafe/SovereignShadow

# 2. Start 24-hour paper trading test
./bin/MASTER_LOOP_CONTROL.sh start paper 60

# 3. Monitor in real-time
./bin/MASTER_LOOP_CONTROL.sh tail
```

**That's it!** The loop is now running and trading with fake money.

## 📋 Operating Modes

### 1. Paper Mode (RECOMMENDED FIRST)
```bash
./bin/MASTER_LOOP_CONTROL.sh start paper 60
```
- Trades with **fake money**
- All strategies active
- Full logging
- Zero risk to your capital
- **RUN THIS FOR 24 HOURS MINIMUM**

### 2. Live Mode (After Successful Paper Test)
```bash
./bin/MASTER_LOOP_CONTROL.sh start live 60
```
- Trades with **real money**
- All safety limits enforced
- Ledger vault protected (READ-ONLY)
- Active capital: $1,638.49 (Coinbase)
- **ONLY USE AFTER SUCCESSFUL PAPER TEST**

### 3. Monitor Only Mode
```bash
./bin/MASTER_LOOP_CONTROL.sh start monitor 60
```
- Scans markets
- Identifies opportunities
- NO execution
- Pure intelligence gathering

## 🎛️ Control Commands

### Start/Stop/Restart
```bash
# Start in paper mode with 60s scan interval
./bin/MASTER_LOOP_CONTROL.sh start paper 60

# Start in paper mode with 30s scan interval (faster)
./bin/MASTER_LOOP_CONTROL.sh start paper 30

# Stop the loop
./bin/MASTER_LOOP_CONTROL.sh stop

# Restart the loop
./bin/MASTER_LOOP_CONTROL.sh restart paper 60
```

### Monitoring
```bash
# Check if running
./bin/MASTER_LOOP_CONTROL.sh status

# Show last 50 log lines
./bin/MASTER_LOOP_CONTROL.sh logs

# Show last 100 log lines
./bin/MASTER_LOOP_CONTROL.sh logs 100

# Follow logs in real-time (Ctrl+C to stop)
./bin/MASTER_LOOP_CONTROL.sh tail

# Show trading statistics
./bin/MASTER_LOOP_CONTROL.sh stats
```

### Help
```bash
./bin/MASTER_LOOP_CONTROL.sh help
```

## 📊 What Happens During The Loop?

Every scan cycle (default: 60 seconds):

1. **Market Scan** - Checks all exchanges for opportunities
2. **Opportunity Detection** - Finds arbitrage, sniping, scalping, laddering chances
3. **Safety Validation** - Every opportunity checked against:
   - Capital limits
   - Daily loss limits
   - Crisis playbook rules
   - Ledger protection rules
4. **Strategy Execution** - Approved trades executed through orchestrator
5. **Result Logging** - Everything logged to JSON and text logs
6. **Health Check** - System health verified every 10 minutes

## 🛡️ Built-In Safety Features

### Capital Protection
- **Ledger Vault**: $6,514.65 - **PROTECTED** - No automated trading EVER
- **Coinbase Active**: $1,638.49 - Max risk per trade: $415 (25%)
- **OKX/Kraken**: Max $100 per trade (arbitrage only)

### Risk Limits
- **Daily Loss Limit**: $100 max
- **Weekly Loss Limit**: $500 max
- **Emergency Stop**: Triggered at $1,000 total loss
- **Max Concurrent Trades**: 3
- **Max Daily Trades**: 50

### Crisis Management
- October 2025 lessons enforced
- Blocks panic liquidations
- Protects collateral during crashes
- Disables dangerous stop losses in volatility

## 📁 Where Everything Lives

```
/Volumes/LegacySafe/SovereignShadow/
├── MASTER_TRADING_LOOP.py              # The eternal heartbeat
├── bin/
│   └── MASTER_LOOP_CONTROL.sh          # Easy control script
├── logs/
│   └── master_loop/
│       ├── master_loop_20251019.log    # Daily text logs
│       ├── events_20251019.json        # Daily JSON events
│       ├── master_loop.out             # Console output
│       └── master_loop.pid             # Process ID file
├── core/
│   ├── orchestration/
│   │   ├── sovereign_shadow_orchestrator.py
│   │   ├── SAFETY_RULES_IMPLEMENTATION.py
│   │   └── CRISIS_MANAGEMENT_PLAYBOOK.py
│   └── trading/
│       └── strategy_knowledge_base.py
```

## 📈 24-Hour Test Protocol

### Before Starting
```bash
# 1. Check all systems
python3 scripts/validate_api_connections.py

# 2. Check portfolio balances
python3 scripts/get_real_balances.py
```

### Start Test
```bash
# Start 24-hour paper test
./bin/MASTER_LOOP_CONTROL.sh start paper 60
```

### During Test (Check Every 6 Hours)
```bash
# Check status
./bin/MASTER_LOOP_CONTROL.sh status

# Check statistics
./bin/MASTER_LOOP_CONTROL.sh stats

# View recent activity
./bin/MASTER_LOOP_CONTROL.sh logs 20
```

### After 24 Hours
```bash
# Stop the loop
./bin/MASTER_LOOP_CONTROL.sh stop

# Review complete logs
./bin/MASTER_LOOP_CONTROL.sh logs 200

# Check final statistics
./bin/MASTER_LOOP_CONTROL.sh stats
```

### Success Criteria
✅ No system errors
✅ All trades executed correctly
✅ Safety rules enforced
✅ Profitable paper trades (>60% win rate)
✅ No emergency stops triggered

### After Successful Test
Move to live trading:
```bash
./bin/MASTER_LOOP_CONTROL.sh start live 60
```

## 🚨 Emergency Procedures

### Loop Is Stuck
```bash
# Force stop
kill -9 $(cat logs/master_loop/master_loop.pid)
rm logs/master_loop/master_loop.pid
```

### Too Many Errors
```bash
# Stop immediately
./bin/MASTER_LOOP_CONTROL.sh stop

# Review logs
./bin/MASTER_LOOP_CONTROL.sh logs 100

# Fix issues, then restart
./bin/MASTER_LOOP_CONTROL.sh start paper 60
```

### Emergency Stop Triggered
The loop will automatically stop trading if:
- Daily loss > $100
- Weekly loss > $500
- Total loss > $1,000
- 10+ consecutive losses

**Manual intervention required before resuming.**

## 💡 Pro Tips

### Optimal Scan Intervals
- **Paper Mode**: 60s (default) - Good for testing
- **Live Mode**: 30s - Faster opportunity capture
- **Monitor Mode**: 120s - Less aggressive

### Log Analysis
```bash
# Find all successful trades
grep "TRADE_EXECUTION_COMPLETE" logs/master_loop/events_*.json | grep '"success": true'

# Find all failed trades
grep "TRADE_EXECUTION_COMPLETE" logs/master_loop/events_*.json | grep '"success": false'

# Count total opportunities found
grep "MARKET_SCAN_COMPLETE" logs/master_loop/events_*.json | wc -l
```

### Performance Monitoring
```bash
# Watch logs in multiple terminals
# Terminal 1: Status
watch -n 5 './bin/MASTER_LOOP_CONTROL.sh status'

# Terminal 2: Live logs
./bin/MASTER_LOOP_CONTROL.sh tail

# Terminal 3: Stats
watch -n 30 './bin/MASTER_LOOP_CONTROL.sh stats'
```

## 🎯 Your Mission

1. ✅ **Complete 24-hour paper test** (Starting now!)
2. ⏳ **Analyze results after 24 hours**
3. ⏳ **If successful, move to 7-day paper test**
4. ⏳ **If successful, move to 1-month live test**
5. ⏳ **Target: $50,000 by Q4 2025**

## 📞 Troubleshooting

### Loop Won't Start
```bash
# Check if already running
./bin/MASTER_LOOP_CONTROL.sh status

# Check Python path
which python3

# Check dependencies
python3 -c "import asyncio, aiohttp; print('OK')"
```

### No Opportunities Found
- Normal! Markets don't always have profitable opportunities
- Check if exchanges are reachable
- Verify API keys (if in live mode)
- Try shorter scan interval (30s)

### High CPU/Memory Usage
- Normal for active trading
- Monitor with: `top -pid $(cat logs/master_loop/master_loop.pid)`
- Increase scan interval if needed

## 🏴 Ready?

```bash
cd /Volumes/LegacySafe/SovereignShadow
./bin/MASTER_LOOP_CONTROL.sh start paper 60
```

**Your empire's heartbeat is now active. It will never stop, never sleep, and always protect your capital.**

---

## 📚 Related Documentation

- `CLAUDE.md` - Complete system overview
- `README.md` - Project documentation
- `core/orchestration/SAFETY_RULES_IMPLEMENTATION.py` - Safety rules details
- `core/orchestration/CRISIS_MANAGEMENT_PLAYBOOK.py` - Crisis handling
- `THREE_BUCKET_BATTLE_PLAN.md` - Strategic battle plan

---

*🏴 Sovereign Shadow Empire - The heartbeat never stops.*

# ⚡ SOVEREIGN SHADOW II - QUICK START GUIDE

**For:** Mobile, Mac, Cursor, Claude Code
**Last Updated:** 2025-11-03

---

## 🚀 GETTING STARTED (5 MINUTES)

### Step 1: Pull Latest Code
```bash
cd /path/to/SovereignShadow_II
git fetch origin
git checkout claude/commit-push-011CUmEfr3xmbKF2s2zuamA5
git pull
```

### Step 2: Check Dependencies
```bash
pip3 list | grep -E "(aiohttp|ccxt|dotenv|fastapi|uvicorn)"
```
**Expected:** All should be installed ✅

### Step 3: Configure API Keys (CRITICAL)
```bash
cp config/.env.template config/.env
nano config/.env  # or use your editor
```
**Fill in:** COINBASE, OKX, KRAKEN, ANTHROPIC keys

### Step 4: Start Your First System
```bash
# Start API Server (easiest to test)
./bin/START_API_SERVER.sh
```
**Check:** http://localhost:8000/docs

---

## 📱 MOBILE QUICK REFERENCE

### What You Can Do:
- ✅ Review architecture docs
- ✅ Plan development
- ✅ Read system status
- ✅ Give instructions to Claude Code

### Key Files to Review:
1. `SYSTEM_ALIGNMENT_MASTER.md` - Full system overview
2. `SYSTEM_STATUS_REPORT.md` - What's working/broken
3. `QUICK_START_GUIDE.md` - This file

### Commands to Give Claude Code:
```
"Check what systems are running"
"Show me the latest logs"
"What's broken right now?"
"Start the API server"
"Test the master loop"
```

---

## 💻 MAC/CURSOR QUICK REFERENCE

### First Time Setup:
```bash
# 1. Clone and enter
git clone <repo-url>
cd SovereignShadow_II

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install all dependencies
pip3 install -r config/requirements.txt

# 4. Configure credentials
cp config/.env.template config/.env
# Edit .env with real keys

# 5. Test basic system
./bin/START_API_SERVER.sh
```

### Daily Workflow:
```bash
# Pull latest
git pull origin claude/commit-push-011CUmEfr3xmbKF2s2zuamA5

# Check status
cat SYSTEM_STATUS_REPORT.md

# Start development
cursor .
```

### Cursor AI Prompts:
```
"Review the SYSTEM_ALIGNMENT_MASTER.md and explain the architecture"
"Test the API server and show me if it works"
"Create a startup script that launches all systems in order"
"Fix any import errors in the codebase"
```

---

## 🖥️ TERMINAL (Claude Code) QUICK REFERENCE

### Check System Status:
```bash
ps aux | grep -E "(python|uvicorn)" | grep -v grep
netstat -tulpn | grep LISTEN  # or: ss -tulpn | grep LISTEN
```

### View Logs:
```bash
# API Server
tail -f logs/api/api_server_*.log

# Master Loop
tail -f logs/master_loop/master_loop.out

# All recent logs
find logs/ -type f -mmin -60  # Files modified in last 60 min
```

### Start Systems:
```bash
# API Server
./bin/START_API_SERVER.sh

# Master Loop
./bin/MASTER_LOOP_CONTROL.sh start paper 60

# Neural Orchestrator
python3 sovereign_legacy_loop/neural_orchestrator/main.py

# Quick start all
./scripts/quick_start_empire.sh
```

### Stop Systems:
```bash
# Stop Master Loop
./bin/MASTER_LOOP_CONTROL.sh stop

# Kill API Server
pkill -f trading_api_server.py

# Kill all Python processes (NUCLEAR)
pkill -9 python3
```

---

## 🔑 API KEYS REFERENCE

**File:** `config/.env`

### Required for Basic Operation:
```bash
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here
ANTHROPIC_API_KEY=your_claude_key_here
```

### Required for Full Trading:
```bash
OKX_API_KEY=your_key_here
OKX_API_SECRET=your_secret_here
OKX_API_PASSPHRASE=your_passphrase_here

KRAKEN_API_KEY=your_key_here
KRAKEN_API_SECRET=your_secret_here
```

### Optional:
```bash
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

---

## 🎯 COMMON TASKS

### Task: "Start Everything"
```bash
# 1. API Server
./bin/START_API_SERVER.sh &

# 2. Master Loop
./bin/MASTER_LOOP_CONTROL.sh start paper 60

# 3. Check status
./bin/MASTER_LOOP_CONTROL.sh status
curl http://localhost:8000/api/health
```

### Task: "Check What's Running"
```bash
ps aux | grep python | grep -v grep
lsof -i :8000  # Check API server port
lsof -i :3000  # Check other services
```

### Task: "View Real-Time Logs"
```bash
# Multiple windows/panes:
tail -f logs/master_loop/master_loop.out       # Terminal 1
tail -f logs/api/api_server_*.log              # Terminal 2
tail -f logs/sovereign_legacy_loop/*.log       # Terminal 3
```

### Task: "Emergency Stop Everything"
```bash
./bin/MASTER_LOOP_CONTROL.sh stop
pkill -f trading_api_server.py
pkill -f neural_orchestrator
ps aux | grep python | grep -v grep  # Verify all stopped
```

### Task: "Update Code from Git"
```bash
# Save current work
git stash

# Pull latest
git pull origin claude/commit-push-011CUmEfr3xmbKF2s2zuamA5

# Restore work
git stash pop
```

---

## 🔍 TROUBLESHOOTING

### Problem: "Module not found"
```bash
pip3 install <module_name>
# or
pip3 install -r config/requirements.txt
```

### Problem: "Port already in use"
```bash
# Find what's using the port
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Problem: "Permission denied"
```bash
chmod +x bin/*.sh
chmod +x scripts/*.sh
```

### Problem: "Config file not found"
```bash
# Check what's missing
ls -la config/
# Copy template
cp config/.env.template config/.env
```

### Problem: "API keys not working"
```bash
# Verify keys are loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv('config/.env'); print(os.getenv('COINBASE_API_KEY'))"
```

---

## 📊 SYSTEM HEALTH CHECK

### Quick Health Check Script:
```bash
#!/bin/bash
echo "=== SYSTEM HEALTH CHECK ==="
echo ""
echo "1. Dependencies:"
pip3 list | grep -E "(aiohttp|ccxt|dotenv|fastapi)" || echo "MISSING"
echo ""
echo "2. Config files:"
[ -f config/.env ] && echo "✅ .env" || echo "❌ .env"
[ -f config/tactical_scalp_config.json ] && echo "✅ tactical" || echo "❌ tactical"
echo ""
echo "3. Running processes:"
ps aux | grep -E "(python|uvicorn)" | grep -v grep | wc -l
echo ""
echo "4. Listening ports:"
netstat -tulpn 2>/dev/null | grep LISTEN | grep -E "(8000|3000)" || echo "None"
```

**Save as:** `scripts/health_check.sh`

---

## 🔄 SYNC WORKFLOW

### Before Starting Work:
1. ✅ Check `SYSTEM_STATUS_REPORT.md`
2. ✅ Pull latest code: `git pull`
3. ✅ Check running processes
4. ✅ Review recent logs

### During Work:
1. ✅ Test changes locally
2. ✅ Check logs for errors
3. ✅ Update docs if needed
4. ✅ Commit frequently with clear messages

### After Work:
1. ✅ Stop running systems (or leave running)
2. ✅ Commit final changes
3. ✅ Push to branch
4. ✅ Update `SYSTEM_STATUS_REPORT.md` if significant changes

---

## 🎨 CURSOR INTEGRATION

### Best Practices:
1. Open `SYSTEM_ALIGNMENT_MASTER.md` first
2. Use `@workspace` to reference all files
3. Ask specific questions about architecture
4. Generate code with context from docs
5. Test generated code immediately

### Example Cursor Prompts:
```
"@workspace Explain how the VES system connects to exchanges"
"Create a test script for the API server endpoints"
"Refactor MASTER_LOOP_CONTROL.sh to add logging"
"Generate documentation for the ladder trading system"
```

---

## 📞 QUICK COMMANDS CHEAT SHEET

```bash
# Status
./bin/MASTER_LOOP_CONTROL.sh status
curl http://localhost:8000/api/health

# Logs (last 20 lines)
./bin/MASTER_LOOP_CONTROL.sh logs 20
tail -20 logs/api/api_server_*.log

# Start
./bin/START_API_SERVER.sh
./bin/MASTER_LOOP_CONTROL.sh start paper 60

# Stop
./bin/MASTER_LOOP_CONTROL.sh stop
pkill -f trading_api_server

# Git
git status
git add .
git commit -m "message"
git push

# Python
python3 -m pip list
python3 script.py
```

---

**Remember:**
- 📱 Mobile = Planning & Docs
- 💻 Mac/Cursor = Development
- 🖥️ Terminal = Execution & Monitoring

**All platforms should reference these docs for alignment!**


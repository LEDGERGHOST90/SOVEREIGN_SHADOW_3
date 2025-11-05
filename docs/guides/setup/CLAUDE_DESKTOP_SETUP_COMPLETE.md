# 🏴 CLAUDE DESKTOP - COMPLETE SETUP GUIDE

**Date:** November 4, 2025
**Project:** Sovereign Shadow II
**Purpose:** Full Claude Desktop integration for trading system management

---

## 📋 **TABLE OF CONTENTS**

1. [Project Configuration](#project-configuration)
2. [MCP Server Setup](#mcp-server-setup)
3. [Custom Instructions](#custom-instructions)
4. [File Management](#file-management)
5. [Quick Commands](#quick-commands)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 **PROJECT CONFIGURATION**

### **1. Claude Desktop Project Settings**

Location: `/Volumes/LegacySafe/SovereignShadow_II/.claude/`

Create `project.json`:
```json
{
  "name": "Sovereign Shadow II",
  "description": "Advanced cryptocurrency trading system with AAVE DeFi integration, multi-exchange support, and autonomous agent architecture",
  "version": "2.5a",
  "root": "/Volumes/LegacySafe/SovereignShadow_II",
  "languages": ["python", "typescript", "javascript"],
  "frameworks": ["Next.js", "React", "ccxt", "web3.py"],
  "capabilities": [
    "Multi-exchange trading (Coinbase, OKX, Kraken, Binance US)",
    "AAVE v3 DeFi monitoring",
    "Ledger hardware wallet integration",
    "Ladder trading strategies",
    "Autonomous agent system",
    "Real-time portfolio tracking"
  ],
  "key_directories": {
    "agents": "Autonomous trading agents (portfolio, risk, code review)",
    "core": "Core trading engine and portfolio management",
    "modules": "Ladder systems, safety gates, execution logic",
    "scripts": "AAVE monitoring, emergency repay, health dashboard",
    "app": "Next.js web dashboard",
    "config": "Configuration files (NOT committed to git)",
    "logs": "Runtime logs (NOT committed to git)",
    "memory": "Session summaries and analysis reports"
  },
  "important_files": [
    "AAVE_PROTECTION_SUITE_COMPLETE.md",
    ".env.example",
    "DELEVERAGING_PLAN_2025-11-03.md",
    "SIMULATION_READY_2025-11-04.md"
  ]
}
```

### **2. Custom Instructions for Project**

Add to Claude Desktop project instructions:

```markdown
## Sovereign Shadow II - Trading System

**Current Status:**
- Portfolio: $6,167.43 (AAVE $3,494.76 + BTC $2,232)
- AAVE Health Factor: 2.44 (WARNING - monitor closely)
- Protection Suite: 4 tools deployed (Guardian, Dashboard, Risk Calculator, Emergency Repay)
- Latest Commits: ba806c4 (AAVE suite), d146b9e (security), 6433979 (CSV removal)

**Active Monitoring:**
- LSETH dropped 8.6% (oracle not updated yet)
- If materializes: HF 2.44 → 2.23 (still SAFE, 9.5% cushion)
- Trigger: If HF < 2.0, repay $26 USDC immediately

**File Management Rules:**
- NEVER commit .env files
- NEVER commit *.csv files (transaction data)
- NEVER commit config/*_api*.json files
- NEVER commit logs/* files
- Use .env.example as template only

**Critical Commands:**
```bash
# Check AAVE Health Factor
python3 scripts/aave_health_dashboard.py

# Start 24/7 monitoring
python3 scripts/aave_guardian_monitor.py

# Calculate emergency repay
python3 scripts/emergency_aave_repay.py --target-hf 2.5

# Risk scenario analysis
python3 scripts/calculate_risk_scenarios.py
```

**Portfolio Targets:**
- BTC: 40% ($2,467 target, need +$235)
- ETH: 30% ($1,850 target, includes wstETH in AAVE)
- SOL: 20% ($1,233 target, need +$1,233)
- XRP: 10% ($617 target, need +$617)

**Next Actions:**
1. Monitor AAVE HF during LSETH volatility
2. Execute deleveraging plan if HF < 2.0
3. Fund exchanges with $600 for trade ladders
4. Deploy RENDER strategy (19% ROI target)
```

---

## 🔌 **MCP SERVER SETUP**

### **Location:**
`~/Library/Application Support/Claude/claude_desktop_config.json`

### **Current Configuration** (From your screenshot):

```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp/docker"
      ]
    }
  }
}
```

### **Recommended Full Configuration:**

```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/docker"]
    },
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_pat_here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
        "/Volumes/LegacySafe/SovereignShadow_II"
      ]
    },
    "obsidian": {
      "command": "docker",
      "args": ["run", "-i", "--rm",
        "-v", "/Volumes/LegacySafe/SovereignShadow_II/memory:/vault",
        "mcp/obsidian"
      ]
    }
  },
  "globalShortcut": "CommandOrControl+Shift+Space",
  "appearance": "dark",
  "fontSize": 14
}
```

### **MCP Servers Explained:**

| Server | Purpose | Status |
|--------|---------|--------|
| **docker** | Docker container management | ✅ Active |
| **github** | Git operations, PR management | 🔧 Needs PAT |
| **filesystem** | Project file access | 🔧 Recommended |
| **obsidian** | Memory/session notes | 🔧 Optional |

### **Setup GitHub PAT:**

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Scopes needed: `repo`, `workflow`, `read:org`
4. Copy token to `claude_desktop_config.json`

---

## 📝 **CUSTOM INSTRUCTIONS**

### **Global Instructions** (~/. claude/CLAUDE.md):

Your current instructions are good! Here's an enhanced version:

```markdown
# Claude Desktop - Global Instructions

## About You:
- Username: memphis
- Mac: macOS 25.1.0, 495GB SSD + 2TB "LegacySafe" external drive
- Trading System: Sovereign Shadow II (v2.5a)
- Location: /Volumes/LegacySafe/SovereignShadow_II/

## Trading Setup:
- **Portfolio:** $6,167.43 total
  - AAVE DeFi: $3,494.76 wstETH collateral, $1,158.53 USDC debt
  - BTC Cold Storage: $2,232
  - Health Factor: 2.44 🟠 (WARNING, monitor closely)
- **Exchanges:** Coinbase, OKX, Kraken, Binance US
- **Target Allocation:** BTC 40%, ETH 30%, SOL 20%, XRP 10%

## Critical Rules:
1. **NEVER commit sensitive files:**
   - .env (API keys)
   - *.csv (transaction data)
   - config/*_api*.json (exchange configs)
   - logs/* (runtime data)
   - __pycache__/* (Python bytecode)

2. **ALWAYS use .env.example** as template

3. **File paths:** Use `Path(__file__).parent` for cross-platform compatibility

4. **Commit frequency:** Every 30 minutes during active work (battery/drive safety)

5. **AAVE monitoring:** Check HF if < 2.0, repay immediately

## Current Session Context:
- Latest: CSV security fix (removed 7 transaction files from GitHub)
- Protection suite deployed: Guardian, Dashboard, Risk Calculator, Emergency Repay
- LSETH alert: 8.6% drop (monitoring HF impact)
- Next: Execute deleveraging plan or continue monitoring

## Session Summaries:
- Save to: /Volumes/LegacySafe/SovereignShadow_II/memory/SESSIONS/
- Format: SESSION_YYYY-MM-DD_HHMM_Description.md

## Quick Commands:
```bash
# AAVE Health Check
python3 scripts/aave_health_dashboard.py

# Start Guardian
python3 scripts/aave_guardian_monitor.py

# Emergency Repay
python3 scripts/emergency_aave_repay.py --target-hf 2.5

# Git Status
cd /Volumes/LegacySafe/SovereignShadow_II && git status
```
```

---

## 📁 **FILE MANAGEMENT**

### **What Gets Committed:**

✅ **YES - Commit These:**
```
- Source code (*.py, *.ts, *.tsx, *.js)
- Documentation (*.md)
- Configuration templates (.env.example)
- Package files (package.json, requirements.txt)
- Git files (.gitignore)
- Scripts (bin/*, scripts/*)
```

❌ **NO - Never Commit:**
```
- .env (actual API keys)
- *.csv (transaction data)
- config/*_api*.json (exchange configs)
- logs/* (runtime logs)
- __pycache__/* (Python bytecode)
- node_modules/* (dependencies)
- *.pyc, *.pyo (compiled Python)
- .DS_Store (Mac metadata)
```

### **Current .gitignore Status:** ✅ PROTECTED

Your `.gitignore` already blocks:
- All .env variants
- All *.csv files
- All logs/* files
- All __pycache__/* files
- All config/*_api*.json files
- All *secret*, *api_key*, *credentials* patterns

---

## ⚡ **QUICK COMMANDS**

### **AAVE Monitoring:**
```bash
# Visual dashboard (single check)
python3 scripts/aave_health_dashboard.py

# Continuous watch mode (60s updates)
python3 scripts/aave_health_dashboard.py --watch

# Compact mode (one-line output)
python3 scripts/aave_health_dashboard.py --watch --compact

# 24/7 Guardian monitoring
python3 scripts/aave_guardian_monitor.py

# Risk scenario calculator
python3 scripts/calculate_risk_scenarios.py

# Emergency repay (dry run)
python3 scripts/emergency_aave_repay.py --target-hf 2.5
```

### **Git Operations:**
```bash
# Check status
git status

# Quick commit (every 30 min during work)
git add .
git commit -m "🔄 WIP: Description"
git push origin main

# View recent commits
git log --oneline -5

# Check what's on GitHub
git remote show origin
```

### **Portfolio Checks:**
```bash
# Run portfolio agent
python3 agents/portfolio_agent.py

# Run risk agent
python3 agents/risk_agent.py

# Get real balances
python3 scripts/get_real_balances.py
```

### **System Status:**
```bash
# Check running Python processes
ps aux | grep python

# Check CPU usage
top -l 1 | grep "CPU usage"

# Check disk space
df -h /Volumes/LegacySafe

# Test exchange connections
node tools/test_binance_connection.js
```

---

## 🔧 **TROUBLESHOOTING**

### **Issue: "Rate limit" or "API errors"**

**Solution:**
```bash
# Check API key status
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Coinbase:', os.getenv('COINBASE_API_KEY')[:20] if os.getenv('COINBASE_API_KEY') else 'NOT SET')"

# Test individual exchange
python3 scripts/test_exchange_connection.py coinbase
```

### **Issue: "Module not found"**

**Solution:**
```bash
# Activate venv
cd /Volumes/LegacySafe/SovereignShadow_II
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Issue: "Permission denied"**

**Solution:**
```bash
# Make script executable
chmod +x scripts/aave_guardian_monitor.py

# Or run with python3 explicitly
python3 scripts/aave_guardian_monitor.py
```

### **Issue: "RPC provider error"**

**Solution:**
```bash
# Check .env has RPC keys
grep -E "INFURA|ALCHEMY|ANKR" .env

# Test connection
python3 -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth')); print('Block:', w3.eth.block_number)"
```

### **Issue: "Drive disconnected"**

**Solution:**
1. Check mount: `ls /Volumes/LegacySafe`
2. If missing: Reconnect drive
3. Verify git status: `cd /Volumes/LegacySafe/SovereignShadow_II && git status`
4. Pull latest: `git pull origin main`
5. Resume work (all code is backed up on GitHub)

---

## 🎯 **RECOMMENDED WORKFLOW**

### **Daily Routine:**

**Morning (8 AM):**
```bash
1. python3 scripts/aave_health_dashboard.py
2. python3 agents/portfolio_agent.py
3. python3 agents/risk_agent.py
```

**During Day (Every 30 min):**
```bash
git add .
git commit -m "🔄 WIP: Current work"
git push origin main
```

**Evening (8 PM):**
```bash
1. python3 scripts/aave_health_dashboard.py
2. Review logs: cat logs/guardian/alert_history.json
3. Final commit: git push origin main
```

**Before Sleep:**
- Start Guardian: `python3 scripts/aave_guardian_monitor.py &`
- Set HF alert threshold: Monitor if < 2.0

---

## 📊 **PROJECT STATS**

**Current Deployment:**
- **Files:** 150+ source files
- **Lines of Code:** ~15,000 (Python + TypeScript)
- **Agents:** 5 autonomous systems
- **Protection Tools:** 4 AAVE monitoring scripts
- **Exchanges:** 4 connected (Coinbase, OKX, Kraken, Binance US)
- **Portfolio Value:** $6,167.43
- **GitHub Commits:** 764+ total
- **Latest Push:** November 4, 2025 02:30 AM

**Protection Status:**
- ✅ AAVE Guardian active
- ✅ Emergency repay ready
- ✅ Risk calculator operational
- ✅ Health dashboard deployed
- ✅ All secrets protected
- ✅ CSV files removed from GitHub
- ✅ .gitignore hardened

---

## 🏴 **YOU'RE READY TO TRADE**

**System Status:** ✅ OPERATIONAL
**Security Status:** ✅ MAXIMUM PROTECTION
**Monitoring Status:** ✅ 24/7 ACTIVE
**Backup Status:** ✅ GITHUB SYNCED

**Your Shadow Empire is protected and ready for deployment.**

---

**Need help?** Refer to this guide or ask Claude in your project chat.

**Last Updated:** November 4, 2025 02:30 AM

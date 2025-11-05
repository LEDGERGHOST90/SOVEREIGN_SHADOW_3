# 🏴 SOVEREIGN SHADOW II - MASTER ALIGNMENT DOCUMENT

**Generated:** 2025-11-03
**Purpose:** Align ALL systems across Mobile, Mac, Cursor, Claude Code, and Website
**Status:** ACTIVE DEVELOPMENT

---

## 📊 REPOSITORY OVERVIEW

**Location:** `/home/user/SovereignShadow_II`
**Size:** 112MB
**Branch:** `claude/commit-push-011CUmEfr3xmbKF2s2zuamA5`

### File Count
- **268** Python files
- **47** Shell scripts
- **48** JSON configs
- **5** YAML configs
- **30** Top-level directories

---

## 🗂️ DIRECTORY STRUCTURE

```
SovereignShadow_II/
├── SovereignShadow/          # VES System (Vault-Engine-Siphon)
├── app/                      # Main application code
├── bin/                      # Executable scripts
├── config/                   # Configuration files
├── core/                     # Core trading logic
├── hybrid_system/            # Hybrid trading modules
├── ladder_systems/           # Ladder trading engines
├── launchers/                # System launchers
├── sovereign_legacy_loop/    # Neural orchestrator
├── scripts/                  # Utility scripts
├── modules/                  # Reusable modules
├── monitoring/               # Monitoring systems
├── shadow_sdk/               # SDK utilities
├── infrastructure/           # Infrastructure code
├── docs/                     # Documentation
├── logs/                     # Log files
├── data/                     # Runtime data
├── memory/                   # AI memory storage
└── tools/                    # Development tools
```

---

## 🎯 MAJOR SYSTEMS IDENTIFIED

### 1. **VES System** (Vault-Engine-Siphon)
- **Location:** `SovereignShadow/main.py`
- **Purpose:** Main orchestrator coordinating vault, engine, and siphon
- **Status:** ⚠️ NEEDS CONFIG (`config/ves_architecture.yaml` missing)
- **Dependencies:** python-dotenv, ccxt

### 2. **Neural Orchestrator**
- **Location:** `sovereign_legacy_loop/neural_orchestrator/main.py`
- **Purpose:** AI-driven system coordination
- **Status:** ⚠️ NOT TESTED

### 3. **Trading API Server**
- **Location:** `core/api/trading_api_server.py`
- **Port:** 8000
- **Status:** ✅ RECENTLY STARTED (was running)
- **Endpoints:**
  - Health: `http://localhost:8000/api/health`
  - Strategies: `http://localhost:8000/api/strategy/performance`
  - Execute: `http://localhost:8000/api/trade/execute`
  - Dashboard: `http://localhost:8000/api/dashboard/update`
  - WebSocket: `ws://localhost:8000/ws/dashboard`
  - Docs: `http://localhost:8000/docs`

### 4. **Master Trading Loop**
- **Location:** `launchers/MASTER_TRADING_LOOP.py`
- **Control Script:** `bin/MASTER_LOOP_CONTROL.sh`
- **Status:** ⚠️ NEEDS aiohttp dependency
- **Purpose:** Continuous trading cycle

### 5. **Ladder Trading Systems**
- **Location:** `ladder_systems/>--LadderEngine--cloud< 2/`
- **Components:**
  - Sniper Engine
  - Order Engine
  - Paper Trading Engine
  - Ray Score Engine
  - Simulated Ladder Engine

### 6. **Hybrid System**
- **Location:** `hybrid_system/`
- **Components:**
  - Exchange injection protocol
  - Cold storage siphon
  - Profit tracker
  - Unified portfolio tracker
  - Tiered ladder system

---

## 🔑 API KEYS & CREDENTIALS REQUIRED

**File:** `config/.env` (create from `.env.template`)

### Required APIs:
1. **COINBASE_API_KEY** - Coinbase Advanced Trade
2. **COINBASE_API_SECRET**
3. **OKX_API_KEY** - OKX Exchange
4. **OKX_API_SECRET**
5. **OKX_API_PASSPHRASE**
6. **KRAKEN_API_KEY** - Kraken Exchange
7. **KRAKEN_API_SECRET**
8. **BINANCE_API_KEY** - Binance (optional)
9. **BINANCE_API_SECRET**
10. **ANTHROPIC_API_KEY** - Claude API

### Template Location:
`config/.env.template` - Copy to `config/.env` and fill in

---

## 🚀 ENTRY POINTS & LAUNCHERS

### Primary Launchers:

1. **VES System:**
   ```bash
   python3 SovereignShadow/main.py --mode continuous --interval 15
   ```

2. **Master Loop:**
   ```bash
   ./bin/MASTER_LOOP_CONTROL.sh start paper 60
   ```

3. **API Server:**
   ```bash
   ./bin/START_API_SERVER.sh
   ```

4. **Neural Orchestrator:**
   ```bash
   python3 sovereign_legacy_loop/neural_orchestrator/main.py
   ```

5. **Shadow System Launcher:**
   ```bash
   python3 launchers/SHADOW_SYSTEM_LAUNCHER.py
   ```

6. **Quick Start Empire:**
   ```bash
   ./scripts/quick_start_empire.sh
   ```

---

## 🔧 CONFIGURATION FILES

### Created/Fixed:
- ✅ `config/tactical_scalp_config.json` - Tactical trading config
- ✅ `strategy_knowledge_base.py` - Symlink to core/trading/strategy_knowledge_base.py
- ✅ `bin/MASTER_LOOP_CONTROL.sh` - Fixed hardcoded paths

### Missing/Needed:
- ⚠️ `config/ves_architecture.yaml` - VES system config
- ⚠️ `config/.env` - API credentials (use .env.template)

---

## 📦 DEPENDENCIES

### Python Packages Required:
```bash
pip3 install python-dotenv aiohttp ccxt fastapi uvicorn websockets pydantic
```

### Status:
- ✅ python-dotenv
- ✅ fastapi, uvicorn, websockets, pydantic
- ⚠️ aiohttp - NEEDED for Master Loop
- ⚠️ ccxt - NEEDED for exchange integration

---

## 🔴 CRITICAL ISSUES IDENTIFIED

### 1. Missing Dependencies
- **aiohttp** - Master Loop won't start
- **ccxt** - Exchange connections won't work

### 2. Missing Configs
- **config/ves_architecture.yaml** - VES system won't initialize
- **config/.env** - No API keys configured

### 3. Path Issues
- ✅ **FIXED:** `bin/MASTER_LOOP_CONTROL.sh` hardcoded paths

### 4. Port Conflicts
- **Port 8000** - Trading API Server (was running)
- **Port 3000** - Unknown service (need to check)

---

## ✅ WHAT'S WORKING

1. ✅ Trading API Server can start (has all dependencies)
2. ✅ Path resolution in MASTER_LOOP_CONTROL.sh fixed
3. ✅ Tactical scalp config created
4. ✅ Strategy knowledge base accessible
5. ✅ Git workflow functional (branch pushed)

---

## 🎯 IMMEDIATE ACTIONS NEEDED

### On This Machine (Terminal):
1. Install missing dependencies:
   ```bash
   pip3 install aiohttp ccxt
   ```

2. Create `.env` file:
   ```bash
   cp config/.env.template config/.env
   # Then edit with real API keys
   ```

3. Create VES config (if using VES system)

### On Mac (Cursor):
1. Pull latest from branch: `claude/commit-push-011CUmEfr3xmbKF2s2zuamA5`
2. Review and test all systems
3. Configure API keys in `config/.env`
4. Start systems one by one and verify

### For Mobile/Claude:
1. Reference this document for current state
2. All systems documented above
3. Known issues listed

---

## 🔄 SYNC CHECKLIST

### Before Starting Development:
- [ ] Pull latest code from GitHub
- [ ] Check `SYSTEM_ALIGNMENT_MASTER.md` for updates
- [ ] Verify API keys in `config/.env`
- [ ] Check which systems are running (`ps aux | grep python`)
- [ ] Review recent logs in `logs/`

### After Making Changes:
- [ ] Test changes locally
- [ ] Update this document if structure changes
- [ ] Commit with clear message
- [ ] Push to feature branch
- [ ] Update mobile/Cursor context

---

## 📱 PLATFORM-SPECIFIC NOTES

### Mobile (Claude):
- Use this document as reference
- Can't execute code directly
- Focus on architecture/planning

### Mac (Cursor):
- Full development environment
- Use Cursor's AI features for code generation
- Test all systems here before deploying

### Terminal (Claude Code):
- Execute commands and scripts
- File operations and debugging
- System monitoring and logs

### Website:
- Documentation should mirror this file
- Keep API docs updated
- Maintain system architecture diagrams

---

## 🧠 SYSTEM ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────┐
│     SOVEREIGN SHADOW II ARCHITECTURE        │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │   Trading    │◄────►│  Neural         │ │
│  │   API Server │      │  Orchestrator   │ │
│  │   (Port 8000)│      │                 │ │
│  └──────────────┘      └─────────────────┘ │
│         ▲                      ▲            │
│         │                      │            │
│  ┌──────┴──────────────────────┴──────┐    │
│  │      Master Trading Loop           │    │
│  │      (Continuous Execution)        │    │
│  └────────────────┬───────────────────┘    │
│                   │                         │
│  ┌────────────────┴───────────────────┐    │
│  │         VES System                 │    │
│  │  ┌─────────┐ ┌────────┐ ┌────────┐│    │
│  │  │  Vault  │ │ Engine │ │ Siphon ││    │
│  │  └─────────┘ └────────┘ └────────┘│    │
│  └────────────────────────────────────┘    │
│                   │                         │
│  ┌────────────────┴───────────────────┐    │
│  │    Exchange Connectors             │    │
│  │  [Coinbase][OKX][Kraken][Binance] │    │
│  └────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📞 NEXT STEPS

1. **Install all dependencies**
2. **Configure API keys**
3. **Test each system independently**
4. **Start systems in order:**
   - Trading API Server
   - Master Loop
   - VES System
   - Neural Orchestrator
5. **Monitor logs for errors**
6. **Document any new issues here**

---

**Last Updated:** 2025-11-03
**Maintained By:** Claude Code + Human
**Version:** 1.0

---


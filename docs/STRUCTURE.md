# 📁 SOVEREIGNSHADOW DIRECTORY STRUCTURE

**Root**: `/Volumes/LegacySafe/SovereignShadow`
**Last Organized**: 2025-10-31

---

## 🎯 ROOT LEVEL (Clean & Minimal)

```
SovereignShadow/
├── sovereign_system.py           # Main unified interface
├── autonomous_trading_loop.py    # 24/7 autonomous trading
├── swarm_deployment.py           # Swarm initialization
├── README.md                     # Project documentation
└── .gitignore                    # Protected: APIs, strategies, financial data
```

---

## 📦 ORGANIZED DIRECTORIES

### `modules/` - Core Trading Systems
Modular architecture (slice/build compatible)
```
modules/
├── ladder/                      # Ladder trading systems
│   ├── unified_ladder_system.py
│   └── tiered_ladder_system.py
├── tracking/                    # Profit tracking & injection
│   ├── unified_profit_tracker.py
│   ├── income_capital_tracker.py
│   ├── exchange_injection_protocol.py
│   └── profit_tracker.py
├── safety/                      # Safety & monitoring
│   └── aave_monitor.py
├── execution/                   # Trade execution
│   ├── shadow_sniper_bridge.py
│   └── [other executors]
└── storage/                     # Cold storage management
    ├── cold_storage_siphon.py
    └── optimal_cold_storage_system.py
```

### `hybrid_system/` - Integration Bridges
```
hybrid_system/
├── swarm_intelligence_bridge.py
├── unified_ladder_system.py
├── tiered_ladder_system.py
└── [other bridges]
```

### `scripts/` - Development & Testing
```
scripts/
├── README.md
├── slice.py                     # Module slicer
├── build.py                     # Module builder
├── test_autonomous_cycle.py     # Test autonomous loop
├── test_all_exchanges.py        # Test exchange connectivity
├── test_apis.py                 # Test API credentials
├── setup_exchanges.py           # Configure exchanges
└── [shell scripts]
```

### `launchers/` - System Launchers
```
launchers/
├── MASTER_TRADING_LOOP.py
├── SHADOW_SYSTEM_LAUNCHER.py
├── JANE_STREET_DEPLOYMENT.py
├── TERMINAL_INTERFACE.py
├── CLAUDE_TERMINAL.py
└── DAILY_STATUS_SYSTEM.py
```

### `tools/` - Development Tools
```
tools/
├── live_dashboard.py
├── live_market_scanner.py
├── master_control.py
├── shadow_scope.py
├── demo_shadow_scope.py
├── demo_shadowscope_simple.py
└── [JS tools]
```

### `docs/` - Documentation
```
docs/
├── README.md
├── BATTLE_PLAN.md                    # Development roadmap
├── MASTER_MEMORY.md                  # System orchestration
├── SWARM_IMPLEMENTATION_SUMMARY.md   # Swarm intelligence
├── FILE_ORGANIZATION.md              # File structure guide
└── [other documentation]
```

### `config/` - Configuration Files
```
config/
├── .env.template                # Environment template
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker setup
└── [JSON configs]

⚠️ EXCLUDED FROM GIT:
- .env (actual credentials)
- *api_key*
- *secret*
- *credentials*
```

### `archive/` - Old/Unused Files
```
archive/
├── [old PDF docs]
├── [CSV ledgers]
├── [old integrations]
└── [deprecated scripts]

✅ NEVER COMMITTED TO GIT
```

### `logs/` - System Logs
```
logs/
├── exchange_injections/
├── ladder_trades/
├── profit_tracking/
└── swarm_intelligence/

✅ NEVER COMMITTED TO GIT
```

---

## 🔐 PROTECTED FILES (.gitignore)

### Never Committed:
1. **API Keys & Secrets**
   - `*api_key*`, `*secret*`, `*credentials*`
   - `.env`, `*.pem`, `*.key`

2. **Trading Strategies**
   - `*strategy*.py`, `*strat*.py`
   - `signal_sources/`, `proprietary/`

3. **Financial Data**
   - `*wallet*`, `*balance*`
   - `*portfolio*.json`, `*pnl*.json`

4. **Logs & Runtime**
   - `logs/`, `*.log`
   - `__pycache__/`

---

## 🚀 USAGE

### Development Workflow:
```bash
# 1. Edit modules
cd modules/ladder/
vim unified_ladder_system.py

# 2. Build system
cd ../../scripts
python3 build.py

# 3. Test
python3 test_autonomous_cycle.py

# 4. Deploy
cd ..
python3 swarm_deployment.py
python3 autonomous_trading_loop.py
```

### Quick Commands:
```bash
# From root directory
python3 sovereign_system.py          # Main interface
python3 autonomous_trading_loop.py   # Start autonomous trading
python3 swarm_deployment.py          # Deploy swarms
python3 scripts/build.py             # Rebuild from modules
python3 scripts/test_autonomous_cycle.py  # Test cycle
```

---

## 🔄 SLICE & BUILD SYSTEM

### Slice (Modules → Files):
```bash
cd scripts
python3 slice.py
```
Breaks monolith into organized modules

### Build (Files → System):
```bash
cd scripts
python3 build.py
```
Assembles modules into unified interface

---

## 📊 DIRECTORY SIZES

Core directories only (excludes archives/logs):
- `modules/`: ~150 KB (11 files)
- `hybrid_system/`: ~120 KB
- `scripts/`: ~50 KB
- `docs/`: ~80 KB (markdown)
- `Root (3 files)`: ~60 KB

**Total Active Codebase**: ~460 KB

---

## 🎯 CLEAN ROOT PHILOSOPHY

**Only 3 Python files in root:**
1. `sovereign_system.py` - Main entry point
2. `autonomous_trading_loop.py` - Core autonomous system
3. `swarm_deployment.py` - Swarm initialization

**Everything else organized into directories**

---

## 🐝 EXTERNAL SWARM LOCATIONS

Swarm systems live in separate directory:
```
/Volumes/LegacySafe/SovereignShadow 2/
└── ClaudeSDK/
    └── agents/
        ├── agent_swarm.py
        ├── shadow_army/shadow_swarm.py
        └── hive_mind.py
```

Bridge connects via absolute paths (no duplication needed)

---

## ✅ ORGANIZATION CHECKLIST

- [x] Root directory cleaned (3 Python files only)
- [x] Scripts organized (`scripts/`)
- [x] Docs organized (`docs/`)
- [x] Tools organized (`tools/`)
- [x] Configs protected (`.gitignore`)
- [x] APIs protected (`.gitignore`)
- [x] Strategies protected (`.gitignore`)
- [x] Slice/build tested ✅
- [x] Main system tested ✅
- [x] README created
- [x] Structure documented

---

**Status**: ✅ Fully Organized & Production Ready

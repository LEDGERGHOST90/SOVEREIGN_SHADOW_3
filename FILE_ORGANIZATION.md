# 📁 SOVEREIGNSHADOW FILE ORGANIZATION
**Last Updated**: 2025-10-31 01:15 UTC

---

## 🗂️ DIRECTORY STRUCTURE

### Primary Repository: `/Volumes/LegacySafe/SovereignShadow`
**Status**: ✅ Active development, pushed to GitHub (SovereignShadow_II)

```
SovereignShadow/
├── modules/
│   ├── ladder/
│   │   ├── unified_ladder_system.py          [CANONICAL]
│   │   └── tiered_ladder_system.py           [CANONICAL]
│   ├── tracking/
│   │   └── exchange_injection_protocol.py    [CANONICAL - Latest v2.5a]
│   └── safety/
│       └── aave_monitor.py
├── hybrid_system/
│   └── swarm_intelligence_bridge.py          [CANONICAL]
├── swarm_deployment.py                       [NEW - v2.5a]
├── autonomous_trading_loop.py                [NEW - v2.5a]
├── test_autonomous_cycle.py                  [NEW - v2.5a]
├── sovereign_system.py                       [Main entry point]
├── BATTLE_PLAN.md                           [Updated with swarm]
├── MASTER_MEMORY.md                         [Updated with assets]
└── SWARM_IMPLEMENTATION_SUMMARY.md          [NEW - Documentation]
```

---

### Secondary Directory: `/Volumes/LegacySafe/SovereignShadow 2`
**Status**: ⚠️ Legacy/Reference files, Swarm systems location

```
SovereignShadow 2/
├── ClaudeSDK/
│   └── agents/
│       ├── agent_swarm.py                    [Swarm System 1]
│       ├── shadow_army/
│       │   └── shadow_swarm.py              [Swarm System 2]
│       └── hive_mind.py                     [Swarm System 3]
├── SwarmAgents/
│   └── core/
│       └── hive_mind.py                     [Hive Mind alternate]
├── ladder_systems/
│   └── TradeBrain/                          [Trade execution engine]
├── hybrid_system/
│   ├── exchange_injection_protocol.py → [SYMLINK to SovereignShadow]
│   ├── exchange_injection_protocol.py.old_v2.5  [Backup - Oct 30]
│   ├── swarm_intelligence_bridge.py        [Same as primary]
│   ├── unified_ladder_system.py            [Same as primary]
│   └── tiered_ladder_system.py             [Same as primary]
└── logs/                                    [Shared with primary]
```

---

## 🔗 FILE RELATIONSHIPS

### Canonical Files (Single Source of Truth):

#### 1. **exchange_injection_protocol.py**
- **Location**: `SovereignShadow/modules/tracking/`
- **Size**: 19KB
- **Last Updated**: Oct 31 00:49 (Today - with 120min cache, BTC, wstETH)
- **Linked From**: `SovereignShadow 2/hybrid_system/` (symlink)
- **Old Version**: `SovereignShadow 2/hybrid_system/exchange_injection_protocol.py.old_v2.5` (14KB, Oct 30)

#### 2. **swarm_intelligence_bridge.py**
- **Location**: `SovereignShadow/hybrid_system/`
- **Duplicate**: `SovereignShadow 2/hybrid_system/swarm_intelligence_bridge.py` (identical)
- **Purpose**: Aggregates P&L from all swarm systems

#### 3. **unified_ladder_system.py**
- **Location**: `SovereignShadow/modules/ladder/`
- **Duplicate**: `SovereignShadow 2/hybrid_system/unified_ladder_system.py` (identical)
- **Size**: 16376 bytes

#### 4. **tiered_ladder_system.py**
- **Location**: `SovereignShadow/modules/ladder/`
- **Duplicate**: `SovereignShadow 2/hybrid_system/tiered_ladder_system.py` (identical)
- **Size**: 20120 bytes

---

## 🐝 SWARM SYSTEM LOCATIONS

### Agent Swarm
- **Path**: `SovereignShadow 2/ClaudeSDK/agents/agent_swarm.py`
- **P&L Data**: `SovereignShadow 2/ClaudeSDK/agents/agent_swarm_pnl.json`
- **Strategy**: Consensus-based coordination (60% threshold)

### Shadow Army
- **Path**: `SovereignShadow 2/ClaudeSDK/agents/shadow_army/shadow_swarm.py`
- **P&L Data**: `SovereignShadow 2/ClaudeSDK/agents/shadow_army/shadow_army_pnl.json`
- **Strategy**: Competitive learning (5 agent types)

### Hive Mind
- **Path 1**: `SovereignShadow 2/SwarmAgents/core/hive_mind.py`
- **Path 2**: `SovereignShadow 2/ClaudeSDK/agents/hive_mind.py`
- **P&L Data**: `SovereignShadow 2/SwarmAgents/hive_mind_pnl.json`
- **Strategy**: 6 specialized agents with 67% voting

---

## 🔄 IMPORT PATHS

### From `sovereign_system.py`:
```python
from ladder import UnifiedLadderSystem, TieredLadderSystem
from tracking import InjectionManager
from safety import AAVEMonitor
```

### From `autonomous_trading_loop.py`:
```python
from ladder import UnifiedLadderSystem, TieredLadderSystem
from tracking import InjectionManager
from hybrid_system.swarm_intelligence_bridge import SwarmIntelligenceBridge
```

### From `swarm_intelligence_bridge.py`:
```python
# Reads from SovereignShadow 2:
agent_swarm_data = swarm_root / "ClaudeSDK" / "agents" / "agent_swarm_pnl.json"
shadow_army_data = swarm_root / "shadow_army" / "shadow_army_pnl.json"
hive_mind_data = sovereign_root / "SwarmAgents" / "hive_mind_pnl.json"
```

---

## 📊 LOG FILE LOCATIONS

### Primary Logs: `/Volumes/LegacySafe/SovereignShadow/logs/`
- Exchange injections (5 platforms)
- Unified profit tracking
- Tiered extraction events
- AAVE health monitoring

### Secondary Logs: `/Volumes/LegacySafe/SovereignShadow 2/logs/`
- Swarm P&L data
- Swarm intelligence bridge output
- Agent performance metrics
- Historical trades (if any)

**Note**: Logs are periodically synced between directories

---

## ✅ DUPLICATE RESOLUTION

### Actions Taken:
1. ✅ Renamed old `exchange_injection_protocol.py` to `.old_v2.5` in SovereignShadow 2
2. ✅ Created symlink from SovereignShadow 2 → SovereignShadow canonical version
3. ✅ Verified `unified_ladder_system.py` identical (no action needed)
4. ✅ Verified `tiered_ladder_system.py` identical (no action needed)
5. ✅ Documented file organization in this file

### Recommendations:
- **Keep**: SovereignShadow as primary development repository
- **Reference**: SovereignShadow 2 for swarm systems and TradeBrain
- **Sync**: Periodically sync logs/ directory between both
- **Backup**: Old versions renamed with `.old_v2.5` suffix

---

## 🚀 DEPLOYMENT NOTES

### When Running Systems:
1. **Working Directory**: `/Volumes/LegacySafe/SovereignShadow`
2. **Swarm Data Location**: `/Volumes/LegacySafe/SovereignShadow 2/ClaudeSDK/`
3. **Bridge**: Automatically finds swarm data via absolute paths
4. **Imports**: All imports resolve to `SovereignShadow/modules/`

### Environment Variables (if needed):
```bash
export SOVEREIGN_ROOT="/Volumes/LegacySafe/SovereignShadow"
export SWARM_ROOT="/Volumes/LegacySafe/SovereignShadow 2/ClaudeSDK/agents"
export LOGS_PATH="/Volumes/LegacySafe/SovereignShadow/logs"
```

---

## 📦 GITHUB REPOSITORY

**Repo**: https://github.com/LEDGERGHOST90/SovereignShadow_II
**Branch**: main
**Latest Commit**: a40477b (Swarm Intelligence implementation)

**Contents**:
- All files from `/Volumes/LegacySafe/SovereignShadow`
- Does NOT include `/Volumes/LegacySafe/SovereignShadow 2` files
- Swarm systems referenced by path but not included in repo

---

## 🔧 MAINTENANCE

### To Sync Changes:
```bash
# If updating files in SovereignShadow 2
cd "/Volumes/LegacySafe/SovereignShadow 2/hybrid_system"
ls -la exchange_injection_protocol.py  # Should show symlink

# If symlink broken
rm exchange_injection_protocol.py
ln -s "../../../SovereignShadow/modules/tracking/exchange_injection_protocol.py" exchange_injection_protocol.py
```

### To Update Duplicates:
1. Edit canonical file in `SovereignShadow/modules/`
2. Symlink or identical copy will auto-update
3. Commit to GitHub from `SovereignShadow` directory

---

**Status**: ✅ File organization documented and duplicates resolved

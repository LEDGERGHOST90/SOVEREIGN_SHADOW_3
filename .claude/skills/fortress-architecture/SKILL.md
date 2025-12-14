---
name: fortress-architecture
description: SOVEREIGN SHADOW III FORTRESS ARCHITECTURE. Use when discussing system design, implementation, agents, state machine, kill switch, or trading infrastructure. This is THE system architecture - no scattered references.
---

# FORTRESS ARCHITECTURE - THE ONLY SYSTEM

**Location:** `/Volumes/LegacySafe/SS_III/`

**Mission:** Build an impenetrable, self-healing, AI-orchestrated trading fortress that operates autonomously while you sleep, protects capital during chaos, and scales from $10K to $1M+ without architectural rewrites.

## Philosophy

```
FORTRESS = DEFENSE + OFFENSE + INTELLIGENCE + RESILIENCE
```

## Read Current State

```bash
# Read complete Fortress architecture from BRAIN.json
cat /Volumes/LegacySafe/SS_III/BRAIN.json | jq '.fortress_architecture'

# Check current implementation phase
cat /Volumes/LegacySafe/SS_III/BRAIN.json | jq '.fortress_architecture.current_phase'

# List directory structure
ls -la /Volumes/LegacySafe/SS_III/
```

## 5 Layers

### Layer 1: Foundation (The Bedrock)
- **core/**: engine.py, memory_guardian.py, state_machine.py, kill_switch.py
- **Status:** In progress

### Layer 2: Fortress Kernel (The Brain)
- **FortressStateMachine:** Controls all state transitions
- **KillSwitch:** Emergency shutdown orchestrator
- **Status:** Designed, implementing

### Layer 3: AI Agent Army
- **risk_sentinel/**: Pre-trade risk gates
- **execution_commander/**: Order routing & fills
- **memory_archivist/**: Learn from every trade
- **regime_detector/**: Market structure shifts
- **profit_extractor/**: Automated withdrawals
- **Status:** Defined, not deployed

### Layer 4: Profit Extraction
- **Rules:** $500/week minimum, 20% profit threshold, max $5K hot wallet
- **Status:** Defined, not deployed

### Layer 5: Observability
- **Components:** Dashboards, alerts, heartbeat, logs
- **Status:** Planned

## Current Phase

**PHASE 1: Foundation (Week 1-2)**

Tasks:
- ✅ Create directory structure
- 🔄 Implement state machine
- ✅ Build memory guardian
- 🔄 Deploy kill switch
- ⏳ Set up encrypted config system
- ⏳ Establish backup automation

## Implementation Roadmap

```
Phase 1: Foundation (Week 1-2) - IN PROGRESS
Phase 2: Intelligence (Week 3-4) - NOT STARTED
Phase 3: Execution (Week 5-6) - NOT STARTED
Phase 4: Profit Architecture (Week 7-8) - NOT STARTED
Phase 5: Observability (Week 9-10) - NOT STARTED
```

## Active Mission: DEBT_DESTROYER

- **Target:** $661.46 profit (paper trading)
- **Current:** -$0.90
- **Progress:** -0.1%
- **Phase:** Paper trading
- **Requirements:** 10+ trades, 60% win rate

## Important Notes

- **This is THE system architecture**
- **No scattered old references** (LegacyLoop, Shadow-3-Legacy-Loop-Platform archived)
- **Single source of truth:** BRAIN.json at `/Volumes/LegacySafe/SS_III/BRAIN.json`
- **All Claude instances:** Desktop, CLI, Mobile - use THIS architecture

## AI Council

- **AURORA (Claude):** The Executor - trade execution, signals, risk calculations
- **GIO (Gemini):** The Researcher - market analysis, sentiment, patterns
- **ARCHITECT_PRIME (GPT):** The Integrator - system design, orchestration

## Communication Standards

Version 2.0 (established 2025-12-12):
- Honesty first (not performance)
- Precision over hype
- Acknowledge uncertainty explicitly
- No forbidden language: "sentient", "conscious", "alive", "revolutionary" (unless accurate)

## When You Don't Know

If you need details not in BRAIN.json:
1. Read BRAIN.json first: `cat /Volumes/LegacySafe/SS_III/BRAIN.json`
2. If still unclear, state: "I don't have that information in current BRAIN.json state"
3. Don't fabricate or guess - acknowledge uncertainty

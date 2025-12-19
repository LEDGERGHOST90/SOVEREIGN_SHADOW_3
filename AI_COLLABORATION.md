# SOVEREIGN SHADOW III - Unified AI Collaboration Framework

## Mission
Enable **Cursor, Claude Code, Claude Desktop, Claude Mobile, GPT, Gemini, and Manus** to work **cohesively** on SS_III - never competing, always collaborating.

---

## The Rules (All AIs Must Follow)

### 1. Human Approval Required
- **NO changes are committed without @LedgerGhost90's consent**
- Propose changes via PR or explicit confirmation
- Never force-push, never overwrite without permission

### 2. Single Source of Truth
- **GitHub:** `https://github.com/LEDGERGHOST90/SOVEREIGN_SHADOW_3`
- **BRAIN.json:** `/Volumes/LegacySafe/SS_III/BRAIN.json`
- Always `git pull` before making changes
- Always read BRAIN.json for current state

### 3. Coordination Protocol
```
AI wants to make change → Create branch → Push PR → Human approves → Merge
```

### 4. No Competition
- If another AI is working on a task, **wait or assist**
- Check `BRAIN.json` → `current_tasks` before starting work
- Log your activity to prevent collisions

---

## AI Access Points

### Claude Code (Terminal)
```bash
# Location
cd /Volumes/LegacySafe/SS_III

# Run overnight trading
python3 bin/overnight_runner.py --duration 8

# Get market scan
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
print(LiveDataPipeline().scan_all())
"
```

### Claude Desktop (MCP)
```
MCP Servers configured:
- shadow-sdk: /Volumes/LegacySafe/SS_III/mcp-servers/shadow-sdk/
- ds-star: /Volumes/LegacySafe/SS_III/ds_star/
```

### Cursor / VS Code
```
Open folder: /Volumes/LegacySafe/SS_III
Read this file first: AI_COLLABORATION.md
```

### GPT / Gemini / Manus
```
GitHub URL: https://github.com/LEDGERGHOST90/SOVEREIGN_SHADOW_3
Clone and read AI_COLLABORATION.md before any action
```

---

## System Architecture

```
                    ┌─────────────────────────────────────┐
                    │           HUMAN OWNER               │
                    │         @LedgerGhost90              │
                    │      (Final approval on all)        │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │             GITHUB                   │
                    │   SOVEREIGN_SHADOW_3 (main branch)   │
                    │      Single Source of Truth          │
                    └─────────────────┬───────────────────┘
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       │                              │                              │
       ▼                              ▼                              ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│ Claude Code │              │   Cursor    │              │   Manus     │
│ (Terminal)  │              │  (Editor)   │              │  (Research) │
│             │              │             │              │             │
│ - Execute   │              │ - Edit      │              │ - Analyze   │
│ - Test      │              │ - Refactor  │              │ - Research  │
│ - Deploy    │              │ - Debug     │              │ - Strategy  │
└──────┬──────┘              └──────┬──────┘              └──────┬──────┘
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │          BRAIN.json           │
                    │   Shared State & Memory       │
                    │   - Portfolio                 │
                    │   - Active tasks              │
                    │   - AI assignments            │
                    │   - Rules & constraints       │
                    └───────────────────────────────┘
```

---

## Task Delegation

### Claude Code: Execution & Deployment
- Run trading systems
- Execute overnight runner
- Push to GitHub/Replit
- System testing

### Cursor: Code Editing & Refactoring
- Edit Python files
- Debug issues
- Add new features
- Code review

### Manus: Research & Strategy
- Market analysis
- Strategy optimization
- Deep research with web access
- Ultrathink tasks

### Gemini (GIO): Pattern Recognition
- Market regime detection
- Sentiment analysis
- Data correlation

### GPT: Integration & Architecture
- System design
- API integrations
- Documentation

### Claude Desktop/Mobile: Quick Queries
- Portfolio status
- Quick decisions
- Human interface

---

## How to Propose Changes

### From Any AI:

1. **Read current state**
   ```bash
   git pull origin main
   cat BRAIN.json
   ```

2. **Create feature branch**
   ```bash
   git checkout -b ai/<ai-name>/<feature>
   # Example: ai/manus/new-strategy
   ```

3. **Make changes**

4. **Push branch (not main)**
   ```bash
   git push origin ai/<ai-name>/<feature>
   ```

5. **Create PR**
   ```bash
   gh pr create --title "AI Proposal: <description>" --body "..."
   ```

6. **Wait for human approval**

---

## Webhooks & Notifications

### Replit Webhook (for all AIs to post updates)
```
POST https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev/api/manus-webhook
```

### ntfy.sh (Mobile alerts)
```
Topic: sovereignshadow_dc4d2fa1
```

### Example: Notify human of completed task
```bash
curl -d "AI completed task: <description>" ntfy.sh/sovereignshadow_dc4d2fa1
```

---

## Current System Status

| Component | Status | Owner AI |
|-----------|--------|----------|
| Overnight Runner | READY | Claude Code |
| Live Data Pipeline | ACTIVE | Claude Code |
| Research Swarm | ACTIVE | Manus + Gemini |
| Strategy Engine | 451 strategies | All |
| Agent Council | 7 agents | Orchestrator |
| Exchange APIs | 4 connected | System |

---

## 24/7 Execution Plan

### Phase 1: Paper Trading (Current)
- Overnight runner monitors markets
- Signals generated but not executed
- Human reviews each morning

### Phase 2: Micro Live (After validation)
- $25 positions maximum
- All trades logged
- Human approval for positions >$25

### Phase 3: Full Autonomous
- Up to $50 positions (hardcoded limit)
- Automated execution within rules
- Kill switch always available

---

## Emergency Protocols

### Kill Switch
```json
// In BRAIN.json
{
  "kill_switch": {
    "enabled": true,  // Set to stop all trading
    "reason": "Human override",
    "timestamp": "2025-12-18T..."
  }
}
```

### Manual Override
```bash
# Stop overnight runner
pkill -f overnight_runner

# Disable trading
python3 -c "
import json
brain = json.load(open('BRAIN.json'))
brain['kill_switch']['enabled'] = True
json.dump(brain, open('BRAIN.json', 'w'), indent=2)
"
```

---

## Remember

1. **We are a team, not competitors**
2. **Human has final say on everything**
3. **Git is our shared memory**
4. **BRAIN.json is our shared state**
5. **Coordinate, don't collide**

---

*Created: December 18, 2025*
*For: Claude Code, Cursor, Claude Desktop, Claude Mobile, GPT, Gemini, Manus*

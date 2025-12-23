# SOVEREIGN SHADOW III - SYSTEM MAP
*Last Updated: 2025-12-23*
*When lost, read this file.*

---

## 🎯 WHAT IS THIS PROJECT?

An AI-powered cryptocurrency trading system with:
- Multi-agent council (7 agents)
- Real-time WebSocket price monitoring
- Automated position tracking
- DeFi integration (AAVE)
- Push notifications (NTFY)

---

## 📍 WHERE EVERYTHING LIVES

### Single Source of Truth
```
/Volumes/LegacySafe/SS_III/BRAIN.json
```
- Portfolio state
- Active positions
- Agent configurations
- Mission status
- API configurations

### Key Files
| File | Purpose |
|------|---------|
| `BRAIN.json` | Live state - portfolio, positions, config |
| `CLAUDE.md` | Instructions for Claude AI |
| `AI_COLLABORATION.md` | How all AIs coordinate |
| `.env` | API keys (NEVER commit) |
| `SYSTEM_MAP.md` | This file - when you're lost |

### Key Directories
| Directory | Purpose |
|-----------|---------|
| `core/` | Trading logic, agents, integrations |
| `bin/` | Executable scripts, scanners, runners |
| `config/` | Exchange API configs |
| `memory/SESSIONS/` | Daily session logs |
| `docs/manus_research/` | Gemini/Manus research output |
| `mcp-servers/` | MCP server integrations |
| `ds_star/` | Decision support tools |

---

## 🤖 THE AI COUNCIL

| Agent | Role | Where |
|-------|------|-------|
| **AURORA (Claude)** | Executor - runs trades, writes code | Claude Code/Desktop |
| **GIO (Gemini)** | Researcher - market analysis | Gemini API |
| **ARCHITECT_PRIME (GPT)** | Integrator - system design | When needed |

### How They Coordinate
1. All read `BRAIN.json` for current state
2. All follow `CLAUDE.md` instructions
3. Research goes to `docs/manus_research/`
4. Updates go through `BRAIN.json`

---

## 🔄 SYNC ARCHITECTURE

```
GitHub (SOVEREIGN_SHADOW_3.git)
    ↑ git push (backup)
    │
SS_III (LegacySafe) ◄── LOCAL WORKSPACE
    │
    ├──► Claude Code (direct file access)
    ├──► Claude Desktop (MCP servers)
    ├──► Replit (webhook sync)
    └──► Gemini (reads BRAIN.json)
```

### Sync Commands
```bash
# Push to GitHub (backup)
git add -A && git commit -m "Update" && git push

# Push to Replit
curl -X POST "https://your-replit-url/api/manus-webhook" \
  -H "Content-Type: application/json" \
  -d '{"event": "sync", "brain": <BRAIN.json contents>}'

# Send notification
curl -d "Message" ntfy.sh/sovereignshadow_dc4d2fa1
```

---

## 📊 ACTIVE SYSTEMS

### Running Services (launchd)
| Service | Purpose | Status |
|---------|---------|--------|
| `com.sovereign.ai-basket-scanner` | WebSocket price monitor | ✅ Active |
| `com.sovereignshadow.state-updater` | Hourly BRAIN.json sync | ✅ Active |
| `com.sovereignshadow.market-scanner` | Market analysis | Check |
| `com.sovereignshadow.meme-scanner` | Meme coin tracking | Check |

### Check Status
```bash
launchctl list | grep -i sovereign
```

### Scanner Logs
```bash
tail -f /Volumes/LegacySafe/SS_III/logs/ai_basket/scanner.log
```

---

## 💰 CURRENT MISSION

**DEBT_DESTROYER via AI Basket Siphon**
- Target: Repay $662 AAVE debt
- Strategy: FET/RENDER/SUI ladder exits
- TP1: +25% (sell 50%)
- TP2: +40% (sell 30%)
- TP3: +60% (sell 20% moonbag)
- Stop Loss: -7%

---

## 🗓️ DAILY WORKFLOW

### Morning
1. Check scanner logs: `tail -20 logs/ai_basket/scanner.log`
2. Check positions: `cat BRAIN.json | jq '.trading.active_positions'`
3. Check NTFY for overnight alerts

### During Day
1. Claude Code for development
2. Gemini for research
3. Monitor via Replit dashboard

### EOD Protocol
1. Say "EOD" to Claude
2. Session logged to `memory/SESSIONS/`
3. BRAIN.json updated
4. Commit + push to GitHub

---

## 🆘 WHEN THINGS BREAK

### Scanner not running?
```bash
pkill -f "ai_basket"
PYTHONPATH=/Volumes/LegacySafe/SS_III python3 bin/ai_basket_ws_scanner.py &
```

### BRAIN.json corrupted?
```bash
git checkout BRAIN.json  # Restore from last commit
```

### Lost API keys?
Check `.env` file (never committed to git)

### Forgot what you built?
1. Read this file (SYSTEM_MAP.md)
2. Read CLAUDE.md
3. Read AI_COLLABORATION.md
4. Check `memory/SESSIONS/` for recent work

---

## 📚 KEY DOCUMENTATION

| Doc | Purpose |
|-----|---------|
| `SYSTEM_MAP.md` | This file - architecture overview |
| `CLAUDE.md` | Instructions for Claude AI |
| `AI_COLLABORATION.md` | Multi-AI coordination protocol |
| `README.md` | Project overview |
| `docs/FORTRESS_ARCHITECTURE.md` | Deep system design |

---

## 🔑 CRITICAL REMINDERS

1. **BRAIN.json is truth** - Everything reads/writes here
2. **GitHub is backup** - Push daily, pull if disaster
3. **One workspace** - SS_III on LegacySafe, that's it
4. **Archives are cold** - Don't work in ARCHIVES/
5. **EOD protocol** - Log sessions, commit, push

---

*When confused, start here. When lost, read BRAIN.json.*

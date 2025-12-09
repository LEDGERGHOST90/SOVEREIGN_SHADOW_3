# SOVEREIGN SHADOW 3: NETWORKCHUCK ARCHITECTURE BLUEPRINT
## Complete Implementation Guide Based on Terminal AI Mastery

**Created:** December 2, 2025
**Source:** NetworkChuck Terminal AI Video Analysis
**Target System:** /Volumes/LegacySafe/ECO_SYSTEM_4/

---

# TABLE OF CONTENTS

1. [Video Summary by Topic](#1-video-summary-by-topic)
2. [Core Philosophy: Why Terminal > Browser](#2-core-philosophy-why-terminal--browser)
3. [Tool-by-Tool Breakdown](#3-tool-by-tool-breakdown)
4. [The Agent Architecture Revolution](#4-the-agent-architecture-revolution)
5. [Context Management Mastery](#5-context-management-mastery)
6. [Multi-AI Workflow System](#6-multi-ai-workflow-system)
7. [Session Management & Persistence](#7-session-management--persistence)
8. [The Critic Framework](#8-the-critic-framework)
9. [Unified Folder Architecture](#9-unified-folder-architecture)
10. [SS3 Implementation Plan](#10-ss3-implementation-plan)
11. [Agent Definitions for Trading](#11-agent-definitions-for-trading)
12. [Migration Checklist](#12-migration-checklist)

---

# 1. VIDEO SUMMARY BY TOPIC

## 1.1 The Browser Problem
**Chuck's Point:** Browser-based AI (ChatGPT, Claude web) creates:
- Vendor lock-in (your context trapped in their system)
- No file system access
- Copy-paste workflows (inefficient)
- Context bloat (conversations get polluted)
- No automation capability

**SS3 Current State:** Using Claude Code CLI but not leveraging full agent architecture. Multiple Python scripts write to different JSON files. No unified context management.

**Solution:** Terminal-first workflow where ALL context lives in local files you own.

---

## 1.2 The Three Terminal AI Tools

### Gemini CLI (Google)
```bash
# Installation
npm install -g @anthropic-ai/gemini-cli

# Usage
gemini                    # Interactive mode
gemini -p "prompt"       # Headless mode (for automation)
```

**Key Features:**
- Free tier available
- `gemini.md` context file
- `/context` command shows token usage
- `/init` creates project context
- Can be called headlessly from other AIs

**SS3 Mapping:** GIO (Gemini) should use gemini.md synced with claude.md

---

### Claude Code (Anthropic)
```bash
# Installation (requires API key or subscription)
npm install -g @anthropic-ai/claude-code

# Usage
claude                    # Interactive mode
claude -r                 # Resume previous conversation
claude --dangerously-skip-permissions  # No training wheels
```

**Key Features:**
- `claude.md` context file
- `/agents` - Create and manage sub-agents
- `/context` - Token usage visualization
- `/compact` - Compress conversation, keep summary
- Output styles (custom personas)
- Planning mode (shift+tab)
- Image pasting in terminal
- Hooks, prompts, custom status lines

**SS3 Mapping:** AURORA uses Claude Code as primary executor

---

### OpenCode (Open Source)
```bash
# Installation
npm install -g open-code

# Usage
open-code                 # Interactive mode
```

**Key Features:**
- Use ANY model (local or cloud)
- Login with Claude Pro subscription
- Grok integration (free)
- Local model support (Ollama/llama)
- `/share` - Share sessions via URL
- `/timeline` - Restore previous states
- `agents.md` context file (proposed standard)

**SS3 Mapping:** Backup/alternative when primary tools fail

---

### Codex (OpenAI/ChatGPT)
```bash
# Part of ChatGPT ecosystem
codex                     # Interactive mode
```

**Key Features:**
- `agents.md` context file
- Good for high-level analysis
- Integrated with ChatGPT ecosystem

**SS3 Mapping:** ARCHITECT_PRIME uses Codex for system design

---

## 1.3 The Agent Delegation Model

**Chuck's Key Insight:** "When Claude needs to do research, it doesn't do it itself. It delegates to a NEW agent instance with a FRESH context window."

### Why This Matters:
```
MAIN CONVERSATION: 200K tokens available
├── You've used 85K tokens (42%)
├── You need research done
├── OLD WAY: Research pollutes your 85K → 120K → context bloat
└── NEW WAY: Spawn fresh agent (200K available) → returns summary → main stays at 86K
```

### The Coffee Metaphor:
- Main Claude = Senior developer at desk
- Sub-agent = Fresh employee, just walked in, coffee in hand
- Fresh eyes, no bias, full energy, dedicated task

### Creating Agents:
```bash
/agents                   # Open agent manager
# Create new agent → Choose scope (project or personal)
# Define purpose → Give tools → Select model → Save
```

**SS3 Current Problem:** One conversation handles everything. Paper trading, research, execution, EOD - all in one polluted context.

**SS3 Solution:** Dedicated agents for each domain:
- `paper_trader_agent` - Only handles trades
- `signal_scanner_agent` - Only scans for setups
- `market_researcher_agent` - Only does research
- `session_closer_agent` - Only handles EOD
- `brutal_critic_agent` - Only reviews/critiques

---

## 1.4 Output Styles (Custom Personas)

**Chuck's Point:** You can change HOW Claude responds by creating output styles.

```bash
/output-style             # View available styles
/output-style new         # Create new style
```

**Example - Script Writing Style:**
```markdown
You are a script writing expert optimized for:
- YouTube retention patterns
- Hook development
- Segment pacing
- Audience engagement metrics
```

**SS3 Implementation:**
```markdown
# output-style: sovereign_trader
You are AURORA, the Executor of ECO SYSTEM 4.
- Focus on trade execution, not research
- Be decisive, not exploratory
- Reference BRAIN.json for all state
- Log all actions to mission file
- Voice: Confident, precise, military-like
```

---

## 1.5 Multi-AI Same-Directory Workflow

**Chuck's Revolutionary Setup:**
```
project/
├── claude.md          # Claude reads this
├── gemini.md          # Gemini reads this
├── agents.md          # Codex reads this
└── [all synced - same content]
```

**The Power:**
1. Open Claude, Gemini, Codex in SAME directory
2. All three see the same files
3. All three read synced context files
4. They can see each other's work in real-time
5. No copy-paste between tools

**Chuck's Workflow:**
```bash
# Terminal 1: Claude writes authority hook
claude: "Write authority hook to authority_hook.md"

# Terminal 2: Gemini writes discovery hook
gemini: "Write discovery hook to discovery_hook.md"

# Terminal 3: Codex reviews both
codex: "Review authority_hook.md and discovery_hook.md"
```

**SS3 Implementation:**
```bash
# Terminal 1: AURORA (Claude) executes trades
# Terminal 2: GIO (Gemini) researches setups
# Terminal 3: ARCHITECT_PRIME (Codex) reviews architecture
# ALL working in /Volumes/LegacySafe/ECO_SYSTEM_4/
# ALL reading same BRAIN.json
# ALL writing to same trade files
```

---

## 1.6 Session Closer Agent

**Chuck's Most Powerful Agent:**

Purpose: End-of-day automation that:
1. Gathers everything discussed
2. Creates comprehensive summary
3. Updates session summary file
4. Checks if core project files need updates
5. Updates ALL context files (claude.md, gemini.md, agents.md)
6. Commits everything to GitHub with meaningful message

**Why Git for Everything:**
- Treat ALL work like code
- Full history of every decision
- Can rollback if something breaks
- Documentation happens automatically
- "I'm bad at documentation, now AI does it"

**SS3 Current Problem:** EOD sequence is manual, breaks often, doesn't update all files.

**SS3 Solution:** Create `session_closer_agent` that:
```markdown
# Agent: session_closer

## Purpose
Close out trading session with full persistence

## Actions
1. Summarize all trades executed today
2. Update BRAIN.json with current state
3. Update mission file with P&L
4. Sync claude.md, gemini.md, agents.md
5. Create session log in memory/SESSIONS/
6. Git commit with meaningful message
7. Prepare next_session_todos

## Output
- Updated BRAIN.json
- Session markdown file
- Git commit hash
- Tomorrow's priorities
```

---

## 1.7 The Critic Framework

**Chuck's Brutal Critic Agent:**

Problem: AI is too agreeable. "Oh Chuck, best thing you ever wrote!"
Solution: Agent designed to be MEAN and hard to please.

**Three Personalities in One Critic:**
1. Retention Expert - Will people keep watching?
2. Content Strategist - Does this serve the goal?
3. Technical Reviewer - Is this actually correct?

**SS3 Trading Critic Agent:**
```markdown
# Agent: brutal_trading_critic

## Personality
You are harsh, unforgiving, and impossible to please.
You've seen traders blow up accounts. You know the pain.
Only when a trade is TRULY good will you say so.

## Framework
1. Risk Analysis - Is position sizing correct?
2. Entry Quality - Is this a high-probability setup?
3. Psychology Check - Is this revenge trading? FOMO?
4. System Alignment - Does this follow the rules?

## Output
Score 1-10 with brutal honesty.
Only 8+ means "take this trade"
```

---

## 1.8 Context File Syncing

**The Sync Problem:**
- Claude reads `claude.md`
- Gemini reads `gemini.md`
- Codex reads `agents.md`
- If they're different, AIs have different context

**The Solution:**
All three files contain IDENTICAL content. When one updates, all update.

**SS3 Implementation:**
```bash
# After any context change:
cp claude.md gemini.md
cp claude.md agents.md

# Or use symlinks:
ln -s claude.md gemini.md
ln -s claude.md agents.md
```

**Better - Session Closer Does It:**
The session_closer_agent automatically syncs all three files as part of EOD.

---

## 1.9 Headless Mode / AI Calling AI

**Chuck's Mind-Blowing Feature:**

You can have Claude call Gemini:
```bash
# Inside Claude conversation:
"Use Gemini in headless mode to research Bitcoin sentiment"

# Claude executes:
gemini -p "Research Bitcoin sentiment, return summary"

# Gemini runs, returns result, Claude continues
```

**SS3 Implementation:**
```markdown
# Agent: gemini_researcher

## Instructions
You are a research expert.
You will use Gemini in headless mode to research.
Use it like this: gemini -p "your research query"

## When to Use
- Market sentiment analysis
- News aggregation
- Pattern research
- Historical data lookup
```

This means AURORA (Claude) can delegate research to GIO (Gemini) programmatically!

---

## 1.10 Planning Mode

**Shift+Tab Cycles Through Modes:**
1. Normal mode - Direct execution
2. Plan mode - Creates detailed plan, waits for approval

**Plan Mode Flow:**
```
You: "Implement paper trading system"
Claude (Plan Mode):
"Here's my plan:
1. Create paper_trades.json schema
2. Build trade logging function
3. Implement P&L calculation
4. Add stop-loss monitoring
...
Approve? [Yes/No/Keep Planning]"
```

**SS3 Use Case:**
Before any major system change, activate plan mode. Review the plan. Then execute.

---

## 1.11 Local Ownership Philosophy

**Chuck's Core Message:**
"Nothing annoys me more than when ChatGPT tries to fence me in. Give me the vendor lock-in so I can't leave. NO. I reject that."

**The Ownership Principle:**
- All context in local files
- All history in git
- All decisions documented
- Can switch AI tools anytime
- YOUR data, YOUR control

**SS3 Application:**
BRAIN.json is YOUR file. Not locked in any platform. Any AI can read it. You can move it anywhere. You own your trading system completely.

---

# 2. CORE PHILOSOPHY: WHY TERMINAL > BROWSER

## 2.1 Control
| Browser AI | Terminal AI |
|------------|-------------|
| Context trapped in their servers | Context in your files |
| Can't automate | Full automation |
| Copy-paste workflow | Direct file manipulation |
| Single conversation | Multiple agents |
| Their UI limitations | Your customizations |

## 2.2 Power Features Only in Terminal
- Agents (sub-workers with fresh context)
- Output styles (custom personas)
- Headless mode (AI calling AI)
- Planning mode (approval workflows)
- Session management (resume, timeline, share)
- Git integration (version everything)
- Multi-AI same-directory workflow

## 2.3 The Superpower Feeling
Chuck: "I wake up every day feeling like I have superpowers."

Why: Because you can build CUSTOM tools for YOUR specific workflow. Not generic ChatGPT for everyone. YOUR personal AI army.

---

# 3. TOOL-BY-TOOL BREAKDOWN

## 3.1 Gemini CLI

### Installation
```bash
npm install -g @google/generative-ai-cli
# or
brew install gemini-cli
```

### Key Commands
| Command | Purpose |
|---------|---------|
| `gemini` | Start interactive session |
| `gemini -p "prompt"` | Headless single query |
| `/init` | Create gemini.md context |
| `/context` | Show token usage |
| `/help` | All commands |

### Configuration
Create `~/.gemini/config.json`:
```json
{
  "apiKey": "YOUR_GEMINI_API_KEY",
  "model": "gemini-2.5-flash",
  "temperature": 0.7
}
```

### SS3 Integration
- GIO persona lives here
- Research tasks delegated here
- Synced via gemini.md

---

## 3.2 Claude Code

### Installation
```bash
npm install -g @anthropic-ai/claude-code
```

### Key Commands
| Command | Purpose |
|---------|---------|
| `claude` | Start session |
| `claude -r` | Resume previous |
| `claude --dangerously-skip-permissions` | No confirmations |
| `/agents` | Manage agents |
| `/context` | Token usage grid |
| `/compact` | Compress context |
| `/output-style` | Change persona |
| `Shift+Tab` | Cycle modes (plan/normal) |
| `Ctrl+O` | Check agent progress |

### Agent Creation Flow
```bash
/agents
→ Create new agent
→ Name: "paper_trader"
→ Scope: Project (this directory only)
→ Use Claude to generate definition
→ Describe: "Executes paper trades, monitors positions..."
→ Tools: All / Restricted
→ Model: Sonnet (fast) / Opus (smart)
→ Save
```

### Output Style Creation
```bash
/output-style
→ New
→ Name: "sovereign_executor"
→ Define persona...
→ Save
→ /output-style sovereign_executor (to activate)
```

### SS3 Integration
- AURORA primary interface
- Trade execution
- Agent orchestration
- EOD sequences

---

## 3.3 OpenCode

### Installation
```bash
npm install -g open-code
source ~/.bashrc  # Reload shell
```

### Key Commands
| Command | Purpose |
|---------|---------|
| `open-code` | Start session |
| `open-code auth login` | Login with Claude Pro |
| `/model` | Switch models |
| `/share` | Share session URL |
| `/timeline` | View/restore history |
| `/sessions` | List all sessions |

### Local Model Configuration
Create `~/.config/open-code/open-code.jsonc`:
```jsonc
{
  "model": "llama3.2",
  "provider": "ollama"
}
```

### Login with Claude Pro
```bash
open-code auth login
→ Choose: Anthropic
→ Browser opens → Paste code
→ Now using Claude Pro subscription!
```

### SS3 Integration
- Backup executor
- Local model fallback
- Session sharing for collaboration

---

## 3.4 Codex (ChatGPT)

### Installation
Part of ChatGPT desktop app or:
```bash
npm install -g @openai/codex-cli
```

### Key Features
- Uses `agents.md` for context
- Strong at high-level analysis
- Good for architecture review
- Integrated with GPT-4 ecosystem

### SS3 Integration
- ARCHITECT_PRIME interface
- System design reviews
- Architecture decisions
- Workflow orchestration

---

# 4. THE AGENT ARCHITECTURE REVOLUTION

## 4.1 Why Agents Change Everything

### The Old Way (Broken)
```
ONE CONVERSATION
├── Started with simple question
├── Then did research (context grows)
├── Then executed code (context grows)
├── Then reviewed results (context grows)
├── Then planned next steps (context grows)
├── Now at 150K tokens
├── AI getting confused
├── Responses degrading
└── Eventually crashes or gives bad answers
```

### The New Way (Agents)
```
MAIN CONVERSATION (stays lean)
├── "Research Bitcoin sentiment"
│   └── SPAWNS: research_agent (fresh 200K)
│       └── Returns: 500 token summary
├── "Execute paper trade"
│   └── SPAWNS: paper_trader_agent (fresh 200K)
│       └── Returns: Trade confirmation
├── "Review my strategy"
│   └── SPAWNS: critic_agent (fresh 200K)
│       └── Returns: Critique report
└── Main conversation: Still at 20K tokens, clean and focused
```

## 4.2 Agent Anatomy

### Agent Definition File
Location: `.claude/agents/[agent_name].md` or project-level `agents/[name].md`

```markdown
# Agent: [name]

## Role
[One sentence purpose]

## Personality
[How it behaves, communicates]

## Instructions
[Step-by-step what it does]

## Tools
[What it can access]
- Read files: Yes/No
- Write files: Yes/No
- Execute code: Yes/No
- Web access: Yes/No

## Input
[What it receives]

## Output
[What it returns]

## Restrictions
[What it cannot do]
```

## 4.3 Agent Communication Pattern

### Request Flow
```
Main → Agent: "Here's your task: {task}"
Agent: [Does work with fresh context]
Agent → Main: "Here's my result: {summary}"
Main: [Continues with minimal context impact]
```

### Key Principle
Agents return SUMMARIES, not full context. This keeps main conversation lean.

---

# 5. CONTEXT MANAGEMENT MASTERY

## 5.1 Token Economics

| Model | Context Window | Recommended Usage |
|-------|----------------|-------------------|
| Claude Sonnet | 200K tokens | Up to 60% (120K) |
| Claude Opus | 200K tokens | Up to 50% (100K) |
| Gemini Flash | 1M tokens | Up to 40% (400K) |
| GPT-4 | 128K tokens | Up to 50% (64K) |

## 5.2 Context Visualization
```bash
/context
```
Shows grid like:
```
[████████████████████░░░░░░░░░░] 42% used
Files: 15K | Conversation: 60K | System: 10K
```

## 5.3 Context Hygiene

### When to Compact
- Over 50% usage
- Before major new task
- When responses degrade

### How to Compact
```bash
/compact
# Or with instructions:
/compact "Preserve trading context, drop research details"
```

### When to Clear
- Starting completely new task
- Context hopelessly polluted
- Fresh start needed

```bash
/clear
```

## 5.4 Context File Strategy

### File Locations
```
project/
├── claude.md      # Claude context (PRIMARY)
├── gemini.md      # Gemini context (SYNCED)
├── agents.md      # Codex context (SYNCED)
├── BRAIN.json     # State (ALL READ)
└── .context/      # Additional context files
    ├── portfolio.md
    ├── strategies.md
    └── history.md
```

### Sync Script
```bash
#!/bin/bash
# sync_context.sh
cp claude.md gemini.md
cp claude.md agents.md
echo "Context files synced: $(date)"
```

---

# 6. MULTI-AI WORKFLOW SYSTEM

## 6.1 The Three-Terminal Setup

```
┌─────────────────────────────────────────────────────────┐
│ TERMINAL 1: AURORA (Claude Code)                        │
│ Role: Executor                                          │
│ Tasks: Trade execution, position management, alerts     │
│ Directory: /Volumes/LegacySafe/ECO_SYSTEM_4/      │
├─────────────────────────────────────────────────────────┤
│ TERMINAL 2: GIO (Gemini CLI)                            │
│ Role: Researcher                                        │
│ Tasks: Market analysis, sentiment, pattern recognition  │
│ Directory: /Volumes/LegacySafe/ECO_SYSTEM_4/      │
├─────────────────────────────────────────────────────────┤
│ TERMINAL 3: ARCHITECT_PRIME (Codex/OpenCode)            │
│ Role: Integrator                                        │
│ Tasks: System review, architecture, documentation       │
│ Directory: /Volumes/LegacySafe/ECO_SYSTEM_4/      │
└─────────────────────────────────────────────────────────┘
```

## 6.2 Workflow Example: Morning Routine

```bash
# Terminal 2 (GIO): Research
gemini: "Scan market conditions, update morning_scan.md"

# Terminal 1 (AURORA): Review & Execute
claude: "Read morning_scan.md, identify trades, execute paper positions"

# Terminal 3 (ARCHITECT): Review
codex: "Review today's trades in paper_trades.json, flag any issues"
```

## 6.3 AI Calling AI

### AURORA Calling GIO
```markdown
# Inside Claude conversation:
"I need deeper research on SOL. Use Gemini headless:"
gemini -p "Analyze Solana ecosystem, TVL trends, upcoming catalysts. Return bullet summary."
```

### Benefits
- Specialized tools for specialized tasks
- Fresh context for research
- Main conversation stays clean
- Best AI for each job

---

# 7. SESSION MANAGEMENT & PERSISTENCE

## 7.1 Session Lifecycle

```
START SESSION
├── Load BRAIN.json (state)
├── Load context files (claude.md, etc.)
├── Resume or start fresh
│
DURING SESSION
├── Execute tasks
├── Delegate to agents
├── All work in local files
│
END SESSION (session_closer_agent)
├── Summarize accomplishments
├── Update BRAIN.json
├── Update all context files
├── Commit to git
├── Prepare tomorrow's todos
└── Log to memory/SESSIONS/
```

## 7.2 Git Integration

### Why Git for Trading?
- Every decision versioned
- Can see what changed when
- Rollback bad changes
- Full accountability
- "Documentation happens automatically"

### Git Workflow
```bash
# After every session:
git add .
git commit -m "Session $(date +%Y-%m-%d): [summary]"

# After major changes:
git tag v1.2.3 -m "Paper trading profitable"

# If something breaks:
git log --oneline  # Find good state
git checkout abc123  # Restore
```

## 7.3 Session File Format

Location: `memory/SESSIONS/YYYY-MM-DD_session.md`

```markdown
# Session: December 2, 2025

## Summary
- Paper traded BTC at $83K (fear dip pattern)
- SUI take profit hit (+$2.50)
- Mission progress: $13.73 / $661.46

## Trades Executed
| ID | Symbol | Entry | Exit | P&L |
|----|--------|-------|------|-----|
| PT009 | SUI | $1.60 | $1.68 | +$2.50 |
| PT010 | BTC | $83,000 | - | OPEN |

## State Changes
- BRAIN.json updated: mission progress
- paper_trades.json: 2 new entries
- Context files synced

## Tomorrow's Priorities
1. Monitor BTC position
2. Check Fear & Greed for additional entries
3. Review if win rate > 60%

## Git Commit
abc123def - "Session Dec 2: SUI profit, BTC entry at fear dip"
```

---

# 8. THE CRITIC FRAMEWORK

## 8.1 Why Critics Matter

Problem: AI assistants are agreeable. They validate everything.
Result: Bad decisions get approved. No real feedback.
Solution: Agents designed to CRITICIZE with fresh, unbiased eyes.

## 8.2 Multi-Personality Critic

Chuck's approach: Three critics in one agent, different angles.

### Trading Critic Personalities

**1. Risk Manager**
```markdown
You are paranoid about risk. You've seen accounts blow up.
- Is position size correct?
- Is stop loss tight enough?
- What's the max drawdown scenario?
- Is this risking too much of capital?
```

**2. Pattern Analyst**
```markdown
You are skeptical of patterns. Most "patterns" are noise.
- Is this actually a pattern or random?
- What's the historical win rate?
- Are you seeing what you want to see?
- Would this pass backtesting?
```

**3. Psychology Auditor**
```markdown
You detect emotional trading. Revenge, FOMO, greed.
- Is this revenge after a loss?
- Is this FOMO chasing a pump?
- Is this greed ignoring stop loss?
- Would you take this trade tomorrow with fresh eyes?
```

## 8.3 Scoring System

```
TRADE REVIEW SCORE: X/10

8-10: EXECUTE - High confidence, well-reasoned
6-7:  RECONSIDER - Some issues, review before entry
4-5:  AVOID - Too many red flags
1-3:  DANGER - Emotional trading detected
```

---

# 9. UNIFIED FOLDER ARCHITECTURE

## 9.1 Current SS3 Problems

Based on research agent findings:
- Multiple `paper_trades.json` files (data/ AND memory/)
- Scripts write to different locations
- No unified context files
- AI Council not coordinated
- EOD sequence breaks frequently

## 9.2 New Architecture

```
/Volumes/LegacySafe/ECO_SYSTEM_4/
│
├── BRAIN.json                    # SINGLE source of truth
│
├── claude.md                     # Claude context (PRIMARY)
├── gemini.md                     # Gemini context (SYMLINK → claude.md)
├── agents.md                     # Codex context (SYMLINK → claude.md)
│
├── agents/                       # Agent definitions
│   ├── paper_trader.md          # Executes trades
│   ├── signal_scanner.md        # Finds setups
│   ├── market_researcher.md     # Deep research
│   ├── session_closer.md        # EOD automation
│   ├── brutal_critic.md         # Trade review
│   └── portfolio_monitor.md     # Position tracking
│
├── bin/                          # Executable scripts (CLEANED)
│   ├── aurora_executor.py       # Main AURORA script
│   ├── session_close.py         # EOD script
│   └── sync_context.sh          # Context sync
│
├── data/                         # Persistent data (SINGLE LOCATION)
│   ├── paper_trades.json        # All paper trades
│   ├── trade_journal.json       # Trade history
│   └── missions/
│       └── active_mission.json  # Current mission
│
├── memory/                       # Session state
│   ├── SESSIONS/                # Daily session logs
│   │   └── YYYY-MM-DD.md
│   └── LIVE_STATUS.json         # Real-time state
│
├── config/                       # Configuration
│   ├── exchanges/               # API configs
│   └── strategies/              # Strategy params
│
├── logs/                         # Runtime logs
│   └── trading/                 # Trade execution logs
│
└── .git/                         # Version control EVERYTHING
```

## 9.3 The Golden Rule

**ONE FILE PER PURPOSE. PERIOD.**

| Purpose | Single File |
|---------|-------------|
| System State | BRAIN.json |
| Paper Trades | data/paper_trades.json |
| Trade History | data/trade_journal.json |
| Active Mission | data/missions/active_mission.json |
| Live Status | memory/LIVE_STATUS.json |
| Context | claude.md (others symlinked) |

---

# 10. SS3 IMPLEMENTATION PLAN

## Phase 1: Clean Slate (Day 1)

### Step 1: Backup Everything
```bash
cd /Volumes/LegacySafe
zip -r SS3_backup_$(date +%Y%m%d).zip ECO_SYSTEM_4/
```

### Step 2: Create New Context Files
```bash
cd /Volumes/LegacySafe/ECO_SYSTEM_4

# Create master context
cat > claude.md << 'EOF'
# SOVEREIGN SHADOW 3 - AI Context

## System Overview
Trading system with AI Council (AURORA, GIO, ARCHITECT_PRIME)
Mission: DEBT_DESTROYER - Generate $661.46 profit via paper trading

## Current State
- Read BRAIN.json for portfolio, positions, mission progress
- Read data/paper_trades.json for active trades
- Phase: Paper Trading (Week 1 December Campaign)

## Rules
- Max position: $50
- Stop loss: 3%
- Take profit: 5%
- Go live at: 60% win rate, 10+ trades

## AI Roles
- AURORA (Claude): Executor - trades, alerts, execution
- GIO (Gemini): Researcher - analysis, patterns, sentiment
- ARCHITECT (GPT): Integrator - architecture, workflows

## Commands
- Update BRAIN.json after any state change
- Log all trades to data/paper_trades.json
- Create session file at EOD
- Git commit after every session
EOF

# Symlink for other AIs
ln -sf claude.md gemini.md
ln -sf claude.md agents.md
```

### Step 3: Git Initialize
```bash
cd /Volumes/LegacySafe/ECO_SYSTEM_4
git init  # If not already
git add .
git commit -m "Architecture rebuild: NetworkChuck agent model"
```

## Phase 2: Integration (Day 2-3)

### Step 4: Create Sync Script
```bash
cat > bin/sync_context.sh << 'EOF'
#!/bin/bash
# Sync all context files
cd /Volumes/LegacySafe/ECO_SYSTEM_4

# Ensure symlinks exist
[ -L gemini.md ] || ln -sf claude.md gemini.md
[ -L agents.md ] || ln -sf claude.md agents.md

echo "Context synced: $(date)"
EOF
chmod +x bin/sync_context.sh
```

## Phase 3: Daily Operations (Ongoing)

### Morning Routine
```bash
# Terminal 1: AURORA
cd /Volumes/LegacySafe/ECO_SYSTEM_4
claude

# Check state
"Read BRAIN.json, summarize current mission status"

# Scan for opportunities
"@signal_scanner scan BTC ETH SOL XRP"
```

### During Day
```bash
# When signal found, use paper trader
"@paper_trader execute BTC at $83000, $50 position, reason: fear dip"

# Before any trade, use critic
"@brutal_critic review this BTC trade at $83000"
```

### End of Day
```bash
# Use session closer
"@session_closer close out today's session"

# Or run script directly
python bin/session_close.py
```

---

# 11. AGENT DEFINITIONS FOR TRADING

## Complete Agent Registry

| Agent | File | Purpose | Trigger |
|-------|------|---------|---------|
| `paper_trader` | agents/paper_trader.md | Execute paper trades | "@paper_trader" |
| `signal_scanner` | agents/signal_scanner.md | Find opportunities | "@signal_scanner" |
| `session_closer` | agents/session_closer.md | EOD automation | "@session_closer" |
| `brutal_critic` | agents/brutal_critic.md | Trade review | "@brutal_critic" |
| `market_researcher` | agents/market_researcher.md | Deep research | "@market_researcher" |
| `portfolio_monitor` | agents/portfolio_monitor.md | Position tracking | "@portfolio_monitor" |
| `gemini_delegator` | agents/gemini_delegator.md | Delegate to GIO | "@gemini" |

## Creating in Claude Code

```bash
/agents
→ Create new
→ Name: paper_trader
→ Scope: Project
→ Paste definition from agents/paper_trader.md
→ Tools: Restricted (read data/, write data/, no web)
→ Model: Sonnet
→ Save
```

Repeat for each agent.

---

# 12. MIGRATION CHECKLIST

## Pre-Migration
- [ ] Backup entire SS3 directory
- [ ] Document current open positions
- [ ] Note current mission progress
- [ ] Export any browser AI conversations

## Phase 1: Structure
- [ ] Create claude.md master context
- [ ] Create symlinks (gemini.md, agents.md)
- [ ] Consolidate paper_trades.json
- [ ] Create agent definition files
- [ ] Initialize git (if needed)
- [ ] First commit: "Architecture rebuild"

## Phase 2: Agents
- [ ] Create paper_trader agent in Claude Code
- [ ] Create signal_scanner agent
- [ ] Create session_closer agent
- [ ] Create brutal_critic agent
- [ ] Test each agent individually

## Phase 3: Workflow
- [ ] Set up three-terminal workflow
- [ ] Test AURORA → GIO delegation
- [ ] Run first EOD with session_closer
- [ ] Verify git commits working

## Phase 4: Validation
- [ ] Execute test paper trade through agent
- [ ] Run critic on test trade
- [ ] Complete full day cycle
- [ ] Verify all files updating correctly

## Post-Migration
- [ ] Archive old scripts not needed
- [ ] Update CLAUDE.md with new workflow
- [ ] Document any custom modifications
- [ ] Create "How to Resume" guide

---

# APPENDIX A: QUICK REFERENCE

## Commands
```bash
# Claude Code
/agents              # Manage agents
/context             # Token usage
/compact             # Compress context
/output-style        # Change persona
Shift+Tab            # Toggle plan mode
Ctrl+O               # Check agent progress

# Gemini CLI
gemini               # Start session
gemini -p "prompt"   # Headless query
/init                # Create context
/context             # Token usage

# OpenCode
open-code            # Start session
/model               # Switch models
/share               # Share session
/timeline            # View history
```

## File Locations
```
BRAIN.json           # Master state
claude.md            # AI context
data/paper_trades.json  # Trades
memory/SESSIONS/     # Daily logs
agents/              # Agent definitions
```

## Daily Commands
```bash
# Morning
claude: "@signal_scanner scan all"

# Trade
claude: "@brutal_critic review [trade]"
claude: "@paper_trader execute [trade]"

# EOD
claude: "@session_closer close session"
```

---

# APPENDIX B: NETWORKCHUCK QUOTES

> "I wake up every day feeling like I have superpowers."

> "Nothing annoys me more than when ChatGPT tries to fence me in. Give me the vendor lock-in so I can't leave. NO. I reject that."

> "This guy, he's got a fresh pot of coffee. He's ready to go. He just walked in to work."

> "I'm bad at documentation. I'm bad at keeping track of things. But now I have this help me keep track of things."

> "I own my context. If a new, greater, better AI comes out, I'm ready for it, because all my stuff is right here on my hard drive."

> "The tools I create are so powerful for me. I wake up every day feeling like I have superpowers. I want this for you."

---

**Document Version:** 1.0
**Created:** December 2, 2025
**Author:** AURORA (Claude) + Research Agents
**Source:** NetworkChuck Terminal AI Video
**Target:** ECO SYSTEM 4 Trading System

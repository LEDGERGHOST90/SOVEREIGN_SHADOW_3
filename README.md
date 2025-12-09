# 🏴 Sovereign Shadow 3 README

Welcome to the official documentation and operator’s guide for Sovereign Shadow 3—a comprehensive, AI-powered cryptocurrency trading platform.

---

## Purpose

This README exists to give users and contributors a thorough understanding of the Sovereign Shadow 3 system. It introduces the philosophy, structure, tools, and processes that run beneath the surface of the platform. Whether you are running the system, developing enhancements, or simply exploring its capabilities, this guide is your central navigation point.

---

## Theme

Sovereign Shadow 3 is engineered for disciplined, transparent, and adaptive trading in volatile crypto markets. At its heart is a multi-agent council: a collection of AI, analytics, strategy, and psychology engines designed to work in tandem, promoting rigorous decision-making and continuous improvement. This approach is about more than just gains—it embodies a philosophy of resilience, responsibility, and calculated risk—summed up in the ethos:

> "Fearless. Bold. Smiling through chaos."

All rules, routines, and safeguards present in the system reflect this guiding principle. Every feature and workflow is documented here for clarity and replicability.

---

## What This README Covers

- **System Philosophy:** Defining the approach and mindset of Sovereign Shadow 3.
- **Architecture Overview:** Explaining how AI agents and subsystems collaborate for decision support, analysis, trading, and learning.
- **Capital and Account Management:** Describing how funds, assets, and risks are managed across multiple exchanges and storage solutions.
- **Agent Council Roles:** Documenting specialized agents, from trade execution to psychology enforcement, and how each contributes to overall strategy.
- **Setup & Operations:** Quick-start guides and detailed instructions for deploying and maintaining every part of the stack—cloud, desktop, and local.
- **Safety and Risk Controls:** Outlining strict risk management, validation steps, paper trading enforcement, and emotional discipline.
- **Project Structure & Files:** Mapping directories, code modules, and major data files, for both developers and auditors.
- **API Integrations & Notifications:** Listing connected exchanges, supported automations, and push/voice notification endpoints.
- **Performance & Campaigns:** Showcasing how trading performance is recorded, campaigns run, and lessons learned are integrated back into the system.
- **Ongoing Learning:** Introducing the built-in education and mentorship layer that ensures continuous user growth and compliance before live trades.

---

## Who This Is For

- **Operators:** For those actively trading or simulating trades and requiring clarity on system logic and limiters.
- **Developers:** For those wishing to customize, extend, or audit the platform's open architecture and agents.
- **Reviewers:** For anyone assessing security, strategy, or compliance within an advanced crypto automation workflow.

---

## How To Use This File

Read from top to bottom to get a holistic vision; jump to specific sections for technical procedures or in-depth explanations. Update references and figures as the system evolves—this is your working blueprint.

---

*"Built for adaptation, governed by discipline, and open to scrutiny. Welcome to Sovereign Shadow 3."*

---- **Neural Hub API:** http://localhost:8000
- **GIO Frontend:** http://localhost:3000
- **SS_III Dashboard:** http://localhost:5001

## 🚀 Quick Start

### 1. Start Services
```bash
# Neural Hub (AURORA backend)
cd neural_hub/backend && python3 -m uvicorn main:app --port 8000 --reload

# GIO Frontend
cd strategySynthai && npm run dev

# SS_III Dashboard
cd REPLIT{SS_III} && npm run dev:client
```

### 2. Desktop Launcher
```bash
open /Applications/SovereignShadow3.app
```

Commands: `dstest`, `score BTC`, `ask "..."`, `balance`, `scan`

## 📊 December Campaign

### Week 1: Paper Trading (Dec 1-7)
| Rule | Value |
|------|-------|
| Max Position | $50 |
| Stop Loss | 3% |
| Take Profit | 5% |
| Max Concurrent | 3 positions |
| Target Win Rate | 60% |

### Strategy: Option C - Partial Repay + Swing Trade
- $300 debt repaid (Nov 30)
- $260 capital for trading
- Week 2+ live trading if >60% win rate

## 🔌 DS-STAR Modules

```
DS-STAR: Decision Support - Strategic Trading Analysis & Research

├── SynopticCore       # Smart Asset Score (0-100)
├── OracleInterface    # NL → Charts & Analysis (Gemini)
├── ArchitectForge     # NL → Strategy Builder
├── Gatekeeper         # Data Normalization & Health
└── TransparentAnalyst # Step-by-step Reasoning
```

## 📁 Project Structure

```
SOVEREIGN_SHADOW_3/
├── neural_hub/          # AURORA execution stack (FastAPI)
├── strategySynthai/     # GIO research frontend (React)
├── REPLIT{SS_III}/      # Cloud dashboard (Vite + React 19)
├── shadow_sdk/          # MCP server
├── ds_star/             # Decision support modules
├── council/             # Trading psychology framework
├── meme_machine/        # Solana scanner
├── memory/              # State files
│   ├── LIVE_STATUS.json
│   ├── paper_trades.json
│   └── SESSIONS/
├── logs/                # Trade journals
└── BRAIN.json           # Master state
```

## 🛡️ Safety Rules

### NEVER
- ❌ Trade with Ledger collateral (READ-ONLY)
- ❌ Commit API keys to git
- ❌ Override stop-losses emotionally
- ❌ Exceed $50 per position (Week 1)
- ❌ Skip paper trading validation

### ALWAYS
- ✅ Respect 3% stop loss
- ✅ Paper trade new strategies first
- ✅ Keep Health Factor > 2.0
- ✅ Log all trades to paper_trades.json
- ✅ Council consensus before large trades

## 🔧 API Status

| Exchange | Status | Permissions |
|----------|--------|-------------|
| Coinbase | ✅ ACTIVE | Trade |
| Kraken | ✅ ACTIVE | Trade |
| Binance US | ✅ ACTIVE | Trade (IPv4) |
| OKX | ❌ DISABLED | - |
| Ledger | 📖 MANUAL | Read-only |

## 📈 Target Portfolio Allocation

| Asset | Target % | Current |
|-------|----------|---------|
| BTC | 40% | ~28% |
| ETH | 30% | ~56% (wstETH collateral) |
| SOL | 20% | 0% |
| XRP | 10% | ~20% |

## 📚 Key Files

- `BRAIN.json` - Master state & council config
- `memory/LIVE_STATUS.json` - Real-time portfolio
- `memory/paper_trades.json` - Paper trade log
- `logs/trading/trade_journal.json` - Trade history

## 📞 Notifications

- **Push:** ntfy.sh/sovereignshadow_dc4d2fa1
- **Voice:** Aurora (ElevenLabs)

## 🏴 Trading Record

- Trades: 1 | Wins: 0 | Losses: 1
- P&L: -$18.11 (ZEC stop-loss)
- Lesson: Entry was premature, defense was correct

---

**Status:** 🟢 DECEMBER CAMPAIGN ACTIVE
**Last Updated:** December 1, 2025
**Version:** 3.0.0

*"Fearless. Bold. Smiling through chaos."*

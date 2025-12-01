# 🏴 Sovereign Shadow 3 Trading System

**Philosophy:** "Fearless. Bold. Smiling through chaos."

## 🎯 System Overview

AI-powered cryptocurrency trading system with multi-agent council architecture for automated analysis, signal generation, and portfolio management.

### 💰 Capital Structure (December 1, 2025)
- **Net Worth:** $5,433.87
- **AAVE Debt:** -$360.94
- **Health Factor:** 3.71
- **Trading Capital:** $260

#### 🔐 Ledger (Cold Storage): $5,715.91
| Asset | Amount | Value |
|-------|--------|-------|
| wstETH | (collateral) | $3,040.25 |
| BTC | 0.0164 | $1,508.32 |
| XRP | 501.9 | $1,099.17 |
| USDC | 53.61 | $53.61 |
| ETH | 0.0048 | $14.56 |

#### 🏦 Coinbase: $1.93
| Asset | Amount |
|-------|--------|
| USDC | 1.93 |

#### 🦑 Kraken: $3.79
| Asset | Amount |
|-------|--------|
| PEPE | 41,666.66 |
| SOL | 0.0059 |
| USDG | 1.26 |
| ETH | 0.00036 |
| DOGE | 2.53 |
| USD | 0.0037 |

#### 🔶 Binance US: $73.18
| Asset | Amount |
|-------|--------|
| USDC | 73.16 |
| RENDER | 0.0094 |
| PEPE | 372.32 |

### 🧠 AI Council
| Agent | Role | Stack |
|-------|------|-------|
| **AURORA** | The Executor | Claude + Neural Hub (FastAPI) |
| **GIO** | The Researcher | Gemini 2.5 Flash + strategySynthai |
| **ARCHITECT_PRIME** | The Integrator | GPT + System Architecture |

### 🌐 Dashboards
- **Cloud Dashboard:** https://sovereignnshadowii.abacusai.app
- **Neural Hub API:** http://localhost:8000
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

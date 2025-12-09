# Shadow-3 Legacy Loop Platform

AI-powered cryptocurrency trading system with multi-agent architecture, autonomous execution, and cold storage integration.

---

## Overview

**150+ Python modules | 68,000+ lines of code | 14 months of development**

Unified repository consolidating the Sovereign Shadow trading ecosystem. Built for disciplined, transparent trading with AI-driven decision support, multi-exchange execution, and hardware wallet security.

> "Fearless. Bold. Smiling through chaos."

---

## Paper Trading System

### Current Phase: VALIDATION MODE

All strategies must pass paper trading validation before live deployment. This is non-negotiable.

### Paper Trading Rules

| Rule | Value | Rationale |
|------|-------|-----------|
| Max Position | $50 | Capital preservation |
| Stop Loss | 3% | Risk per trade = $1.50 max |
| Take Profit | 5% | 1.67:1 reward-to-risk |
| Max Concurrent | 3 positions | Focus over diversification |
| Required Win Rate | 60% | Minimum for live promotion |
| Min Paper Trades | 20 | Statistical significance |

### Validation Criteria

To move from paper to live trading:
1. **Win Rate >= 60%** over minimum 20 trades
2. **Profit Factor >= 1.5** (gross profit / gross loss)
3. **Max Drawdown <= 10%** of paper capital
4. **Consecutive Losses <= 3** without strategy review
5. **Council Consensus** - All AI agents must approve

### Paper Trade Logging

All paper trades recorded in `memory/paper_trades.json`:
```json
{
  "trade_id": "PT-2025-12-09-001",
  "asset": "BTC",
  "entry_price": 94006.57,
  "position_size": 50.00,
  "stop_loss": 91146.37,
  "take_profit": 98706.90,
  "ray_score": 72,
  "swarm_consensus": 0.83,
  "status": "open"
}
```

### Paper Trading Commands

```bash
# Log a paper trade
python3 -m core.trading.paper_logger --asset BTC --size 50 --entry 94000

# View paper trade stats
python3 -m core.trading.paper_stats

# Validate for live promotion
python3 -m core.trading.validate_paper --min-trades 20
```

---

## API Configuration

### Exchange Platforms

| Platform | Status | API Type | Primary Use |
|----------|--------|----------|-------------|
| Kraken | ACTIVE | REST + WS | Primary trading |
| Binance US | ACTIVE | REST (IPv4) | Fiat on-ramp |
| Coinbase | ACTIVE | CDP JWT/ECDSA | Advanced trade |
| OKX | ACTIVE | REST + WS | Sniper execution |

### API Authentication Details

**Coinbase (CDP - Coinbase Developer Platform)**
- Auth: JWT with EC Private Key (ECDSA)
- Key Format: `organizations/{org_id}/apiKeys/{key_id}`
- Signing: ES256 algorithm
- Endpoints: Advanced Trade API v3

**Kraken**
- Auth: API-Key + Private Key signing
- Nonce: Required (timestamp-based)
- Rate Limits: 15 calls/second

**Binance US**
- Auth: HMAC-SHA256 signature
- Requirement: IPv4 connection only
- Rate Limits: 1200 req/min

**OKX**
- Auth: API Key + Secret + Passphrase
- Signing: HMAC-SHA256
- Rate Limits: 20 req/2sec

### AI Services

| Service | Status | Use Case |
|---------|--------|----------|
| Anthropic Claude | ACTIVE | AURORA executor |
| Google Gemini | ACTIVE | GIO researcher |
| ElevenLabs | ACTIVE | Aurora voice |
| Abacus AI | ACTIVE | DS-STAR platform |

### DeFi & Data APIs

| Service | Status | Use Case |
|---------|--------|----------|
| Etherscan | NEEDS KEY | ETH transactions |
| Birdeye | ACTIVE | Solana token data |
| Helius | ACTIVE | Solana RPC |
| CryptoCompare | ACTIVE | Price feeds |

### Configuration Files

```
config/
├── .env.unified          # Local backup (all keys)
└── [Replit Secrets]      # Source of truth
```

**Source of Truth:** Replit DS-STAR Platform Secrets
**Local Backup:** `config/.env.unified`
**SS_III Copy:** `/Volumes/LegacySafe/SS_III/.env`

---

## Core Architecture

```
core/
├── agi/              # Recursive self-improving AGI master
├── swarm/            # HiveMind consensus (6 agents)
├── autonomous/       # 24/7 trading loop
├── ray_score/        # Signal quality scoring (0-100)
├── banking/          # Keyblade engine + wealth management
├── orchestration/    # Battle mode commander
├── exchanges/        # Multi-exchange connectors
├── arbitrage/        # Cross-exchange opportunities
├── ledger/           # Hardware wallet integration
├── mcp_servers/      # Model Context Protocol
├── security/         # Trooper Drone defense
└── voice/            # Aurora synthesis
```

---

## Ray Score Engine

Signal quality filter preventing bad entries:

| Factor | Weight | Description |
|--------|--------|-------------|
| Signal Quality | 20% | Technical indicator alignment |
| Risk/Reward | 25% | TP distance vs SL distance |
| Market Conditions | 15% | Volatility, trend strength |
| Position Sizing | 15% | Risk-adjusted sizing |
| Long-term Outlook | 25% | Higher timeframe bias |

**Minimum Score:** 60 for paper trades, 70 for live
**Auto-Exit Trigger:** Score drops below 40

---

## Swarm Agents

| Agent | Role | Vote Weight |
|-------|------|-------------|
| VolatilityHunter | Momentum detection | 15% |
| RSIReader | Oscillator signals | 15% |
| TechnicalMaster | Chart patterns | 20% |
| PatternMaster | Fibonacci/Golden Ratio | 15% |
| WhaleWatcher | Large transaction tracking | 20% |
| SentimentScanner | Social/news analysis | 15% |

**Consensus Threshold:** 0.65 (65% agreement required)

---

## Portfolio Snapshot (Dec 9, 2025)

### Ledger Cold Storage: $5,715
| Asset | Amount | USD | Allocation |
|-------|--------|-----|------------|
| wstETH | 0.84 | $3,040 | 56% |
| BTC | 0.0165 | $1,508 | 28% |
| XRP | 497 | $1,099 | 20% |
| USDC | 53.63 | $54 | 1% |
| ETH | 0.0048 | $15 | <1% |

### AAVE Position
- Collateral: $3,040 (wstETH)
- Debt: $361 (USDC borrowed)
- Health Factor: 3.71 (Safe > 2.0)
- Liquidation Price: ~$1,200 ETH

### Exchange Holdings: $79 (Paper Trading Capital)
| Exchange | Balance | Purpose |
|----------|---------|---------|
| Binance US | $73 | Primary paper trading |
| Kraken | $4 | Reserve |
| Coinbase | $2 | Reserve |

**Net Worth: $5,434**

---

## Mission: DEBT_DESTROYER

| Metric | Value |
|--------|-------|
| Target Profit | $661.46 |
| Current Progress | 0% |
| Phase | Paper Trading |
| Capital Available | $78.90 |
| Risk Per Trade | 2% ($1.58) |

### Mission Rules
1. Paper trade until 60% win rate achieved
2. Max $50 per position
3. 3% stop loss, 5% take profit
4. No trading Ledger collateral (READ-ONLY)
5. Daily journal in `logs/trading/`

---

## Safety Rules

### HARD STOPS (Non-Negotiable)

| Rule | Trigger | Action |
|------|---------|--------|
| Daily Loss Limit | -$10 | Stop trading for day |
| Consecutive Losses | 3 in a row | Mandatory review |
| Health Factor | < 2.0 | Reduce AAVE debt |
| Ray Score | < 40 | Exit position |

### NEVER
- Trade with Ledger collateral
- Commit API keys to git
- Override stop-losses emotionally
- Skip paper trading validation
- Trade without Council consensus

### ALWAYS
- Log every trade (paper or live)
- Review losses within 24 hours
- Keep Health Factor > 2.0
- Update BRAIN.json after sessions
- Paper trade new strategies first

---

## Quick Start

```bash
# 1. Load environment
source config/.env.unified

# 2. Run paper trade validation
python3 -m core.trading.paper_stats

# 3. Start morning scan
python3 scripts/morning_scan.py

# 4. Log a paper trade
python3 -m core.trading.paper_logger \
  --asset BTC \
  --size 50 \
  --entry 94000 \
  --stop 91180 \
  --target 98700
```

---

## Notifications

- **Push:** ntfy.sh/sovereignshadow_dc4d2fa1
- **Voice:** Aurora (ElevenLabs)
- **Desktop:** SovereignShadow3.app

---

## AI Council

| Agent | Model | Role |
|-------|-------|------|
| AURORA | Claude | Executor - signals, execution |
| GIO | Gemini | Researcher - analysis, patterns |
| ARCHITECT_PRIME | GPT | Integrator - architecture |

---

## Key Files

| File | Purpose |
|------|---------|
| `BRAIN.json` | Master state & config |
| `memory/paper_trades.json` | Paper trade log |
| `memory/LIVE_STATUS.json` | Portfolio snapshot |
| `logs/trading/trade_journal.json` | Trade history |
| `config/.env.unified` | API credentials backup |

---

**Status:** PAPER TRADING PHASE
**Last Updated:** December 9, 2025
**Version:** 3.1.0

*"The Gold is Extracted. The Empire Stands."*

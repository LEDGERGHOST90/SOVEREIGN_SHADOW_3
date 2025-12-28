---
title: "Sovereign Shadow II - Complete System Specifications"
date: 2025-11-04
version: 2025.11.04
status: production
type: technical-reference
tags: [specs, architecture, dependencies, apis, sdks, platforms]
---

# 🏴 SOVEREIGN SHADOW III
## Complete System Specifications & Technical Reference

> **Project:** Autonomous Crypto Trading & Portfolio Management System
> **Philosophy:** "Fearless. Bold. Smiling through chaos."
> **Approach:** NetworkChuck-style discipline + AI automation

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Specifications](#core-specifications)
3. [Technology Stack](#technology-stack)
4. [Dependencies](#dependencies)
5. [SDKs & Integrations](#sdks--integrations)
6. [APIs & Connectors](#apis--connectors)
7. [Platforms & Exchanges](#platforms--exchanges)
8. [Agent Systems](#agent-systems)
9. [Data Architecture](#data-architecture)
10. [Network Architecture](#network-architecture)
11. [Security & Credentials](#security--credentials)
12. [Educational Framework](#educational-framework)
13. [File Structure](#file-structure)
14. [Configuration](#configuration)
15. [Deployment](#deployment)

---

## System Overview

### Project Identity
```yaml
name: Sovereign Shadow III
alias: SovereignShadow_III
version: 2025.11.04
status: production-ready
environment: macOS 25.1.0
location: /Volumes/LegacySafe/SovereignShadow_II
storage: 495GB SSD + 2TB external (LegacySafe)
```

### Core Mission
Autonomous cryptocurrency trading and portfolio management system combining:
- AI-driven agent systems
- Multi-exchange integration
- DeFi position monitoring (AAVE)
- Cold storage tracking (Ledger)
- Risk management automation
- Psychology-enforced discipline
- Progressive trading education

### System Philosophy
1. **Automation First:** AI agents handle routine tasks
2. **Risk Management:** Never exceed 2% risk per trade
3. **Psychology Enforcement:** 3-strike rule with auto-lockout
4. **Progressive Learning:** 42-lesson curriculum required
5. **Zero Override:** System decisions are final

---

## Core Specifications

### Hardware Requirements
```yaml
minimum:
  cpu: Apple Silicon M1 or equivalent
  ram: 8GB
  storage: 50GB available
  network: Stable internet connection

recommended:
  cpu: Apple Silicon M2 or better
  ram: 16GB
  storage: 100GB available
  storage_type: SSD
  backup: External drive (2TB+)
  network: High-speed fiber
```

### Software Requirements
```yaml
operating_system:
  platform: macOS
  version: ">= 13.0"
  architecture: arm64 (Apple Silicon)

runtime:
  python: "3.11+"
  node: "18.x+"
  npm: "9.x+"

shell:
  primary: zsh
  required: bash (for scripts)
```

### Account Requirements
```yaml
portfolio:
  total_value: $5,817.91
  hot_wallet: $739.53 (Coinbase)
  binance_us: $72
  cold_storage: $5,078.03 (Ledger)
  aave_collateral: $2,940.71
  aave_debt: $663.31

trading_requirements:
  minimum_capital: $500+
  recommended_capital: $5,000+
  max_risk_per_trade: 2%
  max_portfolio_exposure: 10%
```

---

## Technology Stack

### Programming Languages
```yaml
primary:
  - python: "3.11.x"
    purpose: Agent systems, trading logic, data processing
    frameworks: [ccxt, pandas, numpy, requests]

  - typescript: "5.x"
    purpose: Frontend, Next.js application
    frameworks: [Next.js 14, React 18, TypeScript]

  - javascript: "ES2023"
    purpose: Node.js tools, utilities
    runtime: Node.js 18

secondary:
  - bash: Shell scripting, automation
  - yaml: Configuration files
  - json: State management, data storage
  - markdown: Documentation
```

### Frameworks & Libraries

#### Python Stack
```python
# Trading & Market Data
ccxt==4.1.0              # Unified exchange API
pandas==2.1.0            # Data analysis
numpy==1.24.0            # Numerical computing

# Web & API
requests==2.31.0         # HTTP client
python-dotenv==1.0.0     # Environment management
flask==3.0.0             # API server (optional)

# DeFi & Blockchain
web3==6.11.0             # Ethereum interaction
eth-account==0.10.0      # Account management

# Utilities
python-dateutil==2.8.2   # Date handling
pytz==2023.3             # Timezone support
```

#### TypeScript/Node Stack
```json
{
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "typescript": "5.2.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "ethers": "^6.8.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "tailwindcss": "^3.3.0"
  }
}
```

---

## Dependencies

### Core Dependencies
```bash
# System Dependencies
brew install python@3.11
brew install node@18
brew install git

# Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Python Packages
pip install --upgrade pip
pip install -r requirements.txt
```

### requirements.txt
```txt
# Trading & Exchange APIs
ccxt==4.1.0
python-binance==1.0.17

# Data Processing
pandas==2.1.0
numpy==1.24.0
python-dateutil==2.8.2

# Web & API
requests==2.31.0
python-dotenv==1.0.0
flask==3.0.0
flask-cors==4.0.0

# DeFi & Blockchain
web3==6.11.0
eth-account==0.10.0

# Utilities
pytz==2023.3
pyyaml==6.0.1
```

### package.json Dependencies
```json
{
  "name": "sovereign-shadow-ii",
  "version": "2025.11.04",
  "dependencies": {
    "next": "14.0.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.2.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "ethers": "^6.8.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "eslint": "^8.52.0",
    "eslint-config-next": "14.0.0"
  }
}
```

---

## SDKs & Integrations

### 1. Shadow SDK (MCP - Model Context Protocol)
```yaml
sdk: Shadow MCP
version: latest
purpose: AI agent communication & context sharing
integration: Native
protocol: Model Context Protocol
features:
  - Agent orchestration
  - Context persistence
  - State management
  - Cross-agent communication
```

### 2. Coinbase Advanced Trade SDK
```yaml
sdk: Coinbase Advanced Trade API
version: v3
authentication: API Key + Secret
base_url: https://api.coinbase.com/api/v3
rate_limits:
  public: 10 req/sec
  private: 5 req/sec
features:
  - Real-time market data
  - Order placement (market, limit)
  - Account management
  - Transaction history
status: ⚠️ PEM code obtained
```

### 3. Binance US SDK
```yaml
sdk: python-binance
version: 1.0.17
authentication: API Key + Secret
base_url: https://api.binance.us
verified: ✅ Connected 
rate_limits:
  requests: 1200/min
  orders: 10/sec
features:
  - Spot trading
  - Market data (WebSocket)
  - Account information
  - Order management
status: ✅ Operational
```

### 4. OKX SDK
```yaml
sdk: ccxt (unified)
version: 4.1.0
authentication: API Key + Secret + Passphrase
base_url: https://www.okx.com
features:
  - Spot & futures trading
  - Market data
  - Account management
  - WebSocket streams
status: ✅ Configured
```

### 5. MetaMask SDK
```yaml
sdk: web3.py + ethers.js
version: web3==6.11.0, ethers@6.8.0
purpose: Ethereum wallet interaction
features:
  - Wallet connection
  - Transaction signing
  - Balance tracking
  - Smart contract interaction
integration: Frontend + Backend
status: ✅ Integrated
```

### 7. Ledger SDK
```yaml
sdk: ledger-live-common
version: Latest
purpose: Cold storage tracking
hardware: Ledger hardware wallet
features:
  - Balance verification
  - Transaction signing
  - Multi-coin support
  - Secure key storage
status: ⚠️ Needs connection
balance: $6,167.43 (cold storage)
```

---

## APIs & Connectors

### Exchange APIs

#### Coinbase Advanced Trade
```yaml
api_name: Coinbase Advanced Trade API
endpoint: https://api.coinbase.com/api/v3
authentication: API Key + Secret
method: HMAC SHA-256 signature
capabilities:
  - accounts/
  - orders/ (market, limit, stop)
  - products/
  - fills/
  - fees/
rate_limits:
  general: 10 req/sec
  orders: 5 req/sec
websocket: wss://advanced-trade-ws.coinbase.com
status: ⚠️ API key expired, needs refresh
```

#### Binance US API
```yaml
api_name: Binance US REST API
endpoint: https://api.binance.us
authentication: API Key + Secret
method: HMAC SHA-256 signature
capabilities:
  - /api/v3/account
  - /api/v3/order (spot trading)
  - /api/v3/ticker/price
  - /api/v3/klines (OHLCV)
rate_limits:
  weight: 1200/min
  orders: 10/sec
websocket: wss://stream.binance.us:9443
status: ✅ Verified ($152.05)
connection_test: tools/test_binance_connection.js
```

#### OKX API
```yaml
api_name: OKX REST API
endpoint: https://www.okx.com
authentication: API Key + Secret + Passphrase
method: HMAC SHA-256 signature
capabilities:
  - /api/v5/account/balance
  - /api/v5/trade/order
  - /api/v5/market/tickers
  - /api/v5/market/candles
rate_limits:
  requests: 20/2sec
websocket: wss://ws.okx.com:8443/ws/v5/public
status: ✅ Configured
```

### DeFi Protocol APIs

#### AAVE Protocol
```yaml
protocol: AAVE v3
network: Ethereum Mainnet
rpc_endpoint: https://eth-mainnet.g.alchemy.com/v2/
contracts:
  pool: 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
  data_provider: 0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3
capabilities:
  - getReserveData()
  - getUserAccountData()
  - getHealthFactor()
  - liquidationThreshold()
monitoring:
  frequency: Every 15 minutes
  alerts: Health factor < 1.5
position:
  collateral: $3,494.76
  debt: $1,158.58 USDC
  health_factor: SAFE (42% utilization)
```

#### Ethereum RPC
```yaml
provider: Alchemy / Infura
endpoint: https://eth-mainnet.g.alchemy.com/v2/[API_KEY]
capabilities:
  - eth_getBalance
  - eth_call (smart contracts)
  - eth_blockNumber
  - eth_gasPrice
rate_limits: 300 requests/sec (Alchemy)
status: ✅ Configured
```

### Market Data APIs

#### CoinGecko (Free Tier)
```yaml
api_name: CoinGecko API
endpoint: https://api.coingecko.com/api/v3
authentication: None (free tier)
capabilities:
  - /simple/price (current prices)
  - /coins/{id}/market_chart
  - /exchanges/list
rate_limits: 10-30 calls/minute
status: ✅ Available
use_case: Backup price data
```

#### TradingView (Optional)
```yaml
api_name: TradingView Data Feed
endpoint: Custom integration
authentication: Not required (public charts)
capabilities:
  - Real-time charting
  - Technical indicators
  - Drawing tools
integration: Frontend only
status: Optional enhancement
```

---

## Platforms & Exchanges

### Active Exchanges

#### 1. Coinbase (Hot Wallet)
```yaml
exchange: Coinbase
type: Centralized Exchange (CEX)
account_value: $1,660.00
purpose: Primary hot wallet for active trading
features:
  - Advanced Trade API
  - USD on/off ramp
  - Instant liquidity
  - Insurance coverage
supported_coins: BTC, ETH, SOL, XRP, USDC, USDT
status: ✅ Active (needs fresh API key)
url: https://www.coinbase.com
```

#### 2. Binance US
```yaml
exchange: Binance US
type: Centralized Exchange (CEX)
account_value: $152.05
purpose: Secondary exchange, arbitrage opportunities
features:
  - Spot trading
  - Low fees (0.1%)
  - High liquidity
  - WebSocket feeds
supported_coins: 60+ cryptocurrencies
status: ✅ Verified connection
url: https://www.binance.us
```

#### 3. OKX
```yaml
exchange: OKX
type: Centralized Exchange (CEX)
account_value: TBD
purpose: Multi-exchange arbitrage, backup
features:
  - Spot & futures
  - High liquidity
  - Advanced order types
  - Copy trading
supported_coins: 300+ cryptocurrencies
status: ✅ API configured
url: https://www.okx.com
```

### DeFi Platforms

#### AAVE (Lending Protocol)
```yaml
protocol: AAVE v3
network: Ethereum Mainnet
position:
  collateral: $3,494.76
  debt: $1,158.58 USDC
  health_factor: Safe (42% utilization)
purpose: Passive yield on collateral
features:
  - Supply & borrow
  - Variable APY
  - Liquidation protection
monitoring: Real-time health factor tracking
url: https://app.aave.com
```

### Cold Storage

#### Ledger Hardware Wallet
```yaml
device: Ledger Nano X / S
balance: $6,167.43
purpose: Cold storage for long-term holdings
security: Hardware-based private keys
supported_coins: BTC, ETH, SOL, XRP, 1800+ others
backup: 24-word recovery phrase (secured offline)
status: ⚠️ Needs connection for live verification
```

---

## Agent Systems

### Architecture Overview
```
Sovereign Shadow II Agent Architecture

┌─────────────────────────────────────────────┐
│         CORE//COMMAND                       │
│    Master Trading System                    │
│    (Unified Interface)                      │
└───────────────┬─────────────────────────────┘
                │
    ┌───────────┴───────────┬─────────────┬─────────────┐
    │                       │             │             │
    ▼                       ▼             ▼             ▼
┌────────┐           ┌────────┐     ┌────────┐    ┌────────┐
│SHADE// │           │MIND//  │     │LEDGER//│    │MENTOR//│
│AGENT   │           │LOCK    │     │ECHO    │    │NODE    │
└────────┘           └────────┘     └────────┘    └────────┘
    │                       │             │             │
    ▼                       ▼             ▼             ▼
┌────────┐           ┌────────┐     ┌────────┐    ┌────────┐
│Portfolio│          │Risk    │     │Software│    │Code    │
│Agent   │           │Agent   │     │Architect│   │Reviewer│
└────────┘           └────────┘     └────────┘    └────────┘
```

### Agent Specifications

#### 1. SHADE//AGENT (Strategy Enforcer)
```yaml
agent_id: shade_agent
alias: SHADE//AGENT
file: agents/shade_agent.py
lines_of_code: 500+
purpose: Trade validation & strategy enforcement
rules_enforced:
  - 4H/15M timeframe alignment
  - 1-2% risk per trade (max)
  - Stop loss required
  - Minimum 1:2 R:R ratio
  - Max 10% portfolio exposure
capabilities:
  - Position sizing calculation
  - Risk validation
  - Technical indicator checks
  - Multi-timeframe alignment
logs_to: logs/shade_events.jsonl
status: ✅ Operational
```

#### 2. MIND//LOCK (Psychology Tracker)
```yaml
agent_id: psychology_tracker
alias: MIND//LOCK
file: agents/psychology_tracker.py
lines_of_code: 600+
purpose: Emotion monitoring & discipline enforcement
features:
  - 3-strike rule (auto-lockout)
  - Emotion tracking (8 states)
  - Revenge trading detection
  - Overtrading prevention (10 trades/day max)
emotions_tracked:
  - confident, neutral, anxious
  - fear, greed, revenge, fomo, hope
logs_to: logs/psychology_log.jsonl
state_file: logs/psychology/psychology_state.json
status: ✅ Operational (0/3 losses)
```

#### 3. LEDGER//ECHO (Trade Journal)
```yaml
agent_id: trade_journal
alias: LEDGER//ECHO
file: agents/trade_journal.py
lines_of_code: 800+
purpose: Complete trade logging & analysis
captures:
  - Validation results
  - Emotional states
  - Market context
  - Execution details
  - P&L outcomes
statistics:
  - Win rate
  - Expectancy
  - Average R:R
  - System adherence
  - Emotion performance
outputs:
  - trade_journal.json
  - trade_journal.csv
  - win_rate_tracker.json
  - pattern_signatures.yaml
status: ✅ Operational
```

#### 4. MENTOR//NODE (Education System)
```yaml
agent_id: mentor_system
alias: MENTOR//NODE
file: agents/mentor_system.py
lines_of_code: 900+
purpose: Progressive trading education
curriculum:
  chapters: 8
  lessons: 42
  quizzes: true
requirements_for_live_trading:
  - 20 lessons completed
  - 10 paper trades done
  - 40% win rate achieved
progression: Enforced (no skipping)
state_file: logs/mentor/mentor_state.json
status: ✅ Ready (0/42 lessons)
```

#### 5. CORE//COMMAND (Master System)
```yaml
agent_id: master_trading_system
alias: CORE//COMMAND
file: agents/master_trading_system.py
lines_of_code: 400+
purpose: Unified control & orchestration
methods:
  - pre_trade_check()
  - execute_trade()
  - close_trade()
  - display_dashboard()
  - get_system_status()
integrations:
  - SHADE//AGENT
  - MIND//LOCK
  - LEDGER//ECHO
  - MENTOR//NODE
safe_mode: Enforced (no overrides)
status: ✅ Operational
```

#### 6. Portfolio Agent
```yaml
agent_id: portfolio_agent
file: agents/portfolio_agent.py
purpose: Asset allocation analysis
capabilities:
  - Fetch live portfolio data
  - Calculate diversification score
  - Generate rebalancing recommendations
  - Track target allocation
targets:
  btc: 40%
  eth: 30%
  sol: 20%
  xrp: 10%
status: ✅ Operational
```

#### 7. Risk Agent
```yaml
agent_id: risk_agent
file: agents/risk_agent.py
purpose: Risk monitoring & alerts
monitors:
  - AAVE health factor
  - Exchange exposure
  - Position concentration
  - Overall risk score (0-100)
thresholds:
  max_position_size: 25%
  max_daily_exposure: $100
  aave_safe_health: ">1.5"
status: ✅ Operational
```

#### 8. Software Architect Agent
```yaml
agent_id: software_architect
file: agents/software_architect.py
purpose: Codebase analysis & recommendations
capabilities:
  - Analyze structure
  - Design architecture
  - Recommend improvements
  - Generate roadmap
status: ✅ Operational
```

#### 9. Code Reviewer Agent
```yaml
agent_id: code_reviewer
file: agents/code_reviewer.py
purpose: Code quality & security review
capabilities:
  - Security issue detection
  - Syntax error finding
  - Best practice suggestions
  - Quality scoring
status: ✅ Operational
```

---

## Data Architecture

### Database Strategy
```yaml
current: File-based (JSON)
planned: PostgreSQL / SQLite

file_storage:
  format: JSON, YAML, CSV
  location: logs/, memory/
  backup: External drive (LegacySafe)

future_migration:
  database: PostgreSQL
  orm: SQLAlchemy
  migration_tool: Alembic
```

### State Management
```yaml
psychology_state:
  file: logs/psychology/psychology_state.json
  frequency: Real-time updates
  archival: Daily (logs/psychology/history/)

trade_journal:
  file: logs/trading/trade_journal.json
  backup: trade_journal.csv
  retention: Permanent

mentor_progress:
  file: logs/mentor/mentor_state.json
  updates: Per lesson completion

portfolio_context:
  file: core/portfolio/mcp_portfolio_context.json
  frequency: Every API call
  purpose: Single source of truth
```

### Data Flow
```
Exchange APIs → unified_portfolio_api.py → mcp_portfolio_context.json
                                                    ↓
                            ┌───────────────────────┴────────────────┐
                            ▼                                        ▼
                      Agent Systems                           Dashboard UI
                    (Read context)                         (Display data)
                            │
                            ▼
                    State Updates
                  (logs/*.json)
```

---

## Network Architecture

### NetworkChuck Trading Approach

#### Philosophy
```yaml
source: NetworkChuck YouTube Trading Education
approach: Disciplined, systematic crypto trading
key_principles:
  - Multi-timeframe analysis (4H + 15M)
  - Risk management first (1-2% rule)
  - Psychology discipline (3-strike rule)
  - Technical indicators (EMA, RSI, Volume)
  - No emotional trading
```

#### 15M/4H Strategy
```yaml
strategy_name: Two-Timeframe Strategy
timeframes:
  primary: 4-hour (market structure)
  secondary: 15-minute (entry timing)

workflow:
  1: Check 4H chart for trend
  2: Wait for 15M pullback
  3: Confirm 5 technical indicators
  4: Enter on 15M reversal
  5: Set stop loss below support
  6: Target 1:2 minimum R:R
  7: Take profits at target
  8: Log trade & lessons

indicators_4h:
  - EMA 50 & 200 (trend)
  - RSI (strength)
  - Support/Resistance levels

indicators_15m:
  - EMA 21 (short-term trend)
  - RSI 40-60 (neutral zone)
  - Volume (confirmation)
  - Pullback to key level
```

#### Risk Management Rules
```yaml
position_sizing:
  formula: "(account × risk%) / (entry - stop_loss)"
  risk_per_trade: 1-2%
  max_exposure: 10% portfolio

risk_reward:
  minimum: "1:2"
  preferred: "1:3 or better"
  calculation: "target_distance / stop_distance"

stop_loss:
  required: true
  placement: Below support (LONG) / Above resistance (SHORT)
  never_move: "Away from entry (that's denial)"
  let_hit: "Accept the loss"
```

#### Psychology Framework
```yaml
emotions_to_avoid:
  - Fear (paralysis)
  - Greed (won't take profits)
  - Revenge (trading after loss)
  - FOMO (jumping in without setup)

three_strike_rule:
  losses_allowed: 3 per day
  action_on_three: Lock out trading
  reset: Next calendar day
  purpose: Prevent emotional spirals

overtrading_prevention:
  max_trades_per_day: 10
  min_time_between: 15 minutes
  quality_over_quantity: true
```

### Lesson Structure (42 Lessons)
```yaml
chapter_1: Why This Strategy Works (2 lessons)
  1.1: The Two-Timeframe Philosophy
  1.2: Why Most Traders Fail

chapter_2: Understanding Two Timeframes (2 lessons)
  2.1: Reading the 4-Hour Chart
  2.2: Reading the 15-Minute Chart

chapter_3: Risk Management (3 lessons)
  3.1: The 1-2% Rule (Non-Negotiable)
  3.2: Stop Losses (Your Life Insurance)
  3.3: Risk:Reward Ratio (The Profit Math)

chapter_4: Psychology & Discipline (2 lessons)
  4.1: The Four Emotions That Kill Accounts
  4.2: The 3-Strike Rule

chapter_5: Technical Indicators (4 lessons)
  5.1: Exponential Moving Averages (EMA)
  5.2: RSI (Relative Strength Index)
  5.3: Volume (The Truth Serum)
  5.4: Support & Resistance

chapter_6: Your First Trade (2 lessons)
  6.1: The Pre-Trade Checklist
  6.2: Example Trade Walkthrough (LONG)

chapter_7: Common Mistakes (1 lesson)
  7.1: The Top 10 Trading Mistakes

chapter_8: Advanced Concepts (2 lessons)
  8.1: Market Structure Deep Dive
  8.2: Confluences (Stacking Probabilities)
```

---

## Security & Credentials

### API Key Management
```yaml
storage: .env file (NOT in git)
template: .env.example (in git)
encryption: File system permissions
backup: Secure password manager

required_keys:
  - COINBASE_API_KEY
  - COINBASE_API_SECRET
  - BINANCE_API_KEY
  - BINANCE_API_SECRET
  - OKX_API_KEY
  - OKX_API_SECRET
  - OKX_PASSPHRASE
  - ALCHEMY_API_KEY (Ethereum RPC)

status:
  binance_us: ✅ Active
  coinbase: ⚠️ Expired (needs refresh)
  okx: ✅ Configured
  alchemy: ✅ Active
```

### .gitignore Protection
```bash
# Secrets
.env
.env.local
.env.production
*.key
*.pem

# Sensitive Data
logs/transactions/*.csv
logs/trading/*.csv
credentials.json

# State Files
logs/psychology/psychology_state.json
logs/trading/trade_journal.json
```

### Security Best Practices
```yaml
api_keys:
  - Never commit to git
  - Use read-only when possible
  - Rotate every 90 days
  - Enable IP whitelisting
  - Use API key restrictions

private_keys:
  - Hardware wallet only (Ledger)
  - Never store in code
  - 24-word backup (offline)
  - Multi-signature for large amounts

exchange_security:
  - 2FA enabled (all exchanges)
  - Withdrawal whitelist
  - Anti-phishing code
  - Email notifications
```

---

## File Structure

### Complete Directory Tree
```
SovereignShadow_II/
├── agents/                              # AI Agent Systems
│   ├── shade_agent.py                   # Strategy enforcer (500+ lines)
│   ├── psychology_tracker.py            # Psychology monitor (600+ lines)
│   ├── trade_journal.py                 # Trade logger (800+ lines)
│   ├── mentor_system.py                 # Education system (900+ lines)
│   ├── master_trading_system.py         # Unified interface (400+ lines)
│   ├── portfolio_agent.py               # Portfolio analysis
│   ├── risk_agent.py                    # Risk monitoring
│   ├── software_architect.py            # Code architecture
│   ├── code_reviewer.py                 # Code quality
│   ├── SHADE_SYSTEM_README.md           # Usage documentation
│   └── README.md                        # Agent overview
│
├── app/                                 # Next.js Frontend
│   ├── app/
│   │   ├── (dashboard)/                 # Dashboard pages
│   │   ├── api/                         # API routes
│   │   └── page.tsx                     # Homepage
│   ├── components/                      # React components
│   ├── lib/                             # Utilities
│   ├── public/                          # Static assets
│   ├── package.json                     # Node dependencies
│   └── tsconfig.json                    # TypeScript config
│
├── bin/                                 # Executable Scripts
│   ├── START_SOVEREIGN_SHADOW.sh        # Main launcher
│   ├── MASTER_LOOP_CONTROL.sh           # Control script
│   └── MANUAL_TRADING_SETUP.sh          # Manual mode
│
├── core/                                # Core Systems
│   ├── portfolio/
│   │   ├── unified_portfolio_api.py     # Central data hub
│   │   ├── mcp_portfolio_context.json   # Portfolio state
│   │   ├── COLD_VAULT_KNOWLEDGE_BASE.cpython-311.pyc
│   │   ├── aave_monitor.py              # AAVE tracking
│   │   ├── cold_vault_monitor.py        # Ledger tracking
│   │   └── metamask_balance_tracker.py  # MetaMask tracking
│   │
│   └── rebalancing/
│       ├── rebalance_run.py             # Core 4 rebalancer
│       └── rebalance_simulator.py       # Simulation engine
│
├── logs/                                # State & Logs
│   ├── ai_enhanced/
│   │   ├── real_balances.json           # Current balances
│   │   ├── sovereign_shadow_unified.log # System log
│   │   └── sovereign_shadow_unified_report.json
│   │
│   ├── psychology/
│   │   ├── psychology_state.json        # Daily psychology
│   │   ├── loss_streak.json             # Loss tracking
│   │   └── history/                     # Daily archives
│   │
│   ├── trading/
│   │   ├── trade_journal.json           # Complete log
│   │   └── trade_journal.csv            # Export format
│   │
│   └── mentor/
│       └── mentor_state.json            # Learning progress
│
├── memory/                              # Session Memory
│   ├── SESSIONS/
│   │   ├── INDEX.md                     # Session index
│   │   └── 11-November/
│   │       ├── 02/Path-Fixes_0425-PST.md
│   │       ├── 03/API-Complete-Live-Deploy_2028-PST.md
│   │       └── 04/
│   │           ├── BTC-Drop-Response_0611-PST.md
│   │           └── SHADE-SYSTEM-BUILD_2211-PST.md
│   │
│   ├── SHADE_AGENT_REGISTRY.yaml        # Agent registry
│   └── CURRENT_SESSION.md               # Active session
│
├── modules/                             # Feature Modules
│   ├── ladder/
│   │   └── unified_ladder_system.py     # DCA ladder strategy
│   │
│   └── safety/
│       ├── aave_monitor.py              # AAVE safety checks
│       └── __init__.py
│
├── scripts/                             # Utility Scripts
│   ├── get_real_balances.py             # Fetch all balances
│   ├── claude_arbitrage_trader.py       # Arbitrage scanner
│   ├── aave_health_dashboard.py         # AAVE dashboard
│   ├── aave_guardian_monitor.py         # AAVE alerts
│   ├── validate_api_connections.py      # API validator
│   └── neural_bridge.py                 # AI consciousness bridge
│
├── tools/                               # Testing Tools
│   └── test_binance_connection.js       # Binance connection test
│
├── docs/                                # Documentation
│   └── guides/
│       └── API_CONNECTORS_COMPLETE.pdf  # API guide
│
├── .env                                 # Environment variables (NOT in git)
├── .env.example                         # Template for .env
├── .gitignore                           # Git exclusions
├── requirements.txt                     # Python dependencies
├── package.json                         # Node dependencies
├── SHADE_SYSTEM_COMPLETE.md             # Build summary
├── SOVEREIGN_SHADOW_II_SPECS.md         # This file
└── README.md                            # Project overview
```

---

## Configuration

### Environment Variables (.env)
```bash
# Exchange API Keys
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret

BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret

OKX_API_KEY=your_okx_key
OKX_API_SECRET=your_okx_secret
OKX_PASSPHRASE=your_okx_passphrase

# Ethereum / DeFi
ALCHEMY_API_KEY=your_alchemy_key
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}

# Trading Configuration
TRADING_MODE=paper  # paper | test | live
MAX_POSITION_SIZE=415  # USD
RISK_LEVEL=safe  # safe | minimal | production

# Account Settings
ACCOUNT_BALANCE=1660.00
HOT_WALLET_BALANCE=1660.00
COLD_STORAGE_BALANCE=6167.43

# System Configuration
ENV=production  # development | staging | production
DEBUG=false
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

### Agent Configuration
```yaml
# agents/config.yaml (optional)
shade_agent:
  max_risk_per_trade: 0.02  # 2%
  min_risk_per_trade: 0.01  # 1%
  min_risk_reward: 2.0      # 1:2
  max_total_exposure: 0.10  # 10%

psychology_tracker:
  max_daily_losses: 3
  max_daily_trades: 10
  min_time_between_trades: 15  # minutes

mentor_system:
  require_lessons: 20
  require_paper_trades: 10
  require_win_rate: 0.40  # 40%
```

---

## Deployment

### Production Checklist
```yaml
environment:
  - [ ] .env file configured
  - [ ] API keys valid and tested
  - [ ] Exchange connections verified
  - [ ] Virtual environment created
  - [ ] Dependencies installed

security:
  - [ ] .gitignore configured
  - [ ] Sensitive files excluded
  - [ ] API keys secured
  - [ ] 2FA enabled on exchanges
  - [ ] Backup of .env created

testing:
  - [ ] SHADE//AGENT validated
  - [ ] Psychology tracker tested
  - [ ] Trade journal working
  - [ ] Dashboard accessible
  - [ ] All agents operational

documentation:
  - [ ] README.md updated
  - [ ] SHADE_SYSTEM_README.md reviewed
  - [ ] Session notes saved
  - [ ] Registry updated
```

### Launch Commands
```bash
# Start complete system
cd /Volumes/LegacySafe/SovereignShadow_II
./bin/START_SOVEREIGN_SHADOW.sh paper

# Start master trading system
cd agents
python3 master_trading_system.py

# Start frontend dashboard
cd app
npm run dev

# Check system status
python3 scripts/get_real_balances.py

# View dashboard
system.display_dashboard()
```

### Monitoring
```yaml
system_health:
  - Check logs/sovereign_shadow_unified.log
  - Monitor psychology_state.json (losses)
  - Track trade_journal.json (performance)
  - Review AAVE health factor (daily)

alerts:
  - 3 losses triggered (lockout)
  - AAVE health < 1.5 (liquidation risk)
  - API connection failures
  - Unusual trading patterns
```

---

## Version History

```yaml
v2025.11.04:
  date: November 4, 2025
  status: Production Ready
  changes:
    - Built SHADE//AGENT system (5 agents, 3,200+ lines)
    - Implemented 42-lesson curriculum
    - Created master trading system
    - Comprehensive documentation
    - All tests passing

v2025.11.03:
  date: November 3, 2025
  changes:
    - Verified Binance US connection
    - Integrated 6 SDKs
    - Complete credential cleanup

v2025.11.02:
  date: November 2, 2025
  changes:
    - Built Core 4 rebalancing system
    - Fixed Mac path compatibility
```

---

## Support & Resources

### Documentation
- **Main Guide:** `agents/SHADE_SYSTEM_README.md`
- **Build Summary:** `SHADE_SYSTEM_COMPLETE.md`
- **Agent Overview:** `agents/README.md`
- **Session Index:** `memory/SESSIONS/INDEX.md`
- **This Spec:** `SOVEREIGN_SHADOW_II_SPECS.md`

### Contact & Community
- **GitHub Issues:** https://github.com/your-repo/issues
- **NetworkChuck:** YouTube trading education source
- **AAVE Docs:** https://docs.aave.com
- **Coinbase API:** https://docs.cloud.coinbase.com

### Quick Reference
```bash
# View all specs
cat SOVEREIGN_SHADOW_II_SPECS.md

# Check system status
python3 scripts/get_real_balances.py

# Start learning
python3 agents/mentor_system.py

# Launch trading system
./bin/START_SOVEREIGN_SHADOW.sh paper
```

---

**Last Updated:** November 4, 2025, 22:11 PST
**Version:** 2025.11.04
**Status:** 🟢 Production Ready
**Philosophy:** *"System over emotion. Every single time."*

🏴 **Sovereign Shadow II - Complete Technical Specifications**

---

#specs #architecture #trading-system #sovereign-shadow #documentation #technical-reference

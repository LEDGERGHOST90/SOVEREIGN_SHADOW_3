# 🏴 SOVEREIGN SHADOW TRADING SYSTEM

**Philosophy:** *"Fearless. Bold. Smiling through chaos."*

---

## 🎯 SYSTEM OVERVIEW

A **professional-grade cryptocurrency trading platform** with multi-exchange arbitrage, AI-powered decision making, hardware wallet integration, and comprehensive risk management.

### 💰 Capital Structure
```
Total Portfolio:     $8,260
├── Cold Storage:    $6,600 (Ledger, READ-ONLY)
├── Active Trading:  $1,660 (Coinbase)
└── Monthly Fuel:    $500 (VA Stipend)

Target: $50,000 by Q4 2025
```

### 🏗️ Architecture
```
SovereignShadow/
├── sovereign_legacy_loop/      # Next.js trading dashboard
├── shadow_sdk/                 # Python AI toolkit
├── config/                     # Exchange integrations
├── scripts/                    # Automation utilities
└── Core Python systems         # Orchestration & execution
```

---

## 🚀 QUICK START

### 1️⃣ Clone & Setup
```bash
git clone https://github.com/Memphispradda/SovereignShadow.git
cd SovereignShadow

# Setup environment
cp env.template .env
nano .env  # Add your API keys

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd sovereign_legacy_loop
npm install
cd ..
```

### 2️⃣ Configure API Keys

#### Required APIs:
1. **Coinbase Advanced Trade**
   - Go to: https://portal.cloud.coinbase.com/access/api
   - Create "Cloud API Trading Keys" (NOT legacy API)
   - Add your IP to allowlist: `YOUR_IP/32`
   - Copy key name and private key to `.env`

2. **OKX Exchange**
   - Go to: https://www.okx.com/account/my-api
   - Create API with Read/Trade/Withdraw permissions
   - Add API key, secret, passphrase to `.env`

3. **Kraken** (Optional)
   - Go to: https://www.kraken.com/u/security/api
   - Create API with Read & Trade permissions

4. **Binance US** (Optional)
   - Go to: https://www.binance.us/en/usercenter/settings/api-management

#### Environment File (`.env`):
```bash
# CAPITAL
TOTAL_PORTFOLIO_VALUE=8260
ACTIVE_TRADING_CAPITAL=1660
LEDGER_COLD_STORAGE=6600

# OKX
OKX_KEY=your_key_here
OKX_SECRET=your_secret_here
OKX_PASSPHRASE=your_passphrase_here

# COINBASE
COINBASE_API_KEY=organizations/YOUR-ORG/apiKeys/YOUR-KEY
COINBASE_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----\nYOUR_KEY\n-----END EC PRIVATE KEY-----\n

# SAFETY LIMITS (2% RULE)
MAX_POSITION_SIZE=33.20        # 2% of capital
MAX_DAILY_EXPOSURE=166.00      # 10% max per day
STOP_LOSS_PER_TRADE=16.60      # 1% max loss
MAX_CONSECUTIVE_LOSSES=3
```

### 3️⃣ Validate APIs
```bash
python3 scripts/validate_api_connections.py
```

### 4️⃣ Launch System
```bash
# Main orchestrator
./START_SOVEREIGN_SHADOW.sh

# Trading dashboard
./LAUNCH_LEGACY_LOOP.sh

# Monitor portfolio
python3 instant_market_snapshot.py
python3 check_aave_position.py
```

---

## 🤖 CORE SYSTEMS

### 🎯 Orchestration
- **`sovereign_shadow_orchestrator.py`** - Main system coordinator
- **`MASTER_CONNECTION_MAP.py`** - Multi-exchange API manager
- **`strategy_knowledge_base.py`** - AI trading intelligence

### 💼 Portfolio Management
- **`REAL_PORTFOLIO_BRIDGE.py`** - Portfolio sync across exchanges
- **`REAL_PORTFOLIO_CONNECTOR.py`** - Exchange connector layer
- **`check_aave_position.py`** - DeFi position monitoring
- **`instant_market_snapshot.py`** - Real-time market data
- **`live_market_scanner.py`** - Multi-exchange scanning

### 📊 Trading Execution
- **`EXECUTE_CDP_TRADE.py`** - Coinbase trade execution
- **`EXECUTE_MANUAL_TRADE.py`** - Manual trading interface
- **`shadow_scope.py`** - Market analysis engine

### 🛡️ Risk Management
- **`SAFETY_RULES_IMPLEMENTATION.py`** - 2% risk enforcement
- **`CRISIS_MANAGEMENT_PLAYBOOK.py`** - Emergency protocols
- **Position sizing:** 2% max per trade
- **Daily exposure:** 10% portfolio max
- **Stop loss:** 1% per trade
- **Circuit breaker:** Stop after 3 consecutive losses

---

## 🧠 AI INTEGRATION

### Claude SDK & MCP Server
The system integrates Claude AI via Model Context Protocol (MCP):

```bash
# MCP Server Location
~/ClaudeSDK/mcp_exchange_server.py

# Available MCP Tools:
- get_multi_exchange_prices      # Price comparison
- detect_arbitrage_opportunities # Arb scanner
- get_portfolio_aggregation      # Total portfolio
- get_best_execution_route       # Smart routing
- monitor_exchange_status        # Health checks
- connect_ledger_live            # Hardware wallet
```

**Configuration:** `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "sovereign-shadow-trading": {
      "command": "python3",
      "args": ["/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/ClaudeSDK/mcp_exchange_server.py"]
    }
  }
}
```

### Obsidian Encrypted Vault
For maximum security, store API keys in an encrypted Obsidian vault:

```
ObsidianVault/
├── secrets/
│   ├── api-keys/
│   │   ├── OKX.md          (encrypted)
│   │   ├── Coinbase.md     (encrypted)
│   │   └── Kraken.md       (encrypted)
│   └── capital/
│       └── portfolio.md    (encrypted)
└── .obsidian/              (not committed)
```

**Code loads from vault via:** `ObsidianEncryptedConfig` class in `sovereign_legacy_loop/app/lib/obsidian-encrypted-config.ts`

---

## 📊 TRADING STRATEGIES

### 1. Cross-Exchange Arbitrage
- Monitor price differences across OKX, Coinbase, Kraken
- Execute when spread > 0.3% (after fees)
- Target: 5-10 trades/day @ 0.5% avg profit

### 2. AI-Powered Scalping
- 1-minute and 15-minute timeframes
- Claude AI analyzes order book depth
- Entry on momentum + volume confluence
- Target: 0.3-0.5% per trade

### 3. Multi-Timeframe Analysis
- **1m/15m:** Scalping opportunities
- **4h/6h:** Swing positions
- **Daily/Weekly:** Position trading
- **Monthly:** Strategic accumulation

### 4. Ledger History Analysis
- 160 days of trading data (May 12 - Oct 17, 2025)
- AI-optimized strategies based on historical performance
- Pattern recognition from past winners
- Risk-adjusted position sizing

### 5. DeFi Leverage Management
- **Aave Position:** WETH collateral → Borrow USDC
- **Health Factor:** Monitor continuously (target > 2.0)
- **Liquidation Protection:** Auto-alerts at 1.5
- **Profit Deployment:** Loop borrowed USDC into active trading

---

## 🐳 DEV CONTAINER SETUP

For isolated, consistent development:

```bash
# Install Docker Desktop
# Install Cursor (or VS Code)

# Open in container
cursor --open-in-dev-container /Volumes/LegacySafe/SovereignShadow

# Or use helper script
./open-dev-container.sh
```

**Benefits:**
- Isolated environment
- Pre-configured dependencies
- Consistent across machines
- No local Python/Node conflicts

**Docs:** See `.devcontainer/` directory

---

## 🛡️ SECURITY

### Protected by `.gitignore`
- All `.env` files
- API keys and secrets
- Live trading logs
- Real balance data
- Obsidian encrypted vault
- Personal strategies

### Never Commit:
- API keys
- Private keys
- Passphrases
- Wallet addresses
- Real portfolio data
- Trading logs with PnL

### Setup Template:
Use `env.template` for clean clones - fill in YOUR keys, never commit real `.env`

---

## 📚 DOCUMENTATION

### Essential Docs
- **`README.md`** (this file) - Main documentation
- **`GITHUB_REPOSITORY_MASTER_PLAN.md`** - Repository structure & security
- **`ABACUS_AI_TRADING_INTELLIGENCE_HANDOFF.md`** - Abacus AI integration
- **`PROMPT_FOR_NEXT_SESSION.md`** - Session continuity
- **`Master_LOOP_Creation/`** - Architecture deep dive

### Key Concepts
1. **2% Rule:** Never risk more than 2% per trade
2. **Portfolio Isolation:** Cold storage (Ledger) vs Active trading (Coinbase)
3. **Multi-Exchange:** Compare prices, execute on best venue
4. **Hardware Security:** Ledger Live for signing high-value trades
5. **AI Orchestration:** Claude + GPT + DeepSeek for decision support

---

## 🚨 MONITORING & ALERTS

### Health Checks
```bash
# Portfolio snapshot
python3 instant_market_snapshot.py

# Aave position health
python3 check_aave_position.py

# Exchange connectivity
python3 scripts/validate_api_connections.py

# System monitor
./monitor_empire.sh
```

### Emergency Protocols
```bash
# Stop all trading
./save_my_empire.sh

# Crisis management
python3 CRISIS_MANAGEMENT_PLAYBOOK.py
```

---

## 📈 PERFORMANCE TRACKING

### Metrics
- **Daily PnL:** Track via `logs/ai_enhanced/`
- **Win Rate:** Target > 60%
- **Risk/Reward:** Minimum 1:2 ratio
- **Max Drawdown:** < 10% of active capital
- **Sharpe Ratio:** Target > 2.0

### Abacus AI Dashboard
- **Live System:** https://legacyloopshadowai.abacusai.app/
- **Auth:** pilot@consciousness.void
- **Features:** Real-time PnL, strategy performance, risk metrics

---

## 🔧 UTILITIES

### Launchers
- `START_SOVEREIGN_SHADOW.sh` - Main system
- `LAUNCH_LEGACY_LOOP.sh` - Web dashboard
- `MANUAL_TRADING_SETUP.sh` - Trading setup

### Monitoring
- `monitor_empire.sh` - System health
- `save_my_empire.sh` - Emergency backup

### Configuration
- `config/ledger_integration.py` - Hardware wallet
- `config/ledger_wallet_integration.py` - Ledger Live
- `config/real_exchange_integration.py` - Exchange APIs

---

## 🎓 PHILOSOPHY

**Sovereign Shadow** embodies:
1. **Self-custody:** Your keys, your crypto
2. **Risk Management:** 2% rule, always
3. **AI Augmentation:** Humans + AI > Either alone
4. **Multi-Exchange:** Never depend on one platform
5. **Continuous Learning:** Every trade teaches
6. **Cold Storage Discipline:** Protect the base
7. **Strategic Patience:** Wait for your pitch

*"The market rewards the patient, the disciplined, and those who smile through chaos."*

---

## 🤝 CONTRIBUTION

This is a **personal trading system**, but the architecture is designed for:
- Code reviews
- AI assistant collaboration
- Security audits
- Portfolio scaling

**For Abacus AI Integration:** See `ABACUS_AI_TRADING_INTELLIGENCE_HANDOFF.md`

---

## 📞 SUPPORT

**System Status:** 🟢 OPERATIONAL

**Components:**
- ✅ Coinbase API (configured)
- ✅ OKX API (configured)
- ✅ Claude MCP Server (running)
- ✅ Ledger Integration (ready)
- ⏳ Kraken API (optional)
- ⏳ Binance US API (optional)

**Next Session:** See `PROMPT_FOR_NEXT_SESSION.md`

---

## 📜 LICENSE

**Private Proprietary System**

This repository contains a personal trading system with proprietary strategies. While the code architecture is viewable for review/collaboration purposes, the trading strategies, AI models, and market intelligence are confidential.

**Security Notice:** Never commit API keys, secrets, or real portfolio data.

---

**SOVEREIGN SHADOW** | *Trading with consciousness, executing with precision* 🏴

---

*Built with: Python, TypeScript, Next.js, Claude AI, Obsidian, Ledger, Docker*

*Last Updated: October 19, 2025*

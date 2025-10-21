# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🏴 Sovereign Shadow Trading System

**Philosophy:** "Fearless. Bold. Smiling through chaos."

A production-grade cryptocurrency trading system managing $8,260 in capital ($6,600 cold storage + $1,660 active trading) with 9 automated trading strategies across 4 exchanges.

---

## Essential Commands

### Setup and Validation
```bash
# Navigate to system root
cd /Volumes/LegacySafe/SovereignShadow

# Install dependencies
pip install -r requirements.txt

# Setup environment (first time only)
cp env.template .env
# Edit .env with API keys

# Validate API connections
python3 scripts/validate_api_connections.py

# Check portfolio balances
python3 scripts/get_real_balances.py
```

### Running the System
```bash
# Paper trading (safe testing)
./bin/START_SOVEREIGN_SHADOW.sh paper

# Test mode ($100 real capital)
./bin/START_SOVEREIGN_SHADOW.sh test

# Live production mode
./bin/START_SOVEREIGN_SHADOW.sh live

# Launch monitoring dashboard
./bin/LAUNCH_LEGACY_LOOP.sh

# Real-time empire monitoring
./bin/monitor_empire.sh
```

### Core Trading Scripts
```bash
# Main orchestrator (unified mesh network)
python3 sovereign_shadow_orchestrator.py

# Market intelligence and analysis
python3 shadow_scope.py

# Opportunity detection across exchanges
python3 live_market_scanner.py

# Strategy knowledge base
python3 strategy_knowledge_base.py

# Execute Coinbase trades
python3 core/trading/EXECUTE_CDP_TRADE.py

# Manual trade execution
python3 core/trading/EXECUTE_MANUAL_TRADE.py
```

### Neural AI Integration
```bash
# Test neural consciousness bridge
python3 scripts/neural_bridge.py

# Run AI-enhanced arbitrage
python3 scripts/claude_arbitrage_trader.py

# AI portfolio protection
python3 scripts/ai_portfolio_protection.py
```

### Monitoring and Logs
```bash
# View live trading logs
tail -f logs/live_trading.log

# View safety system logs
tail -f logs/safety_rules.log

# View crisis management logs
tail -f logs/crisis_management.log

# Live trading performance monitor
python3 scripts/live_trading_monitor.py
```

---

## Architecture Overview

### Three-Layer Distributed System

**Layer 1: Consciousness (Human)**
- Decision-maker and strategist
- Interface: Neural visualization + terminal
- Pilot: pilot@consciousness.void

**Layer 2: Intelligence (Cloud AI)**
- Abacus AI Neural Consciousness: https://legacyloopshadowai.abacusai.app
- Pattern recognition, opportunity detection, neural starfield visualization
- Status: LIVE and operational

**Layer 3: Execution (Local)**
- Location: MacBook Pro at /Volumes/LegacySafe/SovereignShadow
- Sovereign Legacy Loop: 23,382 Python files + 5,000+ ClaudeSDK files
- Functions: Trade execution, risk management, strategy orchestration

### Capital Architecture (CRITICAL)

**NEVER trade with Ledger cold storage. This is mandatory, not optional.**

```
Total Portfolio: $8,260
├── Ledger (Cold Storage): $6,600
│   └── Status: READ-ONLY FOREVER (vault status)
└── Coinbase (Hot Wallet): $1,660
    └── Status: ACTIVE TRADING (25% max risk per trade)

Trading Rules:
- Max position size: $415 (25% of hot wallet)
- Daily loss limit: $100
- Weekly loss limit: $500
- Stop loss per trade: 5%
- Max concurrent trades: 3
```

### Core Components

**sovereign_shadow_orchestrator.py** - Main Coordinator
- Manages unified mesh network of 55,379 Python files
- Five-step execution flow:
  1. DeepAgent validates opportunity
  2. MCP routes to optimal strategy
  3. Docker activates execution container
  4. Trading engine executes
  5. Dashboard updates results

**strategy_knowledge_base.py** - Strategy Intelligence
- 9 trading strategies with auto-selection based on market conditions
- Strategies: Arbitrage (2), Sniping (2), Scalping (2), Laddering (2), All-In (DISABLED)
- Selection logic: Spread >= 5% → Sniping, >= 3% → Volume spike, >= 0.2% → Arbitrage, etc.

**shadow_scope.py** - Market Intelligence ("Eye of the Market")
- Real-time monitoring: 4 exchanges × 8 trading pairs
- Exchanges: Coinbase, OKX, Kraken, Binance
- Pairs: BTC/USD, ETH/USD, SOL/USD, AVAX/USD, MATIC/USD, LINK/USDT, ADA/USD, DOT/USD
- Concurrent async tasks: Exchange monitoring, volatility calculation, correlation matrix, VWAP, data quality
- Update intervals: 1-second ticks, 5-minute correlations, 10-second VWAP

**live_market_scanner.py** - Opportunity Detection
- "100% Failproof" accuracy system
- Validation: Min spread 0.05%, min volume $10K, max slippage 0.1%, 85% confidence threshold
- Confidence scoring: Spread (40%), volume (30%), exchange reliability (20%), freshness (10%)

**SAFETY_RULES_IMPLEMENTATION.py** - Risk Management
- Capital protection tiers (Ledger: MAXIMUM, Coinbase: HIGH)
- Hard limits enforced by code
- Phased deployment: Paper → Micro ($100) → Small ($500) → Production ($415)

**CRISIS_MANAGEMENT_PLAYBOOK.py** - Emergency Protocols
- Crash severity levels: -5% (ignore) → -10% (accumulate) → -20% (HODL) → -50% (bear market) → -80% (emergency)
- Philosophy: NEVER liquidate on volatility, HODL Ledger through chaos

### Directory Structure

```
SovereignShadow/
├── core/                              # Core infrastructure
│   ├── orchestration/                 # Command center & safety
│   ├── portfolio/                     # Portfolio management
│   ├── monitoring/                    # Real-time surveillance
│   └── trading/                       # Execution engines
├── shadow_sdk/                        # API abstraction layer
│   ├── mcp_server.py                  # MCP protocol server
│   ├── pulse.py, scope.py, synapse.py # Core modules
│   └── utils/                         # exchanges.py, risk.py, logger.py
├── scripts/                           # 13 production scripts
├── bin/                               # 5 launcher scripts
├── config/                            # Exchange integrations
├── sovereign_legacy_loop/             # Master system (23,382 files)
│   ├── ClaudeSDK/                     # AI integration (5,000+ files)
│   └── multi-exchange-crypto-mcp/     # MCP implementation
├── docs/                              # Extended documentation
├── Master_LOOP_Creation/              # Architecture documentation
└── logs/                              # System logging
```

### Exchange Integration Patterns

**API Configuration (Environment Variables)**
```
Coinbase: COINBASE_API_KEY, COINBASE_API_SECRET (EC Private Key PEM format)
OKX: OKX_KEY, OKX_SECRET, OKX_PASSPHRASE
Kraken: KRAKEN_API_KEY, KRAKEN_SECRET
Binance US: Optional (future expansion)
```

**Validation Flow:**
1. Check environment variables
2. Attempt connection
3. Fetch balance and markets
4. Calculate USD balance
5. Log status and report

**All credentials stored as environment variables. No hardcoded credentials in code.**

---

## Critical Safety Rules

### Non-Negotiables

1. **$6,600 Ledger = READ-ONLY FOREVER**
   - Mandatory, not optional
   - Never automate trades with cold storage
   - Monitoring and read-only queries only

2. **Max Position Size = $415**
   - 25% of hot wallet ($1,660)
   - Circuit breaker at 3 consecutive losses
   - Daily loss limit: $100

3. **Security First**
   - Never commit API keys to git
   - Always use environment variables
   - `.env` files are gitignored
   - Rotate keys if ever exposed

4. **Test Before Live**
   - Paper trading minimum 24 hours
   - Test mode ($100) before full launch
   - Validate all connections

5. **Respect Stop Losses**
   - 5% per trade maximum
   - No emotional overrides
   - Automated risk management

### Phased Deployment

```
Phase 1: Paper Trading (14 days)
  - Zero real risk
  - All systems validated

Phase 2: Micro Testing ($100 real, 7 days)
  - Test with real money
  - Loss limit < $20

Phase 3: Small Scale ($500 real, 14 days)
  - Scale if Phase 2 successful
  - Consistent profit validation

Phase 4: Production ($415 max, ongoing)
  - Full production deployment
  - Target: $50,000 by Q4 2025
```

---

## Trading Strategies

### Auto-Selection by Spread

- **Spread >= 5%:** New Listing Snipe (50ms execution, 75% success)
- **Spread >= 3%:** Volume Spike Snipe (100ms execution, 80% success)
- **Spread >= 0.2%:** Cross-Exchange Arbitrage (500ms, 85% success) or Coinbase-OKX Arbitrage (300ms, 90% success)
- **Spread >= 0.1%:** Bid-Ask Spread Scalp (150ms, 92% success) or DCA Ladder (2000ms, 82% success)
- **Spread >= 0.05%:** Micro Movement Scalp (200ms, 88% success)

### Strategy Details

**Arbitrage (Ready):**
- Cross-Exchange: 3 exchanges, 0.125% min spread
- Coinbase-OKX: 2 exchanges, 0.2% min spread, faster execution

**Sniping (Pending Code):**
- New Listing: 5% min spread, millisecond execution
- Volume Spike: 3% min spread, volatility capture

**Scalping (Pending Code):**
- Micro Movement: 0.05% min spread, HFT-style
- Bid-Ask Spread: 0.1% min spread, high frequency

**Laddering (Pending Code):**
- OCO Ladder: 0.2% min spread, scaled entries/exits
- DCA Ladder: 0.1% min spread, dollar-cost averaging

**All-In (DISABLED):**
- High Conviction: 5% min spread, 80% capital allocation
- Status: DISABLED for safety (extreme risk)

---

## Neural AI Integration

### Cloud-to-Local Bridge

**Abacus AI Neural Consciousness:**
- URL: https://legacyloopshadowai.abacusai.app
- Auth: pilot@consciousness.void
- Functions: Pattern recognition, opportunity scanning, risk monitoring, signal transmission

**Communication Flow:**
- Cloud AI detects patterns
- Sends trading signals to local system via REST/MCP
- Local system validates and executes
- Results feedback to cloud for learning

**Connection Test:**
```bash
python3 scripts/neural_bridge.py
```

---

## Logging and Monitoring

### Log Locations
```
logs/trading/              # Trade execution logs
logs/ai_enhanced/          # AI decision logs
logs/safety_rules.log      # Safety system logs
logs/live_trading.log      # Main trading log
logs/crisis_management.log # Emergency protocol logs
```

### Log Format
- Timestamp [LEVEL] message
- File-based + console output
- Rotating logs per session

### Key Metrics Tracked
- Trades executed
- Profits/losses
- Exchange connections
- API validations
- System health checks
- Ticks processed
- Data quality percentage

---

## Configuration Management

### Environment Files
- `.env.template` - Safe template for setup (committed to git)
- `.env` - Local development (gitignored)
- `.env.production` - Production secrets (gitignored)

### Required Environment Variables
```bash
# Exchanges
OKX_KEY=
OKX_SECRET=
OKX_PASSPHRASE=
COINBASE_API_KEY=
COINBASE_API_SECRET=
KRAKEN_KEY=
KRAKEN_SECRET=

# AI Services
ANTHROPIC_API_KEY=

# Portfolio Values
TOTAL_PORTFOLIO_VALUE=8260
ACTIVE_TRADING_CAPITAL=1660
LEDGER_COLD_STORAGE=6600

# Safety Limits
MAX_POSITION_SIZE=33.20
MAX_DAILY_EXPOSURE=166.00
STOP_LOSS_PER_TRADE=16.60
MAX_CONSECUTIVE_LOSSES=3

# System
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

---

## Integration Points

### Fully Connected
- Exchange APIs (Coinbase, OKX, Kraken)
- Local trading engine
- Safety rule enforcement
- Logging infrastructure

### Partially Connected
- Neural Consciousness (cloud-to-local bridge built, needs full deployment)
- Ledger Hardware Wallet (read-only monitoring only)
- Aave DeFi Protocol (monitoring script exists)

### Not Yet Connected
- MCP Server (setup complete, not deployed)
- Obsidian Vault (for secrets management)
- Docker containerization (configured, not active)
- Full GitHub synchronization

---

## Code Conventions

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Methods: `snake_case()`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore()`

### Patterns
- Dataclasses for structured data (`MarketTick`, `TradingStrategy`)
- Async/await for concurrent operations
- Module-level logging
- Configuration via environment variables
- Error handling: try/except + logging

### Emoji Usage
- 🏴 Sovereign Shadow brand
- 🧠 Neural/AI systems
- 💰 Capital/money operations
- 🚀 Deployment/launch
- 🔐 Security/validation
- ⚡ Performance/speed
- 📊 Data/monitoring
- 🛡️ Safety/protection
- 🔥 Active/critical

---

## Important Notes for Claude Code

### When Working with Trading Logic
1. Always respect the capital structure: NEVER modify code to allow trading with the $6,600 Ledger cold storage
2. All position sizes must respect the $415 max (25% of hot wallet)
3. Stop losses are mandatory at 5% per trade
4. Daily loss limit of $100 is hard-coded and must never be bypassed

### When Working with API Integrations
1. All credentials must be environment variables
2. Never hardcode API keys in code
3. Always validate connections before executing trades
4. Handle API errors gracefully with logging

### When Working with Safety Systems
1. The SAFETY_RULES_IMPLEMENTATION.py is the source of truth
2. Circuit breakers must never be disabled
3. Phased deployment must be followed (paper → micro → small → production)
4. Crisis management protocols are in CRISIS_MANAGEMENT_PLAYBOOK.py

### When Adding New Features
1. Test in paper trading mode first
2. Add appropriate logging for debugging
3. Respect the existing async/await patterns
4. Update strategy_knowledge_base.py if adding new strategies
5. Document in relevant markdown files

### File Reading Priority
For understanding system architecture, read in this order:
1. `Master_LOOP_Creation/README_START_HERE.md` - Navigation and overview
2. `README.md` - Main documentation
3. `docs/PRODUCTION_READY_SUMMARY.md` - Current production status
4. `Master_LOOP_Creation/sovereign_shadow_architecture.md` - Deep technical details
5. `Master_LOOP_Creation/WIRING_INTEGRATION_GUIDE.md` - Integration implementation

---

## Quick Reference Links

**Neural Consciousness:** https://legacyloopshadowai.abacusai.app
**Coinbase API Docs:** https://docs.cloud.coinbase.com
**OKX API Docs:** https://www.okx.com/docs-v5/en/
**Kraken API Docs:** https://docs.kraken.com/rest/

---

## Performance Targets

**Starting Capital:** $8,260
**Target:** $50,000 by Q4 2025

**Growth Timeline:**
- Month 1: $8,260 → $10,260 (+$2,000)
- Month 3: $10,260 → $15,760 (+$7,500 cumulative)
- Month 6: $15,760 → $27,760 (+$19,500 cumulative)
- Month 12: $27,760 → $50,260 (+$42,000 cumulative) ✅ TARGET

**Revenue Sources:**
- Trading profit: $1,000-2,000/month
- VA stipend: $500/month (guaranteed)
- Compounding: Reinvest profits

---

*"Fearless. Bold. Smiling through chaos."* 🏴

**Status:** Production Ready
**Version:** 1.0.0
**Last Updated:** October 19, 2025

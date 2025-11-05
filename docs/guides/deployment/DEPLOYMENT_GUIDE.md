# 🚀 SOVEREIGN SHADOW II - DEPLOYMENT GUIDE

**Production-Grade Crypto Portfolio & Trading System**

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Keys Setup](#api-keys-setup)
6. [Security Checklist](#security-checklist)
7. [First Run](#first-run)
8. [Agent System](#agent-system)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 SYSTEM OVERVIEW

Sovereign Shadow II is a unified cryptocurrency portfolio management and trading system featuring:

- **Portfolio Tracking**: Ledger, MetaMask, AAVE, Multi-exchange
- **DeFi Integration**: AAVE v3 monitoring with health factor alerts
- **Automated Trading**: Ladder trading, arbitrage detection, momentum signals
- **Risk Management**: 21-point preflight checks, position limits, emergency stops
- **AI Agents**: Portfolio analysis, risk assessment, code review
- **Glass Website**: Next.js dashboard with real-time data

### Architecture

```
SovereignShadow_II/
├── agents/               # Autonomous AI agents
├── modules/safety/       # AAVE monitor, risk controls
├── core/portfolio/       # Portfolio tracking & rebalancing
├── scripts/              # Trading strategies, utilities
├── app/                  # Next.js Glass website
├── logs/                 # System logs, reports
└── .env                  # Configuration (NOT in Git)
```

---

## ⚙️ PREREQUISITES

### Required Software

```bash
# Python 3.9+
python3 --version

# Node.js 18+ and npm
node --version
npm --version

# Git
git --version
```

### Required Accounts

You'll need accounts at:

- **Binance US** (or Binance.com if outside US)
- **Coinbase** (for CDP SDK)
- **OKX** (optional - for sniper exchange)
- **Kraken** (optional - for primary trading)
- **Infura** (Ethereum RPC)
- **AbacusAI** (for AI features)

---

## 📦 INSTALLATION

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/SovereignShadow_II.git
cd SovereignShadow_II
```

### 2. Python Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Node.js Setup

```bash
cd app
npm install --legacy-peer-deps
cd ..
```

---

## 🔧 CONFIGURATION

### 1. Create .env File

```bash
cp .env.example .env
```

### 2. Edit .env

Open `.env` in your editor and fill in ALL required values:

```bash
# CRITICAL: Never commit this file to Git!
nano .env  # or use your preferred editor
```

---

## 🔑 API KEYS SETUP

### Binance US

1. Go to: https://www.binance.us/en/usercenter/settings/api-management
2. Create new API key
3. **Enable IP Restrictions** (highly recommended)
4. Copy to `.env`:
   ```
   BINANCE_US_API_KEY=your_key_here
   BINANCE_US_SECRET_KEY=your_secret_here
   ```

### Coinbase (CDP SDK)

1. Go to: https://portal.cdp.coinbase.com/projects/api-keys
2. Create new API key
3. Download the JSON file
4. Copy to `.env`:
   ```
   COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
   COINBASE_API_SECRET='-----BEGIN EC PRIVATE KEY-----
   Your-Key-Here
   -----END EC PRIVATE KEY-----'
   ```

### OKX (Optional)

1. Go to: https://www.okx.com/account/my-api
2. Create API key
3. **Enable IP Restrictions**
4. Copy to `.env`:
   ```
   OKX_API_KEY=your_key
   OKX_SECRET_KEY=your_secret
   OKX_PASSPHRASE='your_passphrase'
   ```

### Infura (Ethereum RPC)

1. Go to: https://app.infura.io/dashboard
2. Create new project
3. Copy Project ID
4. Add to `.env`:
   ```
   INFURA_PROJECT_ID=your_project_id
   INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   ```

### AbacusAI

1. Go to: https://abacus.ai/app/profile/apikey
2. Generate API key
3. Copy to `.env`:
   ```
   ABACUSAI_API_KEY=your_key_here
   ```

### Database (PostgreSQL)

If using AbacusAI's managed database:

```
DATABASE_URL='postgresql://user:password@host:port/database?connect_timeout=15'
```

### NextAuth Secret

Generate a secure random string:

```bash
openssl rand -base64 32
```

Add to `.env`:
```
NEXTAUTH_SECRET=your_generated_secret_here
```

### Encryption Key

Generate 64-character hex key:

```bash
openssl rand -hex 32
```

Add to `.env`:
```
ENCRYPTION_KEY=your_generated_key_here
```

### Ledger Address

Add your Ethereum address from Ledger:

```
LEDGER_ETH_ADDRESS=0xYourAddressHere
```

---

## 🛡️ SECURITY CHECKLIST

Before running the system, verify:

### ✅ Environment File

- [ ] `.env` exists and has all required values
- [ ] `.env` is NOT tracked by Git (`git status` should not show it)
- [ ] `.env.example` has no real credentials

### ✅ API Keys

- [ ] All API keys have IP restrictions enabled (exchange APIs)
- [ ] API keys have appropriate permissions (read, trade, withdraw)
- [ ] No API keys hardcoded in Python/JavaScript files

### ✅ Safety Limits

Verify these settings in `.env`:

```bash
# Ledger protection
ALLOW_LEDGER_WITHDRAWALS=0  # Keep at 0 unless you need withdrawals

# DeFi protection
ALLOW_DEFI_ACTIONS=0  # Keep at 0 until you're ready
ALLOW_BRIDGE_OPERATIONS=0
EMERGENCY_STOP_DEFI=0

# Risk limits
MAX_SINGLE_DEFI_TRADE_PERCENT=5
MAX_DAILY_DEFI_VOLUME_PERCENT=15
MAX_SLIPPAGE_TOLERANCE=5.0
DEFAULT_SLIPPAGE_TOLERANCE=0.5
```

### ✅ Trading Configuration

```bash
# Exchange selection
PRIMARY_TRADE_EXCHANGE=kraken  # Your primary exchange
SNIPER_EXCHANGE=okx
FIAT_RAIL_EXCHANGE=binanceus

# Environment
TRADING_ENV=production  # or 'development' for testing
ALLOW_LIVE_EXCHANGE=1  # 1 = production, 0 = simulation
```

### ✅ Run Security Audit

Before first run:

```bash
python3 scripts/github_security_audit.py
```

Should output: `✅ No sensitive data found!`

If it finds secrets, review the findings in `logs/security_audit_detailed.json`

---

## 🚀 FIRST RUN

### 1. Test Portfolio API

```bash
python3 core/portfolio/unified_portfolio_api.py
```

Expected output:
```
✅ UNIFIED PORTFOLIO SNAPSHOT GENERATED
Total Portfolio Value: $X,XXX.XX
```

### 2. Test AAVE Monitor

```bash
python3 modules/safety/aave_monitor_v2.py
```

Expected output:
```
✅ Provider: Llama RPC
Chain: Ethereum Mainnet (ID: 1)
Health Factor: X.XX
```

### 3. Run Portfolio Agent

```bash
python3 agents/portfolio_agent.py
```

Expected output:
```
✅ PORTFOLIO ANALYSIS COMPLETE
Recommendations: [...]
```

### 4. Start Glass Website

```bash
cd app
npm run dev
```

Open: http://localhost:3000

---

## 🤖 AGENT SYSTEM

The system includes 4 autonomous AI agents:

### 1. Portfolio Agent

**Purpose**: Analyzes portfolio allocation and generates rebalancing recommendations

```bash
python3 agents/portfolio_agent.py
```

**Output**: JSON report in `logs/portfolio_agent_report.json`

### 2. Risk Agent

**Purpose**: Monitors AAVE health factor and exchange exposure

```bash
python3 agents/risk_agent.py
```

**Output**: Risk score (0-100), alerts for critical issues

### 3. Software Architect

**Purpose**: Analyzes codebase structure and designs improvements

```bash
python3 agents/software_architect.py
```

**Output**: Architecture analysis and recommendations

### 4. Code Reviewer

**Purpose**: Reviews Python files for bugs and security issues

```bash
python3 agents/code_reviewer.py
```

**Output**: List of issues found with severity levels

---

## 🔧 TROUBLESHOOTING

### "Missing LEDGER_ETH_ADDRESS in .env"

**Solution**: Add your Ethereum address to `.env`:
```
LEDGER_ETH_ADDRESS=0xYourAddressHere
```

### "No working mainnet provider"

**Problem**: All RPC providers failed

**Solution**: Check your Infura/Alchemy keys in `.env`, or use public RPCs (already configured as fallbacks)

### Portfolio API returns empty data

**Problem**: Exchange APIs not responding

**Solution**:
1. Verify API keys in `.env`
2. Check API key permissions on exchange
3. Verify IP restrictions allow your IP
4. Check exchange API status

### AAVE Health Factor shows "UNKNOWN"

**Problem**: No debt on AAVE

**Solution**: This is normal if you have no active borrows

### Glass website won't start

**Problem**: Missing dependencies or port in use

**Solution**:
```bash
cd app
npm install --legacy-peer-deps
# If port 3000 is busy:
PORT=3001 npm run dev
```

### "Permission denied" errors

**Problem**: File permissions

**Solution**:
```bash
chmod +x scripts/*.py
chmod +x agents/*.py
```

---

## 📊 MONITORING

### System Health

Run orchestrator for full system check:

```bash
python3 sovereign_legacy_loop/sovereign_shadow_unified.py --once
```

### Logs

Check logs in `logs/` directory:

```bash
tail -f logs/ai_enhanced/sovereign_shadow_unified.log
```

### AAVE Monitoring

For live AAVE position:

```bash
watch -n 60 python3 modules/safety/aave_monitor_v2.py
```

Runs every 60 seconds, alerts if HF < 2.0

---

## 🆘 EMERGENCY PROCEDURES

### Emergency Stop

If something goes wrong:

1. **Stop all trading**:
   ```bash
   # Set in .env:
   EMERGENCY_STOP_DEFI=1
   ALLOW_LIVE_EXCHANGE=0
   ```

2. **Kill all processes**:
   ```bash
   pkill -f sovereign_shadow
   pkill -f npm
   ```

3. **Review logs**:
   ```bash
   cat logs/ai_enhanced/sovereign_shadow_unified.log
   ```

### Critical AAVE Alert (HF < 1.6)

1. **DO NOT PANIC** - You have time before liquidation (HF 1.0)

2. **Check position**:
   ```bash
   python3 modules/safety/aave_monitor_v2.py
   ```

3. **Repay debt** following the repay guide in the output

4. **Monitor** until HF > 2.0

---

## 📚 ADDITIONAL RESOURCES

- **Security Audit Fixes**: `SECURITY_AUDIT_FIXES.md`
- **Complete System Findings**: `memory/COMPLETE_SYSTEM_FINDINGS_2025-11-03.md`
- **Agent System Guide**: `agents/README.md`
- **API Documentation**: `docs/guides/API_CONNECTORS_COMPLETE.pdf`

---

## 🏴 PRODUCTION DEPLOYMENT

### Before Going Live

1. ✅ Run security audit: `python3 scripts/github_security_audit.py`
2. ✅ Test all APIs with small amounts
3. ✅ Verify safety limits are appropriate
4. ✅ Test emergency stop procedures
5. ✅ Set up monitoring/alerting
6. ✅ Document your trading strategy
7. ✅ Have a recovery plan

### Production Settings

```bash
# .env settings for production
TRADING_ENV=production
ALLOW_LIVE_EXCHANGE=1
LOG_LEVEL=INFO

# Keep these at 0 until you're 100% ready
ALLOW_DEFI_ACTIONS=0
ALLOW_LEDGER_WITHDRAWALS=0
ALLOW_BRIDGE_OPERATIONS=0
```

### Monitoring

Set up continuous monitoring:

```bash
# Run orchestrator every 5 minutes
*/5 * * * * cd /path/to/SovereignShadow_II && python3 sovereign_legacy_loop/sovereign_shadow_unified.py --once

# Run AAVE monitor every 15 minutes
*/15 * * * * cd /path/to/SovereignShadow_II && python3 modules/safety/aave_monitor_v2.py
```

---

## 🤝 SUPPORT

If you encounter issues:

1. Check this guide
2. Review logs in `logs/`
3. Run security audit
4. Check session notes in `memory/SESSIONS/`

---

## ⚖️ DISCLAIMER

**USE AT YOUR OWN RISK**

This software is provided "as is" without warranty. Cryptocurrency trading involves substantial risk of loss. The authors are not responsible for any financial losses.

**ALWAYS**:
- Start with small amounts
- Test thoroughly before production
- Keep safety limits enabled
- Monitor your positions
- Have an emergency plan

---

**"Production-grade security. Zero guesswork. Pure math."** 🏴

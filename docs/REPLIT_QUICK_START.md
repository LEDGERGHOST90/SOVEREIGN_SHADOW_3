# 🚀 REPLIT QUICK START - New Systems Setup

**Last Updated:** November 19, 2025
**Purpose:** Get your SovereignShadow_II system running on Replit for remote access

---

## 📋 PREREQUISITES

- ✅ GitHub account connected to Replit
- ✅ Your repo: `github.com/LEDGERGHOST90/SovereignShadow_II`
- ✅ API keys ready (see checklist below)

---

## 🎯 STEP 1: IMPORT PROJECT TO REPLIT

### Option A: Via Replit UI
1. Go to [replit.com](https://replit.com)
2. Click **"Create Repl"**
3. Select **"Import from GitHub"**
4. Choose: `LEDGERGHOST90/SovereignShadow_II`
5. Click **"Import from GitHub"**

### Option B: Direct URL
```
https://replit.com/new/github/LEDGERGHOST90/SovereignShadow_II
```

---

## 🔐 STEP 2: CONFIGURE REPLIT SECRETS

Click the **🔒 Secrets** (lock icon) in the left sidebar, then add these secrets:

### 🏦 Exchange APIs

```bash
# Binance US
BINANCE_US_API_KEY=your_binance_us_api_key
BINANCE_US_SECRET_KEY=your_binance_us_secret_key

# Kraken
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_PRIVATE_KEY=your_kraken_private_key

# Coinbase Advanced Trade
COINBASE_API_KEY=organizations/your-org-id/apiKeys/your-key-id
COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
MHcCAQEEI...your_full_key...
-----END EC PRIVATE KEY-----

# OKX (optional - currently disabled)
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase
```

### 🎨 Website & Database

```bash
# Abacus AI
ABACUSAI_API_KEY=your_abacusai_api_key

# NextAuth
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=https://sovereignnshadowii.abacusai.app

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db?connect_timeout=15
```

### 🔗 Blockchain Connections

```bash
# MetaMask (Ethereum)
METAMASK_RPC_URL=https://mainnet.infura.io/v3/your_project_id
METAMASK_CHAIN_ID=1

# Phantom (Solana)
PHANTOM_RPC_URL=https://solana-api.projectserum.com

# WalletConnect
WALLETCONNECT_PROJECT_ID=your_project_id

# Ledger
LEDGER_HARDWARE_PATH=/dev/hidraw0
LEDGER_ETH_ADDRESS=your_ledger_eth_address
LEDGER_CONFIRMATION_THRESHOLD=1000
ALLOW_LEDGER_WITHDRAWALS=0
```

### ⚙️ System Configuration

```bash
# Trading Safety (IMPORTANT!)
DISABLE_REAL_EXCHANGES=1
ALLOW_LIVE_EXCHANGE=0
ALLOW_DEFI_ACTIONS=0
ALLOW_BRIDGE_OPERATIONS=0
EMERGENCY_STOP_DEFI=0

# Risk Management
MAX_POSITION_SIZE=0.1
RISK_PER_TRADE=0.02
MAX_SINGLE_DEFI_TRADE_PERCENT=5
MAX_DAILY_DEFI_VOLUME_PERCENT=15

# Gas & Slippage
MAX_SLIPPAGE_TOLERANCE=5.0
DEFAULT_SLIPPAGE_TOLERANCE=0.5
MAX_GAS_PRICE_GWEI=100
MAX_TRANSACTION_FEE_USD=50

# Strategy
ARBITRAGE_THRESHOLD=0.5
MOMENTUM_THRESHOLD=2.0

# Exchange Routing
PRIMARY_TRADE_EXCHANGE=kraken
SNIPER_EXCHANGE=okx
FIAT_RAIL_EXCHANGE=binanceus
DEFAULT_DEFI_RAIL=metamask
DEFAULT_SOLANA_RAIL=phantom

# System
TRADING_ENV=production
LOG_LEVEL=INFO
SCAN_INTERVAL=15
ENCRYPTION_KEY=your_encryption_key_here
```

---

## 🎮 STEP 3: CONFIGURE .replit FILE

Your `.replit` file is already configured with safe defaults:

```toml
language = "python3"
run = "python3 sovereign_shadow_unified.py"

[nix]
channel = "stable-23_11"

[env]
SANDBOX = "1"
DISABLE_REAL_EXCHANGES = "1"
ENV = "dev"
ALLOW_LIVE_EXCHANGE = "0"
LEGACY_NO_LEDGER = "1"
PYTHONUNBUFFERED = "1"

[deployment]
run = ["sh", "-c", "python3 sovereign_shadow_unified.py --autonomy --interval 120"]
deploymentTarget = "cloudrun"

[[ports]]
localPort = 8000
externalPort = 80
```

### 🔧 Optional Modifications

**For Dashboard/API mode:**
```toml
run = "python3 core/api/trading_api_server.py"
```

**For Market Scanner mode:**
```toml
run = "python3 bin/market_scanner_15min.py"
```

---

## ▶️ STEP 4: TEST YOUR DEPLOYMENT

### A. Test Basic Imports
Click **"Run"** in Replit. You should see:
```
✅ Shadow SDK loaded
✅ Config loaded from PERSISTENT_STATE.json
✅ Portfolio: $6,167.43
```

### B. Test Exchange Connections
```python
# In Replit console
python3 scripts/test_exchange_connections.py
```

Expected output:
```
✅ Binance US: Connected ($152.05)
✅ Kraken: Connected (1,332 markets)
✅ Coinbase: Connected
⚠️  OKX: Disabled
```

### C. Test SHADE Agents
```python
python3 agents/master_trading_system.py
```

---

## 🌐 STEP 5: CONNECT TO YOUR WEBSITE

Your website: `sovereignnshadowii.abacusai.app`

### Update Frontend API URL

In your Abacus.AI project, set:
```bash
NEXT_PUBLIC_API_URL=https://your-repl-name.your-username.repl.co
```

Or if using Replit's deployment:
```bash
NEXT_PUBLIC_API_URL=https://your-cloudrun-url.run.app
```

---

## 🚨 SAFETY CHECKLIST

Before running ANYTHING live:

- [ ] `DISABLE_REAL_EXCHANGES=1` is set
- [ ] `ALLOW_LIVE_EXCHANGE=0` is set
- [ ] `ALLOW_DEFI_ACTIONS=0` is set
- [ ] All API keys are in **Replit Secrets** (not hardcoded)
- [ ] `.env` file is **NOT** in your GitHub repo
- [ ] Test with paper trading first
- [ ] Verify all 21 preflight checks pass

---

## 🎯 DEPLOYMENT OPTIONS

### Option A: Always-On Replit ($7/month)
- Enable "Always On" in Replit settings
- Your system runs 24/7
- Great for market scanner

### Option B: Cloud Run (Free tier available)
```bash
# Already configured in .replit
# Click "Deploy" in Replit UI
# Select "Cloud Run"
```

### Option C: Scheduled Runs (Free)
Use Replit's cron jobs:
```python
# .replit
[deployment]
schedule = "0 */4 * * *"  # Every 4 hours
```

---

## 🔍 TROUBLESHOOTING

### Issue: "ModuleNotFoundError"
```bash
# In Replit console
pip install -r requirements.txt
```

### Issue: "Connection refused" to exchanges
- Check if `DISABLE_REAL_EXCHANGES=1`
- Verify API keys in Secrets
- Check IP whitelisting on exchange

### Issue: "Database connection failed"
- Verify `DATABASE_URL` in Secrets
- Check if database allows Replit IPs
- Test connection: `psql $DATABASE_URL`

### Issue: Ledger not working
- Set `LEGACY_NO_LEDGER=1` (hardware wallets don't work in cloud)
- Use MetaMask/Phantom for DeFi instead

---

## 📊 MONITORING YOUR SYSTEM

### View Logs
```bash
tail -f logs/market_scanner/latest_scan.json
tail -f logs/ai_enhanced/real_balances.json
```

### Check System Status
```bash
python3 -c "
from pathlib import Path
import json
state = json.loads(Path('PERSISTENT_STATE.json').read_text())
print(f\"Portfolio: ${state['portfolio']['total_value_usd']}\")
print(f\"Last updated: {state['last_updated']}\")
"
```

---

## 🎓 NEXT STEPS

1. ✅ **Verify paper trading works** - Run simulations first
2. ✅ **Test SHADE agents** - Ensure all 4 agents respond
3. ✅ **Monitor for 24 hours** - Check logs for errors
4. ✅ **Connect to dashboard** - Verify live data feeds
5. ✅ **Enable notifications** - Set up price alerts

---

## 📞 SUPPORT

- **Documentation:** `/docs` folder
- **Issues:** Create issue in GitHub repo
- **System Status:** Check `PERSISTENT_STATE.json`
- **Logs:** `logs/` directory

---

**🎯 You're ready to deploy! Start with paper trading and work your way up.**

**Website:** https://sovereignnshadowii.abacusai.app
**Repo:** https://github.com/LEDGERGHOST90/SovereignShadow_II

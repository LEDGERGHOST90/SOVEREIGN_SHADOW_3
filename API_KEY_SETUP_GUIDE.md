# 🔐 API KEY SETUP GUIDE - Sovereign Shadow Empire

Complete guide to securely configure API keys for all exchanges and services.

---

## ⚠️ CRITICAL SECURITY RULES

### BEFORE YOU START:
1. **NEVER share API keys** with anyone (including AI assistants)
2. **NEVER commit keys to git** (.env is in .gitignore)
3. **NEVER screenshot keys** or post online
4. **ALWAYS use IP whitelisting** when possible
5. **ALWAYS set withdrawal restrictions** to DISABLED
6. **START with READ-ONLY permissions** for testing

### API Key Security Checklist:
- ✅ Use `.env` file (never hardcode)
- ✅ Set minimum required permissions
- ✅ Enable IP whitelist (your IP only)
- ✅ Disable withdrawals (trading only)
- ✅ Set 2FA/U2F for API management
- ✅ Monitor API usage regularly
- ✅ Rotate keys periodically (every 90 days)

---

## 1️⃣ COINBASE SETUP

### Step 1: Create API Key

1. Go to: https://www.coinbase.com/settings/api
2. Click **"New API Key"**
3. Set permissions:
   ```
   ✅ View accounts and balances
   ✅ View cryptocurrency addresses
   ✅ View transaction history
   ✅ Trade cryptocurrency (for trading)
   ❌ Transfer funds between accounts (DISABLE)
   ❌ Send cryptocurrency (DISABLE)
   ❌ Bypass 2FA (DISABLE)
   ```
4. **IP Whitelist**: Add your IP address (highly recommended)
5. **Passphrase**: Save this securely (needed for API calls)
6. Copy: API Key, API Secret, API Passphrase

### Step 2: Add to .env

```bash
# Coinbase
COINBASE_API_KEY=your_api_key_here
COINBASE_API_SECRET=your_api_secret_here
COINBASE_API_PASSPHRASE=your_passphrase_here
```

### Verification Command:
```bash
python3 scripts/validate_api_connections.py
```

---

## 2️⃣ OKX SETUP

### Step 1: Create API Key

1. Go to: https://www.okx.com/account/my-api
2. Click **"Create API Key"**
3. Set permissions:
   ```
   ✅ Read - View account data
   ✅ Trade - Place and cancel orders
   ❌ Withdraw - Keep DISABLED
   ```
4. **API Key Nickname**: `SovereignShadow-Trading`
5. **IP Whitelist**: Add your IP (required for trading)
6. **Passphrase**: Create a strong passphrase (NOT your login password)
7. Complete 2FA verification
8. Copy: API Key, API Secret Key, Passphrase

### Step 2: Add to .env

```bash
# OKX
OKX_API_KEY=your_api_key_here
OKX_API_SECRET=your_secret_key_here
OKX_API_PASSPHRASE=your_passphrase_here
```

### OKX Security Notes:
- OKX requires IP whitelist for trading
- Passphrase is case-sensitive
- Keep API Key permission level to "Trading" only
- Never enable "Withdraw" permission

---

## 3️⃣ KRAKEN SETUP

### Step 1: Create API Key

1. Go to: https://www.kraken.com/u/security/api
2. Click **"Generate New Key"**
3. Set permissions:
   ```
   ✅ Query Funds - View balances
   ✅ Query Open Orders & Trades - View trades
   ✅ Query Closed Orders & Trades - View history
   ✅ Create & Modify Orders - Place orders
   ❌ Withdraw Funds - Keep DISABLED
   ❌ Export Data - Not needed
   ❌ Access WebSockets Authentication Token - Not needed
   ```
4. **Key Description**: `SovereignShadow-Trading`
5. **Nonce Window**: 5000 (default)
6. Copy: API Key, API Private Key

### Step 2: Add to .env

```bash
# Kraken
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_private_key_here
```

### Kraken Security Notes:
- No withdrawal permissions needed for trading
- 2FA required for API creation
- Consider using sub-accounts for additional security
- API keys expire based on your tier (Master key recommended)

---

## 4️⃣ METAMASK / WEB3 SETUP

### Purpose:
Monitor your Ledger wallet via MetaMask interface and track AAVE position.

### Step 1: Get Infura Project ID (FREE)

1. Go to: https://infura.io/
2. Sign up / Log in
3. Click **"Create New Key"**
4. Select **"Web3 API"**
5. Name: `SovereignShadow-Monitor`
6. Copy your **Project ID** (looks like: `abc123def456...`)

Your endpoint will be:
```
https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

### Step 2: Get MetaMask Address

1. Open MetaMask
2. Click account name at top
3. Click **"Copy Address"**
4. This is your Ethereum address (starts with 0x)

### Step 3: Add to .env

```bash
# MetaMask / Web3 Integration
INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
METAMASK_ADDRESS=0xYourMetaMaskAddressHere
```

### Alternative: Alchemy (FREE, better rate limits)

1. Go to: https://www.alchemy.com/
2. Create account
3. Create new app → Ethereum → Mainnet
4. Copy HTTP endpoint

```bash
# Alternative: Alchemy
ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

### MetaMask/Ledger Security Notes:
- ✅ This is READ-ONLY monitoring
- ✅ No private keys are exposed
- ✅ Cannot execute transactions
- ✅ Safe for automated monitoring
- 🔒 Your Ledger still requires physical confirmation for all transactions

---

## 5️⃣ COMPLETE .ENV CONFIGURATION

Here's your complete `.env` template:

```bash
# ===================================================================
# SOVEREIGN SHADOW EMPIRE - API CONFIGURATION
# ===================================================================
# ⚠️  SECURITY: Never commit this file to git!
# ⚠️  Keep this file secure and private!
# ===================================================================

# ─────────────────────────────────────────────────────────────────
# COINBASE CONFIGURATION
# ─────────────────────────────────────────────────────────────────
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_api_secret_here
COINBASE_API_PASSPHRASE=your_coinbase_passphrase_here

# ─────────────────────────────────────────────────────────────────
# OKX CONFIGURATION
# ─────────────────────────────────────────────────────────────────
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_secret_key_here
OKX_API_PASSPHRASE=your_okx_passphrase_here

# ─────────────────────────────────────────────────────────────────
# KRAKEN CONFIGURATION
# ─────────────────────────────────────────────────────────────────
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_API_SECRET=your_kraken_private_key_here

# ─────────────────────────────────────────────────────────────────
# METAMASK / WEB3 CONFIGURATION (Read-Only Monitoring)
# ─────────────────────────────────────────────────────────────────
# Get free Infura key at: https://infura.io/
INFURA_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID

# Or use Alchemy (alternative): https://www.alchemy.com/
ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY

# Your MetaMask/Ledger Ethereum address (starts with 0x)
METAMASK_ADDRESS=0xYourMetaMaskAddressHere

# ─────────────────────────────────────────────────────────────────
# AAVE PROTOCOL (For monitoring your stETH collateral)
# ─────────────────────────────────────────────────────────────────
# These are mainnet contract addresses (public, no secrets)
AAVE_POOL_ADDRESS=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
AAVE_DATA_PROVIDER=0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3

# ─────────────────────────────────────────────────────────────────
# SOVEREIGN SHADOW SYSTEM CONFIGURATION
# ─────────────────────────────────────────────────────────────────
SOVEREIGN_MODE=paper          # paper, live, monitor
MAX_POSITION_SIZE=415         # $415 (25% of hot wallet)
DAILY_LOSS_LIMIT=100          # $100 max daily loss
EMERGENCY_STOP_LOSS=1000      # $1,000 emergency stop

# Capital allocation
TOTAL_CAPITAL=8153.14         # Total portfolio
ACTIVE_CAPITAL=1638.49        # Coinbase (hot wallet)
VAULT_CAPITAL=6514.65         # Ledger (READ-ONLY)

# ─────────────────────────────────────────────────────────────────
# LOGGING & MONITORING
# ─────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
ENABLE_JSON_LOGS=true         # Enable structured JSON logging
ENABLE_NOTIFICATIONS=false    # Email/SMS alerts (future feature)

# ─────────────────────────────────────────────────────────────────
# DEEPAGENT / MCP CONFIGURATION (Optional - Advanced Features)
# ─────────────────────────────────────────────────────────────────
DEEPAGENT_URL=http://localhost:8008
MCP_PORT=8765
MCP_ENABLED=false             # Enable MCP server integration

# ===================================================================
# END OF CONFIGURATION
# ===================================================================
```

---

## 6️⃣ VERIFICATION STEPS

### Step 1: Check .env File Exists
```bash
ls -la /Volumes/LegacySafe/SovereignShadow/.env
```

### Step 2: Validate API Connections
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 scripts/validate_api_connections.py
```

Expected output:
```
🔍 VALIDATING API CONNECTIONS
═══════════════════════════════════════
✅ Coinbase: Connected (Balance: $X,XXX.XX)
✅ OKX: Connected (Balance: $XXX.XX)
✅ Kraken: Connected (Balance: $XXX.XX)
✅ Web3: Connected (Block: 12345678)
✅ MetaMask: Address verified
═══════════════════════════════════════
🎯 All connections validated!
```

### Step 3: Test Individual Exchanges
```bash
# Test Coinbase
python3 -c "import ccxt; ex = ccxt.coinbase({'apiKey': 'YOUR_KEY', 'secret': 'YOUR_SECRET'}); print(ex.fetch_balance())"

# Test OKX
python3 -c "import ccxt; ex = ccxt.okx({'apiKey': 'YOUR_KEY', 'secret': 'YOUR_SECRET'}); print(ex.fetch_balance())"

# Test Kraken
python3 -c "import ccxt; ex = ccxt.kraken({'apiKey': 'YOUR_KEY', 'secret': 'YOUR_SECRET'}); print(ex.fetch_balance())"
```

### Step 4: Test MetaMask Monitor
```bash
python3 core/portfolio/metamask_monitor.py
```

Expected output:
```
🦊 METAMASK / LEDGER MONITOR
✅ Connected to Ethereum mainnet
📊 Portfolio Summary:
   Address: 0xYour...Address
   Total Value: $6,514.65
🏦 AAVE Position:
   Collateral: 0.750002 stETH ($3,599.32)
   Borrowed: $1,150.00 USDC
   Health Factor: 2.49
   Status: SAFE
```

---

## 7️⃣ SECURITY BEST PRACTICES

### API Key Permissions Matrix

| Exchange | View | Trade | Withdraw | IP Whitelist |
|----------|------|-------|----------|--------------|
| Coinbase | ✅ | ✅ | ❌ DISABLED | ✅ Recommended |
| OKX | ✅ | ✅ | ❌ DISABLED | ✅ REQUIRED |
| Kraken | ✅ | ✅ | ❌ DISABLED | ✅ Recommended |
| Web3 | ✅ | ❌ N/A | ❌ N/A | N/A |

### Monthly Security Checklist

- [ ] Review API key usage logs
- [ ] Verify no suspicious activity
- [ ] Check IP whitelist is still valid
- [ ] Confirm withdrawal permissions still disabled
- [ ] Test API key still works
- [ ] Review trading bot performance
- [ ] Check for any unauthorized API calls

### API Key Rotation Schedule

```
Every 90 days:
1. Create new API keys with same permissions
2. Update .env file with new keys
3. Test new keys work correctly
4. Delete old API keys from exchange
5. Document key rotation in logs
```

---

## 8️⃣ TROUBLESHOOTING

### Problem: "Invalid API Key"
**Solution**:
- Verify key is copied correctly (no spaces)
- Check API key is enabled on exchange
- Verify IP whitelist includes your IP
- Check 2FA is completed if required

### Problem: "Permission Denied"
**Solution**:
- Verify API key has required permissions
- Check you've enabled "Trade" permission
- Verify account has trading enabled
- Check for any account restrictions

### Problem: "Rate Limit Exceeded"
**Solution**:
- Reduce scan frequency (increase interval)
- Use caching for balance queries
- Consider upgrading exchange API tier
- Implement exponential backoff

### Problem: "Web3 Connection Failed"
**Solution**:
- Verify INFURA_URL is correct
- Check Infura project has sufficient credits
- Try Alchemy as alternative
- Verify internet connection

---

## 9️⃣ WHAT HAPPENS NEXT

### After API Keys Are Configured:

1. **Validation**: Run `python3 scripts/validate_api_connections.py`
2. **Get Real Balances**: Run `python3 scripts/get_real_balances.py`
3. **Master Loop**: The 24-hour paper test will use simulated trades
4. **After Paper Test**: Enable live trading by changing mode to "live"

### Master Loop Will:
- ✅ Connect to all configured exchanges
- ✅ Fetch real-time balances
- ✅ Monitor for opportunities
- ✅ Execute trades (paper mode = simulation)
- ✅ Log all activity
- ✅ Respect safety limits

### Safety Guarantees:
- 🔒 Ledger vault remains READ-ONLY
- 🛡️ Daily loss limit: $100
- 🚨 Emergency stop: $1,000
- 💰 Max position: $415 (25% of hot wallet)
- 📊 All trades logged to JSON

---

## 🎯 QUICK START CHECKLIST

- [ ] Create Coinbase API key (view + trade, NO withdraw)
- [ ] Create OKX API key (view + trade, NO withdraw, IP whitelist)
- [ ] Create Kraken API key (view + trade, NO withdraw)
- [ ] Get Infura project ID (free)
- [ ] Copy MetaMask address
- [ ] Add all keys to `.env` file
- [ ] Run `python3 scripts/validate_api_connections.py`
- [ ] Run `python3 scripts/get_real_balances.py`
- [ ] Verify Master Loop is still running: `./bin/MASTER_LOOP_CONTROL.sh status`
- [ ] Check logs: `./bin/MASTER_LOOP_CONTROL.sh logs`

---

## 🏴 YOU'RE READY!

Once all API keys are configured, your empire will have:
- ✅ Real-time portfolio monitoring across all exchanges
- ✅ Live AAVE health factor tracking
- ✅ Automated opportunity detection
- ✅ Multi-exchange arbitrage capability
- ✅ Complete logging and analytics
- ✅ Maximum security (no withdrawal permissions)

**Next Step**: Follow this guide to create and configure each API key!

---

*🔐 Security is paramount. Never share your API keys!*
*🏴 Sovereign Shadow Empire - Secure. Automated. Profitable.*

# 🏴 SOVEREIGN SHADOW - GITHUB REPOSITORY MASTER PLAN

**Target:** Clean, portable, secure repository that can be cloned anywhere  
**Status:** Pre-sync security audit complete  
**Date:** October 19, 2025

---

## 🎯 PRIMARY OBJECTIVE

Create a GitHub repository that is:
1. ✅ **PORTABLE** - Clone anywhere (local, cloud, any machine)
2. ✅ **SECURE** - Zero hardcoded secrets, zero API keys
3. ✅ **COMPLETE** - Full functionality with proper setup
4. ✅ **PROFESSIONAL** - Ready for code review, collaboration, handoff

---

## 📂 REPOSITORY STRUCTURE

```
Memphispradda/SovereignShadow  (GitHub)
    │
    ├── sovereign_legacy_loop/        ← Full Next.js/TypeScript app
    ├── shadow_sdk/                   ← Python AI toolkit
    ├── config/                       ← Python integration scripts (NO SECRETS)
    ├── scripts/                      ← Utility scripts
    ├── docs/                         ← Documentation
    ├── Master_LOOP_Creation/         ← Architecture docs
    │
    ├── .env.template                 ← Template with placeholders
    ├── .gitignore                    ← Fortress protection
    ├── requirements.txt              ← Python dependencies
    ├── README.md                     ← Setup instructions
    └── SETUP_GUIDE.md                ← Environment configuration
```

---

## 🔒 SECURITY AUDIT STATUS

### ✅ PROTECTED BY .GITIGNORE
- All `.env` files
- All API keys/secrets
- Live trading logs
- Real balance data
- Obsidian encrypted vault
- Personal strategies

### ⚠️ NEEDS REMOVAL FROM GIT HISTORY
```bash
# Currently tracked sensitive files:
config/empire_state.yaml              # (deleted but tracked)
logs/ai_enhanced/*.json               # Contains real balances
.claude/settings.local.json           # May contain settings
CLEANUP_BACKUP/                       # Contains old configs
```

### ✅ SAFE TO COMMIT
- All Python scripts (use env vars)
- All TypeScript/React code (uses Obsidian config loader)
- Documentation
- Architecture diagrams
- Setup guides

---

## 🛡️ SECURITY IMPLEMENTATION

### 1. Environment Variables (.env.template)
```bash
# ════════════════════════════════════════
# 💰 CAPITAL ALLOCATION
# ════════════════════════════════════════
TOTAL_PORTFOLIO_VALUE=YOUR_TOTAL_USD
ACTIVE_TRADING_CAPITAL=YOUR_TRADING_USD
LEDGER_COLD_STORAGE=YOUR_COLD_STORAGE_USD

# ════════════════════════════════════════
# 🔑 API KEYS - REPLACE WITH YOUR REAL KEYS
# ════════════════════════════════════════

# OKX EXCHANGE
OKX_KEY=your_okx_api_key_here
OKX_SECRET=your_okx_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here

# COINBASE ADVANCED TRADE
COINBASE_API_KEY=your_coinbase_key_name_here
COINBASE_PRIVATE_KEY=your_coinbase_private_key_single_line_here

# KRAKEN (OPTIONAL)
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_PRIVATE_KEY=your_kraken_secret_here

# BINANCE US (OPTIONAL)
BINANCE_US_API_KEY=your_binance_key_here
BINANCE_US_SECRET=your_binance_secret_here

# ════════════════════════════════════════
# 🛡️ SAFETY LIMITS (2% RULE)
# ════════════════════════════════════════
MAX_POSITION_SIZE=YOUR_CAPITAL*0.02
MAX_DAILY_EXPOSURE=YOUR_CAPITAL*0.10
STOP_LOSS_PER_TRADE=YOUR_CAPITAL*0.01
MAX_CONSECUTIVE_LOSSES=3
```

### 2. Obsidian Encrypted Vault (Primary Key Storage)
```
ObsidianVault/
    secrets/
        api-keys/
            OKX.md              ← Encrypted
            Coinbase.md         ← Encrypted
            Kraken.md           ← Encrypted
        capital/
            portfolio.md        ← Encrypted
    .obsidian/                  ← Config (not committed)
```

**How it works:**
1. Store ALL real keys in Obsidian vault (encrypted at rest)
2. Code loads from vault via `ObsidianEncryptedConfig` class
3. Vault NEVER committed to GitHub
4. Anyone cloning repo creates their own vault

### 3. API Configuration Files (NO SECRETS)
All files in `config/` use environment variables only:
- ✅ `ledger_integration.py` - Loads from env
- ✅ `ledger_wallet_integration.py` - Loads from env
- ✅ `real_exchange_integration.py` - Loads from env

**NEVER HARDCODE:**
- API keys
- Secrets
- Passphrases
- Private keys
- Account IDs
- Wallet addresses

---

## 📋 PRE-SYNC CHECKLIST

### Phase 1: Clean Git History
```bash
# Remove tracked but deleted files
git rm --cached config/empire_state.yaml
git rm --cached config/okx_credentials.env
git rm --cached config/trading_parameters.env

# Remove sensitive logs
git rm --cached -r logs/ai_enhanced/*.json
git rm --cached logs/api_validation.json

# Remove backup directory
git rm --cached -r CLEANUP_BACKUP/

# Remove local settings
git rm --cached -r .claude/settings.local.json
```

### Phase 2: Create Templates
- [x] `.env.template` - Placeholder values
- [x] `.gitignore` - Fortress protection
- [ ] `SETUP_GUIDE.md` - Environment setup
- [ ] `config/README.md` - Explain Obsidian integration

### Phase 3: Security Scan
```bash
# Scan for hardcoded secrets
grep -r "api[_-]key" --include="*.py" --include="*.ts" .
grep -r "secret" --include="*.py" --include="*.ts" .
grep -r "passphrase" --include="*.py" --include="*.ts" .

# Verify .env is ignored
git check-ignore .env

# Check for API keys in code
grep -r "apikey.*=.*['\"]" --include="*.py" --include="*.ts" .
```

### Phase 4: Test Portability
```bash
# Clone to fresh directory
cd /tmp
git clone https://github.com/Memphispradda/SovereignShadow.git
cd SovereignShadow

# Verify no secrets present
ls -la .env         # Should NOT exist
ls -la config/*.env # Should NOT exist

# Setup environment
cp .env.template .env
# User fills in their own keys

# Install dependencies
pip install -r requirements.txt
cd sovereign_legacy_loop && npm install

# Run validation
python3 scripts/validate_api_connections.py  # Should fail gracefully without keys
```

---

## 🚀 GITHUB SYNC WORKFLOW

### Step 1: Rename Repository (Manual)
1. Go to: `https://github.com/Memphispradda/sovereign_legacy_loop`
2. Settings → Repository name → `SovereignShadow`
3. Click "Rename"

### Step 2: Update Local Git Remote
```bash
cd /Volumes/LegacySafe/SovereignShadow
git remote set-url origin https://github.com/Memphispradda/SovereignShadow.git
```

### Step 3: Clean and Commit
```bash
# Remove sensitive files from tracking
git rm --cached config/empire_state.yaml
git rm --cached -r logs/ai_enhanced/*.json
git rm --cached -r CLEANUP_BACKUP/
git rm --cached -r .claude/

# Commit cleanup
git add .gitignore
git commit -m "🔒 Security: Remove sensitive files from tracking"

# Add new secure structure
git add .env.template
git add SETUP_GUIDE.md
git add GITHUB_REPOSITORY_MASTER_PLAN.md
git commit -m "📚 Docs: Add security templates and setup guide"
```

### Step 4: Push to GitHub
```bash
git push origin main
```

### Step 5: Verify Clean Repository
1. Browse to: `https://github.com/Memphispradda/SovereignShadow`
2. Check: No `.env` files visible
3. Check: No `*.json` with real balances
4. Check: No API keys in any files
5. Verify: `.env.template` exists
6. Verify: Setup guides present

---

## 🌍 PORTABILITY TEST

**Goal:** Anyone (including you on a new machine) can clone and run with their own keys.

### Clean Clone Test
```bash
# On a fresh machine or directory
git clone https://github.com/Memphispradda/SovereignShadow.git
cd SovereignShadow

# Setup environment
cp .env.template .env
nano .env  # Fill in YOUR keys

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd sovereign_legacy_loop
npm install

# Setup Obsidian vault (if using)
./scripts/setup_obsidian_vault.sh

# Validate API connections
python3 scripts/validate_api_connections.py

# Run system
./START_SOVEREIGN_SHADOW.sh
```

**Expected Result:** System runs with user's own API keys, zero hardcoded values.

---

## 📊 COLLABORATION READINESS

### Code Review Checklist
- ✅ No secrets in code
- ✅ Clear documentation
- ✅ Modular architecture
- ✅ Type hints and comments
- ✅ Error handling
- ✅ Logging (no sensitive data)

### Handoff Ready For:
- ✅ **Abacus AI** - Web integration team
- ✅ **Code review** - Senior developers
- ✅ **Auditors** - Security review
- ✅ **AI assistants** - Claude, GPT, DeepSeek
- ✅ **Future you** - On any machine

---

## 🎯 SUCCESS CRITERIA

Repository is ready when:
1. ✅ Can clone to fresh machine
2. ✅ Zero secrets visible on GitHub
3. ✅ Clear setup instructions
4. ✅ All features work with env vars
5. ✅ Professional documentation
6. ✅ Security audit passes
7. ✅ Can share repo URL without risk

---

## 🔄 MAINTENANCE PROTOCOL

### Before Every Push:
```bash
# Security scan
grep -r "sk-" . --include="*.py" --include="*.ts"  # OpenAI keys
grep -r "-----BEGIN" . --include="*.py"            # Private keys

# Verify .env ignored
git status | grep ".env"                           # Should be empty

# Check for sensitive logs
git status | grep "logs/"                          # Should be ignored
```

### Weekly Audits:
1. Review `git log` for accidental commits
2. Check GitHub repo for visible secrets
3. Update `.gitignore` as needed
4. Rotate API keys if any were exposed

---

## 🏴 FINAL STATUS

**This repository represents:**
- $8,260 portfolio management system
- Multi-exchange arbitrage engine  
- AI-powered trading strategies
- Ledger hardware wallet integration
- Claude/GPT AI orchestration
- MCP server tools
- Shadow SDK utilities

**All protected by:**
- Fortress `.gitignore`
- Obsidian encrypted vault
- Environment variable isolation
- Zero hardcoded secrets

**Ready for:**
- Global collaboration
- Code reviews
- AI handoffs
- Portfolio scaling to $100K+

---

*"A sovereign trader's code is portable, secure, and professional."* 🏴

**NEXT ACTION:** Execute Phase 1 cleanup, then push to GitHub.

# 🚀 REPLIT DEPLOYMENT & ENVIRONMENT VARIABLES

**Date:** October 31, 2025
**Purpose:** Explain how Replit integrates with your system and how secrets/env vars work

---

## 🤔 YOUR QUESTION: "Will my .env come with the download?"

### **SHORT ANSWER: NO (and that's GOOD for security!)**

When you download code from Replit or deploy your app:
- ❌ `.env` files are **NOT** included (intentionally)
- ❌ Replit Secrets are **NOT** exported
- ✅ This protects your API keys from being leaked
- ✅ You must manually configure secrets in each environment

---

## 🏗️ HOW REPLIT FITS IN YOUR ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                   YOUR DEPLOYMENT OPTIONS                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OPTION 1: LOCAL DEVELOPMENT                                │
│  /Volumes/LegacySafe/SovereignShadow/                       │
│  ├─ .env (YOUR local secrets)                               │
│  ├─ FastAPI Backend (Port 8000)                             │
│  └─ Next.js Frontend (Port 3000)                            │
│                                                             │
│  OPTION 2: REPLIT CLOUD (Development/Testing)               │
│  replit.com/@YourUsername/MultiMarketShadow_Scanner/        │
│  ├─ Replit Secrets (stored in Replit dashboard)            │
│  ├─ FastAPI Backend (Replit auto-assigns port)             │
│  └─ Next.js Frontend (or separate Repl)                     │
│                                                             │
│  OPTION 3: ABACUS.AI (Production Dashboard)                 │
│  legacyloopshadowai.abacusai.app                            │
│  ├─ Frontend only (UI/dashboard)                            │
│  ├─ Calls API from Option 1 or 2                            │
│  └─ No secrets needed (just API URL)                        │
│                                                             │
│  OPTION 4: PRODUCTION (AWS, Railway, Fly.io, etc.)          │
│  api.sovereignshadow.com                                    │
│  ├─ Environment variables (set in cloud platform)           │
│  ├─ FastAPI Backend (production)                            │
│  └─ Connects to Abacus.AI dashboard                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 HOW SECRETS WORK ACROSS PLATFORMS

### **1. LOCAL DEVELOPMENT (.env files)**

**Location:** `/Volumes/LegacySafe/SovereignShadow/.env`

**Example .env file:**
```bash
# Exchange API Keys
BINANCE_API_KEY=your_binance_key_here
BINANCE_API_SECRET=your_binance_secret_here
COINBASE_API_KEY=your_coinbase_key_here
COINBASE_API_SECRET=your_coinbase_secret_here
OKX_API_KEY=your_okx_key_here
OKX_API_SECRET=your_okx_secret_here
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_API_SECRET=your_kraken_secret_here

# Blockchain APIs
ETHERSCAN_API_KEY=your_etherscan_key_here

# AI APIs
ANTHROPIC_API_KEY=your_claude_api_key_here
ABACUS_API_KEY=your_abacus_api_key_here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Security:**
- ✅ `.env` is in `.gitignore` (NOT pushed to GitHub)
- ✅ Only exists on YOUR local machine
- ⚠️ If you lose this file, you need to recreate it manually

---

### **2. REPLIT SECRETS (Cloud Development)**

**How to access:**
1. Open your Replit project: `MultiMarketShadow_Scanner`
2. Click **Secrets** (lock icon) in left sidebar
3. Add key-value pairs (like .env but in UI)

**Current Replit Secrets (from your screenshot):**
```
BINANCE_US_API_KEY = ab0cb...
BINANCE_US_API_SECRET = 9287b...
```

**How Python code reads Replit Secrets:**
```python
import os

# On Replit, reads from Secrets
# On local, reads from .env file
api_key = os.environ.get('BINANCE_US_API_KEY')
api_secret = os.environ.get('BINANCE_US_API_SECRET')
```

**Important:**
- ✅ Replit Secrets are stored securely in Replit's cloud
- ❌ When you download code, Secrets are **NOT** included
- ✅ This is GOOD - you don't want secrets in downloaded files
- ⚠️ You must manually re-add secrets in each environment

---

### **3. ABACUS.AI (Dashboard - No Secrets Needed!)**

**What Abacus.AI needs:**
```bash
# Only needs to know where your API is
NEXT_PUBLIC_API_URL=https://your-replit-url.repl.co
# OR
NEXT_PUBLIC_API_URL=https://api.sovereignshadow.com
```

**No sensitive keys needed because:**
- ✅ Dashboard only displays data (read-only)
- ✅ API handles all trading/exchange access
- ✅ Frontend just makes fetch() calls to backend

---

### **4. PRODUCTION DEPLOYMENT (Cloud Platforms)**

**Examples of where you might deploy:**
- Railway.app
- Fly.io
- AWS (Lambda, ECS, EC2)
- Google Cloud Run
- DigitalOcean

**How to set environment variables in production:**

#### **Railway.app:**
```bash
# In Railway dashboard → Variables tab
BINANCE_API_KEY=xxx
COINBASE_API_KEY=xxx
# etc.
```

#### **Fly.io:**
```bash
fly secrets set BINANCE_API_KEY=xxx
fly secrets set COINBASE_API_KEY=xxx
```

#### **AWS Lambda:**
```bash
# In AWS Console → Lambda → Configuration → Environment variables
# Or use AWS Secrets Manager
```

---

## 📦 WHAT HAPPENS WHEN YOU DOWNLOAD FROM REPLIT

### **Option A: Download from Replit UI**

**What you GET:**
```
MultiMarketShadow_Scanner/
├── main.py
├── modules/
├── config/
├── requirements.txt
└── README.md
```

**What you DON'T GET:**
```
❌ .env (secrets not included)
❌ Replit Secrets
❌ API keys
❌ Private credentials
```

**What you MUST DO:**
```bash
# 1. Create new .env file manually
touch .env

# 2. Add all your secrets
nano .env
# Paste your API keys

# 3. Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

---

### **Option B: Git Clone from GitHub**

**What you GET:**
```
# From: github.com/LEDGERGHOST90/SovereignShadow_II
git clone https://github.com/LEDGERGHOST90/SovereignShadow_II.git
```

**What you DON'T GET:**
```
❌ .env file (in .gitignore)
❌ API keys
❌ Secrets
```

**What you MUST DO:**
```bash
# Create .env from template
cp .env.example .env

# Edit and add your real keys
nano .env
```

---

## 🔄 HOW TO SYNC SECRETS ACROSS ENVIRONMENTS

### **Recommended Setup:**

#### **1. Keep Master .env Template (NO REAL KEYS)**
```bash
# .env.example (safe to commit to git)
BINANCE_API_KEY=your_binance_key_here
COINBASE_API_KEY=your_coinbase_key_here
OKX_API_KEY=your_okx_key_here
ETHERSCAN_API_KEY=your_etherscan_key_here
```

#### **2. Keep Private .env (NEVER COMMIT)**
```bash
# .env (YOUR REAL KEYS - never commit!)
BINANCE_API_KEY=ab0cb1234567890...
COINBASE_API_KEY=c5d9e8765432...
OKX_API_KEY=f3g7h2345678...
```

#### **3. Sync to Replit Manually**
```
1. Open Replit Secrets UI
2. Copy-paste each key from your local .env
3. Click "Add new secret" for each one
```

#### **4. Sync to Production via CLI**
```bash
# Railway
railway variables set BINANCE_API_KEY=ab0cb...

# Fly.io
fly secrets set BINANCE_API_KEY=ab0cb...

# Or use a secrets management tool:
# - 1Password CLI
# - Doppler
# - AWS Secrets Manager
```

---

## 🎯 YOUR DEPLOYMENT WORKFLOW

### **STEP 1: Develop Locally**
```bash
cd /Volumes/LegacySafe/SovereignShadow

# Create .env with real keys
cat > .env << EOF
BINANCE_API_KEY=ab0cb...
COINBASE_API_KEY=c5d9e...
EOF

# Run backend
python3 core/api/trading_api_server.py

# Run frontend
cd app && npm run dev
```

### **STEP 2: Test on Replit**
```bash
# Push code to GitHub (WITHOUT .env)
git push

# On Replit:
# 1. Import from GitHub
# 2. Add Secrets via UI (manually)
# 3. Run: python3 core/api/trading_api_server.py
```

### **STEP 3: Deploy to Abacus.AI Dashboard**
```bash
# No secrets needed! Just set API URL
NEXT_PUBLIC_API_URL=https://your-replit-url.repl.co

# Or point to production
NEXT_PUBLIC_API_URL=https://api.sovereignshadow.com
```

### **STEP 4: Deploy Backend to Production**
```bash
# Push to production (Railway/Fly.io/etc)
railway up

# Set secrets via CLI
railway variables set BINANCE_API_KEY=ab0cb...
railway variables set COINBASE_API_KEY=c5d9e...
# etc.

# Update Abacus.AI dashboard to use production URL
NEXT_PUBLIC_API_URL=https://sovereignshadow.railway.app
```

---

## ⚠️ SECURITY WARNINGS

### ❌ NEVER DO THIS:
```python
# DON'T hardcode keys in code!
BINANCE_API_KEY = "ab0cb1234567890"  # ❌ WRONG!

# DON'T commit .env to git
git add .env  # ❌ WRONG!

# DON'T share .env in screenshots/logs
print(f"My API key: {BINANCE_API_KEY}")  # ❌ WRONG!
```

### ✅ ALWAYS DO THIS:
```python
# ✅ Use environment variables
import os
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')

# ✅ Check .gitignore includes .env
# .gitignore:
.env
.env.local
*.env

# ✅ Use .env.example as template
# .env.example (safe to commit):
BINANCE_API_KEY=your_key_here
```

---

## 🚀 REPLIT-SPECIFIC TIPS

### **How to Deploy on Replit:**

#### **1. Configure Run Command**
```bash
# .replit file
run = "python3 core/api/trading_api_server.py"

[env]
# These reference Replit Secrets
BINANCE_API_KEY = "${BINANCE_API_KEY}"
COINBASE_API_KEY = "${COINBASE_API_KEY}"
```

#### **2. Access Replit URL**
```
Your API will be at:
https://multimarketshadowscanner.yourname.repl.co

Update frontend:
NEXT_PUBLIC_API_URL=https://multimarketshadowscanner.yourname.repl.co
```

#### **3. Keep Replit Running (24/7)**
```
# Free tier: Repl sleeps after inactivity
# Always On (paid): $7/month keeps it running

# Or use UptimeRobot to ping every 5 minutes:
https://uptimerobot.com
```

---

## 📋 ENVIRONMENT VARIABLE CHECKLIST

### **Required for Backend (Python):**
- [ ] `BINANCE_API_KEY` + `BINANCE_API_SECRET`
- [ ] `COINBASE_API_KEY` + `COINBASE_API_SECRET`
- [ ] `OKX_API_KEY` + `OKX_API_SECRET`
- [ ] `KRAKEN_API_KEY` + `KRAKEN_API_SECRET`
- [ ] `ETHERSCAN_API_KEY` (for MetaMask tracking)

### **Required for AI Features:**
- [ ] `ANTHROPIC_API_KEY` (Claude API)
- [ ] `ABACUS_API_KEY` (Abacus.AI RouteLL M)

### **Required for Frontend (Next.js):**
- [ ] `NEXT_PUBLIC_API_URL` (backend API endpoint)

### **Optional:**
- [ ] `COINBASE_CDP_API_KEY` (Coinbase Commerce)
- [ ] `LIDO_API_KEY` (Lido staking)

---

## 🎯 ANSWER TO YOUR QUESTION

### **Q: "When I download the final app, will my .env come with it?"**

**A: NO, and here's why that's GOOD:**

1. **Security:** If .env was included, anyone who gets your code would have ALL your API keys and could drain your accounts.

2. **Git protection:** `.env` is in `.gitignore`, so it's never pushed to GitHub or included in downloads.

3. **Platform-specific:** Each environment (local, Replit, production) needs its own secrets configured separately.

4. **What you WILL get:**
   ```
   ✅ All your code (.py, .ts, .tsx files)
   ✅ Configuration files
   ✅ .env.example (template with placeholder values)
   ✅ README with setup instructions
   ```

5. **What you MUST do after download:**
   ```bash
   # Copy template
   cp .env.example .env

   # Add your real keys
   nano .env

   # Never commit it
   git add .gitignore  # Make sure .env is listed
   ```

---

## 🔄 RECOMMENDED WORKFLOW

### **For Maximum Security:**

1. **Store secrets in password manager** (1Password, Bitwarden)
2. **Use .env.example** in git (no real keys)
3. **Manually configure** secrets in each environment:
   - Local: `.env` file
   - Replit: Secrets UI
   - Production: Railway/Fly.io variables
4. **Rotate keys regularly** (change API keys every 3-6 months)
5. **Never screenshot** or log API keys

---

**SUMMARY:**
- ❌ .env files are NOT included when downloading
- ✅ This protects your API keys from theft
- 🔐 You must manually set up secrets in each environment
- 📦 Use Replit Secrets UI for cloud development
- 🚀 Use Railway/Fly.io variables for production
- 🎨 Abacus.AI dashboard only needs API URL (no secrets)

**Your secrets stay safe! Each platform has its own secure way to store them.**

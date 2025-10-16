# 🔐 PRODUCTION ENVIRONMENT SETUP GUIDE

## Quick Setup (5 Minutes)

### Step 1: Create .env.production file
```bash
cd /Volumes/LegacySafe/SovereignShadow
cp .env.template .env.production
```

### Step 2: Add Your Real API Keys

Edit `.env.production` and fill in these critical values:

```bash
# Coinbase (Your $1,660 hot wallet)
COINBASE_API_KEY=your_coinbase_key_here
COINBASE_API_SECRET=your_coinbase_secret_here

# OKX (For arbitrage)
OKX_API_KEY=your_okx_key_here
OKX_SECRET_KEY=your_okx_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here

# Kraken (For arbitrage)
KRAKEN_API_KEY=your_kraken_key_here
KRAKEN_PRIVATE_KEY=your_kraken_secret_here
```

### Step 3: Secure the file
```bash
chmod 600 .env.production
```

### Step 4: Validate connections
```bash
python3 scripts/validate_api_connections.py
```

## Capital Configuration

Your `.env.production` should reflect your actual holdings:

```bash
TOTAL_CAPITAL=8260
LEDGER_VAULT=6600        # Cold storage
COINBASE_HOT=1660        # Active trading
```

## Safety First

✅ **Do This:**
- Start with SANDBOX_MODE=true
- Test with PAPER_TRADING=true
- Keep LEDGER_READ_ONLY=true (ALWAYS)
- Set MAX_POSITION_SIZE=100 for first week

❌ **Never Do This:**
- Commit .env.production to git
- Share API keys in any form
- Enable ALL_IN_ENABLED initially
- Disable safety limits

## Quick Test

```bash
# Test API connections
python3 scripts/validate_api_connections.py

# Run neural bridge
python3 scripts/neural_bridge.py

# Deploy (paper mode first)
./DEPLOY_NEURAL_CONSCIOUSNESS.sh
```

## Your Philosophy

"Fearless. Bold. Smiling through chaos."

Target: $8,260 → $50,000 by Q4 2025

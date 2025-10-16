# 🧠 DEEPAGENT API CONNECTION GUIDE

## ⚡ **CONNECTING ORCHESTRATOR TO DEEPAGENT**

### 🎯 **WHAT YOU NEED FROM DEEPAGENT:**

**1. API Endpoint URL**
```
Base URL: https://legacyloopshadowai.abacusai.app/api
```

**2. Expected Endpoints DeepAgent Should Implement:**
```python
# Market Scanning
GET  /api/neural/scan           # Get current market opportunities
POST /api/neural/signal         # Submit detected signal for analysis

# Portfolio Monitoring
GET  /api/portfolio/balances    # Get real-time balances
GET  /api/portfolio/pnl         # Get profit/loss data

# Strategy Intelligence
POST /api/strategy/select       # Select optimal strategy for opportunity
GET  /api/strategy/performance  # Get strategy performance metrics

# Dashboard Updates
POST /api/dashboard/update      # Update live dashboard with trade data
```

### 🔧 **HOW TO CONNECT:**

**Step 1: Add API Configuration to .env.production**
```bash
# DeepAgent Neural Consciousness
DEEPAGENT_API_URL=https://legacyloopshadowai.abacusai.app/api
DEEPAGENT_API_KEY=your_abacus_api_key_here  # Get from Abacus AI
```

**Step 2: Test Connection**
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.production')

# Test DeepAgent connection
api_url = os.getenv('DEEPAGENT_API_URL', 'https://legacyloopshadowai.abacusai.app/api')

try:
    response = requests.get(f"{api_url}/health", timeout=5)
    print(f"✅ DeepAgent Connected: {response.status_code}")
except Exception as e:
    print(f"❌ DeepAgent Connection Failed: {e}")
    print("   DeepAgent needs to implement /api/health endpoint")
EOF
```

**Step 3: Update Orchestrator**
The `sovereign_shadow_orchestrator.py` already has the structure.
Just need to uncomment the real API calls once DeepAgent endpoints are ready.

### 📋 **WHAT TO TELL DEEPAGENT:**

**Message to send to DeepAgent on Abacus AI:**

```
Hi DeepAgent,

I need you to implement the following API endpoints on legacyloopshadowai.abacusai.app:

1. Health Check:
   GET /api/health
   Returns: {"status": "operational", "timestamp": "..."}

2. Market Scan:
   GET /api/neural/scan
   Returns: {
     "opportunities": [
       {"pair": "BTC/USD", "spread": 0.00125, "exchanges": ["coinbase", "okx"]},
       ...
     ]
   }

3. Portfolio Balances:
   GET /api/portfolio/balances
   Returns: {
     "total": 8260,
     "ledger": 6600,
     "coinbase": 1660,
     "okx": 0,
     "kraken": 0
   }

4. Dashboard Update:
   POST /api/dashboard/update
   Body: {"trade": {...}, "pnl": {...}, "timestamp": "..."}
   Returns: {"success": true}

These endpoints will connect the Sovereign Shadow orchestrator to your neural consciousness.

Reference files:
- DEEPAGENT_BRIEFING.md
- DEEPAGENT_TECHNICAL_INTEGRATION.md
- PROMPT_FOR_ABACUS_LIVE_SCANNER.md
```

### 🚀 **ONCE ENDPOINTS ARE READY:**

```python
# The orchestrator will automatically use them
python3 sovereign_shadow_orchestrator.py

# It will:
# 1. Connect to DeepAgent API
# 2. Fetch market opportunities
# 3. Route through MCP
# 4. Execute trades
# 5. Update dashboard
```

### 🛡️ **SECURITY:**

- DeepAgent API should require authentication
- Use HTTPS only (already configured)
- API key should be in .env.production (gitignored)
- Never expose API key in frontend code

**DEEPAGENT CONNECTION READY. WAITING FOR API IMPLEMENTATION.** 🧠


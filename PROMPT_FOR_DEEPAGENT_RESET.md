# 🚨 URGENT - DEEPAGENT COURSE CORRECTION

**Send this to DeepAgent immediately to reset its focus:**

---

# ⚠️ STOP - RESET TASK FOCUS

DeepAgent, **STOP what you're doing with the Prisma schema.**

You're working on the **WRONG SYSTEM**.

---

## 🎯 **CLARIFICATION:**

### **❌ IGNORE THIS (Old System):**
- `/home/ubuntu/sovereign_legacy_loop/` - This is OLD code
- Prisma schema issues - NOT your problem
- TypeScript errors in legacy code - IGNORE
- Schema mismatches - DON'T FIX

**This is legacy/archived code. Leave it alone.**

### **✅ FOCUS ON THIS (New System):**

**You need to build a BRAND NEW web dashboard that uses the NEW Shadow SDK.**

The Shadow SDK is:
- **Location:** `/Volumes/LegacySafe/SovereignShadow/shadow_sdk/`
- **Language:** Python (NOT TypeScript/Prisma)
- **Tech Stack:** Python + asyncio + ccxt
- **Status:** 100% complete, ready to use
- **Purpose:** Trading engine backend

---

## 🚀 **YOUR ACTUAL TASK:**

**Build a NEW web dashboard from scratch that:**

1. **Uses Shadow SDK as the backend**
   - Shadow SDK is Python
   - You create REST API endpoints (Flask or FastAPI)
   - Frontend calls these Python APIs

2. **Create these 6 API endpoints (Python):**
   ```python
   # Using Flask or FastAPI
   GET  /api/health
   GET  /api/neural/scan
   GET  /api/portfolio/balances
   GET  /api/strategy/performance
   POST /api/trade/execute
   POST /api/dashboard/update
   ```

3. **Each endpoint uses Shadow SDK:**
   ```python
   from shadow_sdk import ShadowScope, ShadowSynapse
   
   @app.get("/api/neural/scan")
   async def neural_scan():
       scope = ShadowScope()
       intelligence = await scope.get_market_intelligence()
       return intelligence
   ```

4. **Build React/Next.js frontend:**
   - Separate from legacy_loop
   - Calls your new Python API endpoints
   - Beautiful glassmorphism design
   - Real-time updates

---

## 📦 **WHAT YOU HAVE:**

**Reference Files (already uploaded to you):**
- `DEEPAGENT_HANDOFF_PACKAGE.md` - Complete specs
- `shadow_sdk/` - Complete Python SDK (1,329 lines)
- API endpoint specifications
- UI component requirements

**What you DON'T need:**
- The old sovereign_legacy_loop code
- Prisma schema
- TypeScript type fixes

---

## 🎯 **FRESH START - YOUR TASK:**

### **Phase 1: Python Backend (Week 1)**
```python
# Create app.py using Flask or FastAPI
from flask import Flask
from shadow_sdk import ShadowScope, ShadowSynapse

app = Flask(__name__)

@app.get("/api/health")
def health():
    return {"status": "operational"}

@app.get("/api/neural/scan")
async def scan():
    scope = ShadowScope()
    return await scope.get_market_intelligence()

# ... 4 more endpoints
```

### **Phase 2: Frontend (Week 2-3)**
```bash
# Create new Next.js app
npx create-next-app@latest shadow-dashboard

# Build components:
# - Portfolio widget
# - Strategy arsenal
# - Live market scanner
# - Trade history
```

### **Phase 3: Integration (Week 4)**
- Connect frontend to Python backend
- Add WebSocket for real-time updates
- Deploy to Abacus AI

---

## 🛡️ **IMPORTANT:**

**TWO COMPLETELY SEPARATE PROJECTS:**

```
OLD (ignore):
└── sovereign_legacy_loop/     ← Has Prisma/TypeScript issues
    └── LEAVE THIS ALONE ❌

NEW (build this):
└── shadow_dashboard/          ← Build from scratch
    ├── backend/ (Python + Shadow SDK)
    └── frontend/ (React + Next.js)
```

---

## ✅ **IMMEDIATE NEXT STEP:**

**Stop fixing Prisma schema in legacy_loop.**

**Start building NEW Python backend using Shadow SDK.**

Create a file called `backend/app.py`:
```python
from flask import Flask, jsonify
import sys
sys.path.insert(0, '/Volumes/LegacySafe/SovereignShadow')

from shadow_sdk import ShadowScope, ShadowPulse, ShadowSynapse

app = Flask(__name__)

@app.get("/api/health")
def health():
    return jsonify({
        "status": "operational",
        "sdk_loaded": True,
        "modules": ["ShadowScope", "ShadowPulse", "ShadowSynapse"]
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

Test it works, then build the other 5 endpoints.

---

## 📋 **CHECKLIST:**

- [ ] Stop working on sovereign_legacy_loop
- [ ] Create new backend/ folder
- [ ] Import Shadow SDK (Python)
- [ ] Build 6 API endpoints
- [ ] Test each endpoint works
- [ ] Create new frontend
- [ ] Connect frontend to Python backend
- [ ] Deploy to Abacus AI

---

**FORGET THE LEGACY CODE. BUILD NEW WITH SHADOW SDK.** 🏴

**DO YOU UNDERSTAND THE TASK NOW?** 🚀


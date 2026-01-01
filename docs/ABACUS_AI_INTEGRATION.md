# 🤖 ABACUS.AI INTEGRATION GUIDE

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json.

**Date:** October 31, 2025 (Updated Dec 2025)
**Purpose:** Align Abacus.AI DeepAgent dashboard with Sovereign Shadow backend

---

## 📋 WHAT YOU'RE TRYING TO DO

**Goal:** Use Abacus.AI DeepAgent to create a beautiful frontend dashboard that displays data from your SovereignShadow trading backend.

**Current Status:**
- ✅ Backend is ready (Python FastAPI server)
- ✅ Frontend bridge is connected (mcp-bridge.ts)
- ⚠️ Abacus.AI needs the right files uploaded

**Your uploaded files:**
1. `build.py` - Build/deployment script
2. `agent_swarm_pnl.json` - Swarm agent P&L data
3. `shadow_army_pnl.json` - Shadow army P&L data
4. `shadow_swarm.py` - Swarm coordination logic
5. `shadow_agent.py` - Individual agent logic

---

## 🎯 ABACUS.AI ROLE IN YOUR ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│          YOUR COMPLETE TRADING SYSTEM                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🐍 BACKEND (Python)                                    │
│     /Volumes/LegacySafe/SovereignShadow/                │
│     ├─ unified_portfolio_api.py   → Data aggregation   │
│     ├─ UniversalExchangeManager   → Live trading       │
│     ├─ shadow_swarm.py            → Agent coordination  │
│     └─ shadow_agent.py            → Individual agents   │
│                                                         │
│           ↓ (exposes via)                               │
│                                                         │
│  🌐 API SERVER (FastAPI)                                │
│     Port 8000                                           │
│     ├─ GET  /api/health                                 │
│     ├─ GET  /api/strategy/performance                   │
│     ├─ POST /api/trade/execute                          │
│     └─ WS   /ws/dashboard                               │
│                                                         │
│           ↓ (consumed by)                               │
│                                                         │
│  🎨 FRONTEND (TypeScript/React)                         │
│     ├─ mcp-bridge.ts              → API client          │
│     └─ fetch('http://localhost:8000/api/...')          │
│                                                         │
│           ↓ (hosted on)                                 │
│                                                         │
│  🤖 ABACUS.AI DeepAgent                                 │
│     legacyloopshadowai.abacusai.app                    │
│     ├─ Beautiful UI/UX            → Dashboard           │
│     ├─ Portfolio charts           → Visualizations      │
│     ├─ Trade controls             → Execution panel     │
│     └─ AI chat interface          → RouteLL M           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ IMPORTANT: WHAT TO UPLOAD TO ABACUS.AI

### **WHAT ABACUS.AI NEEDS:**
✅ **Frontend files only** (UI/dashboard components)
✅ **Configuration files** (how to connect to your API)
✅ **Schema definitions** (what data looks like)
❌ **NO backend code** (already running on your machine/Replit)

### **CORRECT FILES TO UPLOAD:**

#### **1. Frontend Dashboard Code**
```
app/
├── components/           → React/Next.js UI components
├── lib/
│   └── mcp-bridge.ts    → API client (already updated!)
├── pages/ or app/       → Dashboard routes
└── public/              → Assets (logos, images)
```

#### **2. Configuration**
```
.env.example             → Template (no real keys!)
NEXT_PUBLIC_API_URL=http://localhost:8000

or for production:
NEXT_PUBLIC_API_URL=https://your-replit-url.repl.co
```

#### **3. Schema Files (Optional)**
```
agent_swarm_pnl.json     → P&L data structure
shadow_army_pnl.json     → Performance metrics structure
```

### **WHAT NOT TO UPLOAD:**

❌ **Backend Python code** - Keep on your local/Replit
❌ **Trading engines** - Too sensitive for dashboard
❌ **API keys / .env files** - Security risk!
❌ **Database files** - Too large, use API instead

---

## 🔄 PROPER INTEGRATION WORKFLOW

### **Step 1: Deploy Backend API** (Choose One)

#### **Option A: Run Locally**
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 core/api/trading_api_server.py
# API available at: http://localhost:8000
```

#### **Option B: Deploy to Replit**
```bash
# Push to Replit
# Set Replit Secrets (API keys)
# Run: python3 core/api/trading_api_server.py
# API available at: https://your-repl-url.repl.co
```

#### **Option C: Deploy to Production**
```bash
# Railway
railway up
railway variables set BINANCE_API_KEY=xxx

# Fly.io
fly deploy
fly secrets set BINANCE_API_KEY=xxx

# API available at: https://api.sovereignshadow.com
```

---

### **Step 2: Upload Frontend to Abacus.AI**

**What to tell DeepAgent:**

```
"I want to create a trading dashboard that displays:

1. Portfolio Overview
   - Total balance: $6,203.94
   - Ledger vault: $6,167.43
   - MetaMask: $36.51
   - AAVE health factor

2. Trading Performance
   - Active strategies
   - Win rate
   - Total profit
   - Recent trades

3. Real-time Updates
   - Live prices
   - Position changes
   - Alerts

The backend API is at: http://localhost:8000
(or https://your-replit-url.repl.co)

Use the mcp-bridge.ts file I uploaded to fetch data.
Create a modern, responsive dashboard with charts and controls."
```

**Files to upload:**
1. `/app/lib/mcp-bridge.ts` ← Already connected to your API!
2. `/app/components/` folder (if you have existing UI components)
3. `agent_swarm_pnl.json` + `shadow_army_pnl.json` ← Shows data format
4. `.env.example` with `NEXT_PUBLIC_API_URL` set

---

### **Step 3: Configure API Connection**

**In Abacus.AI project settings:**
```bash
# Environment variable
NEXT_PUBLIC_API_URL=http://localhost:8000

# Or for Replit
NEXT_PUBLIC_API_URL=https://multimarketshadowscanner.yourname.repl.co

# Or for production
NEXT_PUBLIC_API_URL=https://api.sovereignshadow.com
```

**DeepAgent will then:**
- Read `mcp-bridge.ts` to understand API calls
- Create UI components that call `MCPBridge.getEmpire()`
- Display portfolio, trades, and performance
- Add charts, tables, and controls

---

## 📁 YOUR FILES EXPLAINED

### **1. build.py**
**Purpose:** Build/deployment automation script
**What it likely does:**
- Compiles frontend assets
- Bundles JavaScript/TypeScript
- Prepares for deployment

**Should you upload to Abacus.AI?**
- ❌ NO - Abacus.AI handles builds automatically
- ✅ Keep for local/Replit deployment

---

### **2. agent_swarm_pnl.json**
**Purpose:** Profit & Loss data from agent swarm
**Example structure:**
```json
{
  "total_pnl": 52.35,
  "trades": 12,
  "win_rate": 0.75,
  "agents": [
    {
      "name": "Whale Watcher",
      "pnl": 15.23,
      "confidence": 85
    },
    {
      "name": "Technical Master",
      "pnl": 22.44,
      "confidence": 92
    }
  ]
}
```

**Should you upload to Abacus.AI?**
- ✅ YES - Shows DeepAgent what data format looks like
- ✅ Helps generate correct UI components
- ✅ Acts as schema/example

---

### **3. shadow_army_pnl.json**
**Purpose:** Performance metrics from shadow army (multi-agent system)
**Example structure:**
```json
{
  "army_total_pnl": 84.12,
  "active_agents": 6,
  "strategies": [
    {
      "name": "Ladder Entry SUI",
      "pnl": 28.50,
      "status": "active"
    }
  ]
}
```

**Should you upload to Abacus.AI?**
- ✅ YES - Data format example
- ✅ Helps design dashboard metrics

---

### **4. shadow_swarm.py**
**Purpose:** Swarm coordination logic (hive mind)
**What it does:**
- Coordinates multiple trading agents
- Aggregates signals from all agents
- Makes consensus decisions
- Manages agent lifecycle

**Should you upload to Abacus.AI?**
- ❌ NO - This is backend logic
- ❌ Already running in your Python backend
- ⚠️ If you upload, DeepAgent might try to rebuild it (waste of time)

**What to do instead:**
- ✅ Keep in `/Volumes/LegacySafe/SovereignShadow/SwarmAgents/`
- ✅ Access via API: `GET /api/swarm/status`
- ✅ Tell DeepAgent: "Fetch swarm data from API endpoint"

---

### **5. shadow_agent.py**
**Purpose:** Individual agent logic
**What it does:**
- Single agent behavior (whale watcher, sentiment scanner, etc.)
- Signal generation
- Technical analysis
- Risk assessment

**Should you upload to Abacus.AI?**
- ❌ NO - This is backend logic
- ❌ Already running in your Python backend
- ✅ Instead, create UI component that displays agent status

---

## 🎯 WHAT TO TELL ABACUS.AI DeepAgent

### **Recommended Prompt:**

```
"I have a cryptocurrency trading system with a Python FastAPI backend
running at http://localhost:8000.

I uploaded mcp-bridge.ts which is a TypeScript client that fetches data
from the API.

Please create a modern trading dashboard with these sections:

1. PORTFOLIO OVERVIEW CARD
   - Total balance (from MCPBridge.getEmpire())
   - Ledger vault amount
   - MetaMask balance
   - AAVE health factor
   - Display using large numbers and colors

2. TRADING PERFORMANCE PANEL
   - Strategy list (from MCPBridge.getStrategyPerformance())
   - Win rate percentage
   - Total profit (green if positive, red if negative)
   - Active trades count
   - Display as cards with charts

3. AGENT SWARM STATUS
   - Show data from agent_swarm_pnl.json format
   - Display each agent as a card
   - Show confidence levels as progress bars
   - Color code by performance

4. TRADE EXECUTION PANEL
   - Dropdown to select strategy
   - Input for trading pair (e.g., SUI-USD)
   - Input for amount
   - Button to execute (calls MCPBridge.executeTrade())
   - Show paper/test/live mode toggle

5. REAL-TIME UPDATES
   - WebSocket connection to ws://localhost:8000/ws/dashboard
   - Update portfolio every 30 seconds
   - Show trade notifications as toasts

Use a dark theme with accent colors:
- Primary: #6366f1 (indigo)
- Success: #10b981 (green)
- Warning: #f59e0b (amber)
- Danger: #ef4444 (red)

Make it responsive (mobile-friendly).
Add loading states and error handling.
"
```

---

## 🚀 DEPLOYMENT OPTIONS

### **Option 1: Abacus.AI Dashboard Only** (Recommended)

```
┌─────────────────────────────────────┐
│  🤖 Abacus.AI                       │
│     legacyloopshadowai.abacusai.app │
│     Frontend ONLY (dashboard UI)    │
│                                     │
│           ↓ calls API               │
│                                     │
│  🐍 Your Local Machine / Replit     │
│     FastAPI Backend (Port 8000)     │
│     All trading engines             │
│     Real portfolio access           │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ Simple setup
- ✅ Dashboard updates instantly
- ✅ Backend has direct access to exchanges
- ✅ No secrets in Abacus.AI

---

### **Option 2: Full Stack on Replit**

```
┌─────────────────────────────────────┐
│  🤖 Abacus.AI                       │
│     Frontend (display only)         │
│                                     │
│           ↓ calls API               │
│                                     │
│  🔧 Replit                          │
│     Backend + Frontend together     │
│     API: https://your-repl.repl.co  │
│     24/7 with "Always On" ($7/month)│
└─────────────────────────────────────┘
```

**Pros:**
- ✅ Everything in one place
- ✅ Easy to manage
- ✅ Free tier available (with sleep)

---

### **Option 3: Production Split**

```
┌─────────────────────────────────────┐
│  🤖 Abacus.AI                       │
│     legacyloopshadowai.abacusai.app │
│     Frontend (CDN, fast)            │
│                                     │
│           ↓ calls API               │
│                                     │
│  ☁️ Railway / Fly.io / AWS          │
│     api.sovereignshadow.com         │
│     Backend API (24/7, scaled)      │
│     Professional hosting            │
└─────────────────────────────────────┘
```

**Pros:**
- ✅ Professional setup
- ✅ Scalable
- ✅ Reliable uptime
- ✅ Custom domain

---

## ✅ ACTION PLAN

### **RIGHT NOW:**

1. **Keep backend running locally:**
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 core/api/trading_api_server.py
```

2. **Upload ONLY these to Abacus.AI:**
   - ✅ `app/lib/mcp-bridge.ts` (API client)
   - ✅ `agent_swarm_pnl.json` (data format example)
   - ✅ `shadow_army_pnl.json` (data format example)
   - ❌ NOT: `shadow_swarm.py` (backend logic)
   - ❌ NOT: `shadow_agent.py` (backend logic)
   - ❌ NOT: `build.py` (Abacus handles builds)

3. **Tell DeepAgent:**
```
"Create a trading dashboard using mcp-bridge.ts to fetch data
from my API at http://localhost:8000.

Use the JSON files as examples of data structure.

Create cards for portfolio overview, strategy performance,
and agent swarm status."
```

4. **Test the connection:**
   - Dashboard loads at legacyloopshadowai.abacusai.app
   - Open browser console (F12)
   - Should see fetch calls to localhost:8000
   - Portfolio data appears on dashboard

---

## ⚠️ COMMON MISTAKES TO AVOID

### **❌ DON'T:**
1. Upload entire backend code to Abacus.AI
2. Include API keys or .env files
3. Try to run trading engines in the dashboard
4. Upload shadow_swarm.py or shadow_agent.py

### **✅ DO:**
1. Upload only frontend UI code
2. Upload data format examples (JSON)
3. Upload API client (mcp-bridge.ts)
4. Set NEXT_PUBLIC_API_URL to your backend

---

## 📊 SUCCESS CRITERIA

**You'll know it's working when:**

✅ Abacus.AI dashboard loads
✅ Portfolio balance displays: $6,203.94
✅ AAVE health factor shows up
✅ Strategy performance table appears
✅ Agent swarm cards display
✅ Browser console shows successful API calls
✅ No CORS errors
✅ Real-time updates work

---

## 🎯 SUMMARY

**What Abacus.AI is for:**
- 🎨 Beautiful UI/dashboard (frontend ONLY)
- 📊 Display data from YOUR backend API
- 🖱️ User controls (buttons, inputs, charts)

**What Abacus.AI is NOT for:**
- ❌ Running trading engines
- ❌ Storing API keys
- ❌ Backend logic execution
- ❌ Direct exchange access

**The correct flow:**
```
User opens: legacyloopshadowai.abacusai.app
    ↓
Dashboard calls: fetch('http://localhost:8000/api/health')
    ↓
Your backend responds with: { ledger: 6167.43, metamask: 36.51, ... }
    ↓
Dashboard displays: "Total Portfolio: $6,203.94"
```

**Next step:** Tell Abacus.AI DeepAgent what you want the dashboard to look like, and give it mcp-bridge.ts + the JSON files!

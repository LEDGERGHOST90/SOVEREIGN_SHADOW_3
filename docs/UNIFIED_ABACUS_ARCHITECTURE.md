# Unified SovereignShadow - Abacus AI Architecture

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json.

## Vision
Single command center at `1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev` that combines:
- **StrategyScout AI** (Gemini frontend) - Strategy analysis, transcription, protocols
- **SovereignShadow_II** (Python backend) - Trading execution, portfolio management
- **Persistent Memory** - Database-backed storage, no more localStorage

## Current State

```
┌─────────────────────────────────────────────────────────────────┐
│                     CURRENT (Disconnected)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │ Gemini React App │    │ Abacus Website   │                  │
│  │ (localhost:5173) │    │ (Auth page only) │                  │
│  │                  │    │                  │                  │
│  │ • Strategy Scout │    │ • Landing page   │                  │
│  │ • LocalAgent     │    │ • No backend     │                  │
│  │ • localStorage   │    │                  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│           │                                                     │
│           │ (No connection)                                     │
│           │                                                     │
│  ┌──────────────────┐                                          │
│  │ SovereignShadow  │                                          │
│  │ Python System    │                                          │
│  │                  │                                          │
│  │ • shade_agent    │                                          │
│  │ • meme_machine   │                                          │
│  │ • Exchange APIs  │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED ABACUS DEPLOYMENT                          │
│              sovereignnshadowii.abacusai.app                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND LAYER                        │   │
│  │              (React + Vite, deployed to Abacus)         │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────┐ │   │
│  │  │ Dashboard │ │ Strategy  │ │ Portfolio │ │ Scanner │ │   │
│  │  │           │ │ Analyzer  │ │ View      │ │         │ │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └─────────┘ │   │
│  │                                                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────┐ │   │
│  │  │ Protocols │ │ Trade     │ │ AAVE      │ │ Session │ │   │
│  │  │ (4 types) │ │ Journal   │ │ Monitor   │ │ Memory  │ │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └─────────┘ │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API GATEWAY                           │   │
│  │              (FastAPI / Abacus Functions)               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  /api/portfolio    → Get balances from all exchanges    │   │
│  │  /api/strategies   → CRUD for analyzed strategies       │   │
│  │  /api/trades       → Execute trades via shade_agent     │   │
│  │  /api/scanner      → meme_machine breakout scanner      │   │
│  │  /api/aave         → Health factor, debt status         │   │
│  │  /api/session      → Persistent session state           │   │
│  │  /api/transcribe   → Audio → text via Gemini            │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 BACKEND SERVICES                         │   │
│  │              (Python, running on Abacus)                │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  ┌───────────────────┐  ┌───────────────────┐          │   │
│  │  │   shade_agent     │  │   meme_machine    │          │   │
│  │  │   (Trading Bot)   │  │   (Scanner)       │          │   │
│  │  └───────────────────┘  └───────────────────┘          │   │
│  │                                                         │   │
│  │  ┌───────────────────┐  ┌───────────────────┐          │   │
│  │  │ Exchange Connectors│  │  AAVE Monitor    │          │   │
│  │  │ • Coinbase        │  │  (DeFi Health)   │          │   │
│  │  │ • Kraken          │  │                   │          │   │
│  │  └───────────────────┘  └───────────────────┘          │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  DATA LAYER                              │   │
│  │           (Abacus Database / Supabase)                  │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  strategies    │ trades      │ sessions    │ portfolio │   │
│  │  ─────────────│─────────────│─────────────│───────────│   │
│  │  • id         │ • id        │ • date      │ • asset   │   │
│  │  • name       │ • timestamp │ • state     │ • balance │   │
│  │  • category   │ • asset     │ • memory    │ • value   │   │
│  │  • conditions │ • side      │ • todos     │ • change  │   │
│  │  • sentiment  │ • profit    │             │           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Components Needed

### 1. API Gateway (FastAPI)
Create `/api/` endpoints that bridge frontend to Python backend:

```python
# sovereign_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SovereignShadow API")

@app.get("/api/portfolio")
async def get_portfolio():
    """Aggregate balances from all exchanges"""
    pass

@app.get("/api/strategies")
async def get_strategies():
    """List all analyzed strategies"""
    pass

@app.post("/api/strategies")
async def save_strategy(strategy: dict):
    """Save strategy from Gemini analysis"""
    pass

@app.get("/api/scanner/breakout")
async def get_breakouts():
    """Run meme_machine breakout scanner"""
    pass
```

### 2. Database Schema
Replace localStorage with persistent database:

```sql
-- strategies table
CREATE TABLE strategies (
    id UUID PRIMARY KEY,
    name TEXT,
    category TEXT, -- Vault, Sniper, Ladder, MENACE
    risk_level TEXT,
    buy_conditions JSONB,
    sell_conditions JSONB,
    sentiment INTEGER,
    created_at TIMESTAMP,
    source TEXT -- youtube, audio, manual
);

-- trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    strategy_id UUID REFERENCES strategies(id),
    asset TEXT,
    side TEXT, -- buy/sell
    amount DECIMAL,
    price DECIMAL,
    profit DECIMAL,
    executed_at TIMESTAMP
);

-- sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    date DATE,
    state JSONB,
    portfolio_snapshot JSONB,
    created_at TIMESTAMP
);
```

### 3. Frontend Updates
Modify Gemini app to call API instead of localStorage:

```typescript
// services/apiService.ts
const API_BASE = 'https://sovereignnshadowii.abacusai.app/api';

export const saveStrategy = async (strategy: Strategy) => {
  const res = await fetch(`${API_BASE}/strategies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(strategy)
  });
  return res.json();
};

export const getPortfolio = async () => {
  const res = await fetch(`${API_BASE}/portfolio`);
  return res.json();
};
```

## Deployment Options

### Option A: Abacus AI Native (Recommended)
- Use Abacus AI's built-in deployment for the React frontend
- Use Abacus Functions for Python backend
- Use Abacus Database for persistence

### Option B: Hybrid
- Deploy React frontend to Abacus
- Run Python backend on your Mac (always-on)
- Use ngrok/Cloudflare Tunnel to expose APIs

### Option C: Full Self-Hosted
- Deploy everything to a VPS (Railway, Render, DigitalOcean)
- Point Abacus domain to your server

## Security Requirements

1. **API Keys**: Store in Abacus environment variables, NEVER in code
2. **Authentication**: Add JWT auth to API endpoints
3. **CORS**: Restrict to your domain only
4. **Rate Limiting**: Prevent abuse

## Migration Path

### Phase 1: API Bridge (Week 1)
- [ ] Create FastAPI server with basic endpoints
- [ ] Test locally with existing Python code
- [ ] Add CORS for Gemini app

### Phase 2: Frontend Integration (Week 2)
- [ ] Update Gemini app to call API
- [ ] Add Portfolio view component
- [ ] Add Trade execution UI

### Phase 3: Database Migration (Week 3)
- [ ] Set up Abacus/Supabase database
- [ ] Migrate localStorage to database
- [ ] Add session persistence

### Phase 4: Production Deploy (Week 4)
- [ ] Deploy API to Abacus Functions
- [ ] Deploy frontend to Abacus
- [ ] Configure domain and SSL
- [ ] Security hardening

## Quick Win: Local Bridge Server

Start with a simple bridge that runs locally:

```bash
# Start the bridge server
python3 sovereign_api.py

# Gemini app calls localhost:8000/api/*
# Which talks to your existing Python code
```

This lets you test the full integration before deploying to Abacus.

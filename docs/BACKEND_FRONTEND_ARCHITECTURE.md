# 🏗️ SOVEREIGN SHADOW: BACKEND ↔ FRONTEND ARCHITECTURE

**Date:** October 31, 2025
**Purpose:** Complete data flow from exchanges/wallets → backend engines → API server → frontend dashboard

---

## 📊 COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    🌐 DATA SOURCES (LIVE)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔒 Ledger Hardware     🔥 MetaMask        🏦 Exchanges         │
│     $6,167.43              $36.51            TBD                │
│     • BTC cold            • 3 addresses      • Coinbase         │
│     • AAVE DeFi           • Etherscan API    • OKX              │
│     • CSV export                             • Kraken           │
│                                              • CCXT library      │
│  🔗 DeFi Protocols                                              │
│     • AAVE v3 (health factor monitoring)                        │
│     • Lido stETH rewards                                        │
│                                                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              🐍 PYTHON BACKEND (Data Layer)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 unified_portfolio_api.py                                    │
│     /SovereignShadow/core/portfolio/                            │
│     ├─ get_complete_portfolio()     → Aggregates ALL sources   │
│     ├─ get_metamask_hot_wallet()    → Live Etherscan fetch     │
│     ├─ get_defi_positions()         → AAVE health factor       │
│     ├─ get_hot_wallet_velocity()    → Exchange balances        │
│     └─ export_for_mcp_server()      → MCP JSON context         │
│                                                                 │
│  🔄 UniversalExchangeManager                                    │
│     /SovereignShadow/modules/execution/                         │
│     ├─ connect_all()                → CCXT multi-exchange       │
│     ├─ fetch_ticker(pair)           → Live prices              │
│     └─ execute_order(params)        → Trade execution          │
│                                                                 │
│  💉 InjectionManager                                            │
│     /SovereignShadow/modules/tracking/                          │
│     ├─ inject_all()                 → Aggregate price data     │
│     └─ get_price(pair)              → Cross-exchange pricing   │
│                                                                 │
│  🧠 SwarmAgents (Hive Mind)                                     │
│     /SovereignShadow 2/SwarmAgents/                             │
│     ├─ sentiment_scanner.py         → Social sentiment         │
│     ├─ whale_watcher.py             → Whale movement tracking  │
│     └─ hive_mind.py                 → Consensus decisions       │
│                                                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│          🌐 FASTAPI SERVER (API Layer)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🚀 trading_api_server.py                                       │
│     /SovereignShadow/core/api/                                  │
│     Port: 8000                                                  │
│                                                                 │
│     REST ENDPOINTS:                                             │
│     ├─ GET  /api/health                                         │
│     │   → Server status, AAVE health, session PnL              │
│     │                                                           │
│     ├─ GET  /api/strategy/performance                           │
│     │   → All active strategies, win rate, profits             │
│     │                                                           │
│     ├─ POST /api/trade/execute                                  │
│     │   → Execute trade with risk validation                   │
│     │   Request: {strategy, pair, amount, mode}                │
│     │   Response: {trade_id, status, profit, warnings}         │
│     │                                                           │
│     └─ POST /api/dashboard/update                               │
│         → Broadcast event to connected dashboards              │
│                                                                 │
│     WEBSOCKET:                                                  │
│     └─ WS   /ws/dashboard                                       │
│         → Real-time streaming updates                           │
│         → Broadcasts: trades, balances, alerts                 │
│                                                                 │
│     CORS ALLOWED ORIGINS:                                       │
│     • https://legacyloopshadowai.abacusai.app                  │
│     • http://localhost:3000                                     │
│                                                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│         🎨 FRONTEND BRIDGE (TypeScript Layer)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🌉 mcp-bridge.ts                                               │
│     /SovereignShadow/app/lib/                                   │
│                                                                 │
│     export class MCPBridge {                                    │
│       static async getEmpire(): Promise<EmpireData>             │
│       static async getVault(): Promise<VaultHoldings>           │
│       static async checkBinance(): Promise<HealthCheck>         │
│     }                                                           │
│                                                                 │
│     CURRENT DATA (Hardcoded from Oct 30):                       │
│     • totalValue: $8,707.86                                     │
│     • ledgerVault: $7,685.52                                    │
│     • binanceUs: $977.11                                        │
│                                                                 │
│     ⚠️ TODO: Replace hardcoded data with live API calls:        │
│     const response = await fetch('http://localhost:8000/api...')│
│                                                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│          🤖 ABACUS.AI LAYER (NEW Integration)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📡 RouteLL M API                                               │
│     URL: https://routellm.abacus.ai/v1/chat/completions        │
│     Model: "route-llm"                                          │
│                                                                 │
│     PURPOSE:                                                    │
│     • AI-powered dashboard intelligence                         │
│     • Natural language queries to portfolio                     │
│     • Autonomous decision explanations                          │
│                                                                 │
│     USAGE PATTERN:                                              │
│     ```python                                                   │
│     import requests                                             │
│     import json                                                 │
│                                                                 │
│     url = "https://routellm.abacus.ai/v1/chat/completions"     │
│     headers = {                                                 │
│         "Authorization": "Bearer <api_key>",                    │
│         "Content-Type": "application/json"                      │
│     }                                                           │
│     payload = {                                                 │
│         "model": "route-llm",                                   │
│         "messages": [{                                          │
│             "role": "user",                                     │
│             "content": "What's my portfolio performance?"       │
│         }],                                                     │
│         "stream": True                                          │
│     }                                                           │
│     ```                                                         │
│                                                                 │
│  🎨 DeepAgent Dashboard                                         │
│     URL: https://legacyloopshadowai.abacusai.app               │
│     • Frontend UI/UX (Next.js)                                  │
│     • Real-time portfolio visualization                         │
│     • Trading strategy controls                                 │
│     • Performance charts & analytics                            │
│                                                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│            👤 USER INTERFACE (Dashboard)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Portfolio Overview                                          │
│     • Total balance: $6,203.94 (live)                           │
│     • Ledger cold storage: $2,231.74 BTC                        │
│     • AAVE DeFi position: $3,904.74 (health factor)             │
│     • MetaMask hot: $36.51                                      │
│     • Exchange balances: TBD                                    │
│                                                                 │
│  📈 Trading Dashboard                                           │
│     • Active ladders: 25 positions                              │
│     • Live P&L: +$XX.XX (real-time)                             │
│     • Win rate: XX%                                             │
│     • Today's trades: X                                         │
│                                                                 │
│  🚨 Alerts & Monitoring                                         │
│     • AAVE health factor warnings                               │
│     • Stop loss triggers                                        │
│     • Whale movement alerts                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 HOW IT ALL CONNECTS: DATA FLOW EXAMPLE

### Example: User Opens Dashboard → Sees Portfolio Balance

**Step 1: Frontend Request (Dashboard loads)**
```typescript
// In Next.js component: /app/dashboard/page.tsx
import { MCPBridge } from '@/lib/mcp-bridge';

const portfolioData = await MCPBridge.getEmpire();
// Currently returns hardcoded: $8,707.86
```

**Step 2: MCPBridge Calls FastAPI (SHOULD DO THIS)**
```typescript
// mcp-bridge.ts SHOULD call:
const response = await fetch('http://localhost:8000/api/health');
const data = await response.json();
// Returns: {
//   status: "healthy",
//   ledger_balance: 6167.43,
//   metamask_balance: 36.51,
//   exchange_balance: "TBD",
//   aave_health_factor: 2.45,
//   session_pnl: +15.23
// }
```

**Step 3: FastAPI Calls Python Backend**
```python
# trading_api_server.py endpoint handler
@app.get("/api/health")
async def health_check():
    # Import portfolio API
    from core.portfolio.unified_portfolio_api import UnifiedPortfolioAPI

    portfolio = UnifiedPortfolioAPI()
    complete_data = portfolio.get_complete_portfolio()

    # Returns aggregated data from:
    # - Ledger CSV (cold vault monitor)
    # - MetaMask Etherscan API (live blockchain)
    # - Exchange CCXT (Coinbase, OKX, Kraken)
    # - AAVE protocol (health factor)

    return {
        "status": "healthy",
        "ledger_balance": complete_data["ledger"]["total_usd"],
        "metamask_balance": complete_data["metamask"]["total_usd"],
        "exchange_balance": complete_data["exchanges"]["total_usd"],
        "aave_health_factor": complete_data["defi"]["aave"]["health_factor"],
        "session_pnl": calculate_session_pnl()
    }
```

**Step 4: Python Backend Fetches Live Data**
```python
# unified_portfolio_api.py
class UnifiedPortfolioAPI:
    def get_complete_portfolio(self):
        # 1. Get Ledger (from CSV export)
        ledger_data = self.cold_vault_monitor.get_current_holdings()

        # 2. Get MetaMask (live Etherscan API)
        metamask_data = self.metamask_tracker.get_all_balances()

        # 3. Get Exchanges (live CCXT API)
        exchange_data = self.universal_manager.get_all_balances()

        # 4. Get AAVE DeFi (live protocol query)
        aave_data = self.get_defi_positions()

        # 5. Aggregate and return
        return {
            "ledger": ledger_data,
            "metamask": metamask_data,
            "exchanges": exchange_data,
            "defi": aave_data,
            "total_usd": sum_all()
        }
```

**Step 5: Display in Dashboard**
```tsx
// Dashboard component renders
<PortfolioCard
  total={portfolioData.totalValue}
  ledger={portfolioData.ledgerVault}
  metamask={portfolioData.metamask}
  exchanges={portfolioData.binanceUs}
  healthFactor={portfolioData.aaveHealthFactor}
/>
```

---

## 🔗 CURRENT CONNECTION STATUS

### ✅ WORKING:
1. **Backend Python APIs** - unified_portfolio_api.py aggregates data
2. **FastAPI Server** - trading_api_server.py exposes REST endpoints
3. **CORS Config** - Allows legacyloopshadowai.abacusai.app access

### ⚠️ PARTIALLY WORKING:
1. **MCP Bridge** - Returns hardcoded data instead of calling API
2. **Exchange Balances** - API configured but not fetched (shows "TBD")
3. **AAVE Health** - Position identified but not monitored

### ❌ NOT CONNECTED YET:
1. **Frontend → FastAPI** - mcp-bridge.ts needs to call localhost:8000
2. **Abacus.AI → Backend** - Dashboard needs to integrate with API
3. **Live WebSocket** - Real-time streaming not implemented in frontend

---

## 🚀 HOW TO CONNECT FRONTEND TO BACKEND

### Option 1: Direct API Calls (Recommended)

**Update mcp-bridge.ts:**
```typescript
export class MCPBridge {
  private static API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  static async getEmpire(): Promise<EmpireData> {
    try {
      const response = await fetch(`${this.API_BASE}/api/health`);
      const data = await response.json();

      return {
        totalValue: data.ledger_balance + data.metamask_balance + (data.exchange_balance || 0),
        ledgerVault: data.ledger_balance,
        binanceUs: data.exchange_balance || 0,
        lidoRewards: data.aave_staking_rewards || 0,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to fetch empire data:', error);
      // Fallback to cached/hardcoded data
      return { /* ... fallback data ... */ };
    }
  }

  static async getVault(): Promise<VaultHoldings> {
    const response = await fetch(`${this.API_BASE}/api/portfolio/ledger`);
    const data = await response.json();
    return data.holdings;
  }
}
```

### Option 2: WebSocket for Real-Time Updates

**Add WebSocket client:**
```typescript
export class RealtimePortfolio {
  private ws: WebSocket;

  connect(onUpdate: (data: EmpireData) => void) {
    this.ws = new WebSocket('ws://localhost:8000/ws/dashboard');

    this.ws.onmessage = (event) => {
      const update = JSON.parse(event.data);

      if (update.type === 'portfolio_update') {
        onUpdate(update.data);
      }

      if (update.type === 'trade_executed') {
        // Show toast notification
        toast.success(`Trade executed: ${update.profit} profit`);
      }
    };
  }
}
```

### Option 3: Abacus.AI RouteLL M Integration

**Use for AI queries:**
```python
# Create new endpoint: /api/ai/query
@app.post("/api/ai/query")
async def query_ai(request: AIQueryRequest):
    """
    Natural language queries to portfolio using Abacus.AI
    Example: "Should I enter SUI at current price?"
    """
    # Get current portfolio context
    portfolio = UnifiedPortfolioAPI()
    context = portfolio.get_ai_context_summary()

    # Call Abacus.AI RouteLL M
    import requests
    response = requests.post(
        "https://routellm.abacus.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {ABACUS_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "route-llm",
            "messages": [
                {"role": "system", "content": f"You are a crypto trading advisor with access to this portfolio: {context}"},
                {"role": "user", "content": request.query}
            ]
        }
    )

    return {"answer": response.json()["choices"][0]["message"]["content"]}
```

---

## 📋 NEXT STEPS TO COMPLETE CONNECTION

### Priority 1: Connect Frontend Bridge to API ✅
```bash
# 1. Update mcp-bridge.ts with fetch calls
# 2. Set NEXT_PUBLIC_API_URL=http://localhost:8000
# 3. Test with: npm run dev
```

### Priority 2: Start FastAPI Server ✅
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 core/api/trading_api_server.py

# Should see:
# 🌐 Trading API Server initialized
# 🚀 Listening on http://0.0.0.0:8000
```

### Priority 3: Fetch Exchange Balances ⚠️
```bash
# Add to unified_portfolio_api.py
def get_hot_wallet_velocity(self):
    exchanges = self.universal_manager.connect_all()

    total = 0
    for name, exchange in exchanges.items():
        if exchange:
            balance = exchange.fetch_balance()
            total += balance['total']['USDT']

    return total
```

### Priority 4: Deploy to Production 🎯
```bash
# Update CORS to include production URL
# Deploy FastAPI to same server as Next.js app
# Or use serverless function (Vercel, AWS Lambda)
```

---

## 🎯 COMPLETE INTEGRATION CHECKLIST

- [ ] Update mcp-bridge.ts to call localhost:8000/api/*
- [ ] Start trading_api_server.py (FastAPI backend)
- [ ] Test /api/health endpoint returns live data
- [ ] Implement exchange balance fetching (CCXT)
- [ ] Add AAVE health factor monitoring
- [ ] Connect WebSocket for real-time updates
- [ ] Integrate Abacus.AI RouteLL M for AI queries
- [ ] Deploy FastAPI to production server
- [ ] Update CORS for production URL
- [ ] Test end-to-end: Dashboard → API → Backend → Live Data

---

**CURRENT STATE:** Backend ready, API server ready, frontend needs connection
**MISSING LINK:** mcp-bridge.ts still uses hardcoded data
**FIX:** Replace hardcoded returns with `fetch()` calls to FastAPI

**File to update:** `/Volumes/LegacySafe/SovereignShadow/app/lib/mcp-bridge.ts`

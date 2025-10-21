# 🌐 Sovereign Shadow Trading API Guide

Neural consciousness bridge for the Sovereign Shadow Trading System.

---

## Quick Start

### Launch the API Server

```bash
# Default port (8000)
./bin/START_API_SERVER.sh

# Custom port
./bin/START_API_SERVER.sh 8080
```

The server will be available at:
- **REST API:** `http://localhost:8000/api/`
- **WebSocket:** `ws://localhost:8000/ws/dashboard`
- **Interactive Docs:** `http://localhost:8000/docs`

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check server health and get current system stats.

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "active_strategies": 3,
  "risk_gate_status": "operational",
  "aave_health_factor": 2.45,
  "session_pnl": 15.75
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/health
```

---

### 2. Strategy Performance

**Endpoint:** `GET /api/strategy/performance`

**Description:** Get performance metrics for all active strategies.

**Response:**
```json
{
  "strategies": [
    {
      "name": "Cross-Exchange Arbitrage",
      "type": "arbitrage",
      "total_trades": 9,
      "total_profit": 36.50,
      "success_rate": 0.777,
      "avg_execution_time": 500,
      "last_trade": "2025-10-19T14:30:00Z",
      "status": "active"
    },
    {
      "name": "New Listing Snipe",
      "type": "sniping",
      "total_trades": 4,
      "total_profit": 43.50,
      "success_rate": 0.75,
      "avg_execution_time": 50,
      "last_trade": "2025-10-19T13:45:00Z",
      "status": "active"
    },
    {
      "name": "BTC Range Scalp",
      "type": "scalping",
      "total_trades": 12,
      "total_profit": 28.25,
      "success_rate": 0.833,
      "avg_execution_time": 200,
      "last_trade": "2025-10-19T14:55:00Z",
      "status": "active"
    }
  ],
  "total_profit": 108.25,
  "total_trades": 25,
  "session_start": "2025-10-19T10:00:00Z"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/strategy/performance
```

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/api/strategy/performance")
data = response.json()

print(f"Total Profit: ${data['total_profit']:.2f}")
print(f"Total Trades: {data['total_trades']}")

for strategy in data['strategies']:
    print(f"\n{strategy['name']}:")
    print(f"  Trades: {strategy['total_trades']}")
    print(f"  Profit: ${strategy['total_profit']:.2f}")
    print(f"  Success Rate: {strategy['success_rate']*100:.1f}%")
```

---

### 3. Execute Trade

**Endpoint:** `POST /api/trade/execute`

**Description:** Execute a trade with full risk validation through the tactical risk gate.

**Request:**
```json
{
  "strategy": "Cross-Exchange Arbitrage",
  "pair": "BTC/USD",
  "amount": 100,
  "exchanges": ["coinbase", "okx"],
  "side": "auto",
  "mode": "paper"
}
```

**Parameters:**
- `strategy` (string, required): Strategy name from knowledge base
- `pair` (string, required): Trading pair (e.g., "BTC/USD", "ETH/USD")
- `amount` (float, required): Trade amount in USD
- `exchanges` (array, optional): List of exchanges to use
- `side` (string, optional): Trade direction - "auto", "long", or "short" (default: "auto")
- `mode` (string, optional): Execution mode - "paper", "test", or "live" (default: "paper")

**Response:**
```json
{
  "trade_id": "trade_20251019_145500",
  "status": "completed",
  "profit": 1.25,
  "execution_time": 0.5,
  "timestamp": "2025-10-19T14:55:00Z",
  "validation_warnings": [
    "⚠️ OI spiked +3.2% - size reduced to 0.8× (stop-run risk)"
  ],
  "risk_adjustments": {
    "original_amount": 100,
    "adjusted_amount": 80,
    "size_multiplier": 0.8,
    "stop_loss_bps": 28
  }
}
```

**Error Response (Trade Rejected):**
```json
{
  "detail": {
    "error": "Trade rejected by risk gate",
    "reason": "❌ LSR guard: BTC shorts at 56.2% >= threshold 54% (don't fight squeeze)",
    "warnings": []
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "Cross-Exchange Arbitrage",
    "pair": "BTC/USD",
    "amount": 50,
    "mode": "paper"
  }'
```

**Python Example:**
```python
import requests

payload = {
    "strategy": "Cross-Exchange Arbitrage",
    "pair": "BTC/USD",
    "amount": 50,
    "exchanges": ["coinbase", "okx"],
    "mode": "paper"
}

response = requests.post(
    "http://localhost:8000/api/trade/execute",
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Trade executed: {data['trade_id']}")
    print(f"Profit: ${data['profit']:.2f}")
    print(f"Execution time: {data['execution_time']:.3f}s")
    
    if data['validation_warnings']:
        print("\nWarnings:")
        for warning in data['validation_warnings']:
            print(f"  {warning}")
else:
    error = response.json()
    print(f"❌ Trade rejected: {error['detail']['reason']}")
```

**JavaScript Example:**
```javascript
async function executeTrade() {
    const response = await fetch('http://localhost:8000/api/trade/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            strategy: 'Cross-Exchange Arbitrage',
            pair: 'BTC/USD',
            amount: 50,
            mode: 'paper'
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log(`✅ Trade executed: ${data.trade_id}`);
        console.log(`Profit: $${data.profit.toFixed(2)}`);
    } else {
        console.log(`❌ Trade rejected: ${data.detail.reason}`);
    }
}
```

---

### 4. Dashboard Update

**Endpoint:** `POST /api/dashboard/update`

**Description:** Send dashboard events (trade completion, market updates, health factor changes).

**Request (Trade Completed):**
```json
{
  "event": "trade_completed",
  "data": {
    "trade_id": "trade_20251019_140000",
    "profit": 1.25,
    "strategy": "arbitrage",
    "timestamp": "2025-10-19T14:00:00Z"
  }
}
```

**Request (Market Update):**
```json
{
  "event": "market_update",
  "data": {
    "positioning": {
      "asset": "BTC",
      "long_pct": 43.8,
      "short_pct": 56.2
    }
  }
}
```

**Request (Health Factor Update):**
```json
{
  "event": "health_factor_update",
  "data": {
    "health_factor": 2.45
  }
}
```

**Response:**
```json
{
  "success": true,
  "dashboard_updated": true,
  "timestamp": "2025-10-19T14:00:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/dashboard/update \
  -H "Content-Type: application/json" \
  -d '{
    "event": "trade_completed",
    "data": {
      "trade_id": "trade_20251019_140000",
      "profit": 1.25,
      "strategy": "arbitrage"
    }
  }'
```

---

### 5. WebSocket - Real-Time Dashboard

**Endpoint:** `WS ws://localhost:8000/ws/dashboard`

**Description:** Real-time bidirectional WebSocket connection for live updates.

**Server-to-Client Events:**

```json
{
  "event": "connected",
  "data": {
    "session_start": "2025-10-19T10:00:00Z",
    "active_strategies": 3,
    "status": "operational"
  }
}

{
  "event": "trade_completed",
  "data": {
    "trade_id": "trade_20251019_145500",
    "strategy": "Cross-Exchange Arbitrage",
    "pair": "BTC/USD",
    "amount": 80,
    "profit": 1.25,
    "execution_time": 0.5,
    "timestamp": "2025-10-19T14:55:00Z"
  }
}

{
  "event": "stats_update",
  "data": {
    "session_pnl_usd": 15.75,
    "consecutive_losses": 0,
    "open_trades": 2,
    "closed_trades": 12,
    "total_trades": 14,
    "aave_health_factor": 2.45
  }
}
```

**Client-to-Server Messages:**

```json
{
  "type": "ping"
}

{
  "type": "request_stats"
}
```

**Python WebSocket Client:**
```python
import asyncio
import websockets
import json

async def dashboard_client():
    uri = "ws://localhost:8000/ws/dashboard"
    
    async with websockets.connect(uri) as websocket:
        # Receive connection confirmation
        message = await websocket.recv()
        data = json.loads(message)
        print(f"Connected: {data}")
        
        # Request stats
        await websocket.send(json.dumps({"type": "request_stats"}))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['event'] == 'trade_completed':
                print(f"📈 Trade: {data['data']['trade_id']}")
                print(f"   Profit: ${data['data']['profit']:.2f}")
            
            elif data['event'] == 'stats_update':
                print(f"📊 Session P&L: ${data['data']['session_pnl_usd']:.2f}")

asyncio.run(dashboard_client())
```

**JavaScript WebSocket Client:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

ws.onopen = () => {
    console.log('🔌 Connected to dashboard');
    
    // Request stats every 10 seconds
    setInterval(() => {
        ws.send(JSON.stringify({ type: 'request_stats' }));
    }, 10000);
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.event) {
        case 'connected':
            console.log('✅ Connected:', data.data);
            break;
        
        case 'trade_completed':
            console.log('📈 Trade completed:', data.data.trade_id);
            console.log('   Profit:', data.data.profit);
            break;
        
        case 'stats_update':
            console.log('📊 Stats:', data.data);
            break;
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('🔌 Disconnected from dashboard');
};
```

---

## Integration with Abacus AI Neural Consciousness

### Connection Flow

1. **Abacus AI** detects trading opportunity via pattern recognition
2. **Sends HTTP POST** to `/api/trade/execute` with strategy and parameters
3. **Risk Gate validates** against LSR thresholds, funding divergence, HF floors
4. **Trade executes** if approved (or rejection reason returned)
5. **WebSocket broadcasts** results to all connected dashboards
6. **Abacus AI receives** confirmation and logs outcome

### Example: Neural AI → API → Execution

```python
# In Abacus AI Neural Consciousness
import requests

def execute_neural_trade_signal(signal):
    """
    Execute trade based on neural pattern recognition.
    
    Args:
        signal: {
            'asset': 'BTC',
            'confidence': 0.85,
            'direction': 'long',
            'size_usd': 50,
            'strategy': 'Cross-Exchange Arbitrage'
        }
    """
    
    # Only trade if confidence >= 80%
    if signal['confidence'] < 0.80:
        print(f"⚠️ Confidence {signal['confidence']} too low, skipping")
        return
    
    # Construct API request
    payload = {
        "strategy": signal['strategy'],
        "pair": f"{signal['asset']}/USD",
        "amount": signal['size_usd'],
        "side": signal['direction'],
        "mode": "test"  # Use "live" for production
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/trade/execute",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Neural trade executed: {data['trade_id']}")
            print(f"   Profit: ${data['profit']:.2f}")
            
            # Log for reinforcement learning
            log_neural_trade_outcome(
                signal_id=signal['id'],
                trade_id=data['trade_id'],
                profit=data['profit'],
                execution_time=data['execution_time']
            )
        else:
            error = response.json()
            print(f"❌ Trade rejected: {error['detail']['reason']}")
            
            # Learn from rejection
            log_neural_rejection(
                signal_id=signal['id'],
                reason=error['detail']['reason']
            )
    
    except Exception as e:
        print(f"❌ API error: {e}")

# Example usage
neural_signal = {
    'id': 'neural_20251019_001',
    'asset': 'BTC',
    'confidence': 0.85,
    'direction': 'long',
    'size_usd': 50,
    'strategy': 'Cross-Exchange Arbitrage'
}

execute_neural_trade_signal(neural_signal)
```

---

## Risk Gates & Validation

All trades pass through the **Tactical Risk Gate** which enforces:

### Layer 1: Global Sovereign Shadow Limits
- ✅ Max position: $415 (25% of hot wallet)
- ✅ Max stop loss: 5%
- ✅ Daily loss limit: $100
- ✅ Max concurrent trades: 3

### Layer 2: Tactical Guards
- ✅ **LSR (Long/Short Ratio):** Don't short into heavy shorts (squeeze risk)
- ✅ **Funding Divergence:** Respect exchange funding spread
- ✅ **Open Interest:** Reduce size if OI spiking (stop-run risk)

### Layer 3: Market Conditions
- ✅ **Aave Health Factor:** Min 2.20 for entries, 2.00 critical floor
- ✅ **Daily trade cap:** Max 6 trades per session
- ✅ **Consecutive losses:** Stop after 2 losses in a row

### Layer 4: Kill Switch
- ✅ **Session drawdown:** 1.2% max
- ✅ **Consecutive losses:** 5 max
- ✅ **Critical HF:** Auto-flatten if < 2.00

**All limits are enforced automatically - trades that violate rules are rejected with clear reasons.**

---

## Testing

### 1. Test with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Get strategy performance
curl http://localhost:8000/api/strategy/performance

# Execute paper trade
curl -X POST http://localhost:8000/api/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "Cross-Exchange Arbitrage",
    "pair": "BTC/USD",
    "amount": 25,
    "mode": "paper"
  }'
```

### 2. Interactive API Docs

Open in browser: `http://localhost:8000/docs`

FastAPI provides automatic interactive documentation where you can:
- View all endpoints
- Try requests directly in browser
- See response schemas
- Test WebSocket connections

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Abacus AI Neural Consciousness             │
│              (https://legacyloopshadowai.abacusai.app)      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST / WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Trading API Server (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GET  /api/strategy/performance                      │   │
│  │  POST /api/trade/execute                             │   │
│  │  POST /api/dashboard/update                          │   │
│  │  WS   /ws/dashboard                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Tactical Risk Gate                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Layer 1: Global Sovereign Shadow Limits             │   │
│  │  Layer 2: Tactical Guards (LSR, funding, OI)         │   │
│  │  Layer 3: Market Conditions (HF, caps)               │   │
│  │  Layer 4: Kill Switch (DD, losses)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Strategy Knowledge Base                         │
│              + Exchange Execution Layer                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Logs

API logs are written to:
```
logs/api/api_server_YYYYMMDD_HHMMSS.log
```

Each log includes:
- Timestamp
- Request details
- Validation results
- Trade outcomes
- WebSocket events

---

## Security Notes

1. **CORS:** Configured for Abacus AI domain and localhost only
2. **No Auth Yet:** Add authentication before production deployment
3. **Local Network:** Server binds to 0.0.0.0 (accessible on LAN)
4. **API Keys:** Never exposed via API - all handled server-side

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
./bin/START_API_SERVER.sh 8080
```

### Dependencies Missing

```bash
pip install fastapi uvicorn websockets pydantic
```

### Strategy Not Found

Ensure strategy exists in `strategy_knowledge_base.py`:
```bash
python3 -c "from strategy_knowledge_base import StrategyKnowledgeBase; kb = StrategyKnowledgeBase(); print([s['name'] for s in kb.get_all_strategies()])"
```

---

## Next Steps

1. **Test locally** with paper trades
2. **Connect Abacus AI** via HTTP POST
3. **Monitor WebSocket** stream in real-time
4. **Deploy to production** after validation
5. **Add authentication** for external access

---

*"Fearless. Bold. Smiling through chaos."* 🏴

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** October 19, 2025


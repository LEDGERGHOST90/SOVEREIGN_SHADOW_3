# SOVEREIGN SHADOW NEURAL HUB - BUILDER'S GUIDE

## Overview

Build a **FREE** AI-powered crypto trading system with:
- **Gemini 2.5 Pro** as the neural brain
- **Your Mac** as the execution engine
- **Web dashboard** for visualization
- **Zero monthly costs**

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        SOVEREIGN SHADOW NEURAL HUB                      │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │                     🌐 WEB DASHBOARD                              │  │
│  │                     (React + Vite)                                │  │
│  │                                                                   │  │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │
│  │   │Portfolio│  │ Signals │  │Positions│  │ Neural  │            │  │
│  │   │  View   │  │  Queue  │  │ Monitor │  │   Viz   │            │  │
│  │   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │  │
│  │        │            │            │            │                  │  │
│  │        └────────────┴─────┬──────┴────────────┘                  │  │
│  │                           │                                      │  │
│  │                           ▼                                      │  │
│  │                    ┌─────────────┐                               │  │
│  │                    │  REST API   │                               │  │
│  │                    │  Websocket  │                               │  │
│  │                    └──────┬──────┘                               │  │
│  │                           │                                      │  │
│  └───────────────────────────┼──────────────────────────────────────┘  │
│                              │                                         │
│                              │ HTTP/WS                                 │
│                              │                                         │
│  ┌───────────────────────────┼──────────────────────────────────────┐  │
│  │                           ▼                                      │  │
│  │                    🖥️ LOCAL BACKEND                               │  │
│  │                    (FastAPI on your Mac)                         │  │
│  │                                                                   │  │
│  │   ┌─────────────────────────────────────────────────────────┐   │  │
│  │   │                                                         │   │  │
│  │   │                  🧠 GEMINI NEURAL AGENT                 │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────┐   ┌─────────┐   ┌─────────┐             │   │  │
│  │   │   │ Market  │──▶│ Pattern │──▶│ Signal  │             │   │  │
│  │   │   │Analyzer │   │Detector │   │Generator│             │   │  │
│  │   │   └─────────┘   └─────────┘   └─────────┘             │   │  │
│  │   │        │             │             │                   │   │  │
│  │   │        │      ┌──────┴──────┐      │                   │   │  │
│  │   │        └─────▶│   GEMINI    │◀─────┘                   │   │  │
│  │   │               │   2.5 PRO   │                          │   │  │
│  │   │               └─────────────┘                          │   │  │
│  │   │                                                         │   │  │
│  │   └─────────────────────────────────────────────────────────┘   │  │
│  │                           │                                      │  │
│  │                           ▼                                      │  │
│  │   ┌─────────────────────────────────────────────────────────┐   │  │
│  │   │                                                         │   │  │
│  │   │                  ⚡ EXECUTION ENGINE                     │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────┐   ┌─────────┐   ┌─────────┐             │   │  │
│  │   │   │ Swing   │   │  Risk   │   │  Trade  │             │   │  │
│  │   │   │ Engine  │   │ Manager │   │Executor │             │   │  │
│  │   │   └─────────┘   └─────────┘   └─────────┘             │   │  │
│  │   │                                                         │   │  │
│  │   └─────────────────────────────────────────────────────────┘   │  │
│  │                           │                                      │  │
│  │                           ▼                                      │  │
│  │   ┌─────────────────────────────────────────────────────────┐   │  │
│  │   │                                                         │   │  │
│  │   │                  📡 EXCHANGE CONNECTORS                  │   │  │
│  │   │                                                         │   │  │
│  │   │   ┌─────────┐   ┌─────────┐   ┌─────────┐             │   │  │
│  │   │   │Coinbase │   │ Kraken  │   │ Binance │             │   │  │
│  │   │   └─────────┘   └─────────┘   └─────────┘             │   │  │
│  │   │                                                         │   │  │
│  │   └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Cost | Purpose |
|-------|------------|------|---------|
| **AI Brain** | Gemini 2.5 Pro | FREE | Pattern recognition, analysis |
| **Backend** | FastAPI (Python) | FREE | API server, business logic |
| **Frontend** | React + Vite | FREE | Web dashboard |
| **Database** | SQLite | FREE | Local storage |
| **Hosting** | Your Mac + ngrok | FREE | Run locally, expose to web |
| **Voice** | ElevenLabs | FREE tier | Aurora alerts |
| **Push** | ntfy.sh | FREE | Phone notifications |

---

## Directory Structure

```
SovereignShadow_II/
├── neural_hub/                    # NEW - The Neural Hub
│   ├── backend/                   # FastAPI server
│   │   ├── main.py               # API entry point
│   │   ├── gemini_agent.py       # Gemini neural brain
│   │   ├── routes/
│   │   │   ├── portfolio.py      # Portfolio endpoints
│   │   │   ├── signals.py        # Signal endpoints
│   │   │   ├── trades.py         # Trade endpoints
│   │   │   └── neural.py         # Neural analysis endpoints
│   │   └── services/
│   │       ├── market_data.py    # Price fetching
│   │       ├── analyzer.py       # Technical analysis
│   │       └── executor.py       # Trade execution
│   │
│   ├── frontend/                  # React dashboard
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Portfolio.jsx
│   │   │   │   ├── Signals.jsx
│   │   │   │   ├── Positions.jsx
│   │   │   │   └── NeuralViz.jsx
│   │   │   ├── App.jsx
│   │   │   └── main.jsx
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── database/
│       └── shadow.db              # SQLite database
│
├── strategies/
│   └── swing_trade_engine.py      # EXISTING - Your swing engine
│
├── scanners/
│   ├── realtime_alerts.py         # EXISTING - Price alerts
│   └── platform_scanner.py        # EXISTING - Multi-platform
│
└── BUILDERS_GUIDE.md              # This file
```

---

## Component Specifications

### 1. Gemini Neural Agent

**Purpose:** AI brain that analyzes markets and generates signals

**Input:**
```json
{
  "symbol": "BTC",
  "price": 90628.22,
  "rsi": 45.2,
  "volume_ratio": 1.5,
  "ema_20": 89500.00,
  "market_sentiment": "neutral",
  "recent_news": ["ETF inflows continue", "Fed holds rates"]
}
```

**Output:**
```json
{
  "symbol": "BTC",
  "action": "HOLD",
  "confidence": 65,
  "reasoning": "RSI neutral, no clear entry. Wait for RSI < 30 or breakout above $95K",
  "entry_price": null,
  "stop_loss": null,
  "take_profit": null,
  "risk_level": "medium",
  "timeframe": "4h"
}
```

**Gemini Prompt Template:**
```
You are a crypto trading analyst. Analyze the following market data and provide a trading recommendation.

MARKET DATA:
- Symbol: {symbol}
- Current Price: ${price}
- RSI (14): {rsi}
- Volume vs Average: {volume_ratio}x
- 20 EMA: ${ema_20}
- Market Sentiment: {sentiment}

TRADING RULES:
- Only recommend BUY when RSI < 30 AND volume > 2x AND price > EMA20
- Only recommend SELL when RSI > 70 OR stop loss hit OR take profit hit
- Risk per trade: 2% of portfolio
- Stop loss: 15% below entry
- Take profit 1: 30% above entry (sell 50%)
- Take profit 2: 75% above entry (sell remaining)

Respond in JSON format with: action, confidence (0-100), reasoning, entry_price, stop_loss, take_profit, risk_level, timeframe
```

---

### 2. FastAPI Backend

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio` | Get current portfolio |
| GET | `/api/signals` | Get active signals |
| POST | `/api/signals/generate` | Generate new signal via Gemini |
| GET | `/api/positions` | Get open positions |
| POST | `/api/positions/open` | Open new position |
| POST | `/api/positions/close` | Close position |
| GET | `/api/neural/analyze/{symbol}` | Deep analysis of symbol |
| WS | `/ws/prices` | Real-time price stream |
| WS | `/ws/signals` | Real-time signal stream |

---

### 3. React Dashboard

**Pages:**

1. **Dashboard** (Home)
   - Portfolio value chart
   - Active signals cards
   - Open positions table
   - P&L summary

2. **Signals**
   - Signal queue with confidence scores
   - Accept/Reject buttons
   - Historical signals

3. **Neural**
   - 3D visualization of asset connections
   - Gemini analysis chat
   - Pattern detection display

4. **Positions**
   - Open positions with live P&L
   - Stop loss / Take profit markers
   - Close position buttons

---

### 4. Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

1. MARKET DATA COLLECTION
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │CryptoComp│    │ Birdeye  │    │ Exchanges│
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Market Data    │
              │   Aggregator    │
              └────────┬────────┘
                       │
2. TECHNICAL ANALYSIS  │
                       ▼
              ┌─────────────────┐
              │   Calculate:    │
              │   • RSI         │
              │   • EMA         │
              │   • Volume      │
              │   • ATR         │
              └────────┬────────┘
                       │
3. AI ANALYSIS         │
                       ▼
              ┌─────────────────┐
              │  GEMINI 2.5 PRO │
              │                 │
              │  "Analyze this  │
              │   market data   │
              │   and give me   │
              │   a signal"     │
              └────────┬────────┘
                       │
4. SIGNAL GENERATION   │
                       ▼
              ┌─────────────────┐
              │   Signal:       │
              │   • BUY/SELL    │
              │   • Confidence  │
              │   • Entry/Exit  │
              │   • Risk level  │
              └────────┬────────┘
                       │
5. HUMAN APPROVAL      │
                       ▼
              ┌─────────────────┐
              │   Dashboard     │
              │   shows signal  │
              │                 │
              │   [ACCEPT]      │
              │   [REJECT]      │
              └────────┬────────┘
                       │
6. EXECUTION           │
                       ▼
              ┌─────────────────┐
              │  Swing Engine   │
              │                 │
              │  • Open position│
              │  • Set SL/TP    │
              │  • Monitor      │
              └────────┬────────┘
                       │
7. MONITORING          │
                       ▼
              ┌─────────────────┐
              │   Watch for:    │
              │   • SL hit      │
              │   • TP1 hit     │
              │   • TP2 hit     │
              │   • RSI exit    │
              └─────────────────┘
```

---

## Build Steps

### Phase 1: Backend (30 min)

```bash
# 1. Create directory
mkdir -p neural_hub/backend/routes neural_hub/backend/services

# 2. Create main.py
touch neural_hub/backend/main.py

# 3. Create gemini_agent.py
touch neural_hub/backend/gemini_agent.py

# 4. Install dependencies
pip install fastapi uvicorn google-generativeai websockets
```

### Phase 2: Gemini Integration (20 min)

```python
# gemini_agent.py - Core AI brain
import google.generativeai as genai

class GeminiNeuralAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def analyze(self, market_data: dict) -> dict:
        prompt = self._build_prompt(market_data)
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)
```

### Phase 3: Frontend (30 min)

```bash
# 1. Create React app
cd neural_hub
npm create vite@latest frontend -- --template react

# 2. Install dependencies
cd frontend
npm install axios recharts three @react-three/fiber @react-three/drei

# 3. Start dev server
npm run dev
```

### Phase 4: Connect Everything (20 min)

```bash
# 1. Start backend
cd neural_hub/backend
uvicorn main:app --reload --port 8000

# 2. Start frontend
cd neural_hub/frontend
npm run dev

# 3. Expose to internet (optional)
ngrok http 8000
```

---

## API Key Setup

```bash
# Already in your .env file:
GEMINI_API_KEY=AIzaSyD-fpuaAUm-yllt4D6yC09D6wz3FNhVYzI
CRYPTOCOMPARE_API_KEY=7c9f90b65839b40f072864afba7500d0f41a1f770a57b6758dbb984919a7a396
ELEVENLABS_API_KEY=sk_ff99af0872a9d9420c0fd47d0fd4bc31d395f38260ea5d8e
```

---

## Running the System

```bash
# Terminal 1: Backend
cd /Volumes/LegacySafe/SovereignShadow_II/neural_hub/backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd /Volumes/LegacySafe/SovereignShadow_II/neural_hub/frontend
npm run dev

# Terminal 3: Swing Engine Monitor
cd /Volumes/LegacySafe/SovereignShadow_II
python strategies/swing_trade_engine.py --paper --daemon
```

---

## Testing

```bash
# Test Gemini agent
curl http://localhost:8000/api/neural/analyze/BTC

# Test signal generation
curl -X POST http://localhost:8000/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC"}'

# Test portfolio
curl http://localhost:8000/api/portfolio
```

---

## Security Notes

1. **Never commit .env** - Already in .gitignore
2. **API keys stay local** - Never exposed to frontend
3. **Paper trade first** - Test before real money
4. **Rate limits** - Gemini has 60 req/min free tier

---

## Cost Breakdown

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| Gemini API | 60 req/min | ~10 req/min | $0 |
| CryptoCompare | 100K calls/mo | ~50K calls/mo | $0 |
| ElevenLabs | 10K chars/mo | ~5K chars/mo | $0 |
| Vercel | 100GB bandwidth | ~1GB | $0 |
| ngrok | 1 tunnel | 1 tunnel | $0 |
| **TOTAL** | | | **$0** |

---

## Next Steps After Build

1. **Week 1:** Paper trade with system
2. **Week 2:** Small live trades ($25)
3. **Week 3:** Scale up if profitable
4. **Week 4:** Full automation

---

## Give This to Gemini

Copy this entire guide and paste it to Gemini with:

> "Build this system. Start with the Gemini Neural Agent, then the FastAPI backend, then the React frontend. Give me complete code for each file."

Then compare what Gemini builds vs what I build below.

---

*Builder's Guide v1.0 - Sovereign Shadow Neural Hub*
*Claude Opus 4.5 - November 29, 2025*

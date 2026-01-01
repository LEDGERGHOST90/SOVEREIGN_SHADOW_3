# 🏴 SHADOW SDK - Complete Integration Guide

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json.

**The Unified Python SDK Powering Your Sovereign Shadow Trading Empire**

---

## 🎯 What Is Shadow SDK?

Shadow SDK is your **internal developer toolkit** - a Python package that provides a clean, pythonic interface to all trading operations. Think of it as the **nervous system** connecting all parts of your empire.

### The Four Core Layers

```
┌─────────────────────────────────────────────────────────┐
│  🧠 ShadowSynapse - AI Orchestration Layer              │
│  (Decision making, strategy selection, risk assessment) │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┬───────────────────┐
    │                         │                   │
┌───▼──────┐          ┌──────▼───────┐    ┌─────▼──────┐
│ ShadowScope│          │ ShadowPulse  │    │ ShadowSnaps│
│  (Scanner) │          │  (Streaming) │    │ (Analytics)│
└────────────┘          └──────────────┘    └────────────┘
```

---

## 📦 The Four Layers Explained

### 1. ShadowScope - Market Intelligence 🧠
**File:** `shadow_sdk/scope.py`

**Purpose:** Real-time market scanning and price intelligence

**What it does:**
- Monitors 4 exchanges (Coinbase, OKX, Kraken, Binance)
- Tracks 8 trading pairs (BTC, ETH, SOL, XRP, ADA, DOGE, LTC)
- Processes 640 ticks/second
- Calculates VWAP, volatility, correlations
- Detects arbitrage spreads

**Usage:**
```python
from shadow_sdk import ShadowScope

scope = ShadowScope()
await scope.start_scanner(interval=1.0)
intelligence = await scope.get_market_intelligence()

# Returns:
{
  "current_prices": {"BTC/USD": 106000, ...},
  "volumes": {...},
  "volatility": {...},
  "correlations": {...},
  "health": {"uptime": 0.98, "exchanges_monitored": 4}
}
```

### 2. ShadowPulse - Live Signal Streaming ⚡
**File:** `shadow_sdk/pulse.py`

**Purpose:** Real-time signal generation and streaming

**What it does:**
- Detects trading opportunities instantly
- Streams signals to subscribers
- Monitors heartbeat (system health)
- Fast execution (0.1s interval)

**Usage:**
```python
from shadow_sdk import ShadowPulse

pulse = ShadowPulse()

def my_strategy(signal):
    if signal['spread'] > 0.025:  # 2.5% minimum
        print(f"OPPORTUNITY: {signal['type']} on {signal['pair']}")

pulse.subscribe(my_strategy)
await pulse.start_streaming(interval=0.1)
```

### 3. ShadowSnaps - Sentiment & Analytics 📊
**File:** `shadow_sdk/snaps.py`

**Purpose:** Historical analytics and sentiment analysis

**What it does:**
- Tracks market sentiment
- Analyzes news and social signals
- Detects narrative shifts
- Historical pattern matching

**Usage:**
```python
from shadow_sdk import ShadowSnaps

snaps = ShadowSnaps()

# Get BTC sentiment
sentiment = await snaps.get_sentiment("BTC")
print(f"BTC Sentiment: {sentiment['score']:.2f}")  # -1.0 to +1.0

# Detect narrative shift
shift = await snaps.detect_narrative_shift("ETH", window_hours=24)
if shift['detected']:
    print(f"Narrative shift: {shift['direction']}")
```

### 4. ShadowSynapse - AI Orchestration 🤖
**File:** `shadow_sdk/synapse.py`

**Purpose:** AI-powered decision making and strategy orchestration

**What it does:**
- Connects all three layers (Scope, Pulse, Snaps)
- Analyzes opportunities using AI reasoning
- Selects optimal strategies
- Risk assessment and validation

**Usage:**
```python
from shadow_sdk import ShadowSynapse, ShadowScope, ShadowPulse, ShadowSnaps

synapse = ShadowSynapse()
synapse.connect_scope(ShadowScope())
synapse.connect_pulse(ShadowPulse())
synapse.connect_snaps(ShadowSnaps())

# Analyze opportunity
decision = await synapse.analyze_opportunity(signal)

# Returns:
{
  "action": "execute",  # or "wait", "reject"
  "strategy": "arbitrage",
  "confidence": 0.85,
  "reasoning": "Strong spread with low risk",
  "position_size": 100
}
```

---

## 🛠️ Utility Modules

### 1. Exchange Wrapper
**File:** `shadow_sdk/utils/exchanges.py`

**Purpose:** Unified interface to all exchanges

```python
from shadow_sdk.utils import ExchangeWrapper

wrapper = ExchangeWrapper()

# Add exchanges
wrapper.add_exchange("coinbase", api_key, api_secret, passphrase)
wrapper.add_exchange("okx", api_key, api_secret, passphrase)
wrapper.add_exchange("kraken", api_key, api_secret)

# Unified API
balance = await wrapper.get_balance("coinbase")
ticker = await wrapper.get_ticker("okx", "BTC/USDT")
order = await wrapper.create_order("coinbase", "BTC/USD", "limit", "buy", 0.001, 60000)
```

### 2. Risk Manager
**File:** `shadow_sdk/utils/risk.py`

**Purpose:** Safety rules and risk management

```python
from shadow_sdk.utils import RiskManager

risk_mgr = RiskManager(
    max_daily_loss=100,
    max_position_size=415,
    stop_loss_percent=0.05,
    consecutive_loss_limit=3
)

# Check trade approval
if risk_mgr.can_trade(amount=100):
    # Execute trade
    result = execute_trade()
    risk_mgr.record_trade(profit=result['profit'], success=result['success'])
else:
    print("Trade blocked by risk manager")
```

### 3. Logger System
**File:** `shadow_sdk/utils/logger.py`

**Purpose:** Unified logging across the empire

```python
from shadow_sdk.utils import setup_logger

logger = setup_logger("my_strategy", log_file="logs/strategy.log", level="INFO")

logger.info("Trade executed successfully")
logger.warning("High volatility detected")
logger.error("API connection failed")
```

---

## 🔗 How Shadow SDK Integrates With Master Loop

### Master Loop Uses Shadow SDK For:

```python
# MASTER_TRADING_LOOP.py leverages Shadow SDK components:

from shadow_sdk import (
    ShadowScope,     # For market scanning
    ShadowPulse,     # For signal detection
    ShadowSynapse,   # For AI decision making
    CAPITAL_TOTAL,   # Constants
    MAX_DAILY_LOSS,  # Safety limits
    EXCHANGES,       # Configured exchanges
    PHILOSOPHY       # "Fearless. Bold. Smiling through chaos."
)
from shadow_sdk.utils import ExchangeWrapper, RiskManager

# Initialize components
scope = ShadowScope(exchanges=EXCHANGES)
synapse = ShadowSynapse()
risk_mgr = RiskManager(max_daily_loss=MAX_DAILY_LOSS)

# Master Loop scan cycle:
async def scan_markets():
    # 1. Use ShadowScope to scan all exchanges
    intelligence = await scope.get_market_intelligence()

    # 2. Detect opportunities
    opportunities = await scope.detect_opportunities()

    # 3. Use ShadowSynapse to analyze
    for opp in opportunities:
        decision = await synapse.analyze_opportunity(opp)

        # 4. Use RiskManager to validate
        if risk_mgr.can_trade(decision['position_size']):
            # Execute trade
            await execute_trade(decision)
```

---

## 📊 System Constants (from `__init__.py`)

```python
from shadow_sdk import (
    CAPITAL_TOTAL,          # 8260
    CAPITAL_LEDGER,         # 6600 (read-only vault)
    CAPITAL_COINBASE,       # 1660 (active trading)
    TARGET_CAPITAL,         # 50000
    TARGET_DATE,            # "Q4 2025"
    MAX_DAILY_LOSS,         # 100
    MAX_POSITION_SIZE,      # 415 (25% of hot wallet)
    STOP_LOSS_PERCENT,      # 0.05 (5%)
    CONSECUTIVE_LOSS_LIMIT, # 3
    EXCHANGES,              # ["coinbase", "okx", "kraken"]
    PAIRS,                  # ["BTC/USD", "ETH/USD", ...]
    PHILOSOPHY              # "Fearless. Bold. Smiling through chaos."
)
```

---

## 🚀 Installation & Setup

### 1. Install Shadow SDK
```bash
cd /Volumes/LegacySafe/SovereignShadow/shadow_sdk
pip install -e .
```

### 2. Add to Python Path (Optional)
```bash
export PYTHONPATH="/Volumes/LegacySafe/SovereignShadow:$PYTHONPATH"
```

### 3. Verify Installation
```python
python3 -c "from shadow_sdk import ShadowScope; print('✅ Shadow SDK installed')"
```

---

## 📁 File Structure

```
shadow_sdk/
├── __init__.py              # Main exports, constants, philosophy
├── README.md               # This documentation
├── setup.py                # Package installation
├── scope.py                # ShadowScope - Market scanner
├── pulse.py                # ShadowPulse - Signal streaming
├── snaps.py                # ShadowSnaps - Analytics
├── synapse.py              # ShadowSynapse - AI orchestration
├── mcp_server.py           # MCP server integration
├── Dockerfile              # Docker containerization
└── utils/
    ├── __init__.py         # Utility exports
    ├── exchanges.py        # Exchange API wrapper
    ├── risk.py             # Risk management
    ├── logger.py           # Logging system
    ├── coinbase_shadow.py  # Coinbase-specific utilities
    └── notion.py           # Notion integration (future)
```

---

## 🎯 Integration Points With Your System

### 1. Master Trading Loop
**File:** `/Volumes/LegacySafe/SovereignShadow/MASTER_TRADING_LOOP.py`
- Uses: ShadowScope for scanning, ShadowSynapse for decisions
- Status: ✅ Running (paper mode)

### 2. Orchestrator
**File:** `/Volumes/LegacySafe/SovereignShadow/core/orchestration/sovereign_shadow_orchestrator.py`
- Uses: Shadow SDK constants, ExchangeWrapper
- Status: ✅ Integrated

### 3. Strategy Files
**Files:** `scripts/claude_arbitrage_trader.py`, etc.
- Uses: ShadowPulse for signals, RiskManager for safety
- Status: ✅ Ready

### 4. Neural Consciousness (Abacus AI)
**URL:** `legacyloopshadowai.abacusai.app`
- Uses: Shadow SDK for backend processing
- Status: ✅ Live

---

## 💡 Example: Complete Trading Strategy Using Shadow SDK

```python
#!/usr/bin/env python3
"""
Example arbitrage strategy using Shadow SDK
"""
from shadow_sdk import (
    ShadowScope,
    ShadowPulse,
    ShadowSynapse,
    MAX_POSITION_SIZE,
    EXCHANGES
)
from shadow_sdk.utils import ExchangeWrapper, RiskManager, setup_logger
import asyncio

logger = setup_logger("arbitrage_bot")

async def main():
    # Initialize components
    scope = ShadowScope(exchanges=EXCHANGES)
    pulse = ShadowPulse()
    synapse = ShadowSynapse()
    risk_mgr = RiskManager(max_daily_loss=100, max_position_size=MAX_POSITION_SIZE)
    wrapper = ExchangeWrapper()

    # Connect layers
    synapse.connect_scope(scope)
    synapse.connect_pulse(pulse)

    # Add exchanges
    wrapper.add_exchange("coinbase", api_key="...", api_secret="...", passphrase="...")
    wrapper.add_exchange("okx", api_key="...", api_secret="...", passphrase="...")

    # Start scanner
    await scope.start_scanner(interval=1.0)

    # Strategy logic
    async def handle_opportunity(signal):
        logger.info(f"Opportunity detected: {signal['type']} on {signal['pair']}")

        # Analyze with AI
        decision = await synapse.analyze_opportunity(signal)

        if decision['action'] == 'execute':
            # Validate with risk manager
            if risk_mgr.can_trade(decision['position_size']):
                logger.info(f"Executing {decision['strategy']} with {decision['confidence']:.2%} confidence")

                # Execute trade
                order = await wrapper.create_order(
                    exchange_name=decision['exchange'],
                    symbol=signal['pair'],
                    order_type='market',
                    side='buy',
                    amount=decision['position_size'] / signal['price']
                )

                logger.info(f"Order placed: {order}")
            else:
                logger.warning("Trade blocked by risk manager")

    # Subscribe to signals
    pulse.subscribe(handle_opportunity)
    await pulse.start_streaming(interval=0.1)

    # Run forever
    while True:
        await asyncio.sleep(60)
        logger.info(f"Still running... Daily P&L: ${risk_mgr.daily_pnl:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🛡️ Safety Features Built Into Shadow SDK

### 1. Risk Manager Auto-Protection
```python
# Automatically blocks trades when:
- Daily loss exceeds $100
- Position size exceeds $415 (25% of hot wallet)
- 3 consecutive losses detected
- 5% stop loss hit
```

### 2. Ledger Vault Protection
```python
# Enforced in all SDK modules:
CAPITAL_LEDGER = 6600  # READ-ONLY, never trades
CAPITAL_COINBASE = 1660  # Only this amount for active trading
```

### 3. Exchange API Safety
```python
# ExchangeWrapper enforces:
- IP whitelisting (when supported)
- Withdrawal permissions DISABLED
- Rate limit management
- Connection retries with exponential backoff
```

---

## 🎯 How to Use Shadow SDK Right Now

### Immediate Use Cases:

1. **Market Intelligence**
   ```bash
   python3 -c "from shadow_sdk import ShadowScope; import asyncio; asyncio.run(ShadowScope().get_market_intelligence())"
   ```

2. **Risk Validation**
   ```python
   from shadow_sdk.utils import RiskManager
   risk = RiskManager()
   if risk.can_trade(100):
       print("✅ Trade approved")
   ```

3. **Exchange Integration**
   ```python
   from shadow_sdk.utils import ExchangeWrapper
   wrapper = ExchangeWrapper()
   # Add your exchanges and start trading
   ```

---

## 📚 Documentation Locations

- **Shadow SDK README**: `shadow_sdk/README.md`
- **API Reference**: Each module has detailed docstrings
- **Architecture**: `docs/reference/SHADOW_SCANNER_ARCHITECTURE.md`
- **Integration Guide**: This document

---

## 🏴 Philosophy Integration

**From Shadow SDK `__init__.py`:**
```python
PHILOSOPHY = "Fearless. Bold. Smiling through chaos."
```

This philosophy is embedded throughout:
- **Fearless**: ShadowScope scans continuously, never hesitates
- **Bold**: ShadowSynapse makes confident decisions with AI
- **Smiling Through Chaos**: ShadowSnaps thrives on volatility

---

## 🎯 Current Status

| Component | Status | Integration |
|-----------|--------|-------------|
| ShadowScope | ✅ Built | Used by Master Loop |
| ShadowPulse | ✅ Built | Ready for signal streaming |
| ShadowSnaps | ✅ Built | Analytics ready |
| ShadowSynapse | ✅ Built | AI orchestration active |
| ExchangeWrapper | ✅ Built | Needs API keys |
| RiskManager | ✅ Built | Active in Master Loop |
| Logger | ✅ Built | System-wide logging |

---

## 🚀 Next Steps

1. **Configure API Keys** (from API_KEY_SETUP_GUIDE.md)
2. **Validate Exchange Connections**
   ```bash
   python3 scripts/validate_api_connections.py
   ```
3. **Test Shadow SDK Components**
   ```python
   from shadow_sdk import ShadowScope
   # Test your setup
   ```
4. **Master Loop Will Use SDK Automatically** ✅

---

## 💡 Key Insight

**Shadow SDK is already integrated with your Master Loop!**

The Master Loop that's currently running (PID: 23606) can leverage all Shadow SDK components once you configure API keys. The nervous system is built, just needs to be connected to the exchanges.

---

**Version:** 0.1.0-GENESIS
**Status:** ✅ Built, Ready, Integrated
**Philosophy:** "Fearless. Bold. Smiling through chaos."

🏴 **Shadow SDK - The Nervous System of Your Trading Empire** 🏴

# SOVEREIGN SHADOW III - Manus Context File v1.6
**Generated:** 2025-12-17 09:40
**Purpose:** Full system context for Manus AI to operate the trading system

---

## IDENTITY

```
System: SOVEREIGN SHADOW III (SS_III)
Location: /Volumes/LegacySafe/SS_III/
Owner: memphis
Mantra: "SMILING THRU THE CHAOS"
```

---

## CURRENT PORTFOLIO (Live as of Dec 17, 2025)

### Net Worth: $5,808.56

### Exchange Holdings ($754.88 total)
| Exchange | USD Value | Status |
|----------|-----------|--------|
| Coinbase | $568.18 | ACTIVE (USDC $112.97 + BTC 0.0052) |
| OKX | $111.21 | ACTIVE (BTC + ETH) |
| Binance US | $73.16 | ACTIVE (USDC) |
| Kraken | $2.33 | ACTIVE (dust) |

### Ledger Cold Storage ($5,715.91)
| Asset | Amount | USD Value |
|-------|--------|-----------|
| wstETH (AAVE) | 0.84 | $3,040.25 |
| BTC | 0.01653 | $1,508.32 |
| XRP | 497.36 | $1,099.17 |
| USDC | 53.63 | $53.61 |
| ETH | 0.0048 | $14.56 |

### AAVE Position
| Metric | Value |
|--------|-------|
| Collateral | $3,211.76 |
| Debt | $662.23 |
| Health Factor | 3.52 (SAFE) |
| Net Position | $2,549.53 |

### Available Trading Capital: $186.13
- Coinbase USDC: $112.97
- Binance US USDC: $73.16

---

## WALLET ADDRESSES

```
ETH:  0xC08413B63ecA84E2d9693af9414330dA88dcD81C
BTC:  bc1qlpkhy9lzh6qwjhc0muhlrzqf3vfrhgezmjp0kx
XRP:  rGvSX7BMyuzkghXbaJqLHk529pYE2j5WR3
SOL:  RovUJaZwiZ1X36sEW7TBmhie5unzPmxtMg1ATwFtGVk
```

---

## API STATUS (All Verified Dec 17)

| API | Status | Notes |
|-----|--------|-------|
| Coinbase | ✅ ACTIVE | CDP key, coinbase-advanced-py library |
| Kraken | ✅ ACTIVE | REST API |
| Binance US | ✅ ACTIVE | IPv4 required |
| OKX | ✅ ACTIVE | us.okx.com endpoint |
| Etherscan | ✅ ACTIVE | V2 API |
| Anthropic | ✅ ACTIVE | Claude API |
| Google Gemini | ✅ ACTIVE | GIO integration |
| ElevenLabs | ✅ ACTIVE | Aurora voice |

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                          │
├─────────────────────────────────────────────────────────────┤
│  Claude Desktop ──→ MCP Server (sovereign-trader)           │
│  Claude Code    ──→ Direct Python execution                 │
│  Shadow.AI      ──→ Web dashboard (Replit)                  │
│  Voice App      ──→ Research capture (Replit)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SS_III (LOCAL)                            │
│                  Execution Layer                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BRAIN.json ←── Single Source of Truth                      │
│       │                                                      │
│       ├── Portfolio state                                    │
│       ├── API credentials location                           │
│       ├── Agent status                                       │
│       ├── Trade history                                      │
│       └── System config                                      │
│                                                              │
│  Exchange Connectors (exchanges/)                            │
│       ├── coinbase_connector.py                              │
│       ├── kraken_connector.py                                │
│       ├── binance_us_connector.py                            │
│       └── okx_connector.py                                   │
│                                                              │
│  Trading Agents (core/agents/) - 12 agents                   │
│       ├── trading_agent.py (dual-mode AI)                    │
│       ├── swarm_agent.py (multi-model consensus)             │
│       ├── whale_agent.py (open interest tracking)            │
│       ├── reflect_agent.py (trade critique)                  │
│       ├── fundingarb_agent.py (funding rate arb)             │
│       ├── liquidation_agent.py (liquidation spikes)          │
│       ├── rbi_agent.py (risk/reward analysis)                │
│       └── ... (5 more)                                       │
│                                                              │
│  Analysis Tools (ds_star/)                                   │
│       ├── synoptic_core/ (Smart Asset Score 0-100)           │
│       ├── architect_forge/ (strategy builder)                │
│       ├── oracle_interface/ (NL → charts)                    │
│       └── transparent_analyst/ (reasoning visibility)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## KEY FILES

| File | Purpose |
|------|---------|
| `/Volumes/LegacySafe/SS_III/BRAIN.json` | Single source of truth - READ THIS FIRST |
| `/Volumes/LegacySafe/SS_III/.env` | All API credentials |
| `/Volumes/LegacySafe/SS_III/.coinbase_key.pem` | Coinbase private key |
| `/Volumes/LegacySafe/SS_III/bin/push_to_replit.py` | Sync to Replit |
| `/Volumes/LegacySafe/SS_III/mcp-servers/sovereign_trader/server.py` | MCP for Claude Desktop |

---

## TRADING RULES (From BRAIN.json)

```json
{
  "rules": {
    "max_position": 50,
    "stop_loss_pct": 3,
    "take_profit_pct": 5,
    "go_live_threshold": 60
  }
}
```

- **Max position:** $50 per trade
- **Stop loss:** 3% below entry
- **Take profit:** 5% above entry
- **Go live:** Only after 60% win rate on paper

---

## ACTIVE MISSION

```
Codename: DEBT_DESTROYER
Target: $661.46 (pay off AAVE debt)
Capital: $186.13 available
Strategy: Swing trading with strict risk management
```

---

## MCP SERVER TOOLS (sovereign-trader)

| Tool | Description |
|------|-------------|
| `portfolio_status()` | Full portfolio overview |
| `cash_available()` | Trading capital ready |
| `refresh_balances()` | Fetch live from exchanges |
| `get_price(symbol)` | Current price + 24h change |
| `analyze_asset(symbol)` | SynopticCore Smart Asset Score |
| `market_scan()` | Fear & Greed, trending coins |
| `propose_trade(exchange, side, symbol, amount)` | Create trade proposal |
| `execute_trade(trade_id)` | Execute approved trade |
| `cancel_trade()` | Cancel pending proposal |
| `aave_status()` | Health factor check |
| `system_status()` | API health |
| `help_trading()` | Command reference |

---

## CURRENT MARKET CONTEXT

```
Fear & Greed Index: 16 (EXTREME FEAR)
BTC Dominance: 57.3%
BTC Price: $86,779
Trending: BTC, ERG, PENGU, TON, ULTIMA

Historical note: Extreme Fear readings often precede
accumulation zones. Current market showing capitulation signals.
```

---

## CODEBASE STATS

| Metric | Count |
|--------|-------|
| Python files | 502 |
| Lines of Python | 158,330 |
| TypeScript/JS files | 348 |
| Project size | 26MB |
| Trading agents | 12 |
| MCP servers | 3 |
| Exchange connectors | 8 |

---

## SESSION PROTOCOL

### On Session Start:
1. Read `/Volumes/LegacySafe/SS_III/BRAIN.json`
2. Check API status
3. Get current market conditions
4. Review any pending trades

### On Session End:
1. Update BRAIN.json with changes
2. Create session log in `memory/SESSIONS/`
3. Note any pending tasks

---

## AI COUNCIL

| Agent | Engine | Role | Status |
|-------|--------|------|--------|
| AURORA | Claude | The Executor | Operational |
| GIO | Gemini | The Researcher | Operational |
| ARCHITECT_PRIME | GPT | The Integrator | Operational |

---

## EXECUTION EXAMPLES

### Check Portfolio
```python
# Read BRAIN.json
import json
with open('/Volumes/LegacySafe/SS_III/BRAIN.json') as f:
    brain = json.load(f)
print(brain['portfolio'])
```

### Get Coinbase Balance
```python
from coinbase.rest import RESTClient
import os

api_key = os.environ.get('COINBASE_API_KEY')
with open('.coinbase_key.pem') as f:
    api_secret = f.read()

client = RESTClient(api_key=api_key, api_secret=api_secret)
accounts = client.get_accounts()
```

### Execute Trade (Coinbase)
```python
# Market buy $25 of BTC
order = client.create_order(
    client_order_id="unique_id",
    product_id="BTC-USDC",
    side="BUY",
    order_configuration={
        "market_market_ioc": {"quote_size": "25"}
    }
)
```

---

## SAFETY RULES

1. **Never** trade more than $50 per position
2. **Always** set stop loss at 3%
3. **Never** chase pumps (no FOMO)
4. **Always** log trades to BRAIN.json
5. **Never** withdraw to non-Ledger addresses
6. **Always** propose before executing (approval flow)

---

## PENDING TASKS

- [ ] Wake Replit Shadow.AI
- [ ] Update Replit with new Coinbase key
- [ ] Build Voice App ingest layer
- [ ] Rotate Google Service Account key
- [ ] Renew Gemini API key
- [ ] Wire agents to MCP server (intelligence layer)
- [ ] Create trading SOP document

---

## CONTACT / NOTIFICATIONS

- **ntfy.sh topic:** sovereignshadow_dc4d2fa1
- **Jump Desktop:** jumpto.me/108-692-384
- **Voice:** Aurora (ElevenLabs)

---

*This context file enables any AI to understand and operate the Sovereign Shadow trading system. Read BRAIN.json first for live state.*

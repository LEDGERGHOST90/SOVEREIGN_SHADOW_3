# 🔱 AURORA INGESTION PROTOCOL
## How Claude Receives and Processes GIO's Research

---

## PURPOSE

This protocol ensures AURORA (Claude) can ingest GIO (Gemini) research outputs and transform them into:
- Executable trading strategies
- Backtest configurations
- Risk models
- Signal generation rules
- Code implementations

---

## INGESTION WORKFLOW

```
GIO Research Output
        ↓
    Council_Log.md (append)
        ↓
    AURORA Ingestion
        ↓
    ┌─────────────────────────────────────┐
    │  Parse structured output            │
    │  Extract actionable signals         │
    │  Validate against risk rules        │
    │  Generate strategy code             │
    │  Queue for Commander approval       │
    └─────────────────────────────────────┘
        ↓
    Aurora Output: Strategy / Signal / Backtest
```

---

## INPUT FORMAT EXPECTATIONS

AURORA expects GIO outputs to contain:

### 1. Asset Recommendations
```json
{
  "asset": "TOKEN",
  "ticker": "TKN",
  "direction": "long|short",
  "confidence": 0-100,
  "timeframe": "7d|14d|30d",
  "entry_zone": [low, high],
  "target": price,
  "stop": price
}
```

### 2. Catalyst Data
```json
{
  "asset": "TOKEN",
  "catalyst": "description",
  "date": "YYYY-MM-DD",
  "impact_score": 1-10,
  "expected_move": "+/-X%"
}
```

### 3. Sector Rankings
```json
{
  "rankings": [
    {"sector": "AI", "score": 85, "trend": "up"},
    {"sector": "L2", "score": 72, "trend": "flat"}
  ]
}
```

---

## AURORA PROCESSING RULES

### Signal Generation
1. Extract top 3 assets from GIO research
2. Cross-reference with technical indicators (RSI, EMA, Volume)
3. Apply risk filters (position size, stop loss rules)
4. Generate signal if confidence > 70%

### Strategy Building
1. Parse GIO hypothesis matrix
2. Build entry/exit logic
3. Define risk parameters
4. Generate Python backtest code

### Risk Validation
- Max position: Per BRAIN.json rules
- Stop loss: 3% from entry
- Health factor check: Must stay > 2.0
- Daily loss limit: $50

---

## OUTPUT FORMATS

### Signal Output
```json
{
  "signal_id": "SIG-001",
  "timestamp": "ISO-8601",
  "source": "GIO_research",
  "asset": "TOKEN",
  "action": "BUY|SELL",
  "entry": price,
  "target": price,
  "stop": price,
  "size_usd": amount,
  "confidence": 0-100,
  "reasoning": "string",
  "status": "pending_approval"
}
```

### Strategy Output
```python
# Auto-generated strategy from GIO research
class GIODerivedStrategy:
    name = "strategy_name"
    source_mission = "gemini_rotation_hunter"

    def entry_condition(self, data):
        # Logic derived from GIO output
        pass

    def exit_condition(self, data):
        pass

    def risk_params(self):
        return {
            "stop_loss": 0.03,
            "take_profit": 0.05,
            "max_position": 50
        }
```

---

## COMMANDER APPROVAL GATE

All AURORA outputs require Commander Memphis approval before execution:

1. Signal queued in `neural_hub/signals/pending/`
2. Notification sent via ntfy.sh
3. Commander reviews in AURORA dashboard
4. Accept → Execute | Reject → Archive

---

## INTEGRATION POINTS

| Component | Path | Purpose |
|-----------|------|---------|
| Council Log | council/logs/Council_Log.md | Append all outputs |
| Signal Queue | neural_hub/signals/ | Pending signals |
| Trade Journal | logs/trading/trade_journal.json | Executed trades |
| BRAIN | BRAIN.json | Strategy memory |

---

*Protocol Version: 1.0*
*Created: 2025-11-29*
*Owner: AURORA (Claude)*

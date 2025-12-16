---
name: ds-star
description: Decision support system - SynopticCore asset scoring, OracleInterface for NL→charts, ArchitectForge strategy builder. 15 analysis tools. (project)
---

# DS-STAR - Decision Support System

**Location:** `/Volumes/LegacySafe/SS_III/ds_star/`

## Fortress Integration Map

| DS-STAR Module | Fortress Layer | Purpose |
|---------------|----------------|---------|
| SynopticCore | Layer 3 (AI Agents) | Pre-trade asset scoring → risk_sentinel |
| OracleInterface | Layer 5 (Observability) | NL queries → dashboards |
| ArchitectForge | Layer 3 (AI Agents) | Strategy generation → execution_commander |
| TransparentAnalyst | Layer 5 (Observability) | Explainable analysis → logs |
| Gatekeeper | Layer 1 (Foundation) | Data normalization → core engine |
| DataFeeds | Layer 1 (Foundation) | Market data pipeline |
| Portfolio | Layer 4 (Profit Extraction) | Portfolio tracking |
| VoiceAlerts | Layer 5 (Observability) | Aurora voice notifications |
| VectorStore | Layer 2 (Kernel) | Memory for state machine |

## MCP Tools Available

These tools are exposed via MCP server for Claude Desktop/CLI:

```python
# Asset scoring (0-100)
mcp__ds-star__synoptic_core_assess(asset="BTC", timeframe="1d")

# Natural language market queries
mcp__ds-star__oracle_query(question="What's the BTC trend?")

# Build strategy from description
mcp__ds-star__architect_forge_build(request="RSI oversold buy", symbols=["BTC/USDT"])

# Normalize raw exchange data
mcp__ds-star__gatekeeper_clean(raw_data={...}, source_hint="binance")

# Transparent analysis with reasoning
mcp__ds-star__transparent_analyst_explain(description="Why SOL pumping?", context={})
```

## Key Modules

```
ds_star/
├── synoptic_core/      # Smart Asset Score engine
├── oracle_interface/   # NL → Chart analysis
├── architect_forge/    # NL → Strategy builder
├── transparent_analyst/# Explainable reasoning
├── gatekeeper/         # Data normalization
├── data_feeds/         # Market data (NEW)
├── portfolio/          # Portfolio tracking (NEW)
├── voice_alerts/       # Aurora ElevenLabs (NEW)
├── vector_store/       # Embeddings/RAG (NEW)
├── ai_terminal/        # Terminal interface (NEW)
├── mcp_server/         # MCP integration
└── configs/            # System prompts
```

## Usage Examples

```bash
# Score an asset
python -c "from ds_star.synoptic_core import assess; print(assess('BTC'))"

# Query market
python -c "from ds_star.oracle_interface import query; print(query('BTC RSI'))"

# Build strategy
python -c "from ds_star.architect_forge import build; print(build('MACD crossover'))"
```

## Data Flow

```
Market Data → Gatekeeper (clean) → SynopticCore (score) → ArchitectForge (strategy)
                                          ↓
                               TransparentAnalyst (explain)
                                          ↓
                                  VoiceAlerts (Aurora)
```

## Status

- Files: 15+ analysis modules
- MCP: 5 tools exposed
- Fortress: Integrated with Layers 1, 2, 3, 4, 5

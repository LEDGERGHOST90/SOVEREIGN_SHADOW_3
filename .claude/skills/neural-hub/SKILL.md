---
name: neural-hub
description: Gemini AI integration for market analysis, sentiment tracking, pattern recognition. 6 AI modules. (project)
---

# NEURAL HUB - GIO (Gemini) Integration

**Location:** `/Volumes/LegacySafe/SS_III/neural_hub/`

## AI Council Role

**GIO (Gemini)** = The Researcher
- Market analysis & sentiment
- YouTube strategy extraction
- Pattern recognition
- 4-day research cycle driver

## 4-Day Research Cycle

```
┌─────────────────────────────────────────────────────────┐
│  DAY 1-2: RESEARCH                                      │
│  ├── GIO searches YouTube for trading strategies        │
│  ├── Extracts key concepts, indicators, rules           │
│  └── Stores findings in vector_store                    │
├─────────────────────────────────────────────────────────┤
│  DAY 3: IMPLEMENT                                       │
│  ├── ArchitectForge builds strategies from research     │
│  ├── Deploys to paper trading environment               │
│  └── Sets up performance tracking                       │
├─────────────────────────────────────────────────────────┤
│  DAY 4: TEST                                            │
│  ├── Paper trades execute                               │
│  ├── Performance metrics collected                      │
│  └── Win rate, profit factor calculated                 │
├─────────────────────────────────────────────────────────┤
│  DAY 5+: PURGE & PROMOTE                                │
│  ├── Underperformers (<50% win rate) deleted            │
│  ├── Winners promoted to live consideration             │
│  └── Cycle repeats with new research                    │
└─────────────────────────────────────────────────────────┘
```

## Fortress Integration

| Component | Fortress Layer | Purpose |
|-----------|----------------|---------|
| gemini_agent | Layer 3 (AI Agents) | Research & analysis |
| strategy_extractor | Layer 3 (AI Agents) | YouTube → strategy |
| sentiment_tracker | Layer 5 (Observability) | Market mood |
| pattern_detector | Layer 3 (AI Agents) | Chart patterns |

## Key Modules

```
neural_hub/
├── backend/
│   ├── gemini_agent.py     # GIO API integration
│   ├── youtube_scanner.py  # Strategy extraction
│   └── sentiment.py        # Social sentiment
├── research_cycle/
│   ├── orchestrator.py     # 4-day cycle manager
│   └── performance.py      # Strategy scoring
└── api.py                  # FastAPI backend (port 8000)
```

## Research Cycle Commands

```bash
# Start research phase
python -m neural_hub.research_cycle.orchestrator --phase research

# Check strategy performance
python -m neural_hub.research_cycle.performance --list

# Purge underperformers
python -m neural_hub.research_cycle.orchestrator --phase purge --threshold 0.5
```

## YouTube Strategy Extraction

```python
# GIO extracts strategies from YouTube videos
from neural_hub.backend.youtube_scanner import extract_strategy

strategy = extract_strategy(
    video_url="https://youtube.com/watch?v=...",
    focus=["entry_rules", "exit_rules", "indicators"]
)
# Returns structured strategy for ArchitectForge
```

## Status

- Files: 6+ AI modules
- GIO: Active (Gemini API)
- Research Cycle: Defined, implementing
- Port: 8000 (FastAPI backend)

# 🏴 SOVEREIGN SHADOW II - AUTONOMOUS TRADING SYSTEM

**Skills-Based AI Architecture with Continuous Learning**

## System Architecture

This system implements the **D.O.E. Pattern** (Directive → Orchestration → Execution):

```
┌─────────────────────────────────────────────────────────────┐
│                    DIRECTIVE LAYER                          │
│              Market Regime Detector                          │
│      (Classifies market conditions: trending, choppy, etc)   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER                          │
│              AI Strategy Selector                            │
│   (Picks best strategy for current market regime)            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXECUTION LAYER                             │
│                Strategy Engine                               │
│     (Executes trades via exchange APIs)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  LEARNING LAYER                              │
│              Performance Tracker                             │
│    (Enables self-annealing feedback loop)                    │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
sovereign_shadow_ii/
├── core/
│   ├── exchange_connectors/      # Exchange API integrations
│   │   ├── base_connector.py     # Base connector interface
│   │   ├── coinbase_connector.py # Coinbase Advanced Trade
│   │   ├── okx_connector.py      # OKX
│   │   └── kraken_connector.py   # Kraken
│   ├── intelligence/             # AI decision-making
│   │   ├── regime_detector.py    # Market regime classification
│   │   ├── strategy_selector.py  # Strategy selection AI
│   │   └── performance_tracker.py # Learning database
│   └── orchestrator.py           # Master coordinator
├── strategies/
│   └── modularized/             # Modular strategy components
│       ├── elder_reversion/     # Example strategy
│       │   ├── entry.py
│       │   ├── exit.py
│       │   ├── risk.py
│       │   └── metadata.json
│       └── ... (more strategies)
├── data/                        # Historical data & databases
├── logs/                        # System logs
└── tests/                       # Unit tests
```

## Current Capital

- **Total**: $10,811
  - Ledger: $6,600
  - Coinbase: $1,660
  - AAVE positions: ~$2,551

## Safety Features

- **DEFAULT MODE**: FAKE (paper trading)
- **3-Strike Psychology Rule**: Auto-lockout after 3 losses
- **Position Sizing**: Max 10% per trade
- **Stop Losses**: Mandatory on every trade
- **Risk Management**: 1-2% risk per trade

## Quick Start

```bash
# Set environment to FAKE mode (default)
export ENV=development
export ALLOW_LIVE_EXCHANGE=0
export USE_SANDBOX=true

# Run the orchestrator
python core/orchestrator.py
```

## Configuration

Edit `.env` file:
```bash
# Exchange credentials
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here

# Safety settings
ENV=development  # development or production
ALLOW_LIVE_EXCHANGE=0  # 0 = FAKE mode, 1 = LIVE mode
MAX_POSITION_SIZE=100  # USD
RISK_PER_TRADE=0.01  # 1%
```

## Status

- [x] Core infrastructure created
- [x] Exchange connectors framework
- [x] Market regime detector
- [x] AI strategy selector
- [x] Performance tracker
- [ ] Full strategy library (in progress)
- [ ] Backtesting complete
- [ ] Live trading (LOCKED until validation)

---

**Built for Raymond (LedgerGhost90)**  
*"System over emotion. Every single time."*

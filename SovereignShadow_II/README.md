# SS_III - Autonomous Trading System

**Skills-Based AI Architecture with Continuous Learning**

## Overview

SS_III is an autonomous trading system implementing the **D.O.E. Pattern**:

- **Directive Layer**: Market Regime Detector (classifies market conditions)
- **Orchestration Layer**: AI Strategy Selector (picks best strategy for regime)
- **Execution Layer**: Strategy Engine (executes trades via exchange APIs)
- **Learning Layer**: Performance Tracker (enables self-annealing loop)

## Architecture

```
SS_III/
├── core/
│   ├── exchange_connectors/    # Exchange API connectors
│   │   ├── base_connector.py
│   │   └── coinbase_connector.py
│   ├── intelligence/          # AI components
│   │   ├── performance_tracker.py
│   │   ├── regime_detector.py
│   │   └── strategy_selector.py
│   └── orchestrator.py          # Master coordinator
├── strategies/
│   └── modularized/            # Modularized strategies (from Agents 1-8)
├── config/                     # Configuration files
├── data/                       # SQLite database and data
├── logs/                       # Log files
└── main.py                     # Entry point
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export COINBASE_API_KEY="your_api_key"
export COINBASE_API_SECRET="your_api_secret"
export ENV="development"  # or "production"
export ALLOW_LIVE_EXCHANGE="0"  # Set to "1" for live trading
export USE_SANDBOX="true"  # Use sandbox mode
```

## Safety Guardrails

**DEFAULT TO FAKE MODE** - The system will NOT execute real trades unless:

1. `ENV=production`
2. `ALLOW_LIVE_EXCHANGE=1`
3. Position size checks pass
4. Stop loss is configured

## Usage

**Run the system:**
```bash
python main.py
```

**Development mode (safe, no real trades):**
```bash
export ENV=development
export ALLOW_LIVE_EXCHANGE=0
export USE_SANDBOX=true
python main.py
```

## Components

### Exchange Connectors

- **Coinbase Advanced Trade**: Uses CCXT library with proper authentication
- **Base Connector**: Abstract interface for adding more exchanges (OKX, Kraken, Binance US)

### Performance Tracker

SQLite database tracking:
- Trade history
- Strategy performance metrics
- Market regime history
- Strategy selection logs

### Market Regime Detector

Classifies market into 4 regimes:
- `trending_up`: Strong uptrend
- `trending_down`: Strong downtrend
- `choppy_volatile`: Sideways with high volatility
- `choppy_calm`: Sideways with low volatility

### AI Strategy Selector

Selects optimal strategy based on:
- Current market regime
- Historical performance data
- Strategy suitability metadata

## Integration with Agents 1-9

This system is designed to integrate with modularized strategies from Agents 1-8 and backtest results from Agent 9.

**Strategy Structure:**
```
strategies/modularized/{strategy_name}/
    ├── entry.py          # Entry signal logic
    ├── exit.py           # Exit signal logic
    ├── risk.py           # Risk management
    └── metadata.json     # Strategy metadata
```

## Status

✅ **Core Infrastructure Complete:**
- Exchange connector framework
- Performance tracker database
- Market regime detector
- AI strategy selector
- Master orchestrator

⏳ **Pending:**
- Strategy modularization (Agents 1-8)
- Backtest engine (Agent 9)
- Full integration testing

## License

Proprietary - SS_III

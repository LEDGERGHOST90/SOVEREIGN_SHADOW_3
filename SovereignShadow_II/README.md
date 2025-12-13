# Sovereign Shadow II

## System Overview
Sovereign Shadow II is an autonomous trading system implementing a Skills-Based AI architecture with continuous learning capabilities.

## Architecture (D.O.E. Pattern)
1. **Directive Layer**: Market Regime Detector
2. **Orchestration Layer**: AI Strategy Selector
3. **Execution Layer**: Strategy Engine & Connectors
4. **Learning Layer**: Performance Tracker & Backtest Engine

## Directory Structure
- `core/`: Core infrastructure (connectors, intelligence, orchestrator)
- `strategies/modularized/`: Strategy modules (Entry/Exit/Risk)
- `tests/`: Unit and integration tests
- `performance.db`: SQLite database for trade logging

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables (see `.env.example` - to be created):
   - `COINBASE_API_KEY`
   - `COINBASE_API_SECRET`
   - `ENV` (production/development)
   - `ALLOW_LIVE_EXCHANGE` (1/0)

## Running
- **Orchestrator**: `python core/orchestrator.py`
- **Backtesting**: Use `core/backtesting/backtest_engine.py` or run `tests/integration_test.py`

## Strategies
Currently implemented modular strategies:
- **ElderReversion**: Mean reversion using Elder Ray Index
- **DynamicCrossfire**: Trend following using EMA crossover + RSI

## Agents Status
- Agent 0 (Architect): **COMPLETE**
- Agent 1 (Strategies 1-10): **PARTIAL** (2/10 implemented)
- Agent 9 (Backtester): **COMPLETE**

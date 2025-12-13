# SS_III - Autonomous Trading System

## Project Structure
- `core/`: Core infrastructure (Exchange Connectors, Intelligence, Orchestrator)
- `strategies/modularized/`: Modularized trading strategies (Skills-Based Architecture)
- `tests/`: Integration and unit tests
- `requirements.txt`: Python dependencies

## Deployment Status
- **Agent 0 (Architect)**: Core infrastructure deployed.
    - Exchange Connectors: Coinbase Advanced (Base implemented)
    - Intelligence: Regime Detector, Strategy Selector, Performance Tracker implemented.
    - Orchestrator: Master loop implemented.
- **Agent 1**: ElderReversion strategy modularized and tested.
- **Agent 8**: Strategies 71-80 modularized (Pairs, Coint, TriArb, CrossExchange, Funding, Basis, CashCarry, Options, VolArb, Calendar).
- **Agent 9 (Backtest)**: Backtest Engine implemented and verified.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables in `.env` (copy from template if available, otherwise set keys).
3. Run the orchestrator:
   ```bash
   python3 core/orchestrator.py
   ```

## Development
To add a new strategy, replicate the structure in `strategies/modularized/elder_reversion/` and update the strategy list.

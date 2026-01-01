# SOVEREIGN SHADOW II

## D.O.E. Pattern Autonomous Trading System

An AI-powered autonomous trading system implementing the **D.O.E. (Directive-Orchestration-Execution) Pattern** with a self-annealing learning loop.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN SHADOW II                           │
│                     D.O.E. PATTERN                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │  DIRECTIVE   │────▶│  Market Regime Detector              │  │
│  │    LAYER     │     │  - Classifies market conditions      │  │
│  └──────────────┘     │  - 7 distinct regimes                │  │
│         │             └──────────────────────────────────────┘  │
│         ▼                                                        │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │ ORCHESTRATION│────▶│  AI Strategy Selector                │  │
│  │    LAYER     │     │  - Selects optimal strategy          │  │
│  └──────────────┘     │  - Performance-based ranking         │  │
│         │             └──────────────────────────────────────┘  │
│         ▼                                                        │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │  EXECUTION   │────▶│  Strategy Engine + Exchange API      │  │
│  │    LAYER     │     │  - Modularized strategies            │  │
│  └──────────────┘     │  - Multi-exchange support            │  │
│         │             └──────────────────────────────────────┘  │
│         ▼                                                        │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │  LEARNING    │────▶│  Performance Tracker (SQLite)        │  │
│  │    LAYER     │     │  - Self-annealing loop               │  │
│  └──────────────┘     │  - Strategy ranking updates          │  │
│                       └──────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Paper trading mode (default - no real money)
python main.py

# With custom settings
python main.py --capital 5000 --max-positions 2 --symbol ETH/USD

# Run backtest
python main.py --backtest

# Check system status
python main.py --status

# Single cycle test
python main.py --test
```

## Market Regimes

The system detects 7 distinct market conditions:

| Regime | Description | Best Strategies |
|--------|-------------|-----------------|
| `trending_bullish` | Strong upward momentum | TrendFollowEMA, BreakoutRetest |
| `trending_bearish` | Strong downward momentum | TrendFollowEMA (short), BollingerBounce |
| `choppy_volatile` | High volatility, no trend | ElderReversion, RSIReversion |
| `choppy_calm` | Low volatility, ranging | SupportResistanceBounce, VWAPReversion |
| `breakout_potential` | Consolidation, ready to break | VolatilityBreakout, ChoppyBreakout |
| `capitulation` | Extreme fear, potential reversal | RSIReversion, DivergenceScalp |
| `euphoria` | Extreme greed, potential top | RSIReversion, BollingerBounce |

## Built-in Strategies

### Currently Implemented

1. **ElderReversion** - Mean reversion using Elder Ray indicator
2. **RSIReversion** - RSI-based oversold/overbought reversions
3. **TrendFollowEMA** - EMA crossover trend following

### Modularized Structure

Each strategy is broken into three components:

```
strategies/modularized/agent_N/strategy_name/
    ├── entry.py      # Entry signal generation
    ├── exit.py       # Exit signal generation
    ├── risk.py       # Position sizing & risk management
    ├── metadata.json # Strategy configuration
    └── __init__.py
```

## Safety Features

### Default Safeguards

- **Paper Trading Mode**: Enabled by default
- **Daily Loss Limit**: 5% max daily loss
- **Position Limits**: Max 3 concurrent positions
- **Stop Losses**: Mandatory on all trades

### Live Trading Requirements

```bash
# Required environment variables for live trading
export ENV=production
export ALLOW_LIVE_EXCHANGE=1
export COINBASE_API_KEY=your_key
export COINBASE_API_SECRET=your_secret
```

Live trading also requires manual confirmation:
```
Type 'I UNDERSTAND THE RISKS' to proceed:
```

## Project Structure

```
sovereign_shadow_ii/
├── main.py                          # Main entry point
├── README.md
├── core/
│   ├── intelligence/
│   │   ├── performance_tracker.py   # SQLite learning database
│   │   ├── regime_detector.py       # Market regime classification
│   │   └── strategy_selector.py     # AI-powered strategy selection
│   ├── orchestration/
│   │   ├── orchestrator.py          # Main D.O.E. orchestrator
│   │   └── builtin_strategies.py    # Core strategy implementations
│   ├── backtesting/
│   │   └── backtest_engine.py       # Comprehensive backtester
│   └── exchange_connectors/
│       └── (uses parent connectors)
├── strategies/
│   └── modularized/
│       ├── agent_1/                 # Strategies 1-10
│       ├── agent_2/                 # Strategies 11-20
│       └── ...                      # Up to agent_8
├── data/
│   ├── performance.db               # SQLite database
│   └── backtest_results/
├── logs/
│   └── sovereign_YYYYMMDD.log
└── tests/
```

## Configuration

### OrchestratorConfig

```python
OrchestratorConfig(
    paper_trading=True,              # Default: safe mode
    sandbox_mode=True,               # Use exchange sandboxes
    initial_capital=10000.0,         # Starting capital
    max_position_size_percent=10.0,  # Max 10% per position
    max_open_positions=3,            # Max concurrent positions
    risk_per_trade_percent=1.0,      # 1% risk per trade
    max_daily_loss_percent=5.0,      # 5% daily loss limit
    regime_check_interval_seconds=300,   # 5-minute regime checks
    strategy_check_interval_seconds=60,  # 1-minute strategy checks
)
```

## Performance Tracking

All trades are logged to SQLite with:
- Entry/exit prices and times
- PnL (USD and percentage)
- Strategy and regime context
- Exit reasons

The learning loop updates strategy rankings based on:
- Win rate (40% weight)
- Average PnL (30% weight)
- Sharpe ratio (20% weight)
- Trade count confidence (10% weight)

## Backtesting

```python
from core.backtesting.backtest_engine import BacktestEngine

engine = BacktestEngine(initial_capital=10000.0)
engine.generate_synthetic_data(1000, trend="bullish")
results = engine.run_all_backtests()
report = engine.generate_report(results)
```

## Exchange Support

- **Coinbase** (Primary)
- **Kraken**
- **Binance US**
- **OKX**

Connectors use CCXT for standardized interface.

## Development

### Adding a New Strategy

1. Create strategy directory:
   ```
   strategies/modularized/agent_N/my_strategy/
   ```

2. Implement modules:
   - `entry.py` with `generate_signal(market_data)` method
   - `exit.py` with `generate_signal(market_data, entry_price)` method
   - `risk.py` with `calculate_position_size(portfolio, price, atr)` method

3. Add `metadata.json` with strategy configuration

4. The Strategy Selector will automatically discover and test new strategies

## License

Private - For Raymond (LedgerGhost90) personal use

## Support

For issues or questions, contact via the Sovereign Shadow project repository.

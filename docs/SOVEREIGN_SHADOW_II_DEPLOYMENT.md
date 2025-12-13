# 🏴 SOVEREIGN SHADOW II - DEPLOYMENT GUIDE

## Overview

Sovereign Shadow II is an autonomous cryptocurrency trading system implementing the **D.O.E. Pattern**:

1. **Directive Layer**: Market Regime Detector - Classifies market conditions
2. **Orchestration Layer**: AI Strategy Selector - Picks optimal strategy for regime
3. **Execution Layer**: Strategy Engine - Executes trades via exchange APIs

## Quick Start

### 1. Install Dependencies

```bash
cd /workspace
pip install -r requirements.txt
```

### 2. Run in FAKE Mode (Paper Trading)

```bash
python scripts/start_sovereign_shadow.py --mode=fake --capital=10000
```

### 3. Run Tests

```bash
pytest tests/test_sovereign_shadow.py -v
```

## System Architecture

```
/workspace/
├── core/
│   ├── intelligence/
│   │   ├── regime_detector.py      # Market regime classification
│   │   ├── strategy_selector.py    # AI strategy selection
│   │   └── performance_tracker.py  # Trade logging & analytics
│   ├── safety/
│   │   └── guardrails.py           # Safety limits & validation
│   └── orchestrator.py             # Master coordination
├── strategies/
│   └── modularized/
│       ├── base.py                 # Base strategy classes
│       ├── registry.py             # Strategy registry
│       ├── elder_reversion/        # Elder Reversion strategy
│       ├── trend_follow_ema/       # EMA Trend Following
│       ├── rsi_reversion/          # RSI Mean Reversion
│       ├── bollinger_bounce/       # Bollinger Band Bounce
│       ├── volatility_breakout/    # Volatility Breakout
│       └── banded_stochastic/      # Banded Stochastic
└── exchanges/
    ├── base_connector.py           # Abstract connector
    ├── coinbase_connector.py       # Coinbase integration
    ├── okx_connector.py            # OKX integration
    └── kraken_connector.py         # Kraken integration
```

## Market Regimes

The system classifies markets into four regimes:

| Regime | Characteristics | Best Strategies |
|--------|----------------|-----------------|
| `trending_bull` | Strong uptrend, ADX > 25 | TrendFollowEMA, MomentumScalp |
| `trending_bear` | Strong downtrend | RSIReversion, BollingerBounce |
| `choppy_volatile` | Range-bound, high ATR | ElderReversion, BandedStochastic |
| `choppy_calm` | Range-bound, low ATR | VolatilityBreakout, DynamicCrossfire |

## Modular Strategy Structure

Each strategy consists of three modules:

```python
# Entry Module - Signal generation
class ElderReversionEntry(BaseEntryModule):
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        # Returns: BUY, SELL, or NEUTRAL with confidence

# Exit Module - Exit logic
class ElderReversionExit(BaseExitModule):
    def generate_signal(self, df, entry_price) -> ExitSignal:
        # Returns: SELL or HOLD with reason (TP/SL/Signal)

# Risk Module - Position sizing
class ElderReversionRisk(BaseRiskModule):
    def calculate_position_size(self, portfolio_value, price) -> PositionSizing:
        # Returns: position size, stop loss, take profit
```

## Safety Features

### Mandatory Safety Limits

- **Max Position Size**: 10% of portfolio
- **Max Daily Loss**: 3% stops all trading
- **Min Stop Loss**: 0.5% (enforced)
- **Cooldown**: 5 minutes between trades
- **Max Positions**: 3 concurrent

### Trading Modes

| Mode | Description | Risk |
|------|-------------|------|
| `fake` | Paper trading (default) | None |
| `sandbox` | Exchange testnet | None |
| `live` | Real money | HIGH |

### Enabling Live Trading

⚠️ **WARNING**: Live trading involves real financial risk.

```bash
# Only do this after extensive testing in FAKE mode
export ALLOW_LIVE_TRADING=YES_I_UNDERSTAND_THE_RISKS
python scripts/start_sovereign_shadow.py --mode=live
```

## Configuration

### Environment Variables

```bash
# Trading Mode
export ENV=development  # or production

# Exchange API Keys
export COINBASE_API_KEY=your_key
export COINBASE_API_SECRET=your_secret
export COINBASE_PASSPHRASE=your_passphrase

# OKX (optional)
export OKX_API_KEY=your_key
export OKX_API_SECRET=your_secret
export OKX_PASSPHRASE=your_passphrase

# Safety
export ALLOW_LIVE_TRADING=  # Set to enable live
```

## Monitoring

### Get System Status

```python
from core.orchestrator import create_orchestrator

orchestrator = create_orchestrator(mode="fake", initial_capital=10000)
print(orchestrator.get_summary())
```

### Performance Database

The system stores all trades in SQLite:

```python
from core.intelligence.performance_tracker import PerformanceTracker

tracker = PerformanceTracker("sovereign_shadow.db")
summary = tracker.get_summary()
print(f"Total Trades: {summary['total_trades']}")
print(f"Total P&L: ${summary['total_pnl_usd']}")
```

## Adding New Strategies

1. Create strategy directory:
```bash
mkdir -p strategies/modularized/my_strategy
```

2. Create modules:
```python
# strategies/modularized/my_strategy/__init__.py
from .entry import MyStrategyEntry
from .exit import MyStrategyExit
from .risk import MyStrategyRisk
from strategies.modularized.base import ModularStrategy

def get_strategy():
    return ModularStrategy(
        name="MyStrategy",
        entry_module=MyStrategyEntry(),
        exit_module=MyStrategyExit(),
        risk_module=MyStrategyRisk(),
        suitable_regimes=["trending_bull"],
        timeframes=["1h", "4h"],
        assets=["BTC/USDT"]
    )
```

3. Register in orchestrator:
```python
from strategies.modularized.my_strategy import get_strategy
orchestrator.register_strategy(get_strategy())
```

## Troubleshooting

### Common Issues

1. **"Insufficient data" error**
   - Ensure OHLCV data has at least 100 candles

2. **"Pre-flight checks failed"**
   - Check environment variables
   - Verify API key configuration

3. **"Cooldown active"**
   - Wait for cooldown period (5 minutes)
   - Or adjust `cooldown_seconds` in SafetyGuardrails

### Logs

```bash
# View logs
tail -f sovereign_shadow.log

# Debug mode
python scripts/start_sovereign_shadow.py --mode=fake 2>&1 | tee debug.log
```

## API Reference

### Orchestrator

```python
from core.orchestrator import SovereignOrchestrator

orchestrator = SovereignOrchestrator(
    mode=TradingMode.FAKE,
    initial_capital=10000,
    db_path="sovereign_shadow.db"
)

# Register strategies
orchestrator.register_strategy(strategy)

# Run trading cycle
result = await orchestrator.run_cycle(market_data)

# Get state
state = orchestrator.get_state()
```

### Regime Detector

```python
from core.intelligence.regime_detector import RegimeDetector

detector = RegimeDetector(lookback_period=100)
analysis = detector.detect_regime(ohlcv_df)

print(f"Regime: {analysis.regime}")
print(f"Confidence: {analysis.confidence}%")
print(f"Recommended: {analysis.recommended_strategies}")
```

### Strategy Selector

```python
from core.intelligence.strategy_selector import StrategySelector

selector = StrategySelector(detector, tracker)
selector.register_strategies(["ElderReversion", "TrendFollowEMA"])

selection = selector.select_strategy(df)
print(f"Selected: {selection.strategy_name}")
print(f"Position Size: {selection.suggested_position_size * 100}%")
```

## Support

For issues or questions:
- Review the code in `/workspace/core/`
- Check test examples in `/workspace/tests/`
- Examine strategy implementations in `/workspace/strategies/modularized/`

---

**Remember**: Always test extensively in FAKE mode before considering live trading.
The system is designed to protect capital, but no trading system is without risk.

🏴 *Trade wisely, trade safely.*

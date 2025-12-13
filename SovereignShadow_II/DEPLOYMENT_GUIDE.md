# Sovereign Shadow II - Deployment Guide

## Quick Start

### 1. Environment Setup

```bash
# Clone/copy the SovereignShadow_II directory
cd SovereignShadow_II

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Configure Exchange API Keys

**Coinbase Advanced Trade:**
1. Go to Coinbase Advanced Trade API settings
2. Create API key with trading permissions
3. Set `COINBASE_API_KEY` and `COINBASE_API_SECRET` in `.env`

**Important:** Start with sandbox mode (`USE_SANDBOX=true`)

### 3. Safety Configuration

**Development Mode (Safe - No Real Trades):**
```bash
export ENV=development
export ALLOW_LIVE_EXCHANGE=0
export USE_SANDBOX=true
```

**Production Mode (Live Trading - USE WITH CAUTION):**
```bash
export ENV=production
export ALLOW_LIVE_EXCHANGE=1
export USE_SANDBOX=false
```

⚠️ **WARNING:** Only enable production mode after thorough testing!

### 4. Run System

```bash
# Development mode (safe)
python main.py
```

## System Architecture

### D.O.E. Pattern Flow

```
1. DIRECTIVE LAYER
   └─> Market Regime Detector
       └─> Classifies market: trending_up, trending_down, choppy_volatile, choppy_calm

2. ORCHESTRATION LAYER
   └─> AI Strategy Selector
       └─> Selects best strategy based on regime + performance data

3. EXECUTION LAYER
   └─> Strategy Engine
       └─> Executes trades via Exchange Connectors

4. LEARNING LAYER
   └─> Performance Tracker
       └─> Logs trades, updates performance metrics
```

### Component Overview

**Exchange Connectors:**
- `core/exchange_connectors/coinbase_connector.py` - Coinbase Advanced Trade
- `core/exchange_connectors/base_connector.py` - Base interface for other exchanges

**Intelligence Components:**
- `core/intelligence/performance_tracker.py` - SQLite database for tracking
- `core/intelligence/regime_detector.py` - Market regime classification
- `core/intelligence/strategy_selector.py` - AI strategy selection

**Orchestration:**
- `core/orchestrator.py` - Master coordinator implementing D.O.E. pattern

## Adding Strategies

Strategies are modularized into three components:

1. **Entry Module** (`entry.py`) - Generates buy signals
2. **Exit Module** (`exit.py`) - Generates sell signals
3. **Risk Module** (`risk.py`) - Position sizing and risk management

See `INTEGRATION_NOTES.txt` for detailed templates.

## Monitoring

**Logs:**
- Location: `logs/sovereign_shadow.log`
- Level: INFO (configurable via LOG_LEVEL env var)

**Database:**
- Location: `data/performance.db`
- Tables:
  - `trades` - Trade history
  - `strategy_performance` - Performance metrics per strategy/regime
  - `regime_history` - Market regime detection history
  - `strategy_selections` - Strategy selection log

**Query Performance:**
```python
from core.intelligence import PerformanceTracker

tracker = PerformanceTracker("data/performance.db")
performance = tracker.get_strategy_performance(
    strategy_name="ElderReversion",
    regime="choppy_volatile"
)
print(performance)
```

## Troubleshooting

### Coinbase Connection Issues

**Error: "Missing Coinbase credentials"**
- Check `.env` file has `COINBASE_API_KEY` and `COINBASE_API_SECRET`
- Verify API keys are valid

**Error: "Connection test failed"**
- Check internet connection
- Verify API key permissions
- Try sandbox mode first: `USE_SANDBOX=true`

### Strategy Loading Issues

**Error: "Strategy not found"**
- Verify strategy directory exists: `strategies/modularized/{strategy_name}/`
- Check for `entry.py`, `exit.py`, `risk.py`, `metadata.json`

**Error: "Entry class not found"**
- Verify class name matches: `{StrategyName}Entry` (PascalCase)
- Check `entry.py` has correct class definition

### Performance Tracker Issues

**Database locked errors:**
- Ensure only one instance is running
- Check file permissions on `data/performance.db`

## Production Checklist

Before enabling live trading:

- [ ] Tested in sandbox mode for at least 1 week
- [ ] Reviewed all strategy logic
- [ ] Verified risk management settings
- [ ] Set appropriate position size limits
- [ ] Configured stop losses
- [ ] Tested error handling and recovery
- [ ] Set up monitoring/alerts
- [ ] Backed up database
- [ ] Documented deployment configuration

## Support

For issues or questions:
1. Check `INTEGRATION_NOTES.txt` for integration details
2. Review logs in `logs/sovereign_shadow.log`
3. Check database for trade history and performance metrics

## Next Steps

1. **Agents 1-8**: Modularize strategies (see `INTEGRATION_NOTES.txt`)
2. **Agent 9**: Build backtest engine
3. **Integration**: Test full system with modularized strategies
4. **Deployment**: Gradual rollout with small position sizes

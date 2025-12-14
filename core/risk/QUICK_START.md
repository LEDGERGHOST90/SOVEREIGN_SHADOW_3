# Advanced Risk Module - Quick Start

**2-Minute Integration Guide**

---

## Installation

✅ Already installed at: `/Volumes/LegacySafe/SS_III/core/risk/advanced_risk_module.py`

---

## 30-Second Example

```python
from core.risk.advanced_risk_module import AdvancedRiskManager

# Initialize (once per session)
risk = AdvancedRiskManager(base_risk_pct=0.02)

# Before every trade
result = risk.calculate_position_size(
    equity=5433.87,
    symbol="BTC/USD",
    atr_value=1200,
    sector="Infrastructure",
    strategy="swing_trade",
    use_kelly=True
)

if result.size > 0:
    # Trade approved
    buy(symbol, result.size)
    risk.register_position(symbol, result.size, entry, stop)
else:
    # Trade blocked
    log(f"Blocked: {result.method}")
```

---

## Integration with Existing Code

### Before (Old Way)
```python
def execute_trade(symbol, price):
    # Fixed 2% risk
    risk_amount = portfolio * 0.02
    position_size = risk_amount / stop_distance
    buy(symbol, position_size)
```

### After (New Way)
```python
def execute_trade(symbol, price, atr, sector):
    # Advanced risk management
    result = self.risk_manager.calculate_position_size(
        equity=self.portfolio_value,
        symbol=symbol,
        atr_value=atr,
        sector=sector,
        strategy=self.name,
        use_kelly=True
    )

    if result.size == 0:
        return False  # Blocked by risk management

    buy(symbol, result.size)
    self.risk_manager.register_position(
        symbol, result.size, price,
        price - result.stop_distance, sector
    )
    return True
```

---

## Key Methods

### 1. Calculate Position Size (Main Method)
```python
result = risk.calculate_position_size(
    equity=portfolio_value,
    symbol="SOL/USD",
    atr_value=5.2,
    sector="Infrastructure",
    strategy="swing_trade",
    use_kelly=True  # Optional: use Kelly sizing
)
```

**Returns**:
- `result.size` - Position size to buy
- `result.risk_amount` - Dollar risk
- `result.stop_distance` - Stop loss distance
- `result.method` - Method used (or why blocked)
- `result.warnings` - Any warnings

### 2. Register Position (After Trade)
```python
risk.register_position(
    symbol="BTC/USD",
    size=0.05,
    entry_price=42000,
    stop_loss=40000,
    sector="Infrastructure",
    strategy="swing_trade"
)
```

### 3. Close Position (After Exit)
```python
summary = risk.close_position(
    symbol="BTC/USD",
    exit_price=45000,
    strategy="swing_trade"
)
# Auto-updates circuit breaker based on win/loss
```

### 4. Check Status (Anytime)
```python
summary = risk.get_risk_summary()
print(f"Portfolio Heat: {summary['portfolio_heat']['utilization']*100:.1f}%")
print(f"Open Positions: {summary['open_positions']}")
```

---

## Return Values to Check

### When `result.size == 0`:

| `result.method` | Meaning | Action |
|-----------------|---------|--------|
| `CIRCUIT_BREAKER_PAUSED` | 5 losses, paused 24h | Wait for reset |
| `PORTFOLIO_HEAT_EXCEEDED` | Max 6% heat reached | Close a position |
| `ATR` but size=0 | Other constraints | Check warnings |

### When `result.size > 0`:
- ✅ Trade approved
- Use `result.size` for position size
- Use `result.stop_distance` for stop loss

---

## Common Patterns

### Pattern 1: Simple Trade
```python
result = risk.calculate_position_size(
    equity=5433.87,
    symbol="ETH/USD",
    atr_value=80
)

if result.size > 0:
    execute_trade("ETH/USD", result.size)
```

### Pattern 2: With Omega Risk Manager
```python
# Check correlation first
corr = omega_risk.analyze_portfolio_correlation_risk(positions)

# Then size position
if corr['risk_level'] not in ['CRITICAL', 'HIGH']:
    result = advanced_risk.calculate_position_size(...)
    if result.size > 0:
        execute_trade(...)
```

### Pattern 3: Check Before Multiple Trades
```python
summary = risk.get_risk_summary()

if summary['portfolio_heat']['utilization'] < 0.8:
    # Still have room for trades
    for signal in signals:
        result = risk.calculate_position_size(...)
        if result.size > 0:
            execute_trade(signal, result.size)
```

---

## Configuration Presets

### Conservative (Recommended for SS_III)
```python
risk = AdvancedRiskManager(
    base_risk_pct=0.015,        # 1.5% risk
    max_portfolio_heat=0.05,    # 5% max
    kelly_max_fraction=0.125    # Eighth-Kelly
)
```

### Moderate (Default)
```python
risk = AdvancedRiskManager(
    base_risk_pct=0.02,         # 2% risk
    max_portfolio_heat=0.06,    # 6% max
    kelly_max_fraction=0.25     # Quarter-Kelly
)
```

---

## What Gets Tracked Automatically

✅ **Portfolio Heat** - Total risk across all positions
✅ **Sector Heat** - Risk per sector
✅ **Circuit Breakers** - Consecutive losses per strategy
✅ **ATR History** - Last 100 values per symbol
✅ **Open Positions** - All registered positions

**State persists** across restarts at: `~/.keyblade/advanced_risk_state.json`

---

## Daily Checklist

```python
# Run this every day or in your monitoring loop
summary = risk.get_risk_summary()

# Check alerts
if summary['portfolio_heat']['utilization'] > 0.8:
    alert("Portfolio heat >80%")

for strategy, cb in summary['circuit_breakers'].items():
    if cb['active']:
        alert(f"{strategy}: Circuit breaker active")

# Log to BRAIN.json
update_brain_risk_metrics(summary)
```

---

## Testing

```bash
# Test the module
cd /Volumes/LegacySafe/SS_III/core/risk
python3 advanced_risk_module.py

# Test integration
python3 risk_integration_example.py
```

---

## Benefits Over Fixed % Sizing

| Feature | Fixed 2% | Advanced Risk Module |
|---------|----------|---------------------|
| Volatility adjustment | ❌ | ✅ ATR-based |
| Portfolio heat cap | ❌ | ✅ 6% max |
| Sector concentration | ❌ | ✅ 4% per sector |
| Loss streak protection | ❌ | ✅ Circuit breaker |
| Kelly optimization | ❌ | ✅ Optional |
| State persistence | ❌ | ✅ Auto-saved |

**Research shows**: 25% reduction in maximum drawdown

---

## Next Steps

1. ✅ Module created
2. ✅ Integration example created
3. ⬜ Add to your trading agents
4. ⬜ Test with paper trading
5. ⬜ Monitor for 1 week
6. ⬜ Go live with real trades

---

## Support Files

- **Full Documentation**: `README_ADVANCED_RISK.md`
- **Integration Example**: `risk_integration_example.py`
- **Main Module**: `advanced_risk_module.py`
- **Omega Risk Manager**: `omega_enhanced_risk_manager.py`

---

## Questions?

**Q: Do I need to keep both risk managers?**
A: Yes! Omega handles correlation/diversification, Advanced handles sizing/heat/circuit breakers. Use both.

**Q: Can I adjust parameters?**
A: Yes, pass them when initializing. Start conservative.

**Q: What if it keeps blocking trades?**
A: Check `result.method` and `result.warnings`. Usually means too much heat or circuit breaker active.

**Q: Will it work with my current code?**
A: Yes, just replace position sizing logic. See "Integration with Existing Code" above.

---

**Ready to use!** Start with the 30-second example above.

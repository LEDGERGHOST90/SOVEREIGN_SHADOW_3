# TOP 10 Moon Dev Strategies for SS_III Integration

**Backtested:** 2024-12-23 to 2025-12-23 (1 year, 8604 1h candles)
**Buy & Hold Return:** -10.7%
**Tested:** 450/451 strategies
**Profitable:** 5 (1.1%)

---

## TIER 1: PROFITABLE STRATEGIES

### 1. MomentumBreakout_AI7 - THE CHAMPION
| Metric | Value |
|--------|-------|
| Return | **+12.5%** |
| Alpha vs B&H | **+23.2%** |
| Trades | 9 |
| Win Rate | 55.6% |
| Best Trade | +17.9% |
| Worst Trade | -13.1% |
| Sharpe | 1.14 |

**Core Logic:**
- 10/30 EMA crossover for trend
- RSI(14) < 70 for momentum filter
- Volume > 1.2x 20-day average
- 5-bar momentum > 2%

**Entry:** Golden cross + momentum spike + volume confirmation
**Exit:** Death cross or RSI overbought

---

### 2. BandedMACD_strategy_bt - HIGH FREQUENCY
| Metric | Value |
|--------|-------|
| Return | **+6.9%** |
| Alpha vs B&H | **+17.6%** |
| Trades | 50 |
| Win Rate | 38.0% |

**Core Logic:**
- Bollinger Bands (20,2)
- MACD (12,26,9)
- 2x ATR stop loss

**Entry:** MACD cross up + price > middle band + not overbought
**Exit:** Overbought pullback

---

### 3. VolCliffArbitrage_BTFinal_v3 - HIGH CONVICTION
| Metric | Value |
|--------|-------|
| Return | **+6.4%** |
| Alpha vs B&H | **+17.1%** |
| Trades | 4 |
| Win Rate | **75.0%** |

**Core Logic:**
- Bollinger Width spike detection
- ADX < 25 (range-bound)
- Mean reversion to SMA20

**Entry:** Volatility spike + range-bound + price outside bands
**Exit:** Volatility cliff or mean reversion

---

### 4. MomentumCrossADX_BTFinal
| Metric | Value |
|--------|-------|
| Return | **+1.5%** |
| Trades | 13 |
| Win Rate | 46.2% |

---

### 5. BandMACDDivergence_AI2
| Metric | Value |
|--------|-------|
| Return | **+1.4%** |
| Trades | 33 |
| Win Rate | 42.4% |

---

## TIER 2: BREAK-EVEN STRATEGIES

| Rank | Strategy | Return | Trades |
|------|----------|--------|--------|
| 6 | EarlyBird_BuyHoldDestroyer | -0.0% | 4 |
| 7 | ConfluentHarmonics_BEST | -1.1% | 1 |
| 8 | VolCliffArbitrage_v4 | -1.3% | 35 |

---

## SS_III INTEGRATION RECOMMENDATIONS

### Primary Signal Generator
**MomentumBreakout_AI7** - Use as main entry signal generator
- Highest alpha (+23%)
- Moderate frequency (9 trades/year)
- Best risk/reward

### High Frequency Scanner
**BandedMACD_strategy_bt** - Use for active trading
- 50 trades/year
- Good for smaller positions
- Quick entries/exits

### Conviction Trades
**VolCliffArbitrage_v3** - Use for high-conviction setups
- 75% win rate (best of all)
- Only 4 trades/year
- Go bigger on these

---

## SWARM INTEGRATION

```python
# Proposed SS_III swarm setup:
strategies = {
    "primary": "MomentumBreakout_AI7",    # Main signals
    "scanner": "BandedMACD_strategy_bt",   # Active scanning
    "conviction": "VolCliffArbitrage_v3",  # High-conviction
}

# Signal weighting
weights = {
    "MomentumBreakout_AI7": 0.5,
    "BandedMACD_strategy_bt": 0.3,
    "VolCliffArbitrage_v3": 0.2,
}
```

---

## FILES

- Batch Tester: `bin/batch_strategy_tester.py`
- Results: `research/moondev_strategies/batch_results.json`
- BTC Data: `research/moondev_strategies/data/BTC-USD-15m.csv`

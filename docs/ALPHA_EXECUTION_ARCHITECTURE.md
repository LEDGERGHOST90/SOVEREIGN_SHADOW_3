# Alpha Execution Architecture

## The Complete Flow: Research → Autonomous Execution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RESEARCH LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Manus (54 reports)  →  ALPHA_DIGEST.md  →  BRAIN.json (market_analysis)   │
│         ↓                      ↓                      ↓                      │
│   Whale Signals          Sector Ratings         Regime Classification       │
│   Hayes Rotation         Key Levels             Fear & Greed                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CALIBRATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   alpha_bias.json                                                            │
│   ├── market_regime (TRANSITIONAL_BULLISH, 0/30 peak indicators)            │
│   ├── execution_bias (long_bias: 0.75, size_multiplier: 1.2)                │
│   ├── sector_weights (RWA: 25%, AI: 20%, DeFi: 20%)                         │
│   ├── whale_signals (AVNT, PROVE, PLUME accumulation)                       │
│   ├── risk_parameters (SL: 5%, TP1: 15%, TP2: 30%)                          │
│   └── autonomous_rules (Tier 1/2/3 conditions)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   overnight_runner.py                                                        │
│   ├── Live Data Pipeline (prices, orderbooks)                               │
│   ├── Agent Council (multi-AI consensus)                                    │
│   ├── Opportunity Analysis (technical signals)                              │
│   └── Alpha Executor Integration ← NEW                                      │
│         ↓                                                                    │
│   alpha_executor.py                                                          │
│   ├── apply_bias() → Adjust confidence based on research                    │
│   ├── classify_tier() → Determine execution tier                            │
│   └── process_signal() → Route to appropriate action                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THREE-TIER EXECUTION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   TIER 1: AUTO EXECUTE                                                       │
│   ├── Conditions: <$50, Blue Chip (BTC/ETH/SOL), >80% confidence            │
│   ├── Action: Execute immediately, create paper trade                       │
│   └── Notify: Mobile push confirmation                                      │
│                                                                              │
│   TIER 2: QUEUE FOR APPROVAL                                                 │
│   ├── Conditions: $50-$200, 60-80% confidence                               │
│   ├── Action: Save to pending_approvals.json                                │
│   └── Notify: Mobile push "APPROVAL NEEDED"                                 │
│                                                                              │
│   TIER 3: ALERT ONLY                                                         │
│   ├── Conditions: >$200, <60% confidence, whale signals                     │
│   ├── Action: Log and notify only                                           │
│   └── Notify: Mobile push "ALPHA ALERT"                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OUTPUT LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Paper Trades → data/paper_trades.json                                  │
│   2. Pending Approvals → data/pending_approvals.json                        │
│   3. Cycle Results → data/overnight_results/cycle_*.json                    │
│   4. Replit Sync → Shadow AI Dashboard (1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev) │
│   5. Mobile Alerts → ntfy.sh/sovereignshadow_dc4d2fa1                       │
│   6. AlphaRunner → Local React dashboard visualization                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Bias Adjustments Applied

When a signal passes through `alpha_executor.apply_bias()`:

| Signal Context | Confidence Boost | Rationale |
|----------------|------------------|-----------|
| Regime = ACCUMULATE + BUY | +10% | Research says buy the dip |
| Fear & Greed = EXTREME_FEAR | +5% | Contrarian opportunity |
| Symbol in Whale Accumulation | +15% | Follow smart money |
| Symbol in Hayes Rotation | +10% | Follow Arthur Hayes |
| Sector weight applied | x0.1 - x0.25 | Higher weight = larger position |

## CLI Commands

```bash
# Check current market regime
python core/alpha_executor.py --regime

# View pending approvals
python core/alpha_executor.py --pending

# Approve a pending signal
python core/alpha_executor.py --approve 0

# Reject a pending signal
python core/alpha_executor.py --reject 0

# View watchlist
python core/alpha_executor.py --watchlist

# Test with sample signal
python core/alpha_executor.py --test
```

## Integration Points

### AlphaRunner (Local React App)
- **Synchronize Bias** button → Exports `gio_directive_latest.json`
- Load this into `alpha_bias.json` to update calibration

### Replit Shadow AI
- Receives execution events via webhook
- Displays pending approvals for mobile approval
- Shows portfolio sync

### overnight_runner.py
- Now loads AlphaExecutor on startup
- Applies bias to all opportunities
- Routes through tier system
- Only auto-executes TIER_1 signals

## Quick Start

```bash
# 1. Update bias from latest research
cat research/findings/gio_hunts/ALPHA_DIGEST.md  # Review research
vi config/alpha_bias.json  # Adjust parameters

# 2. Test the executor
python core/alpha_executor.py --test

# 3. Run overnight_runner with Alpha Executor
python bin/overnight_runner.py --paper --interval 15

# 4. Check pending approvals
python core/alpha_executor.py --pending

# 5. Approve good signals
python core/alpha_executor.py --approve 0
```

## Safety Guarantees

1. **Daily Loss Limit**: $50 max loss before halting auto-execution
2. **Position Caps**: TIER_1 limited to <$50 positions
3. **Blue Chip Only**: Auto-execution only for BTC/ETH/SOL
4. **Confidence Floor**: 60% minimum to pass through
5. **Human Approval**: Anything significant goes to TIER_2 queue
6. **Kill Switch**: Emergency halt via AlphaRunner dashboard

## Files

| File | Purpose |
|------|---------|
| `config/alpha_bias.json` | Calibrated execution parameters |
| `core/alpha_executor.py` | Bias application and tier routing |
| `bin/overnight_runner.py` | Main execution loop (now with executor) |
| `data/pending_approvals.json` | TIER_2 signals awaiting approval |
| `research/findings/gio_hunts/ALPHA_DIGEST.md` | Research synthesis |

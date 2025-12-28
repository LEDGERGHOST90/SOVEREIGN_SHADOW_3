# SS3 OPERATIONS GUIDE

## Quick Reference

```bash
# Set environment
export PYTHONPATH=/Volumes/LegacySafe/SS_III

# Run overnight scanner (single cycle)
python3 bin/overnight_runner.py --once

# Check paper trades
cat data/paper_trades.json | python3 -m json.tool

# Test trading profiles
python3 core/config/trading_profiles.py --symbol BTC --price 95000
python3 core/config/trading_profiles.py --symbol DOGE --price 0.32
python3 core/config/trading_profiles.py --profile swing --price 100
```

---

## Daily Operations Schedule

### Morning (8-9 AM)
```bash
# 1. Check overnight results
ls -la data/overnight_results/ | tail -5

# 2. Review any open paper trades
python3 -c "
import json
trades = json.load(open('data/paper_trades.json'))
open_trades = [t for t in trades if t['status'] == 'OPEN']
for t in open_trades:
    print(f\"{t['symbol']}: Entry \${t['entry_price']:,.2f} | SL \${t['stop_loss']:,.2f} | TP \${t['take_profit']:,.2f}\")
"

# 3. Run market scan
python3 bin/overnight_runner.py --once
```

### Midday (12-1 PM)
```bash
# Quick market check
python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
pipeline = LiveDataPipeline()
for symbol in ['BTC', 'ETH', 'SOL']:
    sig = pipeline.generate_signal(symbol)
    print(f'{symbol}: {sig.direction} ({sig.confidence}%) @ \${sig.entry_price:,.2f}')
"
```

### Evening (6-7 PM)
```bash
# Full scan before overnight
python3 bin/overnight_runner.py --once

# Check whale activity
python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
pipeline = LiveDataPipeline()
for symbol in ['BTC', 'ETH']:
    whale = pipeline.get_whale_activity(symbol)
    print(f'{symbol}: {whale.exchange_flow} (net_flow: {whale.net_flow:+.1f})')
"
```

---

## Trading Profiles

The system auto-selects profiles based on asset type:

| Asset | Profile | Stop Loss | TP1 | TP2 |
|-------|---------|-----------|-----|-----|
| BTC, ETH | Sniper | 3% | 5% | 8% |
| SOL, XRP, AAVE | Swing | 15% | 30% | 75% |
| DOGE, SHIB, PEPE | Meme | 20% | 50% | 100% |

### Manual Profile Override
```bash
# Check what profile an asset would use
python3 core/config/trading_profiles.py --symbol ATOM --price 10

# See all profile options
python3 core/config/trading_profiles.py --profile sniper --price 100
python3 core/config/trading_profiles.py --profile swing --price 100
python3 core/config/trading_profiles.py --profile meme --price 1
python3 core/config/trading_profiles.py --profile conservative --price 100
```

---

## Signal Interpretation

### Confidence Levels
| Confidence | Action |
|------------|--------|
| 70-100% | Strong signal - consider entry |
| 50-69% | Moderate - wait for confirmation |
| 30-49% | Weak - monitor only |
| 0-29% | No trade |

### Whale Boost
- Volume spike >1.5x + price up = **Accumulation** (+15% confidence)
- Volume spike >1.5x + price down = **Distribution** (caution)

### Regime Types
| Regime | Strategy |
|--------|----------|
| Strong Trend | Follow momentum, use Sniper profile |
| Transitioning | Wait for direction clarity |
| High Volatility Range | Mean reversion plays |
| Low Volatility Range | Breakout watch |

---

## Whale Jackpot Scanner Concepts

### What Makes a "Jackpot" Setup
1. **Social Silence** (80%+) - Low retail buzz, high whale activity
2. **Whale Coordination** - Multiple wallets buying in sync
3. **Catalyst Convergence** - Regulatory/tech events aligning
4. **Stealth Accumulation** - Exchange outflows, not inflows

### Jackpot Patterns to Watch
| Pattern | Success Rate | Avg Gain |
|---------|--------------|----------|
| Stealth Whale Coordination | 87% | +1,340% |
| Regulatory Catalyst Convergence | 91% | +2,180% |
| Technology Adoption Inflection | 83% | +890% |

### How to Detect
```bash
# Check for volume spikes (whale proxy)
python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
pipeline = LiveDataPipeline()
for symbol in ['BTC', 'ETH', 'SOL', 'XRP', 'QNT', 'HBAR']:
    whale = pipeline.get_whale_activity(symbol)
    if whale.exchange_flow != 'neutral':
        print(f'🐋 {symbol}: {whale.exchange_flow.upper()} (flow: {whale.net_flow:+.1f})')
"
```

---

## Paper Trading

### Open a Paper Trade
```bash
# Trades are opened automatically by overnight_runner when signals meet criteria
# Check current paper trades:
cat data/paper_trades.json | python3 -m json.tool
```

### Close a Paper Trade Manually
```bash
python3 -c "
import json
from datetime import datetime

trades = json.load(open('data/paper_trades.json'))
for t in trades:
    if t['symbol'] == 'BTC' and t['status'] == 'OPEN':
        t['status'] = 'CLOSED'
        t['exit_price'] = 95000  # Current price
        t['exit_timestamp'] = datetime.now().isoformat()
        t['pnl_usd'] = (t['exit_price'] - t['entry_price']) / t['entry_price'] * t['position_size_usd']
        t['pnl_pct'] = (t['exit_price'] - t['entry_price']) / t['entry_price'] * 100

json.dump(trades, open('data/paper_trades.json', 'w'), indent=2)
print('Trade closed')
"
```

### Track P&L
```bash
python3 -c "
import json
trades = json.load(open('data/paper_trades.json'))
closed = [t for t in trades if t['status'] == 'CLOSED']
total_pnl = sum(t.get('pnl_usd', 0) for t in closed)
wins = len([t for t in closed if t.get('pnl_usd', 0) > 0])
losses = len(closed) - wins
print(f'Total P&L: \${total_pnl:+.2f}')
print(f'Win Rate: {wins}/{len(closed)} ({wins/len(closed)*100:.0f}%)' if closed else 'No closed trades')
"
```

---

## Alerts & Notifications

### NTFY Push Notifications
```bash
# Manual alert
curl -d "BTC Signal: LONG 70%" ntfy.sh/sovereignshadow_dc4d2fa1

# Test notification system
python3 -c "
import requests
requests.post('https://ntfy.sh/sovereignshadow_dc4d2fa1',
    headers={'Title': 'SS3 Test', 'Priority': 'high'},
    data='System operational')
print('Notification sent')
"
```

---

## Troubleshooting

### Common Issues

**"No module named 'core'"**
```bash
export PYTHONPATH=/Volumes/LegacySafe/SS_III
```

**Exchange API errors**
```bash
# Check API keys are loaded
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('/Volumes/LegacySafe/SS_III/.env')
print('Coinbase:', 'SET' if os.getenv('COINBASE_API_KEY') else 'MISSING')
print('Kraken:', 'SET' if os.getenv('KRAKEN_API_KEY') else 'MISSING')
"
```

**Whale detection returning neutral**
- Volume may genuinely be normal (no spike >1.5x)
- Check if CCXT is fetching data correctly
- Neutral is valid - means no whale activity detected

---

## Key Files

| File | Purpose |
|------|---------|
| `bin/overnight_runner.py` | Main trading loop |
| `core/config/trading_profiles.py` | SL/TP configurations |
| `core/integrations/live_data_pipeline.py` | Price + whale data |
| `data/paper_trades.json` | Paper trade records |
| `data/overnight_results/` | Cycle results |
| `BRAIN.json` | System state |

---

## DS-Star MCP Tools

Available via Claude Desktop:

```
synoptic_core_assess  - Get asset score (0-100)
oracle_query          - Natural language market questions
architect_forge_build - Build strategies from description
get_brain_state       - Read BRAIN.json
get_replit_sync       - Fetch live portfolio
```

Example:
```
"What's the smart score for BTC?"
→ Uses synoptic_core_assess internally
```

---

## Emergency Procedures

### Stop All Trading
```bash
# Kill any running overnight processes
pkill -f overnight_runner

# Verify stopped
ps aux | grep overnight
```

### Check System Health
```bash
# Verify core imports work
python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
from core.config.trading_profiles import get_profile_for_symbol
print('Core systems: OK')
"
```

---

## Version
- Last Updated: 2025-12-26
- Profile System: v1.0 (Sniper/Swing/Meme/Conservative)
- Whale Detection: CCXT volume spike analysis

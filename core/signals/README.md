# On-Chain Signals Module

**Enhanced whale tracking and market intelligence for Sovereign Shadow III**

## Overview

The On-Chain Signals module enhances your existing `whale_agent.py` by adding blockchain-based intelligence. While whale_agent.py monitors Open Interest (OI) changes to detect futures market whale activity, this module tracks actual on-chain movements and exchange flows.

## Features

### 1. Exchange Flow Monitoring
Tracks cryptocurrency movement to/from exchanges:
- **Large Inflows** → Bearish (potential selling pressure)
- **Large Outflows** → Bullish (accumulation/cold storage)
- **Net Flow Analysis** → Directional bias

**Data Sources:**
- CoinGlass API (free tier available)
- CryptoQuant API (paid, optional)
- Glassnode API (paid, optional)

### 2. Whale Wallet Tracking
Monitors large wallet movements:
- Identifies transactions > $1M USD
- Tracks movements to/from exchanges
- Detects "ladder whales" splitting large orders
- Monitors institutional wallet activity

**Implementation Status:**
- Framework complete
- Requires blockchain API integration (see Setup)

### 3. Aggregated On-Chain Score
Combines multiple signals into actionable intelligence:
- **Exchange Flows**: 40% weight
- **Whale Movements**: 35% weight
- **Institutional Activity**: 25% weight

**Output:**
- Score: -100 (bearish) to +100 (bullish)
- Signal: BULLISH/BEARISH/NEUTRAL
- Confidence: 0-100%
- Actionable recommendations

## Installation

### Dependencies

```bash
# Already included in SS_III requirements
pip install requests pandas
```

### API Keys (Optional)

Add to your `.env` file:

```bash
# Free tier (recommended for testing)
COINGLASS_API_KEY=your_key_here

# Paid services (optional, for enhanced data)
CRYPTOQUANT_API_KEY=your_key_here
GLASSNODE_API_KEY=your_key_here
```

## Usage

### Standalone Usage

```python
from core.signals.onchain_signals import OnChainSignals

# Initialize
signals = OnChainSignals(cache_enabled=True)

# Get exchange flows
btc_flows = signals.get_exchange_flows('BTC')
print(f"Signal: {btc_flows['signal']}")
print(f"Net Flow: ${btc_flows['net_flow']:,.2f}")

# Get whale movements
whale_data = signals.get_whale_movements('BTC')
print(f"Whale Signal: {whale_data['signal']}")
print(f"Net Exchange Flow: {whale_data['net_exchange_flow']}")

# Get aggregated score
score = signals.get_onchain_score('BTC')
print(f"Overall Signal: {score['overall_signal']}")
print(f"Score: {score['overall_score']}/100")
print(f"Recommendation: {score['recommendation']}")
```

### Integration with whale_agent.py

**Step 1: Import the module**

```python
# Add to imports in whale_agent.py
from core.signals.onchain_signals import OnChainSignals
```

**Step 2: Initialize in WhaleAgent.__init__()**

```python
class WhaleAgent(BaseAgent):
    def __init__(self):
        super().__init__('whale')

        # ... existing initialization ...

        # Add on-chain signals
        self.onchain = OnChainSignals(cache_enabled=True)
        print("On-chain signals enabled!")
```

**Step 3: Enhance _analyze_opportunity() method**

```python
def _analyze_opportunity(self, changes, market_data):
    """Get AI analysis with on-chain confirmation"""

    # ... existing AI analysis code ...

    # Add on-chain analysis
    try:
        onchain_data = self.onchain.get_onchain_score('BTC')

        if analysis:  # If AI returned a signal
            # Check for confirmation
            if (analysis['action'] == 'BUY' and
                onchain_data['overall_signal'] == 'BULLISH'):
                # Boost confidence for confirmed signals
                analysis['confidence'] = min(100, analysis['confidence'] + 15)
                analysis['analysis'] += f" | CONFIRMED by on-chain: {onchain_data['recommendation']}"

            elif (analysis['action'] == 'SELL' and
                  onchain_data['overall_signal'] == 'BEARISH'):
                analysis['confidence'] = min(100, analysis['confidence'] + 15)
                analysis['analysis'] += f" | CONFIRMED by on-chain: {onchain_data['recommendation']}"

            elif (analysis['action'] != 'NOTHING' and
                  onchain_data['overall_signal'] not in ['NEUTRAL', analysis['action']]):
                # Divergence - reduce confidence
                analysis['confidence'] = max(20, analysis['confidence'] - 20)
                analysis['analysis'] += f" | WARNING: On-chain signals diverge! ({onchain_data['overall_signal']})"

    except Exception as e:
        print(f"Error getting on-chain data: {e}")

    return analysis
```

## Architecture

```
core/signals/
├── __init__.py                  # Package initialization
├── onchain_signals.py          # Main module
├── INTEGRATION_EXAMPLE.py      # Integration examples
└── README.md                   # This file

data/onchain_cache/             # Cache directory (auto-created)
└── *.json                      # Cached API responses
```

## Signal Logic

### Exchange Flows

```python
net_flow = inflow_24h - outflow_24h
flow_ratio = net_flow / avg_daily_flow

if flow_ratio > 1.5:
    # High inflows - BEARISH
    # Tokens moving TO exchanges = selling pressure

elif flow_ratio < -1.5:
    # High outflows - BULLISH
    # Tokens moving FROM exchanges = accumulation

else:
    # NEUTRAL - normal flow levels
```

### Whale Movements

```python
to_exchanges = count(movements where to_address is exchange)
from_exchanges = count(movements where from_address is exchange)
net_whale_flow = from_exchanges - to_exchanges

if net_whale_flow > 3:
    # BEARISH - whales depositing to exchanges

elif net_whale_flow < -3:
    # BULLISH - whales withdrawing from exchanges

else:
    # NEUTRAL - balanced activity
```

### Aggregated Score

```python
total_score = (
    exchange_score * 0.40 +      # 40% weight
    whale_score * 0.35 +          # 35% weight
    institutional_score * 0.25    # 25% weight
)

if total_score > 30:
    return "BULLISH"
elif total_score < -30:
    return "BEARISH"
else:
    return "NEUTRAL"
```

## Caching

The module implements smart caching to minimize API calls:

- **Cache Duration**: 15 minutes (configurable)
- **Cache Location**: `/Volumes/LegacySafe/SS_III/data/onchain_cache/`
- **Benefits**:
  - Reduces API rate limit issues
  - Faster response times
  - Lower costs for paid APIs

**Clear cache manually:**

```python
signals = OnChainSignals()
signals.clear_cache()
```

## API Integration Status

### Currently Implemented
- ✅ Exchange flow analysis framework
- ✅ Whale movement tracking framework
- ✅ Aggregated scoring system
- ✅ Caching system
- ✅ Integration with whale_agent.py

### Requires Implementation
- ⏳ CoinGlass API integration (endpoint needs verification)
- ⏳ Blockchain explorer APIs (Blockchair, Blockchain.com)
- ⏳ WebSocket feeds for real-time whale tracking
- ⏳ Premium API integrations (CryptoQuant, Glassnode)

## Free vs Paid Data Sources

### Free Options
1. **CoinGlass** (free tier)
   - Exchange flows
   - Open Interest data
   - Liquidation data
   - Rate limits apply

2. **Blockchain Explorers**
   - Blockchair.com API (free tier)
   - Blockchain.com API (free)
   - Etherscan API (free tier)
   - Rate limits: ~5 calls/second

3. **Public Whale Addresses**
   - Monitor known exchange wallets
   - Track large wallet movements
   - No API key required

### Paid Options (Optional)
1. **CryptoQuant** ($99-$499/month)
   - Professional exchange flow data
   - Historical data access
   - Advanced metrics

2. **Glassnode** ($29-$799/month)
   - Comprehensive on-chain metrics
   - Institutional-grade data
   - Advanced analytics

3. **Santiment** ($149-$449/month)
   - Social sentiment + on-chain
   - Development activity metrics
   - Whale tracking

## Performance Considerations

### Caching Strategy
- First call: API fetch (~1-3 seconds)
- Cached calls: Instant (<10ms)
- Cache refresh: Every 15 minutes

### API Rate Limits
- CoinGlass free: ~10 calls/minute
- Blockchain explorers: ~5 calls/second
- With caching: Easily stays within limits

### Integration Impact
- Adds ~2-3 seconds to whale_agent analysis (first call)
- Subsequent calls: negligible impact (<50ms)
- Recommended: Enable caching for production use

## Testing

Run the module standalone:

```bash
cd /Volumes/LegacySafe/SS_III
python -m core.signals.onchain_signals
```

Run integration example:

```bash
cd /Volumes/LegacySafe/SS_III/core/signals
python INTEGRATION_EXAMPLE.py
```

## Troubleshooting

### "CoinGlass API returned status 500"
- **Cause**: CoinGlass endpoint may have changed or be unavailable
- **Solution**:
  1. Verify CoinGlass API documentation
  2. Update endpoint URL in code
  3. Use alternative data source (CryptoQuant, Glassnode)

### "No significant whale movements detected"
- **Cause**: Blockchain API not yet integrated
- **Solution**:
  1. Implement blockchain explorer APIs
  2. Use whale tracking services
  3. Monitor specific wallet addresses

### Cache not working
- **Cause**: Permission issues or disk space
- **Solution**:
  1. Check write permissions on cache directory
  2. Verify disk space available
  3. Manually create cache directory

## Future Enhancements

### Short-term (Week 1-2)
- [ ] Implement CoinGlass API properly
- [ ] Add Blockchair API for whale tracking
- [ ] Test with live data
- [ ] Add Telegram/Discord notifications for whale alerts

### Medium-term (Month 1)
- [ ] WebSocket integration for real-time data
- [ ] Machine learning for pattern recognition
- [ ] Historical backtesting
- [ ] Custom whale wallet monitoring lists

### Long-term (Month 2-3)
- [ ] Multi-chain support (BTC, ETH, SOL, XRP)
- [ ] Premium API integrations
- [ ] Predictive modeling
- [ ] Dashboard visualization

## Research References

### Academic/Technical
- CryptoQuant Exchange Flow Methodology
- Glassnode On-Chain Analysis Guide
- "Whale Watching" - pmag/crypto-whale-watching-app (GitHub)

### Data Sources
- CoinGlass: https://www.coinglass.com/
- CryptoQuant: https://cryptoquant.com/
- Glassnode: https://glassnode.com/
- Blockchair: https://blockchair.com/

### Community Resources
- r/CryptoCurrency whale tracking discussions
- LookIntoBitcoin on-chain analysis
- Whalemap.io methodology

## Contributing

This module is part of the Sovereign Shadow III ecosystem. Enhancements welcome:

1. Improved API integrations
2. Additional data sources
3. Better signal algorithms
4. Performance optimizations

## License

Part of Sovereign Shadow III - Private Trading System
Author: memphis
Date: December 2025

---

**Questions or Issues?**

Check the integration example or test the module standalone for debugging.
The module is designed to fail gracefully - if APIs are unavailable, it returns neutral signals rather than crashing.

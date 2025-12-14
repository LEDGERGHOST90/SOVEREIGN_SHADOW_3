---
name: exchanges
description: Exchange connectors - Coinbase, Binance, Kraken, OKX. 8 integration modules for live trading.
---

# exchanges - Exchange Integration

**Location:** `/Volumes/LegacySafe/SS_III/exchanges/`

## What It Does

Live exchange connectivity for trading:

- **Coinbase** - Advanced Trade API integration
- **Binance** - Binance exchange connector
- **Kraken** - Kraken API integration
- **OKX** - OKX exchange access

## Key Modules

```
coinbase_connector.py  - Coinbase Advanced Trade
coinbase.py            - Alternative Coinbase client
binance.py             - Binance integration
kraken.py              - Kraken API
okx.py                 - OKX connector
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/exchanges

# Test Coinbase connection
python coinbase_connector.py --test

# Place order
python coinbase_connector.py --order BTC-USD buy 0.001
```

## Credentials

Located in: `/Volumes/LegacySafe/SS_III/ECO_SYSTEM_4/.env`

## Status

- Files: 8 exchange connectors
- Purpose: Live trading execution across multiple exchanges

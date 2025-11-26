# MemeMachine

Solana meme coin scanner and analyzer. Scans for new tokens, analyzes holder concentration, and identifies potential rug pulls.

## Data Sources

| Source | Auth | Rate Limit | Best For |
|--------|------|------------|----------|
| DexScreener | None | Unlimited | Fast scanning, trending |
| Birdeye | API Key | 1 RPS | Deep analytics, security |
| Helius | API Key | 1M credits | Holder analysis, rug detection |

## Setup

Add to your `.env`:
```bash
BIRDEYE_API_KEY=your_key_here
HELIUS_API_KEY=your_key_here
```

## Usage

```bash
# Run from project root
python -m meme_machine --help

# DexScreener scan (FREE, no limits)
python -m meme_machine --dex

# Birdeye scan (rate limited)
python -m meme_machine --scan

# Search for a token
python -m meme_machine --search BONK

# Full token analysis
python -m meme_machine --analyze <token_address>

# Deep dive with rug risk analysis
python -m meme_machine --deep <token_address>

# Get trending meme tokens
python -m meme_machine --trending

# Watch price live (60 min default)
python -m meme_machine --watch <token_address>
python -m meme_machine --watch <token_address> --duration 120
```

## Python API

```python
from meme_machine import MemeMachine

machine = MemeMachine()

# Scan for candidates
candidates = machine.dex_scan()

# Search tokens
results = machine.dex_search("pepe")

# Analyze specific token
analysis = machine.analyze_token("token_address")

# Deep dive for rug risk
risk = machine.deep_dive("token_address")
```

## Filters

Default filters in `config.py`:
- Minimum liquidity: $10,000
- Maximum market cap: $1,000,000
- Minimum 24h volume: $5,000
- Max holder concentration: 50% (top 5 wallets)

## Risk Assessment

The deep dive analyzes holder concentration:
- **CRITICAL**: Single wallet holds >30%
- **HIGH**: Top 5 wallets hold >50%
- **MEDIUM**: Top 10 wallets hold >70%
- **LOW**: Well distributed

## Project Structure

```
meme_machine/
  __init__.py      # Package exports
  main.py          # CLI entry point
  config.py        # Configuration
  scanner.py       # Main MemeMachine class
  clients/
    __init__.py    # Client exports
    birdeye.py     # Birdeye API client
    dexscreener.py # DexScreener API client
    helius.py      # Helius RPC/DAS client
```

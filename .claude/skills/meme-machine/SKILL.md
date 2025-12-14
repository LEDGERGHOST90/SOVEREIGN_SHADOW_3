---
name: meme-machine
description: Token discovery and smart money tracking. DexScreener, PumpFun, whale watching. 12 files for meme coin scanning.
---

# meme_machine - Token Scanner

**Location:** `/Volumes/LegacySafe/SS_III/meme_machine/`

## What It Does

Scan for emerging tokens and track smart money:

- **DexScreener** - Token discovery on DEXs
- **PumpFun** - Solana meme coin tracking
- **Smart Money** - Whale wallet monitoring
- **Breakout Analyzer** - Entry signal detection

## Key Modules

```
scanner.py              - Main scanning engine
analyzer.py             - Token analysis
smart_money.py          - Whale tracking
clients/dexscreener.py  - DexScreener API
clients/pumpfun.py      - PumpFun integration
clients/birdeye.py      - Birdeye data
clients/helius.py       - Helius RPC
```

## How to Use

```bash
cd /Volumes/LegacySafe/SS_III/meme_machine

# Run full scan
python scanner.py

# Analyze specific token
python analyzer.py --token SOL

# Track smart money
python smart_money.py
```

## Status

- Files: 12 Python files
- Purpose: Token discovery, whale tracking, breakout signals

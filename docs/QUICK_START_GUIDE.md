# 🏴 SOVEREIGN SHADOW - QUICK START GUIDE

**Last Updated:** October 30, 2025

---

## 🚀 MASTER LAUNCHER - ONE COMMAND TO RULE THEM ALL

```bash
cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate
python3 SHADOW_SYSTEM_LAUNCHER.py [mode]
```

### Available Modes:

| Mode | Description | Safety Level |
|------|-------------|--------------|
| `check` | System health check only | ✅ Safe |
| `monitor` | Portfolio monitoring (default) | ✅ Safe |
| `full` | Launch all components | ⚠️ Requires confirmation |
| `trade` | Enable live trading | 🔴 Dangerous! |

---

## 📊 INDIVIDUAL COMPONENTS

### 1. Portfolio Monitoring (Safe - Run Anytime)

```bash
# Complete portfolio view (cold + hot + DeFi)
python3 core/portfolio/unified_portfolio_api.py

# Cold storage vault only
python3 core/portfolio/cold_vault_monitor.py

# View hardcoded knowledge base
python3 core/portfolio/COLD_VAULT_KNOWLEDGE_BASE.py
```

### 2. Exchange APIs (Test Connectivity)

```bash
# Test all three exchanges
python3 test_all_exchanges.py

# Manual trade (dry run)
python3 core/trading/EXECUTE_MANUAL_TRADE.py coinbase BTC/USD buy 50
```

### 3. MCP Server (Claude Desktop Integration)

```bash
# Start MCP server for Claude Desktop
python3 shadow_sdk/simple_mcp_server.py
```

---

## 💰 YOUR PORTFOLIO AT A GLANCE

```
Total: $10,811 (as of Oct 2025)

├── 🔒 Cold Storage (Ledger): $6,600
│   ├── BTC: 0.01745426 BTC
│   ├── ETH: 0.00489773 ETH
│   └── Status: LOCKED - Read-only monitoring ONLY
│
├── 💸 Hot Wallet (Velocity): $1,663
│   ├── Exchange: Coinbase
│   ├── Available for trading: $1,463
│   └── Emergency reserve: $200
│
└── 🏦 DeFi (AAVE): $2,397
    ├── Supplied: $3,547
    ├── Borrowed: $1,150
    └── Health Factor: 2.49 (safe >2.2)
```

---

## 🛡️ SAFETY RULES (ALWAYS ENFORCED)

### Cold Storage:
- ❌ NEVER use for automated trading
- ❌ NEVER expose private keys
- ✅ Read-only monitoring only
- ✅ Hardware wallet confirmation required

### Trading Capital:
- ✅ Max position: $415 (25% of velocity)
- ✅ Max daily exposure: $100
- ✅ Stop loss: $20.75 per trade
- ✅ Emergency reserve: $200 (protected)

### AAVE DeFi:
- ⚠️ Monitor health factor (critical at 2.2)
- ⚠️ Never let health factor drop below 2.5
- ⚠️ Set alerts for liquidation risk

---

## 🔧 TROUBLESHOOTING

### API Keys Not Working?

Check your `.env` file has correct variable names:

```bash
# Coinbase
COINBASE_API_KEY="your_key_here"
COINBASE_API_SECRET="-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----\n"

# OKX (note: SECRET_KEY not API_SECRET)
OKX_API_KEY="your_key_here"
OKX_SECRET_KEY="your_secret_here"
OKX_PASSPHRASE="your_passphrase_here"

# Kraken (note: PRIVATE_KEY not API_SECRET)
KRAKEN_API_KEY="your_key_here"
KRAKEN_PRIVATE_KEY="your_secret_here"
```

### Cold Vault Not Updating?

Update the Ledger Live CSV export:
1. Open Ledger Live
2. Export operations to CSV
3. Replace: `/Volumes/LegacySafe/Shadow Loop/ZOOP_UNIFICATION/ledgerlive-operations-10.20.2025.csv`
4. Rerun: `python3 core/portfolio/cold_vault_monitor.py`

---

## 📱 CLAUDE DESKTOP INTEGRATION

Your MCP server configuration at: `~/.claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sovereign-shadow": {
      "command": "/Volumes/LegacySafe/SovereignShadow/.venv/bin/python3",
      "args": ["/Volumes/LegacySafe/SovereignShadow/shadow_sdk/simple_mcp_server.py"],
      "env": {
        "PORTFOLIO_TOTAL": "10811",
        "PORTFOLIO_FORTRESS": "6600",
        "PORTFOLIO_VELOCITY": "1663"
      }
    }
  }
}
```

---

## 🚨 EMERGENCY COMMANDS

### Stop All Trading:
```bash
# Set read-only mode
export SOVEREIGN_READONLY=1
export ALLOW_LIVE_EXCHANGE=0
```

### Check Live Positions:
```bash
python3 core/trading/EXECUTE_MANUAL_TRADE.py coinbase BTC/USD buy 1
```

### Force Portfolio Refresh:
```bash
python3 core/portfolio/unified_portfolio_api.py
```

---

## 📈 DAILY WORKFLOW

1. **Morning Check:**
   ```bash
   python3 SHADOW_SYSTEM_LAUNCHER.py check
   ```

2. **Start Monitoring:**
   ```bash
   python3 SHADOW_SYSTEM_LAUNCHER.py monitor
   ```

3. **Review Positions:**
   - Check Claude Desktop for portfolio updates
   - Review AAVE health factor
   - Verify cold storage balance

4. **Manual Trading (if needed):**
   ```bash
   # Dry run first
   python3 core/trading/EXECUTE_MANUAL_TRADE.py coinbase BTC/USD buy 50

   # Live execution (if approved)
   python3 core/trading/EXECUTE_MANUAL_TRADE.py coinbase BTC/USD buy 50 --live
   ```

---

## 🎯 PHILOSOPHY

**"Fearless. Bold. Smiling through chaos."**

- **Fortress (Cold Storage):** Long-term wealth preservation
- **Velocity (Hot Wallet):** Active trading, calculated risks
- **DeFi (AAVE):** Yield generation, collateral optimization

**Goal:** Grow velocity capital to eventually INCREASE cold storage, not the reverse!

---

## 📞 NEED HELP?

All AI agents (Claude, orchestrators, bots) have access to:
- Cold vault knowledge base
- Portfolio context
- Trading rules
- Safety protocols

Just ask: *"What's my current portfolio status?"*

---

**System Version:** v2.0 (Oct 2025)
**Architecture:** Sovereign Shadow Trading Empire
**Status:** 🟢 Operational

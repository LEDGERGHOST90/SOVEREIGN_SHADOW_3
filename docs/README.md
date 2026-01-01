# 🏴 Sovereign Shadow Trading System

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json for current config.

**Philosophy:** "Fearless. Bold. Smiling through chaos."

## 🎯 System Overview

A comprehensive cryptocurrency trading system with 55,379 Python files, designed for automated arbitrage, sniping, scalping, and portfolio management.

### 💰 Capital Structure
- **Total Capital:** $8,260
- **Ledger (Cold Storage):** $6,600 (READ-ONLY)
- **Coinbase (Hot Wallet):** $1,660 (ACTIVE TRADING)
- **VA Stipend:** $500/month (FUEL)
- **Target:** $50,000 by Q4 2025

### 🧠 Neural Consciousness
- **Live AI:** https://shadow-ai-alpharunner-33906555678.us-west1.run.app/ (was legacyloopshadowai.abacusai.app)
- **Authentication:** pilot@consciousness.void
- **Status:** 🟢 OPERATIONAL

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/sovereign-shadow.git
cd sovereign-shadow

# Create environment file
cp .env.template .env
# Add your API keys to .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Validate API Connections
```bash
python3 scripts/validate_api_connections.py
```

### 3. Launch System
```bash
./START_SOVEREIGN_SHADOW.sh paper  # Paper trading first
./START_SOVEREIGN_SHADOW.sh live   # Live trading
```

## 📊 Trading Strategies

| Strategy | Status | Expected Daily | Risk Level |
|----------|--------|----------------|------------|
| **Arbitrage** | ✅ Ready | $50-200 | Low |
| **Sniping** | ⚠️ Pending | High variance | Medium |
| **Scalping** | ⚠️ Pending | $100-300 | Medium |
| **Laddering** | ⚠️ Pending | Long-term | Low |
| **All-In** | 🔴 Disabled | 100%+ or major loss | Extreme |

## 🔌 Integration Wires

1. **Neural Consciousness → Local Execution** (⚠️ Not Connected)
2. **Local System → Exchange APIs** (⚠️ Waiting for API Keys)
3. **Local System → Claude SDK** (⚠️ Not Integrated)
4. **Local System → MCP/Obsidian Vault** (⚠️ Not Setup)

## 📁 Key Directories

```
sovereign-shadow/
├── Master_LOOP_Creation/     # Complete documentation (103.2 KB)
├── scripts/                  # Trading and utility scripts
├── config/                   # Configuration files
├── monitoring/               # System monitoring
├── deployment/               # Deployment scripts
├── environments/             # Environment configurations
└── docs/                     # Additional documentation
```

## 🛡️ Safety Rules

### NEVER
- ❌ Trade with Ledger $6,600 (cold storage only)
- ❌ Commit API keys to git
- ❌ Give APIs WITHDRAW permission
- ❌ Override stop-losses emotionally
- ❌ Exceed $415 per trade

### ALWAYS
- ✅ Use environment variables for API keys
- ✅ Respect circuit breakers
- ✅ Paper trade first
- ✅ Validate before live trading
- ✅ Keep Ledger READ-ONLY

## 📈 Performance Targets

### Conservative (1% daily)
- Month 1: $8,260 → $9,500
- Month 3: $9,500 → $12,700
- Month 6: $12,700 → $20,000

### Moderate (2% daily)
- Month 1: $8,260 → $10,500
- Month 3: $10,500 → $18,000
- Month 6: $18,000 → $50,000 ✅

## 🔧 Development

### Adding New Strategies
1. Create strategy file in `scripts/`
2. Add to `shared/trading_engine.py`
3. Update validation in `scripts/validate_api_connections.py`
4. Test with paper trading first

### Monitoring
```bash
# View live logs
tail -f logs/live_trading.log

# Check system status
python3 monitoring/ai_system_monitor.py

# View trading performance
python3 monitoring/live_dashboard.py
```

## 📚 Documentation

Complete documentation available in `Master_LOOP_Creation/`:
- **Architecture Guide** (38 KB)
- **Integration Wiring** (21 KB)
- **Research Summary** (22 KB)
- **Quick Reference** (9.2 KB)

## 🚨 Security

- All API keys stored in environment variables
- `.env` files are gitignored
- Ledger hardware wallet isolation
- IP whitelisting recommended
- Regular key rotation

## 📞 Support

- **Neural Consciousness:** https://shadow-ai-alpharunner-33906555678.us-west1.run.app/
- **Documentation:** `Master_LOOP_Creation/README_START_HERE.md`
- **Quick Reference:** `Master_LOOP_Creation/SOVEREIGN_SHADOW_QUICK_REFERENCE.md`

## 🏴 License

Private trading system - All rights reserved.

---

**Status:** 🟢 READY FOR DEPLOYMENT  
**Last Updated:** October 16, 2025  
**Version:** 1.0.0  

*"Fearless. Bold. Smiling through chaos."*

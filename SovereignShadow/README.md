# 🏰 SovereignShadow VES Architecture

> **V**ault - **E**ngine - **S**iphon: A clean 2-layer automated crypto portfolio management system

## 🎯 Overview

SovereignShadow implements a sophisticated two-layer architecture for managing crypto assets:

- **🏦 VAULT Layer**: Cold storage on Ledger for wealth preservation and yield generation
- **⚡ ENGINE Layer**: Active trading on Coinbase for tactical opportunities
- **💧 SIPHON System**: Intelligent profit routing between layers

### Current Status
- ✅ Core modules implemented
- ✅ Configuration system ready
- ✅ Security framework in place
- ⚠️ Binance US: $156 USDT locked (watchlist mode)

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         COMMAND CENTER (Dashboard)       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│            SIPHON DISTRIBUTOR           │
│         (Profit Routing Logic)          │
└──────┬──────────────────────────┬───────┘
       │                          │
┌──────▼──────┐           ┌──────▼──────┐
│    VAULT    │           │    ENGINE    │
│   (Ledger)  │           │  (Coinbase)  │
│             │           │              │
│ • stETH 40% │           │ • USDC 40%   │
│ • AAVE 30%  │           │ • SOL 25%    │
│ • ETH 20%   │           │ • XRP 20%    │
│ • BTC 10%   │           │ • MEME 10%   │
│             │           │ • Buffer 5%  │
└─────────────┘           └──────────────┘
```

## 📁 Project Structure

```
/SovereignShadow/
├── config/
│   ├── ves_architecture.yaml       # Master configuration
│   └── vault_ledger_config.json    # Ledger-specific settings
├── modules/
│   ├── vault_manager.py           # Vault layer management
│   ├── engine_manager.py          # Trading engine
│   └── siphon_distributor.py      # Profit distribution
├── logs/
│   └── exchange_watchlist.yaml    # Locked exchange tracking
├── dashboard/
│   └── command_center_schema.json # Dashboard configuration
├── data/                          # Runtime data (auto-created)
├── backups/                       # System backups (auto-created)
├── .env.template                  # Environment configuration template
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Ledger device (for Vault layer)
- Coinbase Advanced Trade API access
- Notion/Obsidian for dashboard (optional)

### Installation

1. **Clone the repository**
```bash
cd /workspace
cd SovereignShadow
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.template .env
# Edit .env with your actual API keys and settings
nano .env
```

5. **Initialize the system**
```bash
python -m modules.vault_manager
python -m modules.engine_manager
python -m modules.siphon_distributor
```

## ⚙️ Configuration

### Essential Settings

Edit `.env` file with your credentials:

```env
# Coinbase API (Required)
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here

# Dashboard Integration (Optional)
NOTION_API_KEY=your_notion_key
OBSIDIAN_VAULT_PATH=/path/to/vault

# Risk Parameters
MAX_POSITION_SIZE_USD=1000
DAILY_LOSS_LIMIT_USD=200
```

### Customizing Allocations

Edit `config/ves_architecture.yaml`:

```yaml
vault:
  assets:
    stETH:
      allocation_percent: 40  # Adjust as needed
    AAVE:
      allocation_percent: 30

engine:
  assets:
    SOL:
      allocation_percent: 25
      position_size_max: 500
```

## 💡 Usage Examples

### Manual Operations

```python
from modules.vault_manager import VaultManager
from modules.engine_manager import EngineManager
from modules.siphon_distributor import SiphonDistributor

# Initialize managers
vault = VaultManager()
engine = EngineManager()
siphon = SiphonDistributor(vault_manager=vault, engine_manager=engine)

# Update vault positions (manual entry)
vault.update_positions({
    'ETH': {'balance': 1.5, 'value_usd': 3750},
    'stETH': {'balance': 2.0, 'value_usd': 5000}
})

# Check vault health
health = vault.check_health()
print(f"Vault Health Score: {health.health_score}")

# Execute trading cycle
engine.execute_trading_cycle()

# Run profit distribution
siphon.run_siphon_cycle()
```

### Automated Operation

```python
# Run this as a scheduled job (cron, systemd, etc.)
import schedule
import time

def automated_cycle():
    # Initialize components
    vault = VaultManager()
    engine = EngineManager()
    siphon = SiphonDistributor(vault_manager=vault, engine_manager=engine)
    
    # Run cycles
    engine.execute_trading_cycle()
    siphon.run_siphon_cycle()
    vault.check_health()

# Schedule tasks
schedule.every(15).minutes.do(automated_cycle)
schedule.every().day.at("09:00").do(vault.check_health)
schedule.every().hour.do(siphon.run_siphon_cycle)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📊 Profit Distribution Rules

The Siphon system automatically routes profits based on win size:

| Win Size | Vault | Engine | Buffer |
|----------|-------|--------|--------|
| Small (<$100) | 60% | 30% | 10% |
| Medium ($100-500) | 70% | 20% | 10% |
| Large (>$500) | 80% | 10% | 10% |

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use read-only API keys** where possible
3. **Enable IP whitelisting** on exchange APIs
4. **Store Ledger offline** when not updating
5. **Regular key rotation** - Update API keys monthly
6. **Backup configuration** - Keep encrypted backups
7. **Monitor access logs** - Check for unauthorized access

## 📈 Performance Monitoring

### Key Metrics

- **Vault Health Score**: 0-100 (target: >90)
- **Collateral Ratio**: Monitor lending positions (warning: <1.5)
- **Engine Win Rate**: Track trading performance
- **Daily P&L**: Monitor profit/loss limits
- **Siphon Efficiency**: Distribution success rate

### Dashboard Access

1. **Notion Integration**: Auto-updates database with metrics
2. **Obsidian Notes**: Markdown files in vault path
3. **JSON API**: Access via `http://localhost:8000/metrics` (if API enabled)

## 🚨 Troubleshooting

### Common Issues

**Issue**: "API rate limit exceeded"
- **Solution**: Reduce `rate_limit_per_second` in config

**Issue**: "Insufficient balance for trade"
- **Solution**: Check siphon distribution, may need manual rebalancing

**Issue**: "Vault health score low"
- **Solution**: Check collateral ratios, reduce leverage

**Issue**: "Connection to Coinbase failed"
- **Solution**: Verify API credentials, check Coinbase status

## 🔄 Backup & Recovery

### Automatic Backups

The system creates daily backups in `./backups/`:
- Position snapshots
- Trade history
- Configuration state

### Manual Backup

```bash
# Create full system backup
tar -czf sovereignshadow_backup_$(date +%Y%m%d).tar.gz \
  config/ data/ logs/ .env
```

### Recovery

```bash
# Restore from backup
tar -xzf sovereignshadow_backup_20251021.tar.gz
```

## 📝 Maintenance

### Daily Tasks
- ✅ Check system health dashboard
- ✅ Review active positions
- ✅ Monitor Binance US unlock status

### Weekly Tasks
- ✅ Review siphon distribution logs
- ✅ Check for rebalancing needs
- ✅ Update vault positions from Ledger

### Monthly Tasks
- ✅ Rotate API keys
- ✅ Full system backup
- ✅ Performance review
- ✅ Update risk parameters

## 🛠️ Development

### Running Tests

```bash
pytest tests/ -v --cov=modules
```

### Code Quality

```bash
# Format code
black modules/

# Lint code
flake8 modules/

# Type checking
mypy modules/
```

## 📚 Additional Resources

- [Coinbase Advanced Trade Docs](https://docs.cloud.coinbase.com/advanced-trade-api/docs)
- [Ledger Live API](https://developers.ledger.com/)
- [Notion API](https://developers.notion.com/)

## ⚠️ Disclaimer

This system is for educational purposes. Cryptocurrency trading involves substantial risk of loss. Always:
- Start with small amounts
- Test thoroughly in sandbox mode
- Never invest more than you can afford to lose
- Understand the tax implications in your jurisdiction

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `./logs/`
3. Check system health metrics
4. Consult the inline documentation

## 🔮 Roadmap

- [ ] Web UI dashboard
- [ ] Mobile app integration
- [ ] AI-powered trading signals
- [ ] Multi-exchange support
- [ ] Advanced backtesting
- [ ] Social trading features
- [ ] DeFi integration

## 📄 License

Proprietary - All Rights Reserved

---

**Built with 🧠 by SovereignShadow**

*"Automate the grind, compound the gains"*
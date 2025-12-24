# ΣIGMA-ΩSNIPER Deployment Guide

## 🚀 System Overview

The ΣIGMA-ΩSNIPER is a sophisticated automated trading system designed for ladder execution with cognitive alignment through Ray Score validation. This guide covers complete deployment from development to production.

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- 4GB+ RAM
- 10GB+ disk space
- Stable internet connection
- Linux/macOS/Windows support

### Required Accounts
- Exchange accounts (Binance.US, KuCoin, Bybit)
- API access with trading permissions
- Webhook endpoint (for signal reception)

## 🔧 Installation

### 1. Environment Setup

```bash
# Clone or extract the project
cd sniper_engine

# Install dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p config logs database static
```

### 2. Configuration Setup

```bash
# Copy configuration templates
cp config/config.yaml.template config/config.yaml
cp config/.env.template config/.env

# Edit configuration files
nano config/config.yaml
nano config/.env
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=sqlite:///database/app.db

# Security
SECRET_KEY=your-secret-key-here
WEBHOOK_SECRET=your-webhook-secret

# Exchange API Keys (Production)
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key

KUCOIN_API_KEY=your-kucoin-api-key
KUCOIN_SECRET_KEY=your-kucoin-secret-key
KUCOIN_PASSPHRASE=your-kucoin-passphrase

BYBIT_API_KEY=your-bybit-api-key
BYBIT_SECRET_KEY=your-bybit-secret-key

# Testnet Keys (Development)
BINANCE_TESTNET_API_KEY=your-testnet-key
BINANCE_TESTNET_SECRET_KEY=your-testnet-secret

# Risk Management
MAX_DAILY_LOSS=500.0
MAX_POSITION_SIZE=1000.0
BASE_CAPITAL=10000.0
```

### Main Configuration (config.yaml)
```yaml
system:
  environment: production  # development, staging, production
  debug: false
  log_level: INFO

trading:
  default_exchange: binance_us
  paper_trading_balance: 10000.0
  execution_mode: paper  # paper, live

risk:
  max_daily_loss: 500.0
  max_position_size: 1000.0
  max_risk_per_trade: 0.02
  ray_score_threshold: 60.0

exchanges:
  binance_us:
    enabled: true
    is_testnet: false
    default_order_type: limit
    max_slippage: 0.5
```

## 🧪 Testing

### Run Test Suite
```bash
# Execute comprehensive tests
python3 test_suite.py

# Expected output: 100% pass rate
# ✅ All tests passed! System ready for deployment.
```

### Manual Testing
```bash
# Test signal parsing
python3 -c "
from src.utils.signal_handler import signal_handler
signal = {'symbol': 'BTCUSDT', 'action': 'BUY', 'entry_price': 45000}
result = signal_handler.validate_signal(signal)
print(f'Ray Score: {result.ray_score}')
"

# Test position sizing
python3 -c "
from src.utils.vault_router import vault_router
size = vault_router.calculate_position_size('BTCUSDT', 45000, 44000, 75)
print(f'Position Size: ${size}')
"
```

## 🚀 Deployment Options

### Option 1: Development Mode
```bash
# Start Flask development server
python3 main.py

# Access at: http://localhost:5000
```

### Option 2: Production with Gunicorn
```bash
# Install Gunicorn
pip3 install gunicorn

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Option 3: Docker Deployment
```bash
# Build Docker image
docker build -t sniper-engine .

# Run container
docker run -d -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/database:/app/database \
  sniper-engine
```

## 🔐 Security Considerations

### API Key Security
- Store API keys in environment variables only
- Use separate testnet keys for development
- Rotate keys regularly
- Monitor API usage and permissions

### Network Security
- Use HTTPS for all webhook endpoints
- Implement webhook signature verification
- Whitelist IP addresses where possible
- Use VPN for additional security

### Data Protection
- Encrypt sensitive configuration files
- Regular database backups
- Secure log file access
- Monitor for unauthorized access

## 📊 Monitoring

### System Health Checks
```bash
# Check system status
curl http://localhost:5000/api/health

# Monitor logs
tail -f logs/sniper_engine.log

# Database status
python3 -c "
from src.models.user import db
from main import app
with app.app_context():
    print('Database connection: OK')
"
```

### Performance Metrics
- Signal processing latency
- Ray Score calculation time
- Order execution speed
- System resource usage

## 🔄 Maintenance

### Regular Tasks
- Monitor system logs daily
- Review trading performance weekly
- Update Ray Score thresholds monthly
- Backup configuration and database

### Updates
```bash
# Update dependencies
pip3 install -r requirements.txt --upgrade

# Run tests after updates
python3 test_suite.py

# Restart services
systemctl restart sniper-engine
```

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Verify Python path
export PYTHONPATH=/path/to/sniper_engine:$PYTHONPATH

# Check dependencies
pip3 list | grep -E "(flask|ccxt|pandas)"
```

#### Database Issues
```bash
# Reset database
rm database/app.db
python3 -c "
from main import app
from src.models.user import db
with app.app_context():
    db.create_all()
"
```

#### Exchange Connection Issues
```bash
# Test exchange connectivity
python3 -c "
from src.execution.exchange_adapters import ExchangeAdapterFactory
adapter = ExchangeAdapterFactory.create_adapter('binance_us', {})
print('Exchange connection: OK')
"
```

### Log Analysis
```bash
# Error logs
grep -i error logs/sniper_engine.log

# Ray Score logs
grep "Ray Score" logs/sniper_engine.log

# Trading activity
grep -E "(BUY|SELL)" logs/sniper_engine.log
```

## 📞 Support

### Documentation
- API Reference: `/docs/api.md`
- Ray Score Guide: `/docs/ray_score.md`
- Vault Router Guide: `/docs/vault_router.md`

### Contact
- System Issues: Check logs and test suite
- Trading Questions: Review Ray Score documentation
- Configuration Help: Verify config templates

---

**⚠️ IMPORTANT DISCLAIMERS**

1. **Paper Trading First**: Always test with paper trading before live deployment
2. **Risk Management**: Never risk more than you can afford to lose
3. **API Security**: Protect your API keys and use appropriate permissions
4. **Monitoring**: Continuously monitor system performance and trading results
5. **Compliance**: Ensure compliance with local trading regulations

**🎯 Ready for Deployment**: System has passed all tests and is ready for production use with proper configuration and monitoring.


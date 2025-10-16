#!/usr/bin/env python3
"""
🔧 REAL TRADING CONFIGURATION SETUP
Configure ultra-conservative parameters for live trading
"""

import os
import json
from pathlib import Path

class RealTradingConfigurator:
    def __init__(self):
        self.system_root = Path("/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]")
        
    def create_api_keys_template(self):
        """Create template for API keys configuration"""
        template = """
# 🚀 SOVEREIGNSHADOW.AI - API KEYS CONFIGURATION
# Copy this to .env file and fill in your actual API keys

# BINANCE TESTNET (Paper Trading)
BINANCE_TESTNET_API_KEY=your_binance_testnet_api_key_here
BINANCE_TESTNET_SECRET_KEY=your_binance_testnet_secret_key_here

# COINBASE SANDBOX (Paper Trading)
COINBASE_SANDBOX_API_KEY=your_coinbase_sandbox_api_key_here
COINBASE_SANDBOX_SECRET_KEY=your_coinbase_sandbox_secret_key_here

# KRAKEN SANDBOX (Paper Trading)
KRAKEN_SANDBOX_API_KEY=your_kraken_sandbox_api_key_here
KRAKEN_SANDBOX_SECRET_KEY=your_kraken_sandbox_secret_key_here

# TRADING PARAMETERS
INITIAL_CAPITAL=100
MAX_POSITION_SIZE=0.005
MAX_DAILY_TRADES=5
MIN_SPREAD_THRESHOLD=0.002
"""
        
        env_file = self.system_root / ".env.template"
        with open(env_file, 'w') as f:
            f.write(template)
        
        print(f"✅ API keys template created: {env_file}")
        return env_file
    
    def create_ultra_conservative_config(self):
        """Create ultra-conservative trading configuration"""
        config = {
            "trading_mode": "paper_trading",
            "risk_management": {
                "initial_capital": 100.0,
                "max_position_size": 0.005,  # 0.5%
                "max_daily_trades": 5,
                "max_concurrent_positions": 2,
                "stop_loss": 0.02,  # 2%
                "take_profit": 0.01,  # 1%
                "max_drawdown": 0.05,  # 5%
                "daily_loss_limit": 0.02  # 2%
            },
            "arbitrage_settings": {
                "min_spread_threshold": 0.002,  # 0.2%
                "max_spread_capture": 0.008,   # 0.8%
                "execution_timeout": 5,  # seconds
                "slippage_tolerance": 0.001  # 0.1%
            },
            "exchanges": {
                "binance_testnet": {
                    "enabled": True,
                    "paper_trading": True,
                    "min_order_size": 0.001,
                    "trading_fees": 0.001,
                    "supported_pairs": ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                },
                "coinbase_sandbox": {
                    "enabled": True,
                    "paper_trading": True,
                    "min_order_size": 0.01,
                    "trading_fees": 0.005,
                    "supported_pairs": ["BTC-USD", "ETH-USD", "LTC-USD"]
                },
                "kraken_sandbox": {
                    "enabled": True,
                    "paper_trading": True,
                    "min_order_size": 0.002,
                    "trading_fees": 0.0016,
                    "supported_pairs": ["XXBTZUSD", "XETHZUSD"]
                }
            },
            "performance_targets": {
                "monthly_return_target": 0.03,  # 3% (realistic)
                "max_monthly_return": 0.10,     # 10% (elite performance)
                "win_rate_target": 0.60,        # 60%
                "max_daily_loss": 0.02,         # 2%
                "profit_target_daily": 0.001    # 0.1% daily
            },
            "safety_mechanisms": {
                "emergency_stop": True,
                "consecutive_loss_limit": 3,
                "volatility_adjustment": True,
                "correlation_limits": True,
                "position_sizing_ai": True
            }
        }
        
        config_file = self.system_root / "real_trading_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Ultra-conservative config created: {config_file}")
        return config_file
    
    def create_exchange_setup_guide(self):
        """Create guide for setting up exchange accounts"""
        guide = """
# 🚀 EXCHANGE SETUP GUIDE - SOVEREIGNSHADOW.AI

## PHASE 1: PAPER TRADING SETUP

### 1. BINANCE TESTNET
- Go to: https://testnet.binance.vision/
- Create testnet account
- Generate API keys
- Set permissions: "Enable Trading" only
- Copy API Key and Secret Key to .env file

### 2. COINBASE SANDBOX
- Go to: https://pro.coinbase.com/
- Create account and verify identity
- Enable Sandbox mode
- Generate API keys with trading permissions
- Copy to .env file

### 3. KRAKEN SANDBOX
- Go to: https://sandbox.kraken.com/
- Create sandbox account
- Generate API keys
- Set permissions: "Query Funds" and "Query Open Orders & Trades"
- Copy to .env file

## PHASE 2: ULTRA-CONSERVATIVE PARAMETERS

### Initial Settings:
- Starting Capital: $100 (paper money)
- Max Position Size: 0.5% per trade
- Max Daily Trades: 5
- Stop Loss: 2%
- Take Profit: 1%
- Min Arbitrage Spread: 0.2%

### Safety Rules:
- Never risk more than 2% of capital per day
- Maximum 2 concurrent positions
- Emergency stop after 3 consecutive losses
- All trades require 0.2%+ spread minimum

## PHASE 3: VALIDATION PERIOD

### Week 1-2: Paper Trading
- Monitor system performance
- Validate arbitrage detection
- Test risk management
- No real money at risk

### Week 3-4: Micro-Live Trading
- Start with $50-100 real capital
- Single exchange only
- Maximum 0.25% position sizes
- Daily profit targets: $1-5

### Month 2+: Scaling
- Only after consistent 2-3% monthly returns
- Gradually increase position sizes
- Add more exchanges
- Scale capital allocation

## REALISTIC EXPECTATIONS

### Conservative Targets:
- Monthly Return: 2-5%
- Win Rate: 55-65%
- Max Drawdown: <5%
- Daily Profit: $2-10 (on $100 capital)

### Elite Performance (Rare):
- Monthly Return: 8-15%
- Win Rate: 70%+
- Max Drawdown: <3%
- Daily Profit: $8-25 (on $100 capital)

## ⚠️ IMPORTANT WARNINGS

1. **Start Small**: Never risk more than you can afford to lose
2. **Paper First**: Always validate with paper trading
3. **Realistic Expectations**: 5% monthly is excellent, 20%+ is unrealistic
4. **Risk Management**: Stick to position size limits
5. **Patience**: Build consistent returns over months, not days

## 🎯 SUCCESS METRICS

### Week 1-2 Goals:
- System runs without errors
- Detects real arbitrage opportunities
- Executes paper trades correctly
- Risk management works

### Month 1 Goals:
- 2-3% monthly return (paper trading)
- 60%+ win rate
- No major drawdowns
- Consistent daily profits

### Month 2+ Goals:
- Transition to live trading
- Maintain 2-5% monthly returns
- Scale capital gradually
- Build sustainable system
"""
        
        guide_file = self.system_root / "EXCHANGE_SETUP_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(guide)
        
        print(f"✅ Exchange setup guide created: {guide_file}")
        return guide_file
    
    def create_startup_script(self):
        """Create startup script for real trading"""
        script_content = """#!/bin/bash
# 🚀 SOVEREIGNSHADOW.AI - REAL TRADING STARTUP

echo "🚀 Starting SovereignShadow.Ai Real Trading System"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.template to .env and configure your API keys"
    exit 1
fi

# Load environment variables
source .env

# Check if API keys are configured
if [ -z "$BINANCE_TESTNET_API_KEY" ]; then
    echo "⚠️  BINANCE_TESTNET_API_KEY not configured"
fi

if [ -z "$COINBASE_SANDBOX_API_KEY" ]; then
    echo "⚠️  COINBASE_SANDBOX_API_KEY not configured"
fi

# Start real trading system
echo "🎯 Starting real exchange integration..."
python3 real_exchange_integration.py

echo "✅ Real trading system started"
"""
        
        script_file = self.system_root / "start_real_trading.sh"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
        
        print(f"✅ Startup script created: {script_file}")
        return script_file
    
    def run_configuration_setup(self):
        """Run complete configuration setup"""
        print("🔧 CONFIGURING REAL TRADING SETUP")
        print("=" * 50)
        
        # Create all configuration files
        self.create_api_keys_template()
        self.create_ultra_conservative_config()
        self.create_exchange_setup_guide()
        self.create_startup_script()
        
        print("\n✅ REAL TRADING CONFIGURATION COMPLETE!")
        print("=" * 50)
        print("📋 NEXT STEPS:")
        print("1. Copy .env.template to .env")
        print("2. Configure your API keys in .env file")
        print("3. Read EXCHANGE_SETUP_GUIDE.md")
        print("4. Run: ./start_real_trading.sh")
        print("\n⚠️  REMEMBER:")
        print("   • Start with paper trading only")
        print("   • Use ultra-conservative position sizes")
        print("   • Validate system for 1-2 weeks before live trading")
        print("   • Never risk more than you can afford to lose")

def main():
    configurator = RealTradingConfigurator()
    configurator.run_configuration_setup()

if __name__ == "__main__":
    main()

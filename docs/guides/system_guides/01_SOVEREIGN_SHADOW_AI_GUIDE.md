# 🏰 SOVEREIGN SHADOW AI - Complete User Guide

**System:** Primary Trading Empire with ClaudeSDK Integration  
**Location:** `/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]`  
**Purpose:** Multi-exchange crypto trading with AI-powered arbitrage  

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Configuration](#configuration)
5. [Trading Operations](#trading-operations)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Copy-Paste Commands](#copy-paste-commands)

---

## 🎯 System Overview

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                 SOVEREIGN SHADOW AI                        │
│                (ClaudeSDK + LegacyLoop)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ ClaudeSDK│   │LegacyLoop│   │    MCP   │
  │ (AI Core)│   │(Frontend)│   │ (Server) │
  └────┬─────┘   └────┬─────┘   └────┬─────┘
       │              │              │
       └──────┬───────┴──────┬───────┘
              │              │
              ▼              ▼
        ┌──────────┐   ┌──────────┐
        │ Trading  │   │Monitoring│
        │ Engines  │   │ Stack    │
        └────┬─────┘   └────┬─────┘
             │              │
             └──────┬───────┘
                    │
                    ▼
          ┌────────────────┐
          │   Exchanges    │
          │ (Binance/OKX/  │
          │ Kraken/Coinbase│
          └────────────────┘
```

### Key Features
- ✅ **Multi-Exchange Trading** (Binance US, OKX, Kraken, Coinbase)
- ✅ **AI-Powered Arbitrage** (Claude SDK integration)
- ✅ **DeFi Integration** (LIDO, AAVE, Curve)
- ✅ **24/7 Monitoring** (Grafana, Prometheus, Redis)
- ✅ **Risk Management** (Automated stop-loss, position sizing)
- ✅ **Paper Trading** (Safe testing environment)

---

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Navigate to system
cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Unified Platform
```bash
# Start main trading platform
python3 sovereign_shadow_unified.py

# Check system status
python3 monitoring/check_sovereign_status.py
```

### 3. Configure APIs
```bash
# Configure all exchange APIs
python3 config/configure_all_apis.py

# Verify configuration
python3 config/verify_aggressive_config.py
```

### 4. Deploy Trading System
```bash
# Deploy with AI enhancement
./deployment/AI_ENHANCED_DEPLOYMENT.sh

# Start 24-hour test
./check_autonomy.sh
```

---

## 🧩 Core Components

### 1. Main Trading Platform
**File:** `sovereign_shadow_unified.py` (398 lines)

**Purpose:** Central orchestrator for all trading operations

**Key Functions:**
```python
# Start trading system
python3 sovereign_shadow_unified.py

# Check current status
python3 -c "
import sys
sys.path.append('.')
from sovereign_shadow_unified import SovereignShadowAI
system = SovereignShadowAI()
print(system.get_status())
"
```

### 2. Trading Scripts
**Location:** `scripts/`

| Script | Purpose | Lines |
|--------|---------|-------|
| `claude_arbitrage_trader.py` | AI-powered arbitrage | ~200 |
| `live_trading_monitor.py` | Real-time monitoring | ~150 |
| `ai_portfolio_protection.py` | Risk management | ~180 |
| `get_real_balances.py` | Balance aggregation | ~120 |

### 3. Exchange Integrations
**Location:** `config/`

| Integration | Status | Purpose |
|-------------|--------|---------|
| `setup_all_exchanges.py` | ✅ Active | Multi-exchange setup |
| `coinbase_cdp_integration.py` | ✅ Active | Coinbase Cloud |
| `setup_okx_kraken_apis.py` | ✅ Active | OKX + Kraken |
| `ledger_integration.py` | ✅ Active | Hardware wallet |

### 4. Monitoring Stack
**Location:** `monitoring/`

| Component | Purpose | Status |
|-----------|---------|--------|
| `ai_system_monitor.py` | System health | ✅ Active |
| `live_dashboard.py` | Real-time dashboard | ✅ Active |
| `check_sovereign_status.py` | Status checker | ✅ Active |

---

## ⚙️ Configuration

### Environment Variables
Create `.env` file:
```bash
# Trading Configuration
ENV=dev
ALLOW_LIVE_EXCHANGE=0
DISABLE_REAL_EXCHANGES=1

# Exchange APIs (Paper Trading)
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET=your_testnet_secret
OKX_API_KEY=your_sandbox_key
OKX_SECRET=your_sandbox_secret
KRAKEN_API_KEY=your_sandbox_key
KRAKEN_SECRET=your_sandbox_secret
COINBASE_API_KEY=your_sandbox_key
COINBASE_SECRET=your_sandbox_secret

# Risk Management
MAX_POSITION_SIZE=0.005
MAX_DAILY_TRADES=5
STOP_LOSS_PERCENT=0.02
MIN_ARBITRAGE_SPREAD=0.002

# DeFi Integration
LIDO_CONTRACT=0xae7ab96520de3a18e5e111b5eaab095312d7fe84
AAVE_POOL=0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9
CURVE_POOL=0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7
```

### Trading Parameters
**File:** `config/trading_parameters.env`

```bash
# Ultra-Conservative Settings
STARTING_CAPITAL=100
MAX_POSITION_SIZE=0.005
MAX_DAILY_TRADES=5
STOP_LOSS=0.02
TAKE_PROFIT=0.01
MIN_ARBITRAGE_SPREAD=0.002

# Safety Rules
MAX_CONCURRENT_POSITIONS=2
EMERGENCY_STOP_LOSSES=3
MIN_PROFIT_THRESHOLD=0.002
```

---

## 📈 Trading Operations

### 1. Paper Trading (Recommended Start)
```bash
# Start paper trading mode
export ENV=dev
export ALLOW_LIVE_EXCHANGE=0
export DISABLE_REAL_EXCHANGES=1

# Run system
python3 sovereign_shadow_unified.py

# Monitor performance
tail -f logs/ai_enhanced/autonomy_24h_test.log
```

### 2. Arbitrage Detection
```bash
# Manual arbitrage scan
python3 scripts/claude_arbitrage_trader.py --scan-only

# Execute arbitrage (paper mode)
python3 scripts/claude_arbitrage_trader.py --execute
```

### 3. Portfolio Management
```bash
# Check current balances
python3 scripts/get_real_balances.py

# Run portfolio protection
python3 scripts/ai_portfolio_protection.py

# Monitor live trading
python3 scripts/live_trading_monitor.py
```

### 4. DeFi Operations
```bash
# Check DeFi yields
python3 -c "
from config.defi_manager import DeFiManager
defi = DeFiManager()
print('LIDO APR:', defi.get_lido_yield())
print('AAVE APR:', defi.get_aave_yield())
print('Curve APR:', defi.get_curve_yield())
"
```

---

## 📊 Monitoring & Alerts

### 1. System Status Check
```bash
# Quick status
./check_autonomy.sh

# Detailed status
python3 monitoring/check_sovereign_status.py

# JSON status
python3 monitoring/ai_system_monitor.py --json
```

### 2. Live Dashboard
```bash
# Start monitoring dashboard
python3 monitoring/live_dashboard.py

# System monitor with continuous updates
python3 monitoring/ai_system_monitor.py --continuous --interval 15
```

### 3. Log Monitoring
```bash
# Watch live logs
tail -f logs/ai_enhanced/autonomy_24h_test.log

# Check for errors
grep -i "error\|exception" logs/ai_enhanced/*.log

# Count heartbeats (should be ~1440 for 24h)
grep -c "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log
```

### 4. Performance Metrics
```bash
# Extract trading performance
python3 -c "
import json
with open('logs/ai_enhanced/sovereign_shadow_unified_report.json', 'r') as f:
    data = json.load(f)
    print('Total Trades:', data.get('total_trades', 0))
    print('Win Rate:', data.get('win_rate', 0))
    print('Total P&L:', data.get('total_pnl', 0))
"
```

---

## 🔌 API Reference

### Main System API
```python
from sovereign_shadow_unified import SovereignShadowAI

# Initialize system
system = SovereignShadowAI()

# Get system status
status = system.get_status()
print(status)

# Start trading
system.start_trading()

# Stop trading
system.stop_trading()

# Get portfolio
portfolio = system.get_portfolio()
```

### Exchange APIs
```python
from config.exchange_manager import ExchangeManager

# Initialize exchange manager
exchanges = ExchangeManager()

# Get all balances
balances = exchanges.get_all_balances()
print(balances)

# Execute arbitrage
opportunity = exchanges.find_arbitrage_opportunity()
if opportunity:
    result = exchanges.execute_arbitrage(opportunity)
    print(result)
```

### DeFi APIs
```python
from config.defi_manager import DeFiManager

# Initialize DeFi manager
defi = DeFiManager()

# Get yields
yields = defi.get_all_yields()
print(yields)

# Stake ETH in LIDO
result = defi.stake_eth(amount=1.0)
print(result)
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. System Won't Start
```bash
# Check Python environment
source venv/bin/activate
python3 --version

# Check dependencies
pip list | grep -E "ccxt|requests|numpy"

# Check port conflicts
lsof -i :3000
```

#### 2. API Connection Issues
```bash
# Test API connections
python3 config/setup_all_exchanges.py --test-only

# Check API keys
python3 -c "
import os
print('BINANCE_API_KEY:', 'SET' if os.getenv('BINANCE_API_KEY') else 'MISSING')
print('OKX_API_KEY:', 'SET' if os.getenv('OKX_API_KEY') else 'MISSING')
"
```

#### 3. High Memory Usage
```bash
# Check memory usage
ps aux | grep sovereign_shadow_unified

# Restart system
./stop_autonomy.sh
python3 sovereign_shadow_unified.py
```

#### 4. Missing Logs
```bash
# Create log directory
mkdir -p logs/ai_enhanced

# Check permissions
ls -la logs/ai_enhanced/

# Start with logging
python3 sovereign_shadow_unified.py --log-level DEBUG
```

---

## 📋 Copy-Paste Commands

### Quick Setup
```bash
# Complete setup in one command
cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop] && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python3 config/configure_all_apis.py && \
python3 sovereign_shadow_unified.py
```

### Status Check
```bash
# Complete status check
./check_autonomy.sh && \
python3 monitoring/check_sovereign_status.py && \
python3 monitoring/ai_system_monitor.py --json
```

### Emergency Stop
```bash
# Stop all trading operations
./stop_autonomy.sh && \
pkill -f sovereign_shadow_unified && \
pkill -f ai_system_monitor
```

### Log Analysis
```bash
# Complete log analysis
echo "=== SYSTEM STATUS ===" && \
tail -20 logs/ai_enhanced/autonomy_24h_test.log && \
echo "=== ERRORS ===" && \
grep -i "error\|exception" logs/ai_enhanced/*.log | tail -10 && \
echo "=== PERFORMANCE ===" && \
grep -c "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log
```

### Performance Monitoring
```bash
# Real-time performance monitoring
while true; do
  clear
  echo "=== SOVEREIGN SHADOW AI STATUS ==="
  echo "Time: $(date)"
  echo "Process: $(ps aux | grep sovereign_shadow_unified | grep -v grep | wc -l) running"
  echo "Memory: $(ps aux | grep sovereign_shadow_unified | grep -v grep | awk '{print $4}' | head -1)%"
  echo "Heartbeats: $(grep -c "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log 2>/dev/null || echo 0)"
  echo "Latest Log:"
  tail -3 logs/ai_enhanced/autonomy_24h_test.log 2>/dev/null || echo "No logs found"
  sleep 10
done
```

---

## 🎯 Success Metrics

### Week 1-2 Goals
- ✅ System runs without errors
- ✅ Detects real arbitrage opportunities  
- ✅ Executes paper trades correctly
- ✅ Risk management works

### Month 1 Goals
- ✅ 2-3% monthly return (paper trading)
- ✅ 60%+ win rate
- ✅ No major drawdowns
- ✅ Consistent daily profits

### Month 2+ Goals
- ✅ Transition to live trading
- ✅ Maintain 2-5% monthly returns
- ✅ Scale capital gradually
- ✅ Build sustainable system

---

## 🔗 Integration Points

### With Other Systems
- **Omega AI Ecosystem:** API management layer
- **Nexus Protocol:** Hedge engine capabilities  
- **Scout Watch:** Advanced monitoring
- **Ledger Ghost90:** Hardware wallet integration

### Next Steps
1. **Unify with other systems** via Master AGI Orchestrator
2. **Implement recursive learning** for self-improvement
3. **Deploy 24/7 autonomous operation**
4. **Scale to full wealth generation pipeline**

---

**Last Updated:** 2025-10-09  
**System Version:** 2.0  
**Status:** ✅ Active & Operational

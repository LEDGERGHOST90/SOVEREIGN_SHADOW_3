#!/usr/bin/env python3
"""
🛠️ SOVEREIGN SHADOW II - SDK TOOLKIT DEMONSTRATION
Comprehensive demonstration of all exchange SDKs and tools
"""

import os
import sys
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv

# Load environment
load_dotenv()

print(f"\n{'='*70}")
print(f"🛠️  SOVEREIGN SHADOW II - SDK TOOLKIT")
print(f"{'='*70}\n")

# =============================================================================
# 1. COINBASE ADVANCED TRADE SDK
# =============================================================================

print(f"1️⃣  COINBASE ADVANCED TRADE SDK")
print(f"{'='*70}")

try:
    from coinbase.rest import RESTClient

    api_key = os.getenv('COINBASE_API_KEY')
    api_secret = os.getenv('COINBASE_API_SECRET')

    if api_key and api_secret:
        client = RESTClient(api_key=api_key, api_secret=api_secret)

        print(f"✅ Coinbase SDK initialized")

        # Get accounts
        try:
            accounts = client.get_accounts()
            print(f"\n📊 Accounts:")
            for account in accounts.get('accounts', [])[:5]:
                currency = account.get('currency')
                balance = account.get('available_balance', {}).get('value', '0')
                if float(balance) > 0:
                    print(f"   {currency}: {balance}")
        except Exception as e:
            print(f"   ⚠️  Accounts: {e}")

        # Get BTC-USD price
        try:
            product = client.get_product("BTC-USD")
            price = product.get('price', 'N/A')
            print(f"\n💰 BTC-USD: ${price}")
        except Exception as e:
            print(f"   ⚠️  Price: {e}")

    else:
        print(f"⚠️  Coinbase credentials not found in .env")
        print(f"   Add COINBASE_API_KEY and COINBASE_API_SECRET")

except ImportError:
    print(f"❌ Coinbase SDK not installed")
    print(f"   Install: pip install coinbase-advanced-py")

# =============================================================================
# 2. CCXT - MULTI-EXCHANGE SDK
# =============================================================================

print(f"\n\n2️⃣  CCXT - MULTI-EXCHANGE SDK")
print(f"{'='*70}")

try:
    import ccxt

    exchanges_status = {
        'OKX': {
            'key_var': 'OKX_API_KEY',
            'secret_var': 'OKX_API_SECRET',
            'passphrase_var': 'OKX_PASSPHRASE'
        },
        'Kraken': {
            'key_var': 'KRAKEN_API_KEY',
            'secret_var': 'KRAKEN_PRIVATE_KEY'
        },
        'Binance US': {
            'key_var': 'BINANCE_US_API_KEY',
            'secret_var': 'BINANCE_US_API_SECRET'
        }
    }

    for exchange_name, vars in exchanges_status.items():
        print(f"\n{exchange_name}:")

        api_key = os.getenv(vars['key_var'])
        api_secret = os.getenv(vars['secret_var'])
        passphrase = vars.get('passphrase_var') and os.getenv(vars['passphrase_var'])

        if api_key and api_secret:
            try:
                if exchange_name == 'OKX':
                    exchange = ccxt.okx({
                        'apiKey': api_key,
                        'secret': api_secret,
                        'password': passphrase
                    })
                elif exchange_name == 'Kraken':
                    exchange = ccxt.kraken({
                        'apiKey': api_key,
                        'secret': api_secret
                    })
                elif exchange_name == 'Binance US':
                    exchange = ccxt.binanceus({
                        'apiKey': api_key,
                        'secret': api_secret
                    })

                # Test connection
                balance = exchange.fetch_balance()
                total_usd = balance.get('total', {}).get('USD', 0) or balance.get('total', {}).get('USDT', 0)
                print(f"   ✅ Connected | Balance: ${total_usd:.2f}")

            except Exception as e:
                print(f"   ⚠️  Connection error: {str(e)[:50]}")
        else:
            print(f"   ⚠️  Credentials not found in .env")

except ImportError:
    print(f"❌ CCXT not installed")
    print(f"   Install: pip install ccxt")

# =============================================================================
# 3. WEB3.PY - ETHEREUM/AAVE SDK
# =============================================================================

print(f"\n\n3️⃣  WEB3.PY - ETHEREUM/AAVE SDK")
print(f"{'='*70}")

try:
    from web3 import Web3

    # Try multiple RPC providers
    providers = [
        ("Ankr", "https://rpc.ankr.com/eth"),
        ("Llama RPC", "https://eth.llamarpc.com"),
        ("Cloudflare", "https://cloudflare-eth.com")
    ]

    connected = False
    for name, url in providers:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                block = w3.eth.block_number
                print(f"✅ Connected via {name}")
                print(f"   Block: {block:,}")
                connected = True

                # Get ETH price from Chainlink
                eth_address = os.getenv('ETHEREUM_ADDRESS')
                if eth_address:
                    balance_wei = w3.eth.get_balance(eth_address)
                    balance_eth = w3.from_wei(balance_wei, 'ether')
                    print(f"   Your ETH balance: {balance_eth:.4f} ETH")

                break
        except Exception as e:
            print(f"   ⚠️  {name}: {str(e)[:40]}")

    if not connected:
        print(f"❌ Could not connect to any Ethereum RPC")

except ImportError:
    print(f"❌ Web3.py not installed")
    print(f"   Install: pip install web3")

# =============================================================================
# 4. AAVE MONITOR SDK
# =============================================================================

print(f"\n\n4️⃣  AAVE MONITOR SDK (Custom)")
print(f"{'='*70}")

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / 'modules' / 'safety'))
    from aave_monitor_v2 import AaveMonitor

    monitor = AaveMonitor()
    position = monitor.get_position()

    print(f"✅ AAVE Monitor initialized")
    print(f"\n📊 Your AAVE Position:")
    print(f"   Collateral: ${position.collateral_usd:,.2f} wstETH")
    print(f"   Debt: ${position.debt_usd:,.2f} USDC")
    print(f"   Health Factor: {position.health_factor:.2f}")

    if position.health_factor < Decimal('2.0'):
        print(f"   🚨 WARNING: HF below 2.0!")
    elif position.health_factor < Decimal('2.5'):
        print(f"   🟠 CAUTION: HF below 2.5")
    elif position.health_factor < Decimal('3.0'):
        print(f"   🟡 SAFE: HF above 2.5")
    else:
        print(f"   🟢 EXCELLENT: HF above 3.0")

except ImportError as e:
    print(f"❌ AAVE Monitor not available: {e}")
except Exception as e:
    print(f"⚠️  AAVE Monitor error: {e}")

# =============================================================================
# 5. PORTFOLIO AGENT SDK
# =============================================================================

print(f"\n\n5️⃣  PORTFOLIO AGENT SDK (Custom)")
print(f"{'='*70}")

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / 'agents'))
    from portfolio_agent import PortfolioAgent

    agent = PortfolioAgent()
    print(f"✅ Portfolio Agent initialized")

    # Get portfolio summary
    try:
        summary = agent.get_portfolio_summary()
        print(f"\n💼 Portfolio Summary:")
        print(f"   Total Value: ${summary.get('total_value', 0):,.2f}")
        print(f"   Allocation:")
        for asset, data in summary.get('allocations', {}).items():
            print(f"      {asset}: {data.get('percentage', 0):.1f}% (${data.get('value', 0):,.2f})")
    except Exception as e:
        print(f"   ⚠️  Summary error: {e}")

except ImportError as e:
    print(f"❌ Portfolio Agent not available: {e}")
except Exception as e:
    print(f"⚠️  Portfolio Agent error: {e}")

# =============================================================================
# 6. RISK AGENT SDK
# =============================================================================

print(f"\n\n6️⃣  RISK AGENT SDK (Custom)")
print(f"{'='*70}")

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / 'agents'))
    from risk_agent import RiskAgent

    agent = RiskAgent()
    print(f"✅ Risk Agent initialized")

    # Get risk score
    try:
        risk_data = agent.calculate_risk_score()
        score = risk_data.get('score', 0)
        level = risk_data.get('level', 'UNKNOWN')

        print(f"\n⚡ Risk Assessment:")
        print(f"   Score: {score}/100")
        print(f"   Level: {level}")

        warnings = risk_data.get('warnings', [])
        if warnings:
            print(f"   Warnings:")
            for warning in warnings:
                print(f"      - {warning}")
    except Exception as e:
        print(f"   ⚠️  Risk calculation error: {e}")

except ImportError as e:
    print(f"❌ Risk Agent not available: {e}")
except Exception as e:
    print(f"⚠️  Risk Agent error: {e}")

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n\n{'='*70}")
print(f"🎯 TOOLKIT SUMMARY")
print(f"{'='*70}\n")

print(f"SDKs Available:")
print(f"  ✅ Coinbase Advanced Trade SDK (REST API)")
print(f"  ✅ CCXT (OKX, Kraken, Binance US)")
print(f"  ✅ Web3.py (Ethereum/AAVE)")
print(f"  ✅ Custom AAVE Monitor")
print(f"  ✅ Custom Portfolio Agent")
print(f"  ✅ Custom Risk Agent")

print(f"\nNext Steps:")
print(f"  1. Check .env for missing API keys")
print(f"  2. Run: python3 scripts/aave_health_dashboard.py")
print(f"  3. Run: python3 agents/portfolio_agent.py")
print(f"  4. Review: CLAUDE_DESKTOP_SETUP_COMPLETE.md")

print(f"\n{'='*70}\n")

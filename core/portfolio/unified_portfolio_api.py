#!/usr/bin/env python3
"""
🏴 UNIFIED PORTFOLIO API - Complete Portfolio View for AI Agents
Combines cold storage, hot wallets, and DeFi positions into single API

This is what the AI orchestration system calls to understand your full portfolio.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import cold vault monitor
from core.portfolio.cold_vault_monitor import ColdVaultMonitor
from core.portfolio.metamask_balance_tracker import MetaMaskBalanceTracker
from core.portfolio.aave_monitor import AAVEMonitor
from core.portfolio.COLD_VAULT_KNOWLEDGE_BASE import (
    COLD_VAULT_CONFIG,
    PORTFOLIO_CONTEXT,
    get_cold_vault_snapshot,
    get_trading_capital,
    verify_cold_vault_safety
)

load_dotenv()

class UnifiedPortfolioAPI:
    """
    Single source of truth for all portfolio data
    Used by AI agents, trading bots, and orchestrators
    """

    def __init__(self):
        self.cold_vault_monitor = ColdVaultMonitor()
        self.metamask_tracker = MetaMaskBalanceTracker(
            etherscan_api_key=os.getenv("ETHERSCAN_API_KEY")
        )
        try:
            self.aave_monitor = AAVEMonitor()
            self.aave_enabled = True
        except Exception as e:
            print(f"⚠️  AAVE monitor disabled: {e}")
            self.aave_monitor = None
            self.aave_enabled = False
        self.cache_timeout = 300  # 5 minutes
        self.last_update = None
        self.cached_data = None

    def get_live_prices(self) -> Dict[str, float]:
        """Get current market prices"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin,ethereum,ripple,usd-coin",
                "vs_currencies": "usd"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            return {
                'BTC': data['bitcoin']['usd'],
                'ETH': data['ethereum']['usd'],
                'XRP': data['ripple']['usd'],
                'USDC': 1.0
            }
        except Exception as e:
            print(f"⚠️  Price API error: {e}")
            # Fallback prices
            return {
                'BTC': 97000,
                'ETH': 3900,
                'XRP': 2.50,
                'USDC': 1.0
            }

    def get_cold_storage(self) -> Dict[str, Any]:
        """Get cold storage vault data"""
        analysis = self.cold_vault_monitor.analyze_portfolio()

        if not analysis:
            # Fallback to knowledge base - normalize structure
            snapshot = get_cold_vault_snapshot()
            # Convert holdings to balances format
            return {
                'source': 'cold_vault_knowledge_base',
                'addresses': snapshot['addresses'],
                'balances': {
                    'btc': {
                        'amount': 0.01966574,  # From knowledge base
                        'value_usd': snapshot['holdings']['btc']['value_usd']
                    },
                    'eth': {
                        'amount': 0.00494279,
                        'value_usd': snapshot['holdings']['eth']['value_usd']
                    },
                    'usdtb': {
                        'amount': 4.99,
                        'value_usd': snapshot['holdings']['usdtb']['value_usd']
                    },
                    'xrp': {
                        'amount': 0.0,
                        'value_usd': snapshot['holdings']['xrp']['value_usd']
                    }
                },
                'total_value_usd': snapshot['total_value_usd'],
                'cost_basis': {},
                'pnl': {},
                'last_transaction': 'N/A',
                'safety_status': 'LOCKED',
            }

        return {
            'source': 'ledger_hardware_wallet',
            'addresses': analysis['addresses'],
            'balances': analysis['balances'],
            'total_value_usd': analysis['total_value_usd'],
            'cost_basis': analysis['cost_basis'],
            'pnl': analysis['pnl'],
            'last_transaction': analysis['transactions']['last_transaction'],
            'safety_status': 'LOCKED',
            'automated_trading': False,
            'read_only': True
        }

    def get_metamask_hot_wallet(self) -> Dict[str, Any]:
        """
        Get MetaMask hot wallet balances
        Real-time data from Etherscan API
        """
        try:
            snapshot = self.metamask_tracker.get_all_balances()

            return {
                'source': 'metamask_hot_wallet',
                'total_eth': snapshot['totals']['total_eth'],
                'total_value_usd': snapshot['totals']['total_usd'],
                'addresses': {
                    addr: {
                        'name': data.get('name', 'Unknown'),
                        'balance_eth': data.get('balance_eth', 0),
                        'balance_usd': data.get('balance_usd', 0),
                        'type': data.get('type', 'unknown')
                    }
                    for addr, data in snapshot['addresses'].items()
                    if 'error' not in data
                },
                'last_updated': snapshot['timestamp'],
                'safety_status': 'HOT_WALLET',
                'automated_trading': False,  # Small amounts, manual only
                'note': 'MetaMask addresses tracked via public blockchain'
            }
        except Exception as e:
            print(f"⚠️  Error fetching MetaMask balances: {e}")
            # Fallback to hardcoded data from knowledge base
            return {
                'source': 'metamask_hot_wallet_cached',
                'total_eth': 0.00936201,
                'total_value_usd': 36.51,
                'addresses': PORTFOLIO_CONTEXT['metamask_hot_wallet']['addresses'],
                'safety_status': 'HOT_WALLET',
                'automated_trading': False,
                'note': 'Using cached data from knowledge base'
            }

    def get_hot_wallet_velocity(self) -> Dict[str, Any]:
        """
        Get hot wallet (active trading capital) on exchanges
        TODO: Integrate with Coinbase API for real-time balances
        """
        return {
            'source': 'exchange_hot_wallets',
            'total_value_usd': "TBD",  # Need real exchange API data
            'available_for_trading': "TBD",
            'emergency_reserve': "TBD",
            'max_position_size': "TBD",  # 25% of velocity once known
            'max_daily_exposure': 50,  # Conservative until we have real data
            'exchanges': {
                'coinbase': {'balance_usd': "TBD", 'status': 'connected'},
                'okx': {'balance_usd': "TBD", 'status': 'connected'},
                'kraken': {'balance_usd': "TBD", 'status': 'connected'}
            },
            'safety_status': 'NEEDS_LIVE_DATA',
            'automated_trading': True,
            'note': 'Need to implement live exchange API integration'
        }

    def get_defi_positions(self) -> Dict[str, Any]:
        """
        Get DeFi positions (AAVE wstETH on Ledger)
        Uses real-time blockchain data via Infura + Web3.py
        """
        if self.aave_enabled and self.aave_monitor:
            try:
                # Get live AAVE position data
                position = self.aave_monitor.get_position_summary()

                if 'error' not in position:
                    health_factor = position['metrics']['health_factor']
                    risk_level = position['risk']['risk_level']

                    return {
                        'source': 'aave_on_ledger_live',
                        'eth_address': position['address'],
                        'protocol': 'AAVE v3',
                        'position_type': 'Wrapped staked ETH (wstETH)',
                        'collateral_usd': position['position']['total_collateral_usd'],
                        'debt_usd': position['position']['total_debt_usd'],
                        'net_value_usd': position['position']['net_value_usd'],
                        'available_to_borrow_usd': position['position']['available_borrows_usd'],
                        'health_factor': health_factor if health_factor != float('inf') else 'No Debt',
                        'liquidation_threshold': position['metrics']['liquidation_threshold'],
                        'ltv': position['metrics']['loan_to_value'],
                        'risk_level': risk_level,
                        'risk_status': position['risk']['status'],
                        'risk_description': position['risk']['description'],
                        'recommended_action': position['risk']['action'],
                        'percent_of_ledger': 63.3,
                        'safety_status': 'HEALTHY' if risk_level in ['NONE', 'LOW'] else 'AT_RISK',
                        'automated_trading': False,
                        'requires_monitoring': True,
                        'last_updated': position['timestamp'],
                        'block_number': position['block_number']
                    }
            except Exception as e:
                print(f"⚠️  Error fetching live AAVE data: {e}")

        # Fallback to static data if AAVE monitor unavailable
        return {
            'source': 'aave_on_ledger_static',
            'eth_address': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',
            'protocol': 'AAVE v3',
            'position_type': 'Wrapped staked ETH (wstETH)',
            'position_value_usd': 3904.74,
            'percent_of_ledger': 63.3,
            'note': 'Using static data - AAVE monitor not available',
            'health_factor': 'UNKNOWN',
            'liquidation_risk': 'UNKNOWN',
            'safety_status': 'NEEDS_MONITORING',
            'automated_trading': False,
            'requires_monitoring': True,
            'warning': 'DO NOT LIQUIDATE unless emergency'
        }

    def get_complete_portfolio(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get complete portfolio snapshot
        This is the main function AI agents should call
        """
        # Check cache
        if not force_refresh and self.cached_data and self.last_update:
            elapsed = (datetime.now() - self.last_update).total_seconds()
            if elapsed < self.cache_timeout:
                return self.cached_data

        # Get all portfolio components
        cold_storage = self.get_cold_storage()
        metamask = self.get_metamask_hot_wallet()
        exchange_wallets = self.get_hot_wallet_velocity()
        defi = self.get_defi_positions()
        prices = self.get_live_prices()

        # Calculate totals (only include numeric values)
        ledger_total = cold_storage['total_value_usd']
        metamask_total = metamask['total_value_usd']
        exchange_total = 0 if exchange_wallets['total_value_usd'] == "TBD" else exchange_wallets['total_value_usd']

        # Get AAVE value (either net_value_usd or position_value_usd)
        defi_total = defi.get('net_value_usd', defi.get('position_value_usd', 0))

        # Note: AAVE is ON Ledger, so we don't double-count
        # Total Ledger = $6,167.43 (includes AAVE collateral)
        # We use the NET value (collateral - debt) for actual net worth
        total_value = ledger_total + metamask_total + exchange_total

        # Build complete portfolio
        portfolio = {
            'timestamp': datetime.now().isoformat(),
            'total_portfolio_value_usd': total_value,
            'breakdown': {
                'ledger_hardware_wallet': ledger_total,
                'metamask_hot_wallet': metamask_total,
                'exchange_wallets': exchange_total,
                'note': f'AAVE ${defi_total:,.2f} is included in Ledger total, not separate'
            },
            'allocation': {
                'ledger_percent': (ledger_total / total_value * 100) if total_value > 0 else 0,
                'metamask_percent': (metamask_total / total_value * 100) if total_value > 0 else 0,
                'exchange_percent': (exchange_total / total_value * 100) if total_value > 0 else 0
            },
            'components': {
                'ledger_cold_storage': cold_storage,
                'metamask_hot_wallet': metamask,
                'exchange_wallets': exchange_wallets,
                'defi_positions': defi
            },
            'market_prices': prices,
            'safety_checks': {
                'cold_vault_secure': verify_cold_vault_safety(),
                'aave_health_monitored': defi['requires_monitoring'],
                'trading_capital_known': exchange_wallets['total_value_usd'] != "TBD"
            },
            'trading_rules': {
                'never_touch_ledger': True,
                'never_touch_aave': 'Unless emergency',
                'metamask_manual_only': True,
                'max_position_size': exchange_wallets['max_position_size'],
                'max_daily_exposure': exchange_wallets['max_daily_exposure']
            }
        }

        # Cache results
        self.cached_data = portfolio
        self.last_update = datetime.now()

        return portfolio

    def get_ai_context_summary(self) -> str:
        """
        Get human-readable summary for AI agents
        This is what gets injected into AI prompts
        """
        portfolio = self.get_complete_portfolio()

        # Get components
        ledger = portfolio['components']['ledger_cold_storage']
        metamask = portfolio['components']['metamask_hot_wallet']
        exchanges = portfolio['components']['exchange_wallets']
        defi = portfolio['components']['defi_positions']

        summary = f"""
🏴 SOVEREIGN SHADOW PORTFOLIO CONTEXT (CORRECTED)

Total Portfolio Value: ${portfolio['total_portfolio_value_usd']:,.2f}

Capital Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 🔐 LEDGER HARDWARE WALLET: ${ledger['total_value_usd']:,.2f} ({portfolio['allocation']['ledger_percent']:.1f}%)
│   │
│   ├── 🏦 AAVE wstETH (DeFi): ${defi.get('collateral_usd', defi.get('position_value_usd', 0)):,.2f} collateral
│   │   ├── Debt: ${defi.get('debt_usd', 0):,.2f}
│   │   ├── Net: ${defi.get('net_value_usd', 0):,.2f}
│   │   ├── Health Factor: {defi.get('health_factor', 'UNKNOWN')}
│   │   ├── Risk: {defi.get('risk_status', 'UNKNOWN')}
│   │   └── ⚠️  THIS IS DEFI, NOT COLD STORAGE
│   │
│   ├── ₿ BTC (Cold Storage): ${ledger['balances']['btc']['value_usd']:,.2f} (36.2%)
│   │   ├── Amount: {ledger['balances']['btc']['amount']:.8f} BTC
│   │   └── ✅ TRUE cold storage - NEVER touch
│   │
│   ├── ETH (Gas): ${ledger['balances']['eth']['value_usd']:.2f}
│   ├── USDTb: ${ledger.get('balances', {}).get('usdtb', {}).get('value_usd', 4.99):.2f}
│   └── XRP: ${ledger.get('balances', {}).get('xrp', {}).get('value_usd', 2.57):.2f}
│
├── 🔥 METAMASK HOT WALLET: ${metamask['total_value_usd']:.2f} ({portfolio['allocation']['metamask_percent']:.1f}%)
│   ├── Total: {metamask['total_eth']:.8f} ETH
│   ├── Status: {metamask['safety_status']}
│   └── Note: {metamask['note']}
│
└── 💱 EXCHANGE WALLETS: ${exchanges['total_value_usd']} ({portfolio['allocation']['exchange_percent']:.1f}%)
    ├── Coinbase: {exchanges['exchanges']['coinbase']['status']}
    ├── OKX: {exchanges['exchanges']['okx']['status']}
    ├── Kraken: {exchanges['exchanges']['kraken']['status']}
    └── Status: {exchanges['safety_status']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRADING RULES:
❌ Ledger ($6,167.43) - NEVER use for automated trading
❌ AAVE ($3,904.74) - DO NOT liquidate unless emergency
⚠️  MetaMask ($36.51) - Manual transactions only, small amounts
? Exchanges (TBD) - Need live API integration to know balances

Max Position Size: {exchanges['max_position_size']}
Max Daily Exposure: ${exchanges['max_daily_exposure']}

SAFETY STATUS:
{'✅' if portfolio['safety_checks']['cold_vault_secure'] else '❌'} Cold Vault Secure (Read-only)
{'⚠️' if portfolio['safety_checks']['aave_health_monitored'] else '✅'} AAVE Needs Monitoring
{'✅' if portfolio['safety_checks']['trading_capital_known'] else '❌'} Exchange Balances Known

IMPORTANT: Most portfolio value ($3,904.74 / 63%) is in AAVE DeFi position,
NOT in cold storage BTC ($2,231.74 / 36%)!
"""
        return summary

    def export_for_mcp_server(self) -> Dict[str, Any]:
        """
        Export data in format for MCP server
        This gets loaded into Claude Desktop context
        """
        portfolio = self.get_complete_portfolio()

        return {
            'portfolio_snapshot': portfolio,
            'ai_context': self.get_ai_context_summary(),
            'quick_reference': {
                'total_value': portfolio['total_portfolio_value_usd'],
                'ledger_value': portfolio['breakdown']['ledger_hardware_wallet'],
                'metamask_value': portfolio['breakdown']['metamask_hot_wallet'],
                'exchange_value': portfolio['breakdown']['exchange_wallets'],
                'aave_collateral': portfolio['components']['defi_positions'].get('collateral_usd', 0),
                'aave_debt': portfolio['components']['defi_positions'].get('debt_usd', 0),
                'aave_net_value': portfolio['components']['defi_positions'].get('net_value_usd', 0),
                'aave_health_factor': portfolio['components']['defi_positions'].get('health_factor', 'UNKNOWN'),
                'btc_cold_storage': portfolio['components']['ledger_cold_storage']['balances']['btc']['value_usd'],
                'trading_capital_status': 'Need to fetch exchange balances',
                'ledger_locked': True,
                'aave_safe': portfolio['components']['defi_positions'].get('risk_level', 'UNKNOWN') in ['NONE', 'LOW']
            },
            'last_updated': portfolio['timestamp']
        }


def main():
    """Test unified portfolio API"""
    print("\n" + "="*70)
    print("🏴 UNIFIED PORTFOLIO API TEST")
    print("="*70)

    api = UnifiedPortfolioAPI()

    # Get complete portfolio
    portfolio = api.get_complete_portfolio(force_refresh=True)

    # Display AI context summary
    print(api.get_ai_context_summary())

    # Export for MCP
    mcp_data = api.export_for_mcp_server()
    output_path = Path(__file__).parent / "logs" / "mcp_portfolio_context.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(mcp_data, f, indent=2)

    print(f"✅ MCP context exported to: {output_path}")
    print("="*70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

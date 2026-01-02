#!/usr/bin/env python3
"""
UNIFIED PROFIT TRACKER
Aggregates profits from ALL sources for siphon calculations

Profit Sources:
1. Shadow Sniper (desktop system)
2. Swarm Intelligence (6 AI agents)
3. Paper Trading Engine
4. Exchange balances (real-time)
5. AAVE position yields

Author: SovereignShadow 2
Last Updated: 2025-10-30
"""

import os
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import centralized portfolio config
try:
    sys.path.insert(0, '/Volumes/LegacySafe/SS_III')
    from core.config.portfolio_config import get_initial_capital, get_portfolio_config, get_aave_config
except ImportError:
    def get_initial_capital(exchange=None):
        return 5438 if exchange is None else 0
    def get_portfolio_config():
        return {"net_worth": {"total": 5438}}
    def get_aave_config():
        return {"health_factor": 3.96, "debt_usd": 609}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedProfitTracker:
    """
    Central profit tracking system for SovereignShadow 2
    Aggregates profits from all trading systems and feeds into siphon
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.logs_path = self.base_path / "logs"
        self.logs_path.mkdir(exist_ok=True)

        # Capital tracking file
        self.capital_tracker_file = self.logs_path / "capital_tracker.json"

        # Initialize capital tracker
        self.capital_data = self._load_capital_tracker()

        logger.info("🧮 Unified Profit Tracker initialized")

    def _load_capital_tracker(self) -> Dict[str, Any]:
        """Load capital tracker data"""
        if self.capital_tracker_file.exists():
            with open(self.capital_tracker_file, 'r') as f:
                data = json.load(f)
                logger.info(f"📊 Loaded capital tracker: Initial ${data.get('initial_capital', 0):.2f}")
                return data

        # Initialize if doesn't exist
        default_data = {
            'initial_capital': get_initial_capital(),  # From portfolio_config.py
            'total_withdrawn': 0.0,
            'reset_capital': 1000.0,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'history': []
        }
        self._save_capital_tracker(default_data)
        return default_data

    def _save_capital_tracker(self, data: Dict[str, Any]) -> None:
        """Save capital tracker data"""
        with open(self.capital_tracker_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_shadow_sniper_pnl(self) -> Dict[str, Any]:
        """
        Get P&L from Shadow Sniper (desktop system)

        Returns:
            Dict with total_pnl, trade_count, win_rate, last_updated
        """
        try:
            # Try to read Shadow Sniper bridge data
            bridge_file = self.logs_path / "shadow_sniper_bridge.json"

            if bridge_file.exists():
                with open(bridge_file, 'r') as f:
                    data = json.load(f)
                    logger.debug(f"📈 Shadow Sniper P&L: ${data.get('total_pnl', 0):.2f}")
                    return data

            # If bridge not set up yet, return placeholder
            logger.warning("⚠️  Shadow Sniper bridge not connected yet")
            return {
                'total_pnl': 0.0,
                'trade_count': 0,
                'win_rate': 0.0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'bridge_pending'
            }

        except Exception as e:
            logger.error(f"Error reading Shadow Sniper data: {e}")
            return {
                'total_pnl': 0.0,
                'trade_count': 0,
                'win_rate': 0.0,
                'error': str(e)
            }

    def get_swarm_intelligence_pnl(self) -> Dict[str, Any]:
        """
        Get P&L from Swarm Intelligence (6 AI agents)

        Returns:
            Dict with total_pnl, agent_count, consensus_rate, last_updated
        """
        try:
            # Try to read Swarm bridge data
            bridge_file = self.logs_path / "swarm_intelligence_bridge.json"

            if bridge_file.exists():
                with open(bridge_file, 'r') as f:
                    data = json.load(f)
                    logger.debug(f"🤖 Swarm Intelligence P&L: ${data.get('total_pnl', 0):.2f}")
                    return data

            # If bridge not set up yet, return placeholder
            logger.warning("⚠️  Swarm Intelligence bridge not connected yet")
            return {
                'total_pnl': 0.0,
                'agent_count': 0,
                'consensus_rate': 0.0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'bridge_pending'
            }

        except Exception as e:
            logger.error(f"Error reading Swarm Intelligence data: {e}")
            return {
                'total_pnl': 0.0,
                'agent_count': 0,
                'consensus_rate': 0.0,
                'error': str(e)
            }

    def get_paper_trading_pnl(self) -> Dict[str, Any]:
        """
        Get P&L from Paper Trading Engine

        Returns:
            Dict with total_pnl, simulation_trades, last_updated
        """
        try:
            # Try to import paper trading tracker
            import sys
            claude_sdk_path = self.base_path / "ClaudeSDK" / "agents"
            if str(claude_sdk_path) not in sys.path:
                sys.path.insert(0, str(claude_sdk_path))

            # Try to get P&L from paper trading tracker
            try:
                from paper_trading_tracker import get_total_profit
                total_pnl = get_total_profit()
                logger.debug(f"📝 Paper Trading P&L: ${total_pnl:.2f}")
                return {
                    'total_pnl': total_pnl,
                    'simulation_trades': 0,  # Would need to track this
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            except ImportError:
                logger.warning("⚠️  Paper trading tracker not available")
                return {
                    'total_pnl': 0.0,
                    'simulation_trades': 0,
                    'status': 'module_not_found'
                }

        except Exception as e:
            logger.error(f"Error reading Paper Trading data: {e}")
            return {
                'total_pnl': 0.0,
                'simulation_trades': 0,
                'error': str(e)
            }

    def get_ledger_balances(self) -> Dict[str, Any]:
        """
        Get Ledger cold storage balances (VAULT)

        Ledger Addresses:
        - ETH/USDC/USDT: 0xC08413B63ecA84E2d9693af9414330dA88dcD81C
        - BTC: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
        """
        try:
            # Use AAVE monitor's Web3 connection to query Ledger balances
            from aave_monitor import AAVEMonitor

            monitor = AAVEMonitor()
            w3 = monitor.w3

            ledger_eth_address = "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"
            ledger_btc_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

            # Get ETH balance
            eth_balance_wei = w3.eth.get_balance(ledger_eth_address)
            eth_balance = float(w3.from_wei(eth_balance_wei, 'ether'))

            # TODO: Add USDC, USDT, BTC balance queries
            # For now, using static data from screenshots

            assets = {
                'ETH': {
                    'balance': eth_balance,
                    'price_usd': 2600.0,  # Will be live once price feed added
                    'value_usd': eth_balance * 2600.0,
                    'platform': 'ledger',
                    'address': ledger_eth_address
                },
                'BTC': {
                    'balance': 0.0,  # Will query blockchain
                    'price_usd': 68000.0,
                    'value_usd': 0.0,
                    'platform': 'ledger',
                    'address': ledger_btc_address
                },
                'USDC': {
                    'balance': 0.0,  # Will query ERC-20 contract
                    'price_usd': 1.0,
                    'value_usd': 0.0,
                    'platform': 'ledger',
                    'address': ledger_eth_address
                }
            }

            total_usd = sum(asset['value_usd'] for asset in assets.values())

            logger.info(f"💎 Ledger VAULT: ${total_usd:.2f}")

            return {
                'total_usd': total_usd,
                'assets': assets,
                'status': 'live',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error reading Ledger balances: {e}")
            return {
                'total_usd': 0.0,
                'assets': {},
                'status': 'error',
                'error': str(e)
            }

    def get_coinbase_balance(self) -> Dict[str, Any]:
        """
        Get Coinbase Exchange balance with asset breakdown

        Returns:
            Dict with total_usd, assets breakdown, status
        """
        try:
            # Check for Coinbase Exchange API credentials
            api_key = os.getenv('COINBASE_EXCHANGE_API_KEY')
            api_secret = os.getenv('COINBASE_EXCHANGE_SECRET')

            if not api_key or not api_secret:
                logger.warning("⚠️  Coinbase Exchange API keys not configured")

                # Return current balance from Coinbase app (screenshots 2025-10-30)
                # Total: $1,869.36 = $1,828.97 crypto + $40.38 cash
                assets = {
                    'USDC': {
                        'balance': 40.38,
                        'price_usd': 1.0,
                        'value_usd': 40.38,
                        'platform': 'coinbase',
                        'apy': 4.25,
                        'allocation_pct': 2.16
                    },
                    'CRYPTO_PORTFOLIO': {
                        'balance': 1.0,  # Represents entire crypto holdings
                        'price_usd': 1828.97,
                        'value_usd': 1828.97,
                        'platform': 'coinbase',
                        'allocation_pct': 97.84,
                        'note': 'Combined: XRP, SOL, ETH, AAVE, others'
                    }
                }

                total_usd = 1869.36  # $1,828.97 crypto + $40.38 USDC

                return {
                    'total_usd': total_usd,
                    'crypto_usd': 1828.97,
                    'cash_usd': 40.38,
                    'assets': assets,
                    'status': 'static_data',
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'source': 'coinbase_app_screenshots_20251030'
                }

            # TODO: Implement Coinbase Exchange API calls here
            # from coinbase.wallet.client import Client
            # client = Client(api_key, api_secret)
            # accounts = client.get_accounts()

            logger.info("✅ Coinbase API ready (not yet implemented)")
            return {
                'total_usd': 1904.00,
                'assets': {},
                'status': 'api_ready_pending_implementation',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching Coinbase balance: {e}")
            return {
                'total_usd': 0.0,
                'assets': {},
                'error': str(e)
            }

    def get_exchange_balances(self) -> Dict[str, Any]:
        """
        Get current exchange balances (real-time)

        Returns:
            Dict with balances per exchange and total USD value
        """
        try:
            # Get Coinbase balance (live or static)
            coinbase_data = self.get_coinbase_balance()
            coinbase_balance = coinbase_data.get('total_usd', 0.0)
            coinbase_assets = coinbase_data.get('assets', {})

            # All exchanges - will be live once API keys added to .env
            balances = {
                'coinbase': coinbase_balance,  # $1,904
                'coinbase_status': coinbase_data.get('status'),
                'coinbase_assets': coinbase_assets,  # Asset breakdown
                'okx': 0.0,  # No balance
                'kraken': 0.0,  # No balance
                'binance_us': 150.0,  # Static until API keys added
                'total_usd': coinbase_balance + 150.0,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'mixed'  # Will be 'live' once all APIs connected
            }

            logger.debug(f"💰 Exchange balances: ${balances['total_usd']:.2f}")
            return balances

        except Exception as e:
            logger.error(f"Error reading exchange balances: {e}")
            return {
                'total_usd': 0.0,
                'error': str(e)
            }

    def get_aave_position_yield(self) -> Dict[str, Any]:
        """
        Get AAVE position yield earnings

        Returns:
            Dict with yield_earned, health_factor, net_value
        """
        try:
            # Try to use AAVE monitor
            aave_monitor_path = self.base_path / "hybrid_system"
            import sys
            if str(aave_monitor_path) not in sys.path:
                sys.path.insert(0, str(aave_monitor_path))

            try:
                from aave_monitor import AAVEMonitor

                monitor = AAVEMonitor()
                account_data = monitor.get_account_data()

                # Calculate yield (this is net value, not just yield)
                # In a real implementation, we'd track yield separately
                yield_data = {
                    'net_position_value': account_data.get('net_position_usd', 0.0),
                    'health_factor': account_data.get('health_factor', 0.0),
                    'collateral_usd': account_data.get('total_collateral_usd', 0.0),
                    'debt_usd': account_data.get('total_debt_usd', 0.0),
                    'yield_earned': 0.0,  # TODO: Track this separately
                    'last_updated': account_data.get('timestamp'),
                    'status': 'live'
                }

                logger.debug(f"🛡️  AAVE Position: ${yield_data['net_position_value']:.2f} (HF: {yield_data['health_factor']:.2f})")
                return yield_data

            except ImportError:
                logger.warning("⚠️  AAVE monitor not available")
                return {
                    'net_position_value': 2735.57,  # Known value
                    'health_factor': 2.7239,
                    'yield_earned': 0.0,
                    'status': 'static_data'
                }

        except Exception as e:
            logger.error(f"Error reading AAVE data: {e}")
            return {
                'net_position_value': 0.0,
                'health_factor': 0.0,
                'yield_earned': 0.0,
                'error': str(e)
            }

    def get_total_profit(self) -> Dict[str, Any]:
        """
        Calculate total profit across ALL sources

        This is the main method used by siphon system

        Returns:
            Comprehensive profit data from all sources
        """
        logger.info("\n" + "="*70)
        logger.info("📊 UNIFIED PROFIT TRACKER - Aggregating All Sources")
        logger.info("="*70)

        # Get data from all sources
        shadow_sniper = self.get_shadow_sniper_pnl()
        swarm_intelligence = self.get_swarm_intelligence_pnl()
        paper_trading = self.get_paper_trading_pnl()
        ledger_vault = self.get_ledger_balances()
        exchange_balances = self.get_exchange_balances()
        aave_position = self.get_aave_position_yield()

        # Calculate current total portfolio value
        current_portfolio_value = (
            ledger_vault.get('total_usd', 0.0) +
            exchange_balances.get('total_usd', 0.0) +
            aave_position.get('net_position_value', 0.0)
        )

        # Calculate total realized P&L from trading
        total_trading_pnl = (
            shadow_sniper.get('total_pnl', 0.0) +
            swarm_intelligence.get('total_pnl', 0.0) +
            paper_trading.get('total_pnl', 0.0)
        )

        # Calculate net profit (current value - initial capital - already withdrawn)
        initial_capital = self.capital_data.get('initial_capital', 0.0)
        total_withdrawn = self.capital_data.get('total_withdrawn', 0.0)

        # Net profit = current portfolio - initial capital - already withdrawn
        net_profit = current_portfolio_value - initial_capital - total_withdrawn

        # Compile comprehensive result
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),

            # Portfolio Overview
            'current_portfolio_value': current_portfolio_value,
            'initial_capital': initial_capital,
            'total_withdrawn': total_withdrawn,
            'net_profit': net_profit,

            # Trading P&L Breakdown
            'shadow_sniper_pnl': shadow_sniper.get('total_pnl', 0.0),
            'swarm_intelligence_pnl': swarm_intelligence.get('total_pnl', 0.0),
            'paper_trading_pnl': paper_trading.get('total_pnl', 0.0),
            'total_trading_pnl': total_trading_pnl,

            # Position Values
            'exchange_balances_usd': exchange_balances.get('total_usd', 0.0),
            'aave_net_position_usd': aave_position.get('net_position_value', 0.0),

            # Detailed Source Data
            'sources': {
                'shadow_sniper': shadow_sniper,
                'swarm_intelligence': swarm_intelligence,
                'paper_trading': paper_trading,
                'ledger_vault': ledger_vault,
                'exchange_balances': exchange_balances,
                'aave_position': aave_position
            },

            # Platform Breakdown
            'platform_breakdown': {
                'ledger_vault': {
                    'total_usd': ledger_vault.get('total_usd', 0.0),
                    'allocation_pct': (ledger_vault.get('total_usd', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'assets': ledger_vault.get('assets', {})
                },
                'coinbase': {
                    'total_usd': exchange_balances.get('coinbase', 0.0),
                    'allocation_pct': (exchange_balances.get('coinbase', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'assets': exchange_balances.get('coinbase_assets', {})
                },
                'binance_us': {
                    'total_usd': exchange_balances.get('binance_us', 0.0),
                    'allocation_pct': (exchange_balances.get('binance_us', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'assets': {}  # Will add when API keys connected
                },
                'okx': {
                    'total_usd': exchange_balances.get('okx', 0.0),
                    'allocation_pct': (exchange_balances.get('okx', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'assets': {}  # Will add when API keys connected
                },
                'kraken': {
                    'total_usd': exchange_balances.get('kraken', 0.0),
                    'allocation_pct': (exchange_balances.get('kraken', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'assets': {}  # Will add when API keys connected
                },
                'aave_v3': {
                    'total_usd': aave_position.get('net_position_value', 0.0),
                    'allocation_pct': (aave_position.get('net_position_value', 0.0) / current_portfolio_value * 100) if current_portfolio_value > 0 else 0,
                    'collateral_usd': aave_position.get('collateral_usd', 0.0),
                    'debt_usd': aave_position.get('debt_usd', 0.0),
                    'health_factor': aave_position.get('health_factor', 0.0)
                }
            },

            # Debt Tracking (CRITICAL: Pay debt FIRST before siphon)
            'aave_debt_usd': aave_position.get('debt_usd', 0.0),
            'total_debt': aave_position.get('debt_usd', 0.0),  # ONLY AAVE debt

            # Debt Repayment Priority (ALWAYS FIRST)
            # User rule: "add in rule to syphon any debt first Allways"
            'debt_repayment_needed': aave_position.get('debt_usd', 0.0),
            'profit_after_debt': max(0, net_profit - aave_position.get('debt_usd', 0.0)),

            # Siphon Calculations (30/70) - ONLY from profit AFTER debt paid
            'siphon_amount_30_pct': max(0, net_profit - aave_position.get('debt_usd', 0.0)) * 0.30,
            'buffer_amount_70_pct': max(0, net_profit - aave_position.get('debt_usd', 0.0)) * 0.70,

            # Safety Checks
            'aave_health_factor': aave_position.get('health_factor', 0.0),
            'safe_to_siphon': (
                (net_profit - aave_position.get('debt_usd', 0.0)) >= 100.0 and  # $100 profit AFTER debt
                aave_position.get('health_factor', 0.0) >= 2.5  # AAVE safety threshold
            )
        }

        # Log summary
        logger.info(f"\n📊 PROFIT SUMMARY:")
        logger.info(f"  Current Portfolio: ${current_portfolio_value:,.2f}")
        logger.info(f"  Initial Capital:   ${initial_capital:,.2f}")
        logger.info(f"  Total Withdrawn:   ${total_withdrawn:,.2f}")
        logger.info(f"  ─────────────────────────────────")
        logger.info(f"  NET PROFIT:        ${net_profit:,.2f}")
        logger.info(f"\n💰 TRADING P&L:")
        logger.info(f"  Shadow Sniper:     ${shadow_sniper.get('total_pnl', 0.0):,.2f}")
        logger.info(f"  Swarm Intelligence: ${swarm_intelligence.get('total_pnl', 0.0):,.2f}")
        logger.info(f"  Paper Trading:     ${paper_trading.get('total_pnl', 0.0):,.2f}")
        logger.info(f"  ─────────────────────────────────")
        logger.info(f"  TOTAL:             ${total_trading_pnl:,.2f}")
        logger.info(f"\n💎 SIPHON CALCULATION (30/70):")
        logger.info(f"  30% to VAULT:      ${result['siphon_amount_30_pct']:,.2f}")
        logger.info(f"  70% to BUFFER:     ${result['buffer_amount_70_pct']:,.2f}")
        logger.info(f"\n🛡️  SAFETY STATUS:")
        logger.info(f"  AAVE Health Factor: {result['aave_health_factor']:.4f}")
        logger.info(f"  Safe to Siphon:    {'✅ YES' if result['safe_to_siphon'] else '❌ NO'}")
        logger.info("="*70 + "\n")

        return result

    def record_withdrawal(self, amount: float, destination: str, notes: str = "") -> None:
        """
        Record a siphon withdrawal

        Args:
            amount: Amount withdrawn in USD
            destination: Ledger address or description
            notes: Optional notes about withdrawal
        """
        withdrawal_record = {
            'amount': amount,
            'destination': destination,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'notes': notes
        }

        # Update capital tracker
        self.capital_data['total_withdrawn'] += amount
        self.capital_data['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.capital_data['history'].append(withdrawal_record)

        self._save_capital_tracker(self.capital_data)

        logger.info(f"💎 Recorded withdrawal: ${amount:.2f} → {destination}")
        logger.info(f"📊 Total withdrawn: ${self.capital_data['total_withdrawn']:.2f}")

    def reset_capital(self, new_initial_capital: float, reason: str = "milestone_reached") -> None:
        """
        Reset initial capital (e.g., after milestone extraction)

        Args:
            new_initial_capital: New starting capital
            reason: Reason for reset
        """
        old_initial = self.capital_data['initial_capital']

        self.capital_data['initial_capital'] = new_initial_capital
        self.capital_data['total_withdrawn'] = 0.0
        self.capital_data['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.capital_data['history'].append({
            'type': 'capital_reset',
            'old_initial': old_initial,
            'new_initial': new_initial_capital,
            'reason': reason,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

        self._save_capital_tracker(self.capital_data)

        logger.info(f"🔄 Capital reset: ${old_initial:.2f} → ${new_initial_capital:.2f}")
        logger.info(f"📝 Reason: {reason}")

    def get_profit_history(self) -> List[Dict[str, Any]]:
        """Get historical profit/withdrawal data"""
        return self.capital_data.get('history', [])

    def export_to_json(self, filepath: Optional[str] = None) -> str:
        """
        Export current profit data to JSON file

        Args:
            filepath: Optional custom filepath, defaults to logs/profit_snapshot.json

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.logs_path / f"profit_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        profit_data = self.get_total_profit()

        with open(filepath, 'w') as f:
            json.dump(profit_data, f, indent=2)

        logger.info(f"📁 Exported profit data to: {filepath}")
        return str(filepath)


def main():
    """CLI interface for Unified Profit Tracker"""
    print("\n" + "="*70)
    print("🧮 UNIFIED PROFIT TRACKER")
    print("="*70)

    tracker = UnifiedProfitTracker()

    # Get total profit
    profit_data = tracker.get_total_profit()

    # Export snapshot
    tracker.export_to_json()

    print("\n✅ Profit tracking complete")
    print(f"📁 Data saved to: {tracker.logs_path}")


if __name__ == "__main__":
    main()

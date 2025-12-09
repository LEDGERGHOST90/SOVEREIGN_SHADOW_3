#!/usr/bin/env python3
"""
🏦 COLD STORAGE SIPHON - 30% Profit Withdrawal System
Automatically withdraw 30% of profits to Ledger cold storage

SAFETY RULES:
- Only withdraws PROFITS, never touches principal
- Requires minimum profit threshold ($50)
- Daily withdrawal limit ($1,000)
- Manual approval for large amounts (>$500)
- Withdrawal addresses are HARDCODED (cannot be changed by code)
"""

import os
import time
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import ccxt

load_dotenv()


class ColdStorageSiphon:
    """Automated 30% profit withdrawal to Ledger cold storage"""

    # 🔒 HARDCODED LEDGER ADDRESSES (CANNOT BE MODIFIED BY CODE)
    LEDGER_ADDRESSES = {
        'BTC': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
        'ETH': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',
        'USDC': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',  # ERC-20
        'USDT': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',  # ERC-20
    }

    # Safety parameters
    PROFIT_SIPHON_PERCENTAGE = 0.30  # 30%
    MIN_PROFIT_TO_WITHDRAW = 50.0    # $50 minimum
    DAILY_WITHDRAWAL_LIMIT = 1000.0  # $1,000 per day
    MANUAL_APPROVAL_THRESHOLD = 500.0 # $500 requires manual approval

    def __init__(self):
        """Initialize Cold Storage Siphon"""
        self.exchanges = self._initialize_exchanges()
        self.withdrawal_history = []
        self.daily_withdrawal_total = 0.0
        self.last_reset_date = datetime.now().date()

        print("🏦 Cold Storage Siphon initialized")
        print(f"📊 30% of profits → Ledger cold storage")
        print(f"🔒 Destination addresses:")
        for asset, address in self.LEDGER_ADDRESSES.items():
            print(f"   {asset}: {address[:10]}...{address[-6:]}")

    def _initialize_exchanges(self) -> Dict[str, ccxt.Exchange]:
        """Initialize exchange connections"""
        exchanges = {}

        # Coinbase Advanced Trade
        try:
            exchanges['coinbase'] = ccxt.coinbaseadvanced({
                'apiKey': os.getenv('COINBASE_API_KEY'),
                'secret': os.getenv('COINBASE_API_SECRET'),
                'enableRateLimit': True,
            })
            print("✅ Coinbase connected")
        except Exception as e:
            print(f"⚠️  Coinbase unavailable: {e}")

        # OKX
        try:
            exchanges['okx'] = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET_KEY'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'enableRateLimit': True,
            })
            print("✅ OKX connected")
        except Exception as e:
            print(f"⚠️  OKX unavailable: {e}")

        # Kraken
        try:
            exchanges['kraken'] = ccxt.kraken({
                'apiKey': os.getenv('KRAKEN_API_KEY'),
                'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
                'enableRateLimit': True,
            })
            print("✅ Kraken connected")
        except Exception as e:
            print(f"⚠️  Kraken unavailable: {e}")

        return exchanges

    def calculate_profits(self, exchange_name: str) -> Dict[str, Any]:
        """
        Calculate current profits on an exchange

        Returns:
            {
                'total_balance_usd': float,
                'initial_capital': float,
                'profit_usd': float,
                'profit_percentage': float,
                'withdrawable_amount': float (30% of profit)
            }
        """
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            return {'error': f'Exchange {exchange_name} not available'}

        try:
            # Fetch balance
            balance = exchange.fetch_balance()
            total_usd = float(balance.get('total', {}).get('USD', 0))

            # Get initial capital (from config or database)
            # For now, using environment variable
            initial_capital = float(os.getenv(f'{exchange_name.upper()}_INITIAL_CAPITAL', 0))

            # Calculate profit
            profit_usd = total_usd - initial_capital
            profit_percentage = (profit_usd / initial_capital * 100) if initial_capital > 0 else 0

            # Calculate 30% withdrawable amount
            withdrawable_amount = profit_usd * self.PROFIT_SIPHON_PERCENTAGE

            return {
                'exchange': exchange_name,
                'total_balance_usd': total_usd,
                'initial_capital': initial_capital,
                'profit_usd': profit_usd,
                'profit_percentage': profit_percentage,
                'withdrawable_amount': withdrawable_amount,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': str(e)}

    def _reset_daily_limit_if_needed(self):
        """Reset daily withdrawal limit at midnight"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_withdrawal_total = 0.0
            self.last_reset_date = today
            print(f"📅 Daily withdrawal limit reset: ${self.DAILY_WITHDRAWAL_LIMIT:,.2f} available")

    def _check_withdrawal_safety(self, amount_usd: float, asset: str) -> Dict[str, Any]:
        """
        Comprehensive safety checks before withdrawal

        Returns:
            {
                'safe': bool,
                'reason': str,
                'requires_approval': bool
            }
        """
        self._reset_daily_limit_if_needed()

        # Check 1: Minimum profit threshold
        if amount_usd < self.MIN_PROFIT_TO_WITHDRAW:
            return {
                'safe': False,
                'reason': f'Below minimum threshold (${self.MIN_PROFIT_TO_WITHDRAW})',
                'requires_approval': False
            }

        # Check 2: Daily limit
        if self.daily_withdrawal_total + amount_usd > self.DAILY_WITHDRAWAL_LIMIT:
            remaining = self.DAILY_WITHDRAWAL_LIMIT - self.daily_withdrawal_total
            return {
                'safe': False,
                'reason': f'Daily limit exceeded. Remaining: ${remaining:,.2f}',
                'requires_approval': False
            }

        # Check 3: Ledger address exists
        if asset not in self.LEDGER_ADDRESSES:
            return {
                'safe': False,
                'reason': f'No Ledger address configured for {asset}',
                'requires_approval': False
            }

        # Check 4: Manual approval for large amounts
        if amount_usd > self.MANUAL_APPROVAL_THRESHOLD:
            return {
                'safe': True,
                'reason': 'Large withdrawal - requires manual approval',
                'requires_approval': True
            }

        # All checks passed
        return {
            'safe': True,
            'reason': 'All safety checks passed',
            'requires_approval': False
        }

    def withdraw_to_cold_storage(
        self,
        exchange_name: str,
        asset: str,
        amount: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Withdraw funds to Ledger cold storage

        Args:
            exchange_name: 'coinbase', 'okx', or 'kraken'
            asset: 'BTC', 'ETH', 'USDC', etc.
            amount: Amount in asset units (not USD)
            dry_run: If True, simulate withdrawal without executing

        Returns:
            {
                'success': bool,
                'txid': str (if success),
                'error': str (if failure),
                'details': dict
            }
        """
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            return {'success': False, 'error': f'Exchange {exchange_name} not available'}

        # Get Ledger destination address
        ledger_address = self.LEDGER_ADDRESSES.get(asset)
        if not ledger_address:
            return {'success': False, 'error': f'No Ledger address for {asset}'}

        # Get current price for USD value check
        try:
            ticker = exchange.fetch_ticker(f'{asset}/USDT')
            price_usd = ticker['last']
            amount_usd = amount * price_usd
        except:
            amount_usd = 0

        # Safety checks
        safety_check = self._check_withdrawal_safety(amount_usd, asset)

        if not safety_check['safe']:
            return {
                'success': False,
                'error': safety_check['reason'],
                'safety_check': safety_check
            }

        if safety_check['requires_approval']:
            print(f"⚠️  MANUAL APPROVAL REQUIRED")
            print(f"   Amount: {amount} {asset} (${amount_usd:,.2f})")
            print(f"   Destination: {ledger_address}")
            approval = input("   Type 'CONFIRM' to proceed: ")
            if approval != 'CONFIRM':
                return {'success': False, 'error': 'Manual approval denied'}

        # DRY RUN MODE
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'DRY RUN - No actual withdrawal',
                'details': {
                    'exchange': exchange_name,
                    'asset': asset,
                    'amount': amount,
                    'amount_usd': amount_usd,
                    'destination': ledger_address,
                    'safety_check': safety_check
                }
            }

        # LIVE WITHDRAWAL
        try:
            print(f"🚀 Initiating withdrawal...")
            print(f"   Exchange: {exchange_name}")
            print(f"   Asset: {asset}")
            print(f"   Amount: {amount}")
            print(f"   Destination: {ledger_address}")

            # Execute withdrawal via exchange API
            withdrawal = exchange.withdraw(
                code=asset,
                amount=amount,
                address=ledger_address,
                params={}
            )

            # Update daily total
            self.daily_withdrawal_total += amount_usd

            # Record withdrawal
            withdrawal_record = {
                'timestamp': datetime.now().isoformat(),
                'exchange': exchange_name,
                'asset': asset,
                'amount': amount,
                'amount_usd': amount_usd,
                'destination': ledger_address,
                'txid': withdrawal.get('id', 'unknown'),
                'status': withdrawal.get('status', 'pending')
            }
            self.withdrawal_history.append(withdrawal_record)

            print(f"✅ Withdrawal initiated!")
            print(f"   TX ID: {withdrawal.get('id', 'unknown')}")
            print(f"   Status: {withdrawal.get('status', 'pending')}")

            return {
                'success': True,
                'txid': withdrawal.get('id'),
                'status': withdrawal.get('status'),
                'details': withdrawal_record
            }

        except Exception as e:
            print(f"❌ Withdrawal failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def auto_siphon_profits(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Automatically calculate and withdraw 30% of profits to cold storage

        Process:
        1. Calculate profits on each exchange
        2. Determine 30% withdrawable amount
        3. Check safety limits
        4. Execute withdrawals to Ledger

        Args:
            dry_run: If True, simulate without executing
        """
        print("\n" + "="*70)
        print("🏦 AUTO-SIPHON: 30% Profits → Ledger Cold Storage")
        print("="*70)

        results = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': {},
            'total_profits': 0.0,
            'total_withdrawable': 0.0,
            'total_withdrawn': 0.0,
            'dry_run': dry_run
        }

        for exchange_name in self.exchanges.keys():
            print(f"\n📊 Checking {exchange_name.upper()}...")

            # Calculate profits
            profit_data = self.calculate_profits(exchange_name)

            if 'error' in profit_data:
                print(f"   ❌ Error: {profit_data['error']}")
                results['exchanges'][exchange_name] = profit_data
                continue

            profit_usd = profit_data['profit_usd']
            withdrawable = profit_data['withdrawable_amount']

            print(f"   Total Balance: ${profit_data['total_balance_usd']:,.2f}")
            print(f"   Initial Capital: ${profit_data['initial_capital']:,.2f}")
            print(f"   Profit: ${profit_usd:,.2f} ({profit_data['profit_percentage']:.2f}%)")
            print(f"   30% Withdrawable: ${withdrawable:,.2f}")

            results['total_profits'] += profit_usd
            results['total_withdrawable'] += withdrawable
            results['exchanges'][exchange_name] = profit_data

            # Only withdraw if profitable and above threshold
            if withdrawable >= self.MIN_PROFIT_TO_WITHDRAW:
                # Determine best asset to withdraw (prefer stablecoins)
                asset = 'USDC'  # Default to USDC for simplicity

                # Calculate asset amount based on price
                try:
                    exchange = self.exchanges[exchange_name]
                    ticker = exchange.fetch_ticker(f'{asset}/USDT')
                    amount = withdrawable / ticker['last']

                    # Execute withdrawal
                    withdrawal_result = self.withdraw_to_cold_storage(
                        exchange_name=exchange_name,
                        asset=asset,
                        amount=amount,
                        dry_run=dry_run
                    )

                    if withdrawal_result['success']:
                        results['total_withdrawn'] += withdrawable
                        print(f"   ✅ Withdrawal: {amount:.4f} {asset}")
                    else:
                        print(f"   ❌ Withdrawal failed: {withdrawal_result.get('error')}")

                    results['exchanges'][exchange_name]['withdrawal'] = withdrawal_result

                except Exception as e:
                    print(f"   ❌ Withdrawal error: {e}")
            else:
                print(f"   ⏸️  Below threshold - no withdrawal")

        # Summary
        print("\n" + "="*70)
        print("📊 SIPHON SUMMARY")
        print("="*70)
        print(f"Total Profits: ${results['total_profits']:,.2f}")
        print(f"Total Withdrawable (30%): ${results['total_withdrawable']:,.2f}")
        print(f"Total Withdrawn: ${results['total_withdrawn']:,.2f}")
        print(f"Daily Limit Used: ${self.daily_withdrawal_total:,.2f} / ${self.DAILY_WITHDRAWAL_LIMIT:,.2f}")

        if dry_run:
            print("\n⚠️  DRY RUN MODE - No actual withdrawals executed")

        print("="*70)

        return results

    def get_withdrawal_history(self) -> list:
        """Get history of cold storage withdrawals"""
        return self.withdrawal_history


def main():
    """Run Cold Storage Siphon"""
    siphon = ColdStorageSiphon()

    # Run auto-siphon in DRY RUN mode
    print("\n🧪 Running in DRY RUN mode (no actual withdrawals)")
    results = siphon.auto_siphon_profits(dry_run=True)

    print("\n" + "="*70)
    print("To execute LIVE withdrawals:")
    print("  siphon.auto_siphon_profits(dry_run=False)")
    print("="*70)


if __name__ == "__main__":
    main()

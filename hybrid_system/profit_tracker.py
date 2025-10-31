#!/usr/bin/env python3
"""
📊 PROFIT TRACKER - Calculate 30% Cold Storage Allocation
Simple profit tracking without interfering with automation

DOES NOT:
- Execute any trades
- Withdraw funds automatically
- Modify exchange balances
- Interfere with trading automation

ONLY DOES:
- Track profits
- Calculate 30% allocation
- Save recommendations to file
- Display what to manually withdraw
"""

import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import ccxt

load_dotenv()


class ProfitTracker:
    """Track trading profits and calculate cold storage allocation"""

    # 🔒 LEDGER DESTINATION ADDRESSES (REFERENCE ONLY)
    LEDGER_ADDRESSES = {
        'BTC': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
        'ETH': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',
        'USDC': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',
        'USDT': '0xC08413B63ecA84E2d9693af9414330dA88dcD81C',
    }

    COLD_STORAGE_PERCENTAGE = 0.30  # 30%

    def __init__(self):
        """Initialize Profit Tracker"""
        self.report_file = 'logs/profit_tracker_report.json'
        os.makedirs('logs', exist_ok=True)

        # Load initial capital from config
        self.initial_capital = {
            'coinbase': float(os.getenv('COINBASE_INITIAL_CAPITAL', 2016.48)),
            'okx': float(os.getenv('OKX_INITIAL_CAPITAL', 149.06)),
            'kraken': float(os.getenv('KRAKEN_INITIAL_CAPITAL', 0)),
        }

        print("📊 Profit Tracker initialized")
        print(f"💰 Tracking 30% cold storage allocation")

    def fetch_exchange_balances(self) -> Dict[str, Dict]:
        """Fetch current balances from all exchanges"""
        balances = {}

        # Coinbase
        try:
            coinbase = ccxt.coinbaseadvanced({
                'apiKey': os.getenv('COINBASE_API_KEY'),
                'secret': os.getenv('COINBASE_API_SECRET'),
                'enableRateLimit': True,
            })
            balance = coinbase.fetch_balance()
            total_usd = sum([
                float(balance['total'].get(asset, 0)) * coinbase.fetch_ticker(f'{asset}/USDT')['last']
                for asset in balance['total']
                if balance['total'].get(asset, 0) > 0
            ])
            balances['coinbase'] = {
                'total_usd': total_usd,
                'balances': balance['total'],
                'timestamp': datetime.now().isoformat()
            }
            print(f"✅ Coinbase: ${total_usd:,.2f}")
        except Exception as e:
            print(f"⚠️  Coinbase error: {e}")
            balances['coinbase'] = {'error': str(e)}

        # OKX
        try:
            okx = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET_KEY'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'enableRateLimit': True,
            })
            balance = okx.fetch_balance()
            total_usd = float(balance['total'].get('USDT', 0))
            balances['okx'] = {
                'total_usd': total_usd,
                'balances': balance['total'],
                'timestamp': datetime.now().isoformat()
            }
            print(f"✅ OKX: ${total_usd:,.2f}")
        except Exception as e:
            print(f"⚠️  OKX error: {e}")
            balances['okx'] = {'error': str(e)}

        return balances

    def calculate_profits(self, balances: Dict) -> Dict[str, Any]:
        """Calculate profits and 30% allocation"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': {},
            'totals': {
                'current_balance': 0,
                'initial_capital': 0,
                'total_profit': 0,
                'profit_percentage': 0,
                'cold_storage_allocation': 0
            },
            'recommendations': []
        }

        for exchange_name, balance_data in balances.items():
            if 'error' in balance_data:
                report['exchanges'][exchange_name] = balance_data
                continue

            current_balance = balance_data['total_usd']
            initial = self.initial_capital.get(exchange_name, 0)
            profit = current_balance - initial
            profit_pct = (profit / initial * 100) if initial > 0 else 0
            allocation = profit * self.COLD_STORAGE_PERCENTAGE

            report['exchanges'][exchange_name] = {
                'current_balance': current_balance,
                'initial_capital': initial,
                'profit': profit,
                'profit_percentage': profit_pct,
                'cold_storage_allocation_30pct': allocation,
                'profitable': profit > 0
            }

            # Update totals
            report['totals']['current_balance'] += current_balance
            report['totals']['initial_capital'] += initial
            report['totals']['total_profit'] += profit

            # Add recommendation if profitable
            if profit > 0 and allocation > 50:  # Minimum $50
                report['recommendations'].append({
                    'exchange': exchange_name,
                    'action': 'MANUAL_WITHDRAWAL',
                    'amount_usd': round(allocation, 2),
                    'suggested_asset': 'USDC',
                    'destination': self.LEDGER_ADDRESSES['USDC'],
                    'note': f'Withdraw ~{allocation:.2f} USDC to cold storage'
                })

        # Calculate overall percentages
        total_profit = report['totals']['total_profit']
        total_initial = report['totals']['initial_capital']
        report['totals']['profit_percentage'] = (
            (total_profit / total_initial * 100) if total_initial > 0 else 0
        )
        report['totals']['cold_storage_allocation'] = total_profit * self.COLD_STORAGE_PERCENTAGE

        return report

    def save_report(self, report: Dict):
        """Save profit report to file"""
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Report saved: {self.report_file}")

    def print_report(self, report: Dict):
        """Print formatted profit report"""
        print("\n" + "="*70)
        print("📊 PROFIT TRACKER REPORT")
        print("="*70)
        print(f"Timestamp: {report['timestamp']}")

        print("\n💰 TOTALS:")
        totals = report['totals']
        print(f"   Current Balance: ${totals['current_balance']:,.2f}")
        print(f"   Initial Capital: ${totals['initial_capital']:,.2f}")
        print(f"   Total Profit: ${totals['total_profit']:,.2f} ({totals['profit_percentage']:.2f}%)")
        print(f"   30% Allocation: ${totals['cold_storage_allocation']:,.2f}")

        print("\n📈 BY EXCHANGE:")
        for exchange_name, data in report['exchanges'].items():
            if 'error' in data:
                print(f"\n   {exchange_name.upper()}: ❌ {data['error']}")
                continue

            print(f"\n   {exchange_name.upper()}:")
            print(f"      Balance: ${data['current_balance']:,.2f}")
            print(f"      Initial: ${data['initial_capital']:,.2f}")
            print(f"      Profit: ${data['profit']:,.2f} ({data['profit_percentage']:.2f}%)")
            print(f"      30% to cold storage: ${data['cold_storage_allocation_30pct']:,.2f}")

        if report['recommendations']:
            print("\n🏦 COLD STORAGE RECOMMENDATIONS:")
            print("   (Manual withdrawal suggested)")
            for rec in report['recommendations']:
                print(f"\n   [{rec['exchange'].upper()}]")
                print(f"   Action: {rec['action']}")
                print(f"   Amount: ${rec['amount_usd']} {rec['suggested_asset']}")
                print(f"   To: {rec['destination'][:10]}...{rec['destination'][-6:]}")
                print(f"   Note: {rec['note']}")
        else:
            print("\n✅ No withdrawals recommended at this time")

        print("\n" + "="*70)

    def run_report(self):
        """Generate complete profit report"""
        print("\n🔍 Fetching exchange balances...")
        balances = self.fetch_exchange_balances()

        print("\n📊 Calculating profits...")
        report = self.calculate_profits(balances)

        self.print_report(report)
        self.save_report(report)

        return report


def main():
    """Run Profit Tracker"""
    tracker = ProfitTracker()
    tracker.run_report()

    print("\n💡 This report is for information only")
    print("   No automatic withdrawals will be executed")
    print("   To withdraw, use your exchange manually")


if __name__ == "__main__":
    main()

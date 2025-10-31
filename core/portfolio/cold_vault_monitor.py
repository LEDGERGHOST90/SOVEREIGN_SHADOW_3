#!/usr/bin/env python3
"""
🏴 COLD VAULT MONITOR - Ledger Hardware Wallet Integration
Comprehensive monitoring system for your $6,600 cold storage vault

Tracks:
- BTC holdings via xpub
- ETH holdings via wallet address
- Historical transaction analysis
- Real-time balance updates
- Cost basis and P&L tracking
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

class ColdVaultMonitor:
    """Monitor Ledger hardware wallet cold storage"""

    def __init__(self):
        # Ledger wallet addresses from CSV export
        self.btc_xpub = "xpub6BgzNEknk2B5tMGRKoNrpCbu435dtAQQXiq1DENttBFToUeZvNtr7CeQhPEGrzGHZ4vyMWQYaR9yH1PNSEFpqDvee1dp49SMxqgBN2K3fg6"
        self.eth_address = "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"

        # CSV data path
        self.csv_path = Path("/Volumes/LegacySafe/Shadow Loop/ZOOP_UNIFICATION/ledgerlive-operations-10.20.2025.csv")

        # Cache
        self.btc_balance = 0.0
        self.eth_balance = 0.0
        self.total_value_usd = 0.0

    def load_ledger_export(self) -> pd.DataFrame:
        """Load Ledger Live CSV export"""
        try:
            df = pd.read_csv(self.csv_path)
            df['Operation Date'] = pd.to_datetime(df['Operation Date'])
            return df
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return None

    def calculate_btc_balance(self, df: pd.DataFrame) -> float:
        """Calculate current BTC balance from transaction history"""
        btc_txs = df[df['Currency Ticker'] == 'BTC'].copy()

        balance = 0.0
        for _, tx in btc_txs.iterrows():
            if tx['Status'] != 'Confirmed':
                continue

            amount = tx['Operation Amount']
            fees = tx['Operation Fees'] if pd.notna(tx['Operation Fees']) else 0

            if tx['Operation Type'] == 'IN':
                balance += amount - fees
            elif tx['Operation Type'] == 'OUT':
                balance -= amount + fees

        return balance

    def calculate_eth_balance(self, df: pd.DataFrame) -> float:
        """Calculate current ETH balance from transaction history"""
        eth_txs = df[df['Currency Ticker'] == 'ETH'].copy()

        balance = 0.0
        for _, tx in eth_txs.iterrows():
            if tx['Status'] not in ['Confirmed', 'Failed']:
                continue

            amount = tx['Operation Amount']
            fees = tx['Operation Fees'] if pd.notna(tx['Operation Fees']) else 0

            if tx['Status'] == 'Failed':
                # Failed transactions only cost gas fees
                balance -= fees
            elif tx['Operation Type'] == 'IN':
                balance += amount - fees
            elif tx['Operation Type'] == 'OUT':
                balance -= amount + fees
            elif tx['Operation Type'] == 'FEES':
                balance -= fees

        return balance

    def get_live_btc_price(self) -> float:
        """Get current BTC price from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "bitcoin", "vs_currencies": "usd"}
            response = requests.get(url, params=params, timeout=10)
            return response.json()['bitcoin']['usd']
        except Exception as e:
            print(f"⚠️  Using fallback BTC price: {e}")
            return 97000  # Fallback

    def get_live_eth_price(self) -> float:
        """Get current ETH price from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "ethereum", "vs_currencies": "usd"}
            response = requests.get(url, params=params, timeout=10)
            return response.json()['ethereum']['usd']
        except Exception as e:
            print(f"⚠️  Using fallback ETH price: {e}")
            return 3900  # Fallback

    def verify_balance_with_blockchain(self) -> Dict[str, float]:
        """
        Verify balances with blockchain explorers

        For production, integrate:
        - Blockstream API for BTC (xpub lookup)
        - Etherscan API for ETH
        - Alchemy/Infura for Web3 queries
        """
        verified = {
            'btc_verified': False,
            'eth_verified': False,
            'btc_balance': self.btc_balance,
            'eth_balance': self.eth_balance
        }

        # ETH balance via Etherscan (requires API key)
        etherscan_key = os.getenv('ETHERSCAN_API_KEY')
        if etherscan_key:
            try:
                url = f"https://api.etherscan.io/api"
                params = {
                    'module': 'account',
                    'action': 'balance',
                    'address': self.eth_address,
                    'tag': 'latest',
                    'apikey': etherscan_key
                }
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                if data['status'] == '1':
                    verified['eth_balance'] = float(data['result']) / 1e18
                    verified['eth_verified'] = True
            except Exception as e:
                print(f"⚠️  Etherscan verification failed: {e}")

        return verified

    def analyze_portfolio(self) -> Dict:
        """Comprehensive portfolio analysis"""
        df = self.load_ledger_export()
        if df is None:
            return None

        # Calculate balances
        self.btc_balance = self.calculate_btc_balance(df)
        self.eth_balance = self.calculate_eth_balance(df)

        # Get live prices
        btc_price = self.get_live_btc_price()
        eth_price = self.get_live_eth_price()

        # Calculate USD values
        btc_value = self.btc_balance * btc_price
        eth_value = self.eth_balance * eth_price
        self.total_value_usd = btc_value + eth_value

        # Calculate cost basis and P&L
        btc_cost_basis = df[df['Currency Ticker'] == 'BTC']['Countervalue at Operation Date'].sum()
        eth_cost_basis = df[df['Currency Ticker'] == 'ETH']['Countervalue at Operation Date'].sum()

        total_pnl = self.total_value_usd - (btc_cost_basis + eth_cost_basis)
        pnl_percent = (total_pnl / (btc_cost_basis + eth_cost_basis) * 100) if (btc_cost_basis + eth_cost_basis) > 0 else 0

        # Transaction summary
        btc_txs = df[df['Currency Ticker'] == 'BTC']
        eth_txs = df[df['Currency Ticker'] == 'ETH']

        return {
            'timestamp': datetime.now().isoformat(),
            'balances': {
                'btc': {
                    'amount': self.btc_balance,
                    'price': btc_price,
                    'value_usd': btc_value
                },
                'eth': {
                    'amount': self.eth_balance,
                    'price': eth_price,
                    'value_usd': eth_value
                }
            },
            'total_value_usd': self.total_value_usd,
            'cost_basis': {
                'btc': btc_cost_basis,
                'eth': eth_cost_basis,
                'total': btc_cost_basis + eth_cost_basis
            },
            'pnl': {
                'unrealized_usd': total_pnl,
                'unrealized_percent': pnl_percent
            },
            'transactions': {
                'btc_count': len(btc_txs),
                'eth_count': len(eth_txs),
                'first_transaction': df['Operation Date'].min().isoformat(),
                'last_transaction': df['Operation Date'].max().isoformat()
            },
            'addresses': {
                'btc_xpub': self.btc_xpub,
                'eth_address': self.eth_address
            }
        }

    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Get most recent transactions"""
        df = self.load_ledger_export()
        if df is None:
            return []

        recent = df.nlargest(limit, 'Operation Date')

        transactions = []
        for _, tx in recent.iterrows():
            transactions.append({
                'date': tx['Operation Date'].isoformat(),
                'currency': tx['Currency Ticker'],
                'type': tx['Operation Type'],
                'amount': tx['Operation Amount'],
                'fees': tx['Operation Fees'],
                'value_usd': tx['Countervalue at Operation Date'],
                'status': tx['Status'],
                'hash': tx['Operation Hash']
            })

        return transactions

    def export_summary(self, output_path: Optional[Path] = None) -> str:
        """Export portfolio summary to JSON"""
        analysis = self.analyze_portfolio()

        if output_path is None:
            output_path = Path(__file__).parent / "logs" / f"cold_vault_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        return str(output_path)


def main():
    """Run cold vault analysis"""
    print("\n" + "="*70)
    print("🏴 SOVEREIGN SHADOW - COLD VAULT MONITOR")
    print("="*70 + "\n")

    monitor = ColdVaultMonitor()
    analysis = monitor.analyze_portfolio()

    if not analysis:
        print("❌ Failed to analyze portfolio")
        return 1

    # Display results
    print("📊 COLD STORAGE PORTFOLIO")
    print("-" * 70)
    print(f"\n💰 BITCOIN")
    print(f"   Balance: {analysis['balances']['btc']['amount']:.8f} BTC")
    print(f"   Price: ${analysis['balances']['btc']['price']:,.2f}")
    print(f"   Value: ${analysis['balances']['btc']['value_usd']:,.2f}")

    print(f"\n💎 ETHEREUM")
    print(f"   Balance: {analysis['balances']['eth']['amount']:.8f} ETH")
    print(f"   Price: ${analysis['balances']['eth']['price']:,.2f}")
    print(f"   Value: ${analysis['balances']['eth']['value_usd']:,.2f}")

    print(f"\n💵 TOTAL VALUE: ${analysis['total_value_usd']:,.2f}")

    print(f"\n📈 PROFIT & LOSS")
    print(f"   Cost Basis: ${analysis['cost_basis']['total']:,.2f}")
    print(f"   Unrealized P&L: ${analysis['pnl']['unrealized_usd']:,.2f} ({analysis['pnl']['unrealized_percent']:.2f}%)")

    print(f"\n📝 TRANSACTION HISTORY")
    print(f"   BTC Transactions: {analysis['transactions']['btc_count']}")
    print(f"   ETH Transactions: {analysis['transactions']['eth_count']}")
    print(f"   First: {analysis['transactions']['first_transaction'][:10]}")
    print(f"   Latest: {analysis['transactions']['last_transaction'][:10]}")

    print(f"\n🔐 WALLET ADDRESSES")
    print(f"   BTC (xpub): {analysis['addresses']['btc_xpub'][:40]}...")
    print(f"   ETH: {analysis['addresses']['eth_address']}")

    # Recent transactions
    print(f"\n📋 RECENT TRANSACTIONS (Last 5)")
    print("-" * 70)
    recent = monitor.get_recent_transactions(5)
    for tx in recent:
        print(f"   {tx['date'][:10]} | {tx['currency']} {tx['type']:4} | {tx['amount']:>12.8f} | ${tx['value_usd']:>8.2f}")

    # Export summary
    output_file = monitor.export_summary()
    print(f"\n✅ Summary exported to: {output_file}")

    print("\n" + "="*70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

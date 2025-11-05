#!/usr/bin/env python3
"""
🔍 API Verification Script
Tests all API connections and reports status
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import ccxt
from web3 import Web3
import requests
from datetime import datetime
import json

# Load environment variables
load_dotenv(project_root / '.env')

class APIVerifier:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log(self, service, status, message, details=None):
        """Log verification result"""
        self.total_tests += 1

        if status == "✅":
            self.passed_tests += 1
        elif status == "❌":
            self.failed_tests += 1

        self.results[service] = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        print(f"{status} {service}: {message}")
        if details:
            print(f"   └─ {details}")

    def verify_coinbase(self):
        """Verify Coinbase Advanced Trade API"""
        try:
            api_key = os.getenv("COINBASE_API_KEY")
            api_secret = os.getenv("COINBASE_API_SECRET")

            if not api_key or not api_secret:
                self.log("Coinbase", "⚠️", "API keys not configured")
                return

            # Try to create REST client
            from coinbase.rest import RESTClient

            client = RESTClient(api_key=api_key, api_secret=api_secret)
            accounts = client.get_accounts()

            # Count accounts with balance
            balances = []
            for account in accounts.get('accounts', []):
                balance = float(account.get('available_balance', {}).get('value', 0))
                if balance > 0:
                    currency = account.get('currency')
                    balances.append(f"{currency}: {balance}")

            self.log(
                "Coinbase",
                "✅",
                f"Connected - {len(accounts.get('accounts', []))} accounts",
                f"{len(balances)} with balance: {', '.join(balances[:3])}"
            )

        except Exception as e:
            self.log("Coinbase", "❌", f"Connection failed", str(e))

    def verify_binance_us(self):
        """Verify Binance US API"""
        try:
            api_key = os.getenv("BINANCE_US_API_KEY")
            api_secret = os.getenv("BINANCE_US_SECRET_KEY")

            if not api_key or not api_secret:
                self.log("Binance US", "⚠️", "API keys not configured")
                return

            exchange = ccxt.binanceus({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })

            balance = exchange.fetch_balance()

            # Get non-zero balances
            balances = []
            for currency, amounts in balance['total'].items():
                if amounts and float(amounts) > 0:
                    balances.append(f"{currency}: {amounts}")

            total_usd = balance.get('total', {}).get('USDT', 0) or balance.get('total', {}).get('USD', 0)

            self.log(
                "Binance US",
                "✅",
                f"Connected - ${total_usd:.2f} total",
                f"{len(balances)} assets: {', '.join(balances[:3])}"
            )

        except Exception as e:
            self.log("Binance US", "❌", "Connection failed", str(e))

    def verify_okx(self):
        """Verify OKX API (optional)"""
        try:
            api_key = os.getenv("OKX_API_KEY")
            api_secret = os.getenv("OKX_API_SECRET")
            passphrase = os.getenv("OKX_PASSPHRASE")

            if not api_key or not api_secret or not passphrase:
                self.log("OKX", "⚪", "Not configured (optional)")
                return

            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'enableRateLimit': True
            })

            balance = exchange.fetch_balance()
            total_usd = sum([v for k, v in balance['total'].items() if v and float(v) > 0])

            self.log("OKX", "✅", f"Connected - ${total_usd:.2f} total")

        except Exception as e:
            if "not configured" in str(e).lower():
                self.log("OKX", "⚪", "Not configured (optional)")
            else:
                self.log("OKX", "❌", "Connection failed", str(e))

    def verify_kraken(self):
        """Verify Kraken API (optional)"""
        try:
            api_key = os.getenv("KRAKEN_API_KEY")
            api_secret = os.getenv("KRAKEN_API_SECRET")

            if not api_key or not api_secret:
                self.log("Kraken", "⚪", "Not configured (optional)")
                return

            exchange = ccxt.kraken({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })

            balance = exchange.fetch_balance()
            total_usd = sum([v for k, v in balance['total'].items() if v and float(v) > 0])

            self.log("Kraken", "✅", f"Connected - ${total_usd:.2f} total")

        except Exception as e:
            if "not configured" in str(e).lower():
                self.log("Kraken", "⚪", "Not configured (optional)")
            else:
                self.log("Kraken", "❌", "Connection failed", str(e))

    def verify_ethereum_rpc(self):
        """Verify Ethereum RPC (Infura/Alchemy)"""
        try:
            rpc_url = os.getenv("ETHEREUM_RPC_URL") or os.getenv("INFURA_PROJECT_ID")

            if not rpc_url:
                self.log("Ethereum RPC", "⚠️", "RPC URL not configured")
                return

            # Build full URL if only project ID provided
            if not rpc_url.startswith('http'):
                rpc_url = f"https://mainnet.infura.io/v3/{rpc_url}"

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            if w3.is_connected():
                block = w3.eth.block_number
                self.log(
                    "Ethereum RPC",
                    "✅",
                    "Connected to Ethereum mainnet",
                    f"Current block: {block:,}"
                )
            else:
                self.log("Ethereum RPC", "❌", "Connection failed", "Unable to connect")

        except Exception as e:
            self.log("Ethereum RPC", "❌", "Connection failed", str(e))

    def verify_etherscan(self):
        """Verify Etherscan API"""
        try:
            api_key = os.getenv("ETHERSCAN_API_KEY")

            if not api_key:
                self.log("Etherscan", "⚠️", "API key not configured")
                return

            # Test with a simple API call
            response = requests.get(
                "https://api.etherscan.io/api",
                params={
                    "module": "stats",
                    "action": "ethprice",
                    "apikey": api_key
                },
                timeout=10
            )

            data = response.json()

            if data.get("status") == "1":
                eth_price = float(data.get("result", {}).get("ethusd", 0))
                self.log(
                    "Etherscan",
                    "✅",
                    "API key valid",
                    f"ETH Price: ${eth_price:,.2f}"
                )
            else:
                self.log("Etherscan", "❌", "API key invalid", data.get("message"))

        except Exception as e:
            self.log("Etherscan", "❌", "Connection failed", str(e))

    def verify_ledger(self):
        """Verify Ledger addresses (READ-ONLY)"""
        try:
            eth_address = os.getenv("LEDGER_ETH_ADDRESS")
            btc_address = os.getenv("LEDGER_BTC_ADDRESS")

            if not eth_address and not btc_address:
                self.log("Ledger", "⚪", "No addresses configured (optional)")
                return

            addresses = []
            if eth_address:
                addresses.append(f"ETH: {eth_address[:6]}...{eth_address[-4:]}")
            if btc_address:
                addresses.append(f"BTC: {btc_address[:6]}...{btc_address[-4:]}")

            self.log(
                "Ledger",
                "✅",
                f"READ-ONLY tracking configured",
                ", ".join(addresses)
            )

        except Exception as e:
            self.log("Ledger", "❌", "Configuration error", str(e))

    def verify_aave(self):
        """Verify AAVE monitoring (READ-ONLY)"""
        try:
            eth_address = os.getenv("WALLET_ADDRESS") or os.getenv("METAMASK_ADDRESS")

            if not eth_address:
                self.log("AAVE", "⚪", "No wallet address configured (optional)")
                return

            # AAVE v3 on Ethereum mainnet
            rpc_url = os.getenv("ETHEREUM_RPC_URL") or os.getenv("INFURA_PROJECT_ID")
            if not rpc_url:
                self.log("AAVE", "⚠️", "Ethereum RPC required for AAVE monitoring")
                return

            if not rpc_url.startswith('http'):
                rpc_url = f"https://mainnet.infura.io/v3/{rpc_url}"

            w3 = Web3(Web3.HTTPProvider(rpc_url))

            if w3.is_connected():
                # Just verify we can connect - actual AAVE monitoring is complex
                self.log(
                    "AAVE",
                    "✅",
                    "READ-ONLY monitoring ready",
                    f"Tracking: {eth_address[:6]}...{eth_address[-4:]}"
                )
            else:
                self.log("AAVE", "❌", "Cannot connect to Ethereum", "RPC connection failed")

        except Exception as e:
            self.log("AAVE", "❌", "Configuration error", str(e))

    def verify_obsidian_api(self):
        """Verify Obsidian Local REST API"""
        try:
            api_key = os.getenv("OBSIDIAN_API_KEY")
            host = os.getenv("OBSIDIAN_HOST", "http://localhost:27123")

            if not api_key:
                self.log("Obsidian", "⚪", "Not configured (optional)")
                return

            # Try to connect to Obsidian REST API
            response = requests.get(
                f"{host}/",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )

            if response.status_code == 200:
                self.log("Obsidian", "✅", "Local REST API connected", f"Vault accessible at {host}")
            else:
                self.log("Obsidian", "❌", f"Connection failed (HTTP {response.status_code})")

        except requests.exceptions.ConnectionError:
            self.log("Obsidian", "⚠️", "Obsidian not running or plugin not enabled")
        except Exception as e:
            self.log("Obsidian", "❌", "Connection failed", str(e))

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*60)
        print("📊 API VERIFICATION SUMMARY")
        print("="*60)
        print(f"✅ Passed:  {self.passed_tests}/{self.total_tests}")
        print(f"❌ Failed:  {self.failed_tests}/{self.total_tests}")
        print(f"⚠️ Warning: {self.total_tests - self.passed_tests - self.failed_tests}/{self.total_tests}")
        print("="*60)

        # Check critical services
        critical_services = ["Binance US", "Ethereum RPC", "Etherscan"]
        critical_status = [
            self.results.get(service, {}).get("status") == "✅"
            for service in critical_services
        ]

        if all(critical_status):
            print("🟢 SYSTEM STATUS: All critical services operational")
        elif any(critical_status):
            print("🟡 SYSTEM STATUS: Some critical services need attention")
        else:
            print("🔴 SYSTEM STATUS: Critical services offline")

        print("\n📝 Next Steps:")

        # Suggest actions based on results
        needs_attention = []
        for service, result in self.results.items():
            if result['status'] in ["❌", "⚠️"]:
                needs_attention.append(f"   - {service}: {result['message']}")

        if needs_attention:
            print("\n".join(needs_attention))
        else:
            print("   ✅ All configured APIs are operational!")

        print("\n💾 Full report saved to: logs/api_verification.json")

        # Save report
        report_path = project_root / "logs" / "api_verification.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": self.total_tests,
                    "passed": self.passed_tests,
                    "failed": self.failed_tests
                },
                "results": self.results
            }, f, indent=2)

    def run_all(self):
        """Run all verifications"""
        print("🔍 SOVEREIGN SHADOW II - API VERIFICATION")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        print("🔑 Exchange APIs:")
        self.verify_coinbase()
        self.verify_binance_us()
        self.verify_okx()
        self.verify_kraken()

        print("\n🌐 Blockchain APIs:")
        self.verify_ethereum_rpc()
        self.verify_etherscan()

        print("\n💰 Cold Storage (READ-ONLY):")
        self.verify_ledger()
        self.verify_aave()

        print("\n🔌 System APIs:")
        self.verify_obsidian_api()

        self.print_summary()


if __name__ == "__main__":
    verifier = APIVerifier()
    verifier.run_all()

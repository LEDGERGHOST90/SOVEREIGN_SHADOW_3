#!/usr/bin/env python3
"""
💉 EXCHANGE INJECTION PROTOCOL
Standardized data injection system for all exchanges and wallets

Platforms Supported:
1. Ledger (cold storage)
2. Coinbase
3. Binance US
4. OKX
5. Kraken

Each platform follows the same injection format for seamless integration
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("exchange_injection")

class ExchangeInjector(ABC):
    """
    Base class for all exchange injectors

    All exchanges must implement this interface for standardized data injection
    """

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logs_path = Path("/Volumes/LegacySafe/SovereignShadow 2/logs/injections")
        self.logs_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch_balances(self) -> Dict[str, Any]:
        """
        Fetch current balances from exchange

        Must return standardized format:
        {
            'platform': str,
            'total_usd': float,
            'assets': {
                'ASSET_SYMBOL': {
                    'balance': float,
                    'price_usd': float,
                    'value_usd': float,
                    'allocation_pct': float
                }
            },
            'status': str,
            'timestamp': str
        }
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test API connection to exchange"""
        pass

    def inject_data(self, force: bool = False, cache_minutes: int = 120) -> bool:
        """
        Standard injection flow with caching:
        1. Check cache (skip if recent and not forced)
        2. Test connection
        3. Fetch balances
        4. Validate data
        5. Save to injection file

        Args:
            force: Force fresh data fetch ignoring cache
            cache_minutes: Cache validity duration (default 120 min = 2 calls/4hr = 1 ETH RPC/hour = 24/day)
        """
        try:
            # Check cache first (unless forced)
            if not force:
                filename = f"{self.platform_name.lower().replace(' ', '_')}_injection.json"
                filepath = self.logs_path / filename

                if filepath.exists():
                    file_age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
                    if file_age.total_seconds() < (cache_minutes * 60):
                        logger.info(f"⚡ {self.platform_name} using cached data (age: {file_age.total_seconds()/60:.1f} min)")
                        return True

            logger.info(f"💉 Injecting fresh data from {self.platform_name}...")

            # Test connection
            if not self.test_connection():
                logger.error(f"❌ Connection test failed for {self.platform_name}")
                self._save_empty_injection()
                return False

            # Fetch balances
            data = self.fetch_balances()

            # Validate
            if not self._validate_data(data):
                logger.error(f"❌ Invalid data format from {self.platform_name}")
                self._save_empty_injection()
                return False

            # Save injection
            self._save_injection(data)
            logger.info(f"✅ {self.platform_name} data injected: ${data.get('total_usd', 0):.2f}")

            return True

        except Exception as e:
            logger.error(f"❌ Error injecting {self.platform_name} data: {e}")
            self._save_empty_injection()
            return False

    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data follows standard format"""
        required_fields = ['platform', 'total_usd', 'assets', 'status', 'timestamp']
        return all(field in data for field in required_fields)

    def _save_injection(self, data: Dict[str, Any]):
        """Save injection data to file"""
        filename = f"{self.platform_name.lower().replace(' ', '_')}_injection.json"
        filepath = self.logs_path / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.debug(f"📁 Saved to: {filepath}")

    def _save_empty_injection(self):
        """Save empty injection when connection fails"""
        empty_data = {
            'platform': self.platform_name,
            'total_usd': 0.0,
            'assets': {},
            'status': 'injection_failed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self._save_injection(empty_data)


class LedgerInjector(ExchangeInjector):
    """Ledger cold storage injector"""

    def __init__(self):
        super().__init__("Ledger")
        self.eth_address = "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"
        self.btc_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

    def test_connection(self) -> bool:
        """Test blockchain connection via AAVE monitor"""
        try:
            from safety.aave_monitor import AAVEMonitor
            monitor = AAVEMonitor()
            return monitor.w3.is_connected()
        except Exception as e:
            logger.error(f"Ledger connection test failed: {e}")
            return False

    def fetch_balances(self) -> Dict[str, Any]:
        """Fetch Ledger balances via blockchain"""
        from safety.aave_monitor import AAVEMonitor
        import requests

        monitor = AAVEMonitor()
        w3 = monitor.w3

        # Get live prices
        try:
            prices_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin,wrapped-steth,solana,ripple&vs_currencies=usd', timeout=5)
            prices = prices_response.json()
            eth_price = prices.get('ethereum', {}).get('usd', 3834.0)
            btc_price = prices.get('bitcoin', {}).get('usd', 109500.0)
            wsteth_price = prices.get('wrapped-steth', {}).get('usd', 4664.0)
            sol_price = prices.get('solana', {}).get('usd', 200.0)
            xrp_price = prices.get('ripple', {}).get('usd', 2.48)
        except:
            # Fallback prices
            eth_price = 3834.0
            btc_price = 109500.0
            wsteth_price = 4664.0
            sol_price = 200.0
            xrp_price = 2.48

        assets = {}

        # Get ETH balance
        try:
            eth_balance_wei = w3.eth.get_balance(self.eth_address)
            eth_balance = float(w3.from_wei(eth_balance_wei, 'ether'))
            if eth_balance > 0:
                assets['ETH'] = {
                    'balance': eth_balance,
                    'price_usd': eth_price,
                    'value_usd': eth_balance * eth_price,
                    'address': self.eth_address
                }
        except Exception as e:
            logger.warning(f"Could not fetch ETH balance: {e}")

        # Get wstETH token balance (ERC-20)
        try:
            wsteth_contract_address = '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            wsteth_abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
            wsteth_contract = w3.eth.contract(address=wsteth_contract_address, abi=wsteth_abi)
            wsteth_balance_wei = wsteth_contract.functions.balanceOf(self.eth_address).call()
            wsteth_balance = float(w3.from_wei(wsteth_balance_wei, 'ether'))
            if wsteth_balance > 0:
                assets['wstETH'] = {
                    'balance': wsteth_balance,
                    'price_usd': wsteth_price,
                    'value_usd': wsteth_balance * wsteth_price,
                    'address': self.eth_address,
                    'token_address': wsteth_contract_address
                }
        except Exception as e:
            logger.warning(f"Could not fetch wstETH balance: {e}")

        # Get BTC balance (via blockchain API)
        try:
            btc_response = requests.get(f'https://blockchain.info/q/addressbalance/{self.btc_address}', timeout=5)
            btc_balance_satoshis = int(btc_response.text)
            btc_balance = btc_balance_satoshis / 100000000.0  # Convert satoshis to BTC
            if btc_balance > 0:
                assets['BTC'] = {
                    'balance': btc_balance,
                    'price_usd': btc_price,
                    'value_usd': btc_balance * btc_price,
                    'address': self.btc_address
                }
        except Exception as e:
            logger.warning(f"Could not fetch BTC balance: {e}")

        # Add XRP balance
        # TODO: Query XRP ledger for live balance
        xrp_balance = 1.00054  # From screenshot
        if xrp_balance > 0:
            assets['XRP'] = {
                'balance': xrp_balance,
                'price_usd': xrp_price,
                'value_usd': xrp_balance * xrp_price,
                'note': 'static_balance_pending_api'
            }

        # Add SOL balance
        # TODO: Query Solana blockchain for live balance
        # Commenting out SOL for now as balance not shown in screenshot
        # sol_balance = 0.0
        # if sol_balance > 0:
        #     assets['SOL'] = {
        #         'balance': sol_balance,
        #         'price_usd': sol_price,
        #         'value_usd': sol_balance * sol_price
        #     }

        # Calculate total and allocation percentages
        total_usd = sum(asset['value_usd'] for asset in assets.values())

        for asset in assets.values():
            asset['allocation_pct'] = (asset['value_usd'] / total_usd * 100) if total_usd > 0 else 0

        return {
            'platform': 'Ledger',
            'total_usd': total_usd,
            'assets': assets,
            'status': 'live_blockchain',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'addresses': {
                'eth': self.eth_address,
                'btc': self.btc_address
            }
        }


class CoinbaseInjector(ExchangeInjector):
    """Coinbase exchange injector"""

    def __init__(self):
        super().__init__("Coinbase")
        self.api_key = os.getenv('COINBASE_EXCHANGE_API_KEY')
        self.api_secret = os.getenv('COINBASE_EXCHANGE_SECRET')

    def test_connection(self) -> bool:
        """Test Coinbase API connection"""
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️  Coinbase API keys not configured")
            return True  # Allow static data injection

        # TODO: Implement actual API test
        return True

    def fetch_balances(self) -> Dict[str, Any]:
        """Fetch Coinbase balances"""
        if not self.api_key or not self.api_secret:
            # Return static data from screenshots until API configured
            assets = {
                'USDC': {
                    'balance': 40.38,
                    'price_usd': 1.0,
                    'value_usd': 40.38,
                    'allocation_pct': 2.16,
                    'apy': 4.25
                },
                'CRYPTO_PORTFOLIO': {
                    'balance': 1.0,
                    'price_usd': 1828.97,
                    'value_usd': 1828.97,
                    'allocation_pct': 97.84
                }
            }

            return {
                'platform': 'Coinbase',
                'total_usd': 1869.36,
                'assets': assets,
                'status': 'static_data',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        # TODO: Implement Coinbase Exchange API
        # from coinbase.wallet.client import Client
        # client = Client(self.api_key, self.api_secret)
        # accounts = client.get_accounts()

        return {
            'platform': 'Coinbase',
            'total_usd': 1869.36,
            'assets': {},
            'status': 'api_pending',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


class BinanceUSInjector(ExchangeInjector):
    """Binance US exchange injector"""

    def __init__(self):
        super().__init__("Binance_US")
        self.api_key = os.getenv('BINANCE_US_API_KEY')
        self.api_secret = os.getenv('BINANCE_US_SECRET_KEY')

    def test_connection(self) -> bool:
        """Test Binance US API connection"""
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️  Binance US API keys not configured")
            return True  # Allow static data

        # TODO: Implement actual API test
        return True

    def fetch_balances(self) -> Dict[str, Any]:
        """Fetch Binance US balances"""
        if not self.api_key or not self.api_secret:
            # Return static known balance
            return {
                'platform': 'Binance_US',
                'total_usd': 150.0,
                'assets': {},
                'status': 'static_data',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        # TODO: Implement Binance US API
        # from binance.us import Client
        # client = Client(self.api_key, self.api_secret)
        # balances = client.get_account()['balances']

        return {
            'platform': 'Binance_US',
            'total_usd': 150.0,
            'assets': {},
            'status': 'api_pending',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


class OKXInjector(ExchangeInjector):
    """OKX exchange injector"""

    def __init__(self):
        super().__init__("OKX")
        self.api_key = os.getenv('OKX_API_KEY')
        self.secret_key = os.getenv('OKX_SECRET_KEY')
        self.passphrase = os.getenv('OKX_PASSPHRASE')

    def test_connection(self) -> bool:
        """Test OKX API connection"""
        if not self.api_key or not self.secret_key or not self.passphrase:
            logger.warning("⚠️  OKX API keys not configured")
            return True

        # TODO: Implement actual API test
        return True

    def fetch_balances(self) -> Dict[str, Any]:
        """Fetch OKX balances"""
        if not self.api_key or not self.secret_key:
            return {
                'platform': 'OKX',
                'total_usd': 0.0,
                'assets': {},
                'status': 'static_data',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        # TODO: Implement OKX API
        # import okx
        # client = okx.Account(self.api_key, self.secret_key, self.passphrase)
        # balances = client.get_balance()

        return {
            'platform': 'OKX',
            'total_usd': 0.0,
            'assets': {},
            'status': 'api_pending',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


class KrakenInjector(ExchangeInjector):
    """Kraken exchange injector"""

    def __init__(self):
        super().__init__("Kraken")
        self.api_key = os.getenv('KRAKEN_API_KEY')
        self.private_key = os.getenv('KRAKEN_PRIVATE_KEY')

    def test_connection(self) -> bool:
        """Test Kraken API connection"""
        if not self.api_key or not self.private_key:
            logger.warning("⚠️  Kraken API keys not configured")
            return True

        # TODO: Implement actual API test
        return True

    def fetch_balances(self) -> Dict[str, Any]:
        """Fetch Kraken balances"""
        if not self.api_key or not self.private_key:
            return {
                'platform': 'Kraken',
                'total_usd': 4.63,
                'assets': {},
                'status': 'static_data',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        # TODO: Implement Kraken API
        # import krakenex
        # client = krakenex.API(key=self.api_key, secret=self.private_key)
        # balances = client.query_private('Balance')

        return {
            'platform': 'Kraken',
            'total_usd': 4.63,
            'assets': {},
            'status': 'api_pending',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


class InjectionManager:
    """
    Central manager for all exchange injections

    Coordinates data injection from all platforms
    """

    def __init__(self):
        self.injectors = [
            LedgerInjector(),
            CoinbaseInjector(),
            BinanceUSInjector(),
            OKXInjector(),
            KrakenInjector()
        ]

        logger.info("💉 Injection Manager initialized with 5 platforms")

    def inject_all(self) -> Dict[str, bool]:
        """Inject data from all platforms"""
        results = {}

        logger.info("\n" + "="*70)
        logger.info("💉 EXCHANGE INJECTION PROTOCOL - Starting Full Injection")
        logger.info("="*70)

        for injector in self.injectors:
            success = injector.inject_data()
            results[injector.platform_name] = success

        # Summary
        total = len(results)
        successful = sum(results.values())

        logger.info("\n" + "="*70)
        logger.info(f"📊 INJECTION SUMMARY: {successful}/{total} platforms successful")
        logger.info("="*70)

        for platform, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {status} {platform}")

        return results

    def get_aggregated_data(self) -> Dict[str, Any]:
        """Aggregate all injected data"""
        logs_path = Path("/Volumes/LegacySafe/SovereignShadow 2/logs/injections")

        aggregated = {
            'platforms': {},
            'total_portfolio_usd': 0.0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        for injector in self.injectors:
            filename = f"{injector.platform_name.lower().replace(' ', '_')}_injection.json"
            filepath = logs_path / filename

            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    platform_total = data.get('total_usd', 0.0)
                    aggregated['platforms'][injector.platform_name] = data
                    aggregated['total_portfolio_usd'] += platform_total

        return aggregated


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("💉 EXCHANGE INJECTION PROTOCOL")
    print("="*70)
    print()
    print("Standardized data injection for 5 platforms:")
    print("  1. Ledger (cold storage)")
    print("  2. Coinbase")
    print("  3. Binance US")
    print("  4. OKX")
    print("  5. Kraken")
    print()

    # Create manager and inject all
    manager = InjectionManager()
    results = manager.inject_all()

    # Get aggregated data
    aggregated = manager.get_aggregated_data()

    print()
    print("="*70)
    print(f"💰 TOTAL PORTFOLIO: ${aggregated['total_portfolio_usd']:,.2f}")
    print("="*70)
    print()
    print(f"📁 Injection files saved to:")
    print(f"   /Volumes/LegacySafe/SovereignShadow 2/logs/injections/")
    print()

if __name__ == "__main__":
    main()

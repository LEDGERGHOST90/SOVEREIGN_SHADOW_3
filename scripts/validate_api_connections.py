#!/usr/bin/env python3
"""
🔐 API CONNECTION VALIDATOR
Tests all exchange API connections and validates permissions

Usage:
    python3 validate_api_connections.py
    python3 validate_api_connections.py --exchange coinbase
    python3 validate_api_connections.py --full-test
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import ccxt
from datetime import datetime
import json

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class ExchangeValidator:
    """Validate exchange API connections and permissions"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'exchanges': {},
            'summary': {
                'tested': 0,
                'working': 0,
                'failed': 0
            }
        }
    
    def test_coinbase(self):
        """Test Coinbase Advanced Trade API"""
        exchange_name = "Coinbase"
        print(f"\n🔍 Testing {exchange_name}...")
        
        try:
            api_key = os.getenv('COINBASE_API_KEY')
            secret = os.getenv('COINBASE_API_SECRET')
            
            if not api_key or not secret:
                raise ValueError("API credentials not found in environment")
            
            exchange = ccxt.coinbase({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            })
            
            # Test connection
            balance = exchange.fetch_balance()
            markets = exchange.fetch_markets()
            
            # Calculate total balance
            total_usd = 0
            assets = {}
            for currency, amount in balance['total'].items():
                if amount > 0:
                    assets[currency] = amount
                    # Rough USD estimation (would need price data for accurate conversion)
                    if currency == 'USD':
                        total_usd += amount
            
            self.results['exchanges'][exchange_name] = {
                'status': 'connected',
                'balance_usd': total_usd,
                'assets': assets,
                'markets_available': len(markets),
                'api_key': f"{api_key[:10]}..." if api_key else None
            }
            
            print(f"   ✅ Connected successfully")
            print(f"   💰 Balance: ${total_usd:.2f} USD")
            print(f"   📊 Assets: {list(assets.keys())}")
            print(f"   🔗 Markets: {len(markets)} available")
            
            self.results['summary']['working'] += 1
            return True
            
        except Exception as e:
            self.results['exchanges'][exchange_name] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"   ❌ Connection failed: {str(e)[:100]}")
            self.results['summary']['failed'] += 1
            return False
        finally:
            self.results['summary']['tested'] += 1
    
    def test_okx(self):
        """Test OKX API"""
        exchange_name = "OKX"
        print(f"\n🔍 Testing {exchange_name}...")
        
        try:
            api_key = os.getenv('OKX_API_KEY')
            secret = os.getenv('OKX_SECRET_KEY')
            passphrase = os.getenv('OKX_PASSPHRASE')
            
            if not all([api_key, secret, passphrase]):
                raise ValueError("API credentials not found in environment")
            
            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': secret,
                'password': passphrase,
                'enableRateLimit': True
            })
            
            # Test connection
            balance = exchange.fetch_balance()
            
            total_usd = balance.get('total', {}).get('USDT', 0)
            assets = {k: v for k, v in balance['total'].items() if v > 0}
            
            self.results['exchanges'][exchange_name] = {
                'status': 'connected',
                'balance_usdt': total_usd,
                'assets': assets,
                'api_key': f"{api_key[:10]}..." if api_key else None
            }
            
            print(f"   ✅ Connected successfully")
            print(f"   💰 Balance: ${total_usd:.2f} USDT")
            print(f"   📊 Assets: {list(assets.keys())}")
            
            self.results['summary']['working'] += 1
            return True
            
        except Exception as e:
            self.results['exchanges'][exchange_name] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"   ❌ Connection failed: {str(e)[:100]}")
            self.results['summary']['failed'] += 1
            return False
        finally:
            self.results['summary']['tested'] += 1
    
    def test_kraken(self):
        """Test Kraken API"""
        exchange_name = "Kraken"
        print(f"\n🔍 Testing {exchange_name}...")
        
        try:
            api_key = os.getenv('KRAKEN_API_KEY')
            secret = os.getenv('KRAKEN_PRIVATE_KEY')
            
            if not api_key or not secret:
                raise ValueError("API credentials not found in environment")
            
            exchange = ccxt.kraken({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            })
            
            # Test connection
            balance = exchange.fetch_balance()
            
            total_usd = balance.get('total', {}).get('USD', 0)
            assets = {k: v for k, v in balance['total'].items() if v > 0}
            
            self.results['exchanges'][exchange_name] = {
                'status': 'connected',
                'balance_usd': total_usd,
                'assets': assets,
                'api_key': f"{api_key[:10]}..." if api_key else None
            }
            
            print(f"   ✅ Connected successfully")
            print(f"   💰 Balance: ${total_usd:.2f} USD")
            print(f"   📊 Assets: {list(assets.keys())}")
            
            self.results['summary']['working'] += 1
            return True
            
        except Exception as e:
            self.results['exchanges'][exchange_name] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"   ❌ Connection failed: {str(e)[:100]}")
            self.results['summary']['failed'] += 1
            return False
        finally:
            self.results['summary']['tested'] += 1
    
    def test_binance_us(self):
        """Test Binance US API"""
        exchange_name = "Binance US"
        print(f"\n🔍 Testing {exchange_name}...")
        
        try:
            api_key = os.getenv('BINANCE_US_API_KEY')
            secret = os.getenv('BINANCE_US_SECRET')
            
            if not api_key or not secret:
                raise ValueError("API credentials not found in environment")
            
            exchange = ccxt.binanceus({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            })
            
            # Test connection
            balance = exchange.fetch_balance()
            
            total_usd = balance.get('total', {}).get('USD', 0)
            assets = {k: v for k, v in balance['total'].items() if v > 0}
            
            self.results['exchanges'][exchange_name] = {
                'status': 'connected',
                'balance_usd': total_usd,
                'assets': assets,
                'api_key': f"{api_key[:10]}..." if api_key else None
            }
            
            print(f"   ✅ Connected successfully")
            print(f"   💰 Balance: ${total_usd:.2f} USD")
            print(f"   📊 Assets: {list(assets.keys())}")
            
            self.results['summary']['working'] += 1
            return True
            
        except Exception as e:
            self.results['exchanges'][exchange_name] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"   ❌ Connection failed: {str(e)[:100]}")
            self.results['summary']['failed'] += 1
            return False
        finally:
            self.results['summary']['tested'] += 1
    
    def run_all_tests(self):
        """Run validation on all exchanges"""
        print("\n" + "="*70)
        print("🔐 SOVEREIGN SHADOW - API CONNECTION VALIDATOR")
        print("="*70)
        
        self.test_coinbase()
        self.test_okx()
        self.test_kraken()
        self.test_binance_us()
        
        # Summary
        print("\n" + "="*70)
        print("📊 VALIDATION SUMMARY")
        print("="*70)
        print(f"   Total Tested: {self.results['summary']['tested']}")
        print(f"   ✅ Working: {self.results['summary']['working']}")
        print(f"   ❌ Failed: {self.results['summary']['failed']}")
        
        # Verdict
        if self.results['summary']['working'] >= 2:
            print("\n✅ SUFFICIENT EXCHANGES FOR TRADING")
            print("   At least 2 exchanges connected - arbitrage possible")
            status = 0
        else:
            print("\n⚠️  INSUFFICIENT EXCHANGES")
            print("   Need at least 2 working exchanges for arbitrage")
            status = 1
        
        # Save results
        results_file = Path(__file__).parent.parent / "logs" / "api_validation.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
        print("="*70 + "\n")
        
        return status


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate exchange API connections")
    parser.add_argument('--exchange', help="Test specific exchange (coinbase, okx, kraken, binance)")
    parser.add_argument('--full-test', action='store_true', help="Run comprehensive tests")
    
    args = parser.parse_args()
    
    validator = ExchangeValidator()
    
    if args.exchange:
        exchange = args.exchange.lower()
        if exchange == 'coinbase':
            validator.test_coinbase()
        elif exchange == 'okx':
            validator.test_okx()
        elif exchange == 'kraken':
            validator.test_kraken()
        elif exchange == 'binance':
            validator.test_binance_us()
        else:
            print(f"Unknown exchange: {exchange}")
            sys.exit(1)
    else:
        status = validator.run_all_tests()
        sys.exit(status)


if __name__ == "__main__":
    main()


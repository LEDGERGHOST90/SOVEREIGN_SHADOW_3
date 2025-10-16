#!/usr/bin/env python3
"""
🚀 COMPLETE EXCHANGE API SETUP
Setup and testing for OKX, Kraken, and Coinbase exchanges
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_enhanced/all_exchanges_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("all_exchanges_setup")

class AllExchangesSetup:
    """Setup and test OKX, Kraken, and Coinbase APIs"""
    
    def __init__(self):
        self.exchanges = {}
        self.test_results = {}
        
        logger.info("🚀 Complete Exchange API Setup Initialized")
    
    def setup_okx_api(self):
        """Setup OKX API configuration"""
        logger.info("🔧 Setting up OKX API...")
        
        okx_config = {
            'api_key': os.getenv('OKX_API_KEY', ''),
            'secret_key': os.getenv('OKX_SECRET_KEY', ''),
            'passphrase': os.getenv('OKX_PASSPHRASE', ''),
            'sandbox': os.getenv('OKX_SANDBOX', 'true').lower() == 'true',
            'base_url': 'https://www.okx.com',
            'rate_limit': 20,  # 20 requests per second
            'timeout': 30000,
            'pairs': ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT', 'BNB-USDT']
        }
        
        self.exchanges['okx'] = okx_config
        
        if not okx_config['api_key'] or not okx_config['secret_key'] or not okx_config['passphrase']:
            logger.warning("⚠️  OKX API keys not found")
            return False
        
        logger.info("✅ OKX API configuration loaded")
        return True
    
    def setup_kraken_api(self):
        """Setup Kraken API configuration"""
        logger.info("🔧 Setting up Kraken API...")
        
        kraken_config = {
            'api_key': os.getenv('KRAKEN_API_KEY', ''),
            'secret_key': os.getenv('KRAKEN_SECRET_KEY', ''),
            'sandbox': False,  # Kraken doesn't have sandbox
            'base_url': 'https://api.kraken.com',
            'rate_limit': 1,  # 1 request per second
            'timeout': 30000,
            'pairs': ['XXBTZUSD', 'XETHZUSD', 'SOLUSD', 'ADAUSD', 'BNBUSD']
        }
        
        self.exchanges['kraken'] = kraken_config
        
        if not kraken_config['api_key'] or not kraken_config['secret_key']:
            logger.warning("⚠️  Kraken API keys not found")
            return False
        
        logger.info("✅ Kraken API configuration loaded")
        return True
    
    def setup_coinbase_api(self):
        """Setup Coinbase API configuration"""
        logger.info("🔧 Setting up Coinbase API...")
        
        coinbase_config = {
            'api_key': os.getenv('COINBASE_SANDBOX_KEY', ''),
            'secret_key': os.getenv('COINBASE_SANDBOX_SECRET', ''),
            'sandbox': True,  # Using sandbox for safety
            'base_url': 'https://api-public.sandbox.pro.coinbase.com',
            'ws_url': 'wss://ws-feed-public.sandbox.pro.coinbase.com',
            'rate_limit': 10,  # 10 requests per second
            'timeout': 30000,
            'pairs': ['BTC-USD', 'ETH-USD', 'LTC-USD', 'ADA-USD', 'SOL-USD']
        }
        
        self.exchanges['coinbase'] = coinbase_config
        
        if not coinbase_config['api_key'] or not coinbase_config['secret_key']:
            logger.warning("⚠️  Coinbase API keys not found")
            return False
        
        logger.info("✅ Coinbase API configuration loaded")
        return True
    
    def test_okx_connection(self):
        """Test OKX API connection"""
        logger.info("🧪 Testing OKX API connection...")
        
        try:
            import ccxt
            
            okx = ccxt.okx({
                'apiKey': self.exchanges['okx']['api_key'],
                'secret': self.exchanges['okx']['secret_key'],
                'password': self.exchanges['okx']['passphrase'],
                'sandbox': self.exchanges['okx']['sandbox'],
                'enableRateLimit': True,
                'rateLimit': 1000 // self.exchanges['okx']['rate_limit'],
                'timeout': self.exchanges['okx']['timeout'],
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            markets = okx.load_markets()
            ticker = okx.fetch_ticker('BTC/USDT')
            
            logger.info(f"✅ OKX connection successful - {len(markets)} markets, BTC/USDT: ${ticker['last']}")
            
            self.test_results['okx'] = {
                'status': 'SUCCESS',
                'markets_count': len(markets),
                'test_price': ticker['last'],
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except ImportError:
            logger.error("❌ CCXT library not installed. Run: pip install ccxt")
            self.test_results['okx'] = {'status': 'ERROR', 'error': 'CCXT not installed'}
            return False
        except Exception as e:
            logger.error(f"❌ OKX connection failed: {e}")
            self.test_results['okx'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_kraken_connection(self):
        """Test Kraken API connection"""
        logger.info("🧪 Testing Kraken API connection...")
        
        try:
            import ccxt
            
            kraken = ccxt.kraken({
                'apiKey': self.exchanges['kraken']['api_key'],
                'secret': self.exchanges['kraken']['secret_key'],
                'enableRateLimit': True,
                'rateLimit': 3000,
                'timeout': self.exchanges['kraken']['timeout'],
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            markets = kraken.load_markets()
            ticker = kraken.fetch_ticker('BTC/USD')
            
            logger.info(f"✅ Kraken connection successful - {len(markets)} markets, BTC/USD: ${ticker['last']}")
            
            self.test_results['kraken'] = {
                'status': 'SUCCESS',
                'markets_count': len(markets),
                'test_price': ticker['last'],
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except ImportError:
            logger.error("❌ CCXT library not installed. Run: pip install ccxt")
            self.test_results['kraken'] = {'status': 'ERROR', 'error': 'CCXT not installed'}
            return False
        except Exception as e:
            logger.error(f"❌ Kraken connection failed: {e}")
            self.test_results['kraken'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_coinbase_connection(self):
        """Test Coinbase API connection"""
        logger.info("🧪 Testing Coinbase API connection...")
        
        try:
            import ccxt
            
            # Use Coinbase Exchange for API access
            coinbase = ccxt.coinbaseexchange({
                'apiKey': self.exchanges['coinbase']['api_key'],
                'secret': self.exchanges['coinbase']['secret_key'],
                'sandbox': self.exchanges['coinbase']['sandbox'],
                'enableRateLimit': True,
                'rateLimit': 1000 // self.exchanges['coinbase']['rate_limit'],
                'timeout': self.exchanges['coinbase']['timeout'],
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            markets = coinbase.load_markets()
            ticker = coinbase.fetch_ticker('BTC/USD')
            
            logger.info(f"✅ Coinbase connection successful - {len(markets)} markets, BTC/USD: ${ticker['last']}")
            
            self.test_results['coinbase'] = {
                'status': 'SUCCESS',
                'markets_count': len(markets),
                'test_price': ticker['last'],
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except ImportError:
            logger.error("❌ CCXT library not installed. Run: pip install ccxt")
            self.test_results['coinbase'] = {'status': 'ERROR', 'error': 'CCXT not installed'}
            return False
        except Exception as e:
            logger.error(f"❌ Coinbase connection failed: {e}")
            self.test_results['coinbase'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def create_environment_template(self):
        """Create comprehensive environment template"""
        logger.info("📝 Creating environment template...")
        
        template_content = """# COMPLETE EXCHANGE API CONFIGURATION
# Copy this to your .env file and fill in your actual API keys

# OKX API Configuration
# Get your keys from: https://www.okx.com/account/my-api
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here
OKX_SANDBOX=true  # Set to false for live trading

# Kraken API Configuration  
# Get your keys from: https://www.kraken.com/features/api
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_SECRET_KEY=your_kraken_secret_key_here

# Coinbase Sandbox API Configuration
# Get your keys from: https://pro.coinbase.com/ (sandbox mode)
COINBASE_SANDBOX_KEY=your_coinbase_sandbox_api_key_here
COINBASE_SANDBOX_SECRET=your_coinbase_sandbox_secret_key_here

# Note: Kraken doesn't have sandbox mode - use with caution!
# Coinbase sandbox is recommended for testing
"""
        
        with open('all_exchanges_api_template.env', 'w') as f:
            f.write(template_content)
        
        logger.info("✅ Environment template created: all_exchanges_api_template.env")
    
    def generate_setup_report(self):
        """Generate comprehensive setup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': {}
        }
        
        for exchange_name, config in self.exchanges.items():
            report['exchanges'][exchange_name] = {
                'configured': bool(config.get('api_key')),
                'sandbox': config.get('sandbox', False),
                'test_result': self.test_results.get(exchange_name, {}),
                'config': {
                    'rate_limit': config.get('rate_limit'),
                    'pairs': config.get('pairs', [])
                }
            }
        
        # Add recommendations
        report['recommendations'] = []
        for exchange_name, status in report['exchanges'].items():
            if not status['configured']:
                report['recommendations'].append(f"Set up {exchange_name.upper()} API keys in environment variables")
            if status['test_result'].get('status') == 'ERROR':
                report['recommendations'].append(f"Fix {exchange_name.upper()} API connection issues")
        
        return report
    
    def display_setup_status(self):
        """Display comprehensive setup status"""
        report = self.generate_setup_report()
        
        print("\n" + "="*80)
        print("🚀 COMPLETE EXCHANGE API SETUP STATUS")
        print("="*80)
        print(f"📅 Timestamp: {report['timestamp']}")
        
        for exchange_name, status in report['exchanges'].items():
            print(f"\n🔧 {exchange_name.upper()} CONFIGURATION:")
            print("-" * 40)
            config_status = "✅ CONFIGURED" if status['configured'] else "❌ NOT CONFIGURED"
            print(f"Status: {config_status}")
            print(f"Sandbox Mode: {status['sandbox']}")
            print(f"Rate Limit: {status['config']['rate_limit']} req/sec")
            print(f"Test Result: {status['test_result'].get('status', 'NOT TESTED')}")
            if 'test_price' in status['test_result']:
                print(f"Test Price: ${status['test_result']['test_price']}")
        
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            print("-" * 40)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("="*80)
        
        return report
    
    def run_setup(self):
        """Run complete setup process"""
        logger.info("🚀 Starting complete exchange API setup...")
        
        # Setup configurations
        okx_configured = self.setup_okx_api()
        kraken_configured = self.setup_kraken_api()
        coinbase_configured = self.setup_coinbase_api()
        
        # Test connections if configured
        if okx_configured:
            self.test_okx_connection()
        
        if kraken_configured:
            self.test_kraken_connection()
        
        if coinbase_configured:
            self.test_coinbase_connection()
        
        # Create environment template
        self.create_environment_template()
        
        # Display status
        report = self.display_setup_status()
        
        # Save report
        with open('logs/ai_enhanced/all_exchanges_setup_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📄 Setup report saved to: logs/ai_enhanced/all_exchanges_setup_report.json")
        
        return report

def main():
    """Main function"""
    setup = AllExchangesSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()

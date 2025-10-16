#!/usr/bin/env python3
"""
🚀 OKX & KRAKEN API SETUP
Comprehensive setup and testing for OKX and Kraken exchanges
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
        logging.FileHandler('logs/ai_enhanced/api_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_setup")

class ExchangeAPISetup:
    """Setup and test OKX and Kraken APIs"""
    
    def __init__(self):
        self.okx_config = {}
        self.kraken_config = {}
        self.test_results = {}
        
        logger.info("🚀 OKX & Kraken API Setup Initialized")
    
    def setup_okx_api(self):
        """Setup OKX API configuration"""
        logger.info("🔧 Setting up OKX API...")
        
        # OKX API Configuration
        okx_config = {
            'api_key': os.getenv('OKX_API_KEY', ''),
            'secret_key': os.getenv('OKX_SECRET_KEY', ''),
            'passphrase': os.getenv('OKX_PASSPHRASE', ''),
            'sandbox': os.getenv('OKX_SANDBOX', 'true').lower() == 'true',
            'base_url': 'https://www.okx.com' if not os.getenv('OKX_SANDBOX', 'true').lower() == 'true' else 'https://www.okx.com',
            'sandbox_url': 'https://www.okx.com',  # OKX uses same URL for sandbox
            'rate_limit': 20,  # 20 requests per second
            'timeout': 30000,
            'pairs': ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT', 'BNB-USDT']
        }
        
        self.okx_config = okx_config
        
        # Validate configuration
        if not okx_config['api_key'] or not okx_config['secret_key'] or not okx_config['passphrase']:
            logger.warning("⚠️  OKX API keys not found in environment variables")
            logger.info("   Required environment variables:")
            logger.info("   • OKX_API_KEY")
            logger.info("   • OKX_SECRET_KEY") 
            logger.info("   • OKX_PASSPHRASE")
            logger.info("   • OKX_SANDBOX (optional, defaults to true)")
            return False
        
        logger.info("✅ OKX API configuration loaded")
        logger.info(f"   • API Key: {okx_config['api_key'][:8]}...")
        logger.info(f"   • Sandbox Mode: {okx_config['sandbox']}")
        logger.info(f"   • Rate Limit: {okx_config['rate_limit']} req/sec")
        
        return True
    
    def setup_kraken_api(self):
        """Setup Kraken API configuration"""
        logger.info("🔧 Setting up Kraken API...")
        
        # Kraken API Configuration
        kraken_config = {
            'api_key': os.getenv('KRAKEN_API_KEY', ''),
            'secret_key': os.getenv('KRAKEN_SECRET_KEY', ''),
            'sandbox': False,  # Kraken doesn't have sandbox
            'base_url': 'https://api.kraken.com',
            'rate_limit': 1,  # 1 request per second (very conservative)
            'timeout': 30000,
            'pairs': ['XXBTZUSD', 'XETHZUSD', 'SOLUSD', 'ADAUSD', 'BNBUSD']
        }
        
        self.kraken_config = kraken_config
        
        # Validate configuration
        if not kraken_config['api_key'] or not kraken_config['secret_key']:
            logger.warning("⚠️  Kraken API keys not found in environment variables")
            logger.info("   Required environment variables:")
            logger.info("   • KRAKEN_API_KEY")
            logger.info("   • KRAKEN_SECRET_KEY")
            return False
        
        logger.info("✅ Kraken API configuration loaded")
        logger.info(f"   • API Key: {kraken_config['api_key'][:8]}...")
        logger.info(f"   • Rate Limit: {kraken_config['rate_limit']} req/sec")
        
        return True
    
    def test_okx_connection(self):
        """Test OKX API connection"""
        logger.info("🧪 Testing OKX API connection...")
        
        try:
            import ccxt
            
            # Create OKX exchange instance
            okx = ccxt.okx({
                'apiKey': self.okx_config['api_key'],
                'secret': self.okx_config['secret_key'],
                'password': self.okx_config['passphrase'],
                'sandbox': self.okx_config['sandbox'],
                'enableRateLimit': True,
                'rateLimit': 1000 // self.okx_config['rate_limit'],  # Convert to ms
                'timeout': self.okx_config['timeout'],
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            # Test basic connection
            markets = okx.load_markets()
            logger.info(f"✅ OKX connection successful - {len(markets)} markets loaded")
            
            # Test price fetch
            ticker = okx.fetch_ticker('BTC/USDT')
            logger.info(f"✅ OKX price fetch successful - BTC/USDT: ${ticker['last']}")
            
            # Test account balance (if not sandbox)
            if not self.okx_config['sandbox']:
                try:
                    balance = okx.fetch_balance()
                    logger.info("✅ OKX account balance fetch successful")
                except Exception as e:
                    logger.warning(f"⚠️  OKX balance fetch failed: {e}")
            
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
            
            # Create Kraken exchange instance
            kraken = ccxt.kraken({
                'apiKey': self.kraken_config['api_key'],
                'secret': self.kraken_config['secret_key'],
                'enableRateLimit': True,
                'rateLimit': 3000,  # 3 seconds between requests
                'timeout': self.kraken_config['timeout'],
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            # Test basic connection
            markets = kraken.load_markets()
            logger.info(f"✅ Kraken connection successful - {len(markets)} markets loaded")
            
            # Test price fetch
            ticker = kraken.fetch_ticker('BTC/USD')
            logger.info(f"✅ Kraken price fetch successful - BTC/USD: ${ticker['last']}")
            
            # Test account balance
            try:
                balance = kraken.fetch_balance()
                logger.info("✅ Kraken account balance fetch successful")
            except Exception as e:
                logger.warning(f"⚠️  Kraken balance fetch failed: {e}")
            
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
    
    def create_environment_template(self):
        """Create environment template file"""
        logger.info("📝 Creating environment template...")
        
        template_content = """# OKX & KRAKEN API CONFIGURATION
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

# Note: Kraken doesn't have sandbox mode - use with caution!
"""
        
        with open('okx_kraken_api_template.env', 'w') as f:
            f.write(template_content)
        
        logger.info("✅ Environment template created: okx_kraken_api_template.env")
    
    def generate_setup_report(self):
        """Generate comprehensive setup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': {
                'okx': {
                    'configured': bool(self.okx_config.get('api_key')),
                    'sandbox': self.okx_config.get('sandbox', False),
                    'test_result': self.test_results.get('okx', {}),
                    'config': {
                        'rate_limit': self.okx_config.get('rate_limit'),
                        'pairs': self.okx_config.get('pairs', [])
                    }
                },
                'kraken': {
                    'configured': bool(self.kraken_config.get('api_key')),
                    'sandbox': self.kraken_config.get('sandbox', False),
                    'test_result': self.test_results.get('kraken', {}),
                    'config': {
                        'rate_limit': self.kraken_config.get('rate_limit'),
                        'pairs': self.kraken_config.get('pairs', [])
                    }
                }
            },
            'recommendations': []
        }
        
        # Add recommendations
        if not report['exchanges']['okx']['configured']:
            report['recommendations'].append("Set up OKX API keys in environment variables")
        
        if not report['exchanges']['kraken']['configured']:
            report['recommendations'].append("Set up Kraken API keys in environment variables")
        
        if report['exchanges']['okx']['test_result'].get('status') == 'ERROR':
            report['recommendations'].append("Fix OKX API connection issues")
        
        if report['exchanges']['kraken']['test_result'].get('status') == 'ERROR':
            report['recommendations'].append("Fix Kraken API connection issues")
        
        return report
    
    def display_setup_status(self):
        """Display setup status"""
        report = self.generate_setup_report()
        
        print("\n" + "="*80)
        print("🚀 OKX & KRAKEN API SETUP STATUS")
        print("="*80)
        print(f"📅 Timestamp: {report['timestamp']}")
        
        print("\n🔧 OKX CONFIGURATION:")
        print("-" * 40)
        okx_status = "✅ CONFIGURED" if report['exchanges']['okx']['configured'] else "❌ NOT CONFIGURED"
        print(f"Status: {okx_status}")
        print(f"Sandbox Mode: {report['exchanges']['okx']['sandbox']}")
        print(f"Rate Limit: {report['exchanges']['okx']['config']['rate_limit']} req/sec")
        print(f"Test Result: {report['exchanges']['okx']['test_result'].get('status', 'NOT TESTED')}")
        
        print("\n🔧 KRAKEN CONFIGURATION:")
        print("-" * 40)
        kraken_status = "✅ CONFIGURED" if report['exchanges']['kraken']['configured'] else "❌ NOT CONFIGURED"
        print(f"Status: {kraken_status}")
        print(f"Sandbox Mode: {report['exchanges']['kraken']['sandbox']} (Not Available)")
        print(f"Rate Limit: {report['exchanges']['kraken']['config']['rate_limit']} req/sec")
        print(f"Test Result: {report['exchanges']['kraken']['test_result'].get('status', 'NOT TESTED')}")
        
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            print("-" * 40)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("="*80)
        
        return report
    
    def run_setup(self):
        """Run complete setup process"""
        logger.info("🚀 Starting OKX & Kraken API setup...")
        
        # Setup configurations
        okx_configured = self.setup_okx_api()
        kraken_configured = self.setup_kraken_api()
        
        # Test connections if configured
        if okx_configured:
            self.test_okx_connection()
        
        if kraken_configured:
            self.test_kraken_connection()
        
        # Create environment template
        self.create_environment_template()
        
        # Display status
        report = self.display_setup_status()
        
        # Save report
        with open('logs/ai_enhanced/okx_kraken_setup_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📄 Setup report saved to: logs/ai_enhanced/okx_kraken_setup_report.json")
        
        return report

def main():
    """Main function"""
    setup = ExchangeAPISetup()
    setup.run_setup()

if __name__ == "__main__":
    main()

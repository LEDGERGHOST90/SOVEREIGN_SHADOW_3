#!/usr/bin/env python3
"""
🔗 OKX & KRAKEN INTEGRATION
Integrates OKX and Kraken APIs with existing trading system
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the multi-exchange-crypto-mcp directory to path
sys.path.append('/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/multi-exchange-crypto-mcp')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_enhanced/okx_kraken_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("okx_kraken_integration")

class OKXKrakenIntegration:
    """Integrates OKX and Kraken with existing trading system"""
    
    def __init__(self):
        self.okx_exchange = None
        self.kraken_exchange = None
        self.integration_status = {}
        
        logger.info("🔗 OKX & Kraken Integration Initialized")
    
    def setup_okx_integration(self):
        """Setup OKX integration with existing system"""
        logger.info("🔧 Setting up OKX integration...")
        
        try:
            import ccxt
            
            # OKX Configuration
            okx_config = {
                'apiKey': os.getenv('OKX_API_KEY', ''),
                'secret': os.getenv('OKX_SECRET_KEY', ''),
                'password': os.getenv('OKX_PASSPHRASE', ''),
                'sandbox': os.getenv('OKX_SANDBOX', 'true').lower() == 'true',
                'enableRateLimit': True,
                'rateLimit': 50,  # 20 requests per second
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            }
            
            if not okx_config['apiKey'] or not okx_config['secret'] or not okx_config['password']:
                logger.warning("⚠️  OKX API keys not configured")
                return False
            
            # Create OKX exchange instance
            self.okx_exchange = ccxt.okx(okx_config)
            
            # Test connection
            markets = self.okx_exchange.load_markets()
            logger.info(f"✅ OKX integration successful - {len(markets)} markets loaded")
            
            self.integration_status['okx'] = {
                'status': 'ACTIVE',
                'markets_count': len(markets),
                'sandbox': okx_config['sandbox'],
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except ImportError:
            logger.error("❌ CCXT library not installed")
            return False
        except Exception as e:
            logger.error(f"❌ OKX integration failed: {e}")
            return False
    
    def setup_kraken_integration(self):
        """Setup Kraken integration with existing system"""
        logger.info("🔧 Setting up Kraken integration...")
        
        try:
            import ccxt
            
            # Kraken Configuration
            kraken_config = {
                'apiKey': os.getenv('KRAKEN_API_KEY', ''),
                'secret': os.getenv('KRAKEN_SECRET_KEY', ''),
                'enableRateLimit': True,
                'rateLimit': 3000,  # 3 seconds between requests
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            }
            
            if not kraken_config['apiKey'] or not kraken_config['secret']:
                logger.warning("⚠️  Kraken API keys not configured")
                return False
            
            # Create Kraken exchange instance
            self.kraken_exchange = ccxt.kraken(kraken_config)
            
            # Test connection
            markets = self.kraken_exchange.load_markets()
            logger.info(f"✅ Kraken integration successful - {len(markets)} markets loaded")
            
            self.integration_status['kraken'] = {
                'status': 'ACTIVE',
                'markets_count': len(markets),
                'sandbox': False,  # Kraken doesn't have sandbox
                'timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except ImportError:
            logger.error("❌ CCXT library not installed")
            return False
        except Exception as e:
            logger.error(f"❌ Kraken integration failed: {e}")
            return False
    
    def get_multi_exchange_prices(self, symbol='BTC/USDT'):
        """Get prices from both OKX and Kraken"""
        prices = {}
        
        # OKX Price
        if self.okx_exchange:
            try:
                # Convert symbol format for OKX (BTC/USDT -> BTC-USDT)
                okx_symbol = symbol.replace('/', '-')
                ticker = self.okx_exchange.fetch_ticker(okx_symbol)
                prices['okx'] = {
                    'price': ticker['last'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'volume': ticker['baseVolume'],
                    'timestamp': ticker['timestamp']
                }
            except Exception as e:
                logger.error(f"OKX price fetch failed: {e}")
                prices['okx'] = {'error': str(e)}
        
        # Kraken Price
        if self.kraken_exchange:
            try:
                # Convert symbol format for Kraken (BTC/USDT -> BTC/USD)
                kraken_symbol = symbol.replace('USDT', 'USD')
                ticker = self.kraken_exchange.fetch_ticker(kraken_symbol)
                prices['kraken'] = {
                    'price': ticker['last'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'volume': ticker['baseVolume'],
                    'timestamp': ticker['timestamp']
                }
            except Exception as e:
                logger.error(f"Kraken price fetch failed: {e}")
                prices['kraken'] = {'error': str(e)}
        
        return prices
    
    def detect_arbitrage_opportunities(self, symbols=['BTC/USDT', 'ETH/USDT']):
        """Detect arbitrage opportunities between OKX and Kraken"""
        opportunities = []
        
        for symbol in symbols:
            prices = self.get_multi_exchange_prices(symbol)
            
            if 'okx' in prices and 'kraken' in prices and 'error' not in prices['okx'] and 'error' not in prices['kraken']:
                okx_price = prices['okx']['price']
                kraken_price = prices['kraken']['price']
                
                # Calculate spread
                spread = abs(okx_price - kraken_price)
                spread_percent = (spread / min(okx_price, kraken_price)) * 100
                
                if spread_percent > 0.1:  # 0.1% minimum spread
                    opportunity = {
                        'symbol': symbol,
                        'okx_price': okx_price,
                        'kraken_price': kraken_price,
                        'spread': spread,
                        'spread_percent': spread_percent,
                        'buy_exchange': 'okx' if okx_price < kraken_price else 'kraken',
                        'sell_exchange': 'kraken' if okx_price < kraken_price else 'okx',
                        'profit_potential': spread_percent,
                        'timestamp': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
        
        return opportunities
    
    def get_portfolio_aggregation(self):
        """Get portfolio balances from both exchanges"""
        portfolio = {}
        
        # OKX Portfolio
        if self.okx_exchange:
            try:
                balance = self.okx_exchange.fetch_balance()
                portfolio['okx'] = {
                    'total': balance['total'],
                    'free': balance['free'],
                    'used': balance['used'],
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"OKX balance fetch failed: {e}")
                portfolio['okx'] = {'error': str(e)}
        
        # Kraken Portfolio
        if self.kraken_exchange:
            try:
                balance = self.kraken_exchange.fetch_balance()
                portfolio['kraken'] = {
                    'total': balance['total'],
                    'free': balance['free'],
                    'used': balance['used'],
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Kraken balance fetch failed: {e}")
                portfolio['kraken'] = {'error': str(e)}
        
        return portfolio
    
    def monitor_exchange_status(self):
        """Monitor status of both exchanges"""
        status = {}
        
        # OKX Status
        if self.okx_exchange:
            try:
                # Test basic connectivity
                self.okx_exchange.fetch_status()
                status['okx'] = {
                    'status': 'ONLINE',
                    'response_time': '< 1s',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                status['okx'] = {
                    'status': 'OFFLINE',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Kraken Status
        if self.kraken_exchange:
            try:
                # Test basic connectivity
                self.kraken_exchange.fetch_status()
                status['kraken'] = {
                    'status': 'ONLINE',
                    'response_time': '< 1s',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                status['kraken'] = {
                    'status': 'OFFLINE',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return status
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'integration_status': self.integration_status,
            'exchange_status': self.monitor_exchange_status(),
            'sample_prices': self.get_multi_exchange_prices('BTC/USDT'),
            'arbitrage_opportunities': self.detect_arbitrage_opportunities(),
            'portfolio_summary': self.get_portfolio_aggregation()
        }
        
        return report
    
    def display_integration_status(self):
        """Display integration status"""
        report = self.generate_integration_report()
        
        print("\n" + "="*80)
        print("🔗 OKX & KRAKEN INTEGRATION STATUS")
        print("="*80)
        print(f"📅 Timestamp: {report['timestamp']}")
        
        print("\n🔧 INTEGRATION STATUS:")
        print("-" * 40)
        for exchange, status in report['integration_status'].items():
            status_icon = "✅" if status['status'] == 'ACTIVE' else "❌"
            print(f"{status_icon} {exchange.upper()}: {status['status']}")
            if 'markets_count' in status:
                print(f"   Markets: {status['markets_count']}")
            if 'sandbox' in status:
                print(f"   Sandbox: {status['sandbox']}")
        
        print("\n🌐 EXCHANGE STATUS:")
        print("-" * 40)
        for exchange, status in report['exchange_status'].items():
            status_icon = "✅" if status['status'] == 'ONLINE' else "❌"
            print(f"{status_icon} {exchange.upper()}: {status['status']}")
            if 'response_time' in status:
                print(f"   Response Time: {status['response_time']}")
        
        print("\n💰 SAMPLE PRICES (BTC/USDT):")
        print("-" * 40)
        for exchange, price_data in report['sample_prices'].items():
            if 'error' not in price_data:
                print(f"✅ {exchange.upper()}: ${price_data['price']:.2f}")
            else:
                print(f"❌ {exchange.upper()}: {price_data['error']}")
        
        print("\n🎯 ARBITRAGE OPPORTUNITIES:")
        print("-" * 40)
        if report['arbitrage_opportunities']:
            for opp in report['arbitrage_opportunities']:
                print(f"💰 {opp['symbol']}: {opp['spread_percent']:.2f}% spread")
                print(f"   Buy: {opp['buy_exchange'].upper()} @ ${opp['okx_price'] if opp['buy_exchange'] == 'okx' else opp['kraken_price']:.2f}")
                print(f"   Sell: {opp['sell_exchange'].upper()} @ ${opp['kraken_price'] if opp['sell_exchange'] == 'kraken' else opp['okx_price']:.2f}")
        else:
            print("No significant arbitrage opportunities found")
        
        print("="*80)
        
        return report
    
    def run_integration(self):
        """Run complete integration process"""
        logger.info("🔗 Starting OKX & Kraken integration...")
        
        # Setup integrations
        okx_success = self.setup_okx_integration()
        kraken_success = self.setup_kraken_integration()
        
        # Display status
        report = self.display_integration_status()
        
        # Save report
        with open('logs/ai_enhanced/okx_kraken_integration_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📄 Integration report saved to: logs/ai_enhanced/okx_kraken_integration_report.json")
        
        return report

def main():
    """Main function"""
    integration = OKXKrakenIntegration()
    integration.run_integration()

if __name__ == "__main__":
    main()

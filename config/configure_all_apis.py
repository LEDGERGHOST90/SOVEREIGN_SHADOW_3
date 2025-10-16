#!/usr/bin/env python3
"""
🔑 API CONFIGURATION WIZARD
Interactive setup for all exchange and service APIs
"""

import os
import json
import getpass
from pathlib import Path
from datetime import datetime

class APIConfigurationWizard:
    """Interactive API configuration for all services"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.env_file = self.root / '.env'
        self.config_file = self.root / 'config' / 'api_config.json'
        
        self.apis = {
            'exchanges': {
                'coinbase': {
                    'name': 'Coinbase',
                    'required': ['COINBASE_API_KEY', 'COINBASE_API_SECRET'],
                    'optional': ['COINBASE_SANDBOX_KEY', 'COINBASE_SANDBOX_SECRET'],
                    'docs': 'https://docs.cloud.coinbase.com/',
                    'ip_whitelist': '76.86.125.32/32'
                },
                'binance_us': {
                    'name': 'Binance.US',
                    'required': ['BINANCE_US_API_KEY', 'BINANCE_US_SECRET'],
                    'optional': ['BINANCE_TESTNET_KEY', 'BINANCE_TESTNET_SECRET'],
                    'docs': 'https://docs.binance.us/',
                    'ip_whitelist': '76.86.125.32/32'
                },
                'okx': {
                    'name': 'OKX',
                    'required': ['OKX_API_KEY', 'OKX_SECRET', 'OKX_PASSPHRASE'],
                    'optional': [],
                    'docs': 'https://www.okx.com/docs-v5/en/',
                    'ip_whitelist': '76.86.125.32/32'
                },
                'kraken': {
                    'name': 'Kraken',
                    'required': ['KRAKEN_API_KEY', 'KRAKEN_SECRET'],
                    'optional': [],
                    'docs': 'https://docs.kraken.com/rest/',
                    'ip_whitelist': '76.86.125.32/32'
                },
                'kucoin': {
                    'name': 'KuCoin',
                    'required': ['KUCOIN_API_KEY', 'KUCOIN_SECRET', 'KUCOIN_PASSPHRASE'],
                    'optional': [],
                    'docs': 'https://docs.kucoin.com/',
                    'ip_whitelist': '76.86.125.32/32'
                },
                'bybit': {
                    'name': 'Bybit',
                    'required': ['BYBIT_API_KEY', 'BYBIT_SECRET'],
                    'optional': [],
                    'docs': 'https://bybit-exchange.github.io/docs/v5/intro',
                    'ip_whitelist': '76.86.125.32/32'
                }
            },
            'services': {
                'coinbase_cdp': {
                    'name': 'Coinbase CDP (Developer Platform)',
                    'required': ['CDP_API_KEY_NAME', 'CDP_PRIVATE_KEY'],
                    'optional': [],
                    'docs': 'https://docs.cdp.coinbase.com/',
                    'project_id': 'f5b80ba9-92fd-4d0f-bb26-b9f546edcc1e'
                },
                'ethereum': {
                    'name': 'Ethereum RPC',
                    'required': ['ETHEREUM_RPC_URL'],
                    'optional': ['ALCHEMY_API_KEY', 'INFURA_API_KEY'],
                    'docs': 'https://ethereum.org/en/developers/docs/apis/json-rpc/'
                },
                'ledger': {
                    'name': 'Ledger Hardware Wallet',
                    'required': [],
                    'optional': ['LEDGER_DEVICE_PATH'],
                    'docs': 'https://developers.ledger.com/'
                }
            }
        }
        
        self.config = {}
    
    def display_header(self):
        """Display wizard header"""
        print("\n" + "="*80)
        print("🔑 SOVEREIGNSHADOW.AI - API CONFIGURATION WIZARD")
        print("="*80)
        print("\n📋 This wizard will help you configure:")
        print("   • Exchange APIs (Coinbase, Binance.US, OKX, Kraken, KuCoin, Bybit)")
        print("   • Coinbase Developer Platform (CDP)")
        print("   • Ethereum RPC endpoints")
        print("   • Ledger hardware wallet")
        print("\n💡 Your public IP: 76.86.125.32")
        print("   Add this to IP whitelists on exchange platforms")
        print("="*80)
    
    def configure_exchange(self, exchange_key, exchange_info):
        """Configure a single exchange"""
        print(f"\n📊 Configuring {exchange_info['name']}")
        print("-" * 60)
        print(f"   📖 Docs: {exchange_info['docs']}")
        if 'ip_whitelist' in exchange_info:
            print(f"   🌐 IP Whitelist: {exchange_info['ip_whitelist']}")
        
        configure = input(f"\n   Configure {exchange_info['name']}? (y/n, Enter=skip): ").lower()
        
        if configure != 'y':
            print(f"   ⏭️  Skipped {exchange_info['name']}")
            return
        
        exchange_config = {}
        
        # Required fields
        print(f"\n   🔑 Required API credentials:")
        for field in exchange_info['required']:
            if 'SECRET' in field or 'PRIVATE' in field or 'PASSPHRASE' in field:
                value = getpass.getpass(f"      {field}: ")
            else:
                value = input(f"      {field}: ").strip()
            
            if value:
                exchange_config[field] = value
        
        # Optional fields
        if exchange_info['optional']:
            print(f"\n   📝 Optional fields (for testnet/sandbox):")
            for field in exchange_info['optional']:
                value = input(f"      {field} (Enter=skip): ").strip()
                if value:
                    exchange_config[field] = value
        
        if exchange_config:
            self.config[exchange_key] = exchange_config
            print(f"   ✅ {exchange_info['name']} configured")
        else:
            print(f"   ❌ No credentials provided for {exchange_info['name']}")
    
    def configure_service(self, service_key, service_info):
        """Configure a single service"""
        print(f"\n🔧 Configuring {service_info['name']}")
        print("-" * 60)
        print(f"   📖 Docs: {service_info['docs']}")
        if 'project_id' in service_info:
            print(f"   🆔 Project ID: {service_info['project_id']}")
        
        configure = input(f"\n   Configure {service_info['name']}? (y/n, Enter=skip): ").lower()
        
        if configure != 'y':
            print(f"   ⏭️  Skipped {service_info['name']}")
            return
        
        service_config = {}
        
        # Required fields
        if service_info['required']:
            print(f"\n   🔑 Required credentials:")
            for field in service_info['required']:
                if 'PRIVATE' in field or 'SECRET' in field:
                    value = getpass.getpass(f"      {field}: ")
                else:
                    value = input(f"      {field}: ").strip()
                
                if value:
                    service_config[field] = value
        
        # Optional fields
        if service_info['optional']:
            print(f"\n   📝 Optional fields:")
            for field in service_info['optional']:
                value = input(f"      {field} (Enter=skip): ").strip()
                if value:
                    service_config[field] = value
        
        if service_config:
            self.config[service_key] = service_config
            print(f"   ✅ {service_info['name']} configured")
        else:
            print(f"   ⚠️  No credentials provided for {service_info['name']}")
    
    def save_config(self):
        """Save configuration to .env and JSON"""
        print("\n💾 Saving configuration...")
        
        # Create .env file
        env_lines = [
            "# SovereignShadow.AI API Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            ""
        ]
        
        # Add all configured APIs to .env
        for category_key, category in [('exchanges', self.apis['exchanges']), 
                                         ('services', self.apis['services'])]:
            env_lines.append(f"\n# {category_key.upper()}")
            for api_key in category.keys():
                if api_key in self.config:
                    for field, value in self.config[api_key].items():
                        env_lines.append(f"{field}={value}")
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_lines))
        
        print(f"   ✅ Saved to: {self.env_file}")
        
        # Save JSON config (without secrets)
        config_summary = {
            'generated': datetime.now().isoformat(),
            'configured_apis': list(self.config.keys()),
            'total_apis': len(self.config),
            'ip_address': '76.86.125.32'
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config_summary, f, indent=4)
        
        print(f"   ✅ Summary saved to: {self.config_file}")
        
        # Create .env for ClaudeSDK if it doesn't exist
        claudesdk_env = self.root / 'sovereign_legacy_loop' / 'ClaudeSDK' / '.env'
        if not claudesdk_env.exists():
            claudesdk_env.parent.mkdir(parents=True, exist_ok=True)
            with open(claudesdk_env, 'w') as f:
                f.write('\n'.join(env_lines))
            print(f"   ✅ ClaudeSDK .env created: {claudesdk_env}")
    
    def display_summary(self):
        """Display configuration summary"""
        print("\n" + "="*80)
        print("✅ API CONFIGURATION COMPLETE")
        print("="*80)
        print(f"\n📊 Configured APIs: {len(self.config)}")
        
        for category_name, category_apis in [('Exchanges', self.apis['exchanges']), 
                                               ('Services', self.apis['services'])]:
            configured = [k for k in category_apis.keys() if k in self.config]
            if configured:
                print(f"\n{category_name}:")
                for api_key in configured:
                    api_name = category_apis[api_key]['name']
                    num_fields = len(self.config[api_key])
                    print(f"   ✅ {api_name} ({num_fields} credentials)")
        
        print("\n📝 Next Steps:")
        print("   1. Verify API keys work: python3 tests/test_all_exchanges.py")
        print("   2. Check system status: python3 sovereign_shadow_unified.py")
        print("   3. Deploy staging: ./deployment/AI_ENHANCED_DEPLOYMENT.sh")
        print("\n⚠️  SECURITY:")
        print("   • Keep .env file secure (already in .gitignore)")
        print("   • Never commit API keys to version control")
        print("   • Rotate keys periodically")
        print("="*80)
    
    def run(self):
        """Run the configuration wizard"""
        self.display_header()
        
        # Configure exchanges
        print("\n" + "="*80)
        print("📊 EXCHANGE APIS")
        print("="*80)
        for exchange_key, exchange_info in self.apis['exchanges'].items():
            self.configure_exchange(exchange_key, exchange_info)
        
        # Configure services
        print("\n" + "="*80)
        print("🔧 SERVICE APIS")
        print("="*80)
        for service_key, service_info in self.apis['services'].items():
            self.configure_service(service_key, service_info)
        
        # Save configuration
        if self.config:
            self.save_config()
            self.display_summary()
        else:
            print("\n❌ No APIs configured. Run the wizard again when ready.")

def main():
    """Main execution"""
    wizard = APIConfigurationWizard()
    wizard.run()

if __name__ == "__main__":
    main()


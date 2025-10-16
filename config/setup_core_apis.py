#!/usr/bin/env python3
"""
🔑 CORE API SETUP
Configure Coinbase, OKX, Kraken, and Ledger only
"""

import os
import json
import getpass
from pathlib import Path
from datetime import datetime

class CoreAPISetup:
    """Setup for core trading platforms only"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.env_file = self.root / '.env'
        
        self.core_platforms = {
            'coinbase': {
                'name': 'Coinbase',
                'fields': {
                    'COINBASE_API_KEY': 'API Key',
                    'COINBASE_API_SECRET': 'API Secret'
                },
                'docs': 'https://docs.cloud.coinbase.com/',
                'ip': '76.86.125.32/32'
            },
            'okx': {
                'name': 'OKX',
                'fields': {
                    'OKX_API_KEY': 'API Key',
                    'OKX_SECRET': 'Secret Key',
                    'OKX_PASSPHRASE': 'Passphrase'
                },
                'docs': 'https://www.okx.com/docs-v5/en/',
                'ip': '76.86.125.32/32'
            },
            'kraken': {
                'name': 'Kraken',
                'fields': {
                    'KRAKEN_API_KEY': 'API Key',
                    'KRAKEN_SECRET': 'Private Key'
                },
                'docs': 'https://docs.kraken.com/rest/',
                'ip': '76.86.125.32/32'
            },
            'ledger': {
                'name': 'Ledger Hardware Wallet',
                'fields': {},
                'note': 'Physical device - no API keys needed',
                'docs': 'https://www.ledger.com/'
            }
        }
        
        self.config = {}
    
    def display_welcome(self):
        """Show welcome message"""
        print("\n" + "="*80)
        print("🔑 SOVEREIGNSHADOW.AI - CORE API SETUP")
        print("="*80)
        print("\n📋 Configuring your core trading platforms:")
        print("   1. Coinbase  - Main exchange")
        print("   2. OKX       - Global trading")
        print("   3. Kraken    - Secure exchange")
        print("   4. Ledger    - Hardware wallet")
        print("\n💡 Your IP for whitelisting: 76.86.125.32/32")
        print("="*80 + "\n")
    
    def setup_exchange(self, key, info):
        """Setup individual exchange"""
        print(f"\n{'='*80}")
        print(f"📊 {info['name'].upper()}")
        print('='*80)
        print(f"📖 Documentation: {info['docs']}")
        
        if 'ip' in info:
            print(f"🌐 Whitelist this IP: {info['ip']}")
        
        if 'note' in info:
            print(f"ℹ️  Note: {info['note']}")
            input("\n   Press Enter to continue...")
            return
        
        print("\n" + "-"*80)
        configure = input(f"Configure {info['name']}? (y/n): ").lower().strip()
        
        if configure != 'y':
            print(f"⏭️  Skipped {info['name']}\n")
            return
        
        exchange_config = {}
        print(f"\n🔑 Enter {info['name']} API credentials:\n")
        
        for field_key, field_name in info['fields'].items():
            if any(x in field_key for x in ['SECRET', 'PRIVATE', 'PASSPHRASE']):
                value = getpass.getpass(f"   {field_name}: ")
            else:
                value = input(f"   {field_name}: ").strip()
            
            if value:
                exchange_config[field_key] = value
        
        if exchange_config:
            self.config[key] = exchange_config
            print(f"\n✅ {info['name']} configured successfully!")
        else:
            print(f"\n⚠️  No credentials entered for {info['name']}")
    
    def save_configuration(self):
        """Save to .env file"""
        if not self.config:
            print("\n❌ No APIs configured. Exiting...")
            return False
        
        print("\n" + "="*80)
        print("💾 SAVING CONFIGURATION")
        print("="*80)
        
        env_lines = [
            "# SovereignShadow.AI - Core API Configuration",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# Exchanges: Coinbase, OKX, Kraken + Ledger",
            ""
        ]
        
        for platform, credentials in self.config.items():
            info = self.core_platforms[platform]
            env_lines.append(f"\n# {info['name']}")
            for key, value in credentials.items():
                env_lines.append(f"{key}={value}")
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_lines))
        
        print(f"\n✅ Configuration saved to: {self.env_file}")
        
        # Also save to ClaudeSDK
        claudesdk_env = self.root / 'sovereign_legacy_loop' / 'ClaudeSDK' / '.env'
        claudesdk_env.parent.mkdir(parents=True, exist_ok=True)
        with open(claudesdk_env, 'w') as f:
            f.write('\n'.join(env_lines))
        
        print(f"✅ Configuration saved to: {claudesdk_env}")
        
        return True
    
    def show_summary(self):
        """Display final summary"""
        print("\n" + "="*80)
        print("✅ CORE API SETUP COMPLETE")
        print("="*80)
        
        print(f"\n📊 Configured Platforms: {len(self.config)}")
        for platform, credentials in self.config.items():
            info = self.core_platforms[platform]
            print(f"   ✅ {info['name']} - {len(credentials)} credentials")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Test connections:")
        print("      python3 tests/test_all_exchanges.py")
        print("\n   2. View system status:")
        print("      python3 sovereign_shadow_unified.py")
        print("\n   3. Start paper trading:")
        print("      ./deployment/AI_ENHANCED_DEPLOYMENT.sh")
        
        print("\n🔒 SECURITY REMINDERS:")
        print("   • .env file is gitignored (safe)")
        print("   • Never share your API keys")
        print("   • Keep Ledger device secure")
        print("   • Use IP whitelisting on exchanges")
        
        print("\n" + "="*80 + "\n")
    
    def run(self):
        """Run the setup wizard"""
        self.display_welcome()
        
        # Setup each platform
        for key, info in self.core_platforms.items():
            self.setup_exchange(key, info)
        
        # Save and summarize
        if self.save_configuration():
            self.show_summary()

def main():
    """Main execution"""
    setup = CoreAPISetup()
    setup.run()

if __name__ == "__main__":
    main()


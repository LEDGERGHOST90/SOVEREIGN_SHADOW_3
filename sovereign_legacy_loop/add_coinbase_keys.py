#!/usr/bin/env python3
"""
Quick script to add Coinbase API keys to .env
"""
import os

print("\n🔑 ADD COINBASE API KEYS")
print("="*50)
print("Get your API keys from: https://www.coinbase.com/settings/api")
print("You need: API Key and API Secret")
print("="*50)

api_key = input("\nEnter Coinbase API Key: ").strip()
api_secret = input("Enter Coinbase API Secret: ").strip()

if api_key and api_secret:
    env_content = f"""
# Coinbase API Keys
COINBASE_KEY={api_key}
COINBASE_SECRET={api_secret}
CB_API_KEY={api_key}
CB_API_SECRET={api_secret}

# System Configuration
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Coinbase keys saved to .env")
    print("\n🔄 Restarting system with Coinbase...")
    
    # Kill old process
    os.system("pkill -f sovereign_shadow_unified.py")
    
    # Export environment
    os.system("export ENV=prod")
    os.system("export ALLOW_LIVE_EXCHANGE=1")
    os.system("export DISABLE_REAL_EXCHANGES=0")
    
    print("\n🚀 Starting system with Coinbase integration...")
    os.system("python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &")
    
    print("\n✅ System restarted with Coinbase!")
    print("\n📊 Check status:")
    print("   tail -f logs/ai_enhanced/sovereign_shadow_unified.log")
else:
    print("\n❌ No keys entered. Exiting.")

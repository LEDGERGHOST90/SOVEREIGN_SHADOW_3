#!/usr/bin/env python3
"""
Setup Coinbase CDP API connection using the JSON key file
"""
import json
import os

print("🔑 Setting up Coinbase CDP Connection")
print("="*50)

# Read the CBase_api_key.json
try:
    with open('CBase_api_key.json', 'r') as f:
        cdp_config = json.load(f)
    
    api_key_name = cdp_config.get('name', '')
    private_key = cdp_config.get('privateKey', '')
    
    # Extract the API key ID from the name
    if '/' in api_key_name:
        api_key_id = api_key_name.split('/')[-1]
    else:
        api_key_id = api_key_name
    
    print(f"✅ Found CDP API Key: {api_key_id[:8]}...")
    
    # Create .env with CDP configuration
    env_content = f"""# Coinbase CDP Configuration
COINBASE_CDP_API_KEY_NAME={api_key_name}
COINBASE_CDP_API_KEY_ID={api_key_id}
COINBASE_CDP_PRIVATE_KEY={private_key}

# Regular Coinbase API (CDP format)
COINBASE_KEY={api_key_id}
COINBASE_SECRET={private_key}
CB_API_KEY={api_key_id}
CB_API_SECRET={private_key}

# System Configuration
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ CDP keys saved to .env")
    print("\n🔄 Restarting system with Coinbase CDP...")
    
    # Kill old process
    os.system("pkill -f sovereign_shadow_unified.py")
    
    print("🚀 Starting with Coinbase CDP integration...")
    os.system("python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &")
    
    print("\n✅ System started with Coinbase CDP!")
    print("\n📊 Check connection:")
    print("   tail -f logs/ai_enhanced/sovereign_shadow_unified.log")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure CBase_api_key.json contains your actual private key")

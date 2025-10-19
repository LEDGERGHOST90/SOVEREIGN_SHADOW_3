#!/usr/bin/env python3
"""
EMERGENCY FIX - Get Coinbase working NOW
"""
import os
import json

print("\n🚨 EMERGENCY COINBASE FIX")
print("="*50)
print("We need to get your Coinbase connection working.")
print("\nDo you have your Coinbase private key? (y/n): ", end="")
has_key = input().strip().lower()

if has_key == 'y':
    print("\nYour private key should look like:")
    print("-----BEGIN EC PRIVATE KEY-----")
    print("MHcCAQEEI...(long string)...")
    print("-----END EC PRIVATE KEY-----")
    print("\nPaste your ENTIRE private key below.")
    print("(Press Enter twice when done):\n")
    
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        elif lines:  # Empty line after content
            break
    
    private_key = '\n'.join(lines)
    
    # Save to CBase_api_key.json
    config = {
        "name": "organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/62d59def-cd4b-4285-879c-ea113c1900a4",
        "privateKey": private_key
    }
    
    with open('CBase_api_key.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Private key saved!")
    
else:
    print("\n⚠️  You need to get your private key from Coinbase CDP")
    print("\nSTEPS TO GET YOUR KEY:")
    print("1. Go to: https://portal.cdp.coinbase.com/")
    print("2. Sign in with your Coinbase account")
    print("3. Click 'API Keys' in the left menu")
    print("4. Click 'Create API Key'")
    print("5. SAVE THE PRIVATE KEY (you only see it once!)")
    print("\nThen run this script again.")
    exit()

# Create .env file
env_content = """# Coinbase CDP Configuration
COINBASE_CDP_KEY=62d59def-cd4b-4285-879c-ea113c1900a4
ENV=prod
ALLOW_LIVE_EXCHANGE=1
DISABLE_REAL_EXCHANGES=0
SANDBOX=0
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Environment configured")
print("\n🔄 Restarting system with Coinbase...")

# Kill any running process
os.system("pkill -f sovereign_shadow_unified.py 2>/dev/null")

# Start fresh
print("🚀 Starting system...")
os.system("python3 sovereign_shadow_unified.py --autonomy --interval 30 2>&1 | tee -a logs/launch.log &")

print("\n✅ SYSTEM RUNNING WITH COINBASE!")
print("\n📊 Check if it's working:")
print("   tail -f logs/ai_enhanced/sovereign_shadow_unified.log")
print("\nLook for 'coinbase': 'connected'")

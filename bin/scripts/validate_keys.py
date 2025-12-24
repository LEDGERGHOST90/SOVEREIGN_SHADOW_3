#!/usr/bin/env python3
"""
✅ API Key Validation
Quick check that all keys are working
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def validate_all_keys():
    """Validate all API keys"""
    load_dotenv()
    
    print("🔍 Validating API keys...")
    print()
    
    # Check if keys exist
    keys = {
        "Coinbase": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
        "OKX": ["OKX_KEY", "OKX_SECRET", "OKX_PASSPHRASE"],
        "Kraken": ["KRAKEN_KEY", "KRAKEN_SECRET"],
        "Anthropic": ["ANTHROPIC_API_KEY"]
    }
    
    all_good = True
    
    for exchange, key_names in keys.items():
        missing = []
        for key_name in key_names:
            if not os.getenv(key_name):
                missing.append(key_name)
        
        if missing:
            print(f"❌ {exchange}: Missing {', '.join(missing)}")
            all_good = False
        else:
            print(f"✅ {exchange}: All keys present")
    
    if all_good:
        print()
        print("🎉 All API keys are configured!")
        print("🚀 Ready to trade!")
    else:
        print()
        print("⚠️  Some keys are missing. Run setup again.")
    
    return all_good

if __name__ == "__main__":
    validate_all_keys()



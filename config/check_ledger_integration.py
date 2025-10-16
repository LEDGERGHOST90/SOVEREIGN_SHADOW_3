#!/usr/bin/env python3
"""
LEDGER INTEGRATION CHECKER
Find and connect to your Ledger hardware wallet
"""
import subprocess
import json
import os
from pathlib import Path

def check_ledger_integration():
    """Check for Ledger hardware wallet integration"""
    
    print("🔍 CHECKING LEDGER INTEGRATION...")
    print("=" * 50)
    
    # Check if Ledger Live is installed
    ledger_paths = [
        "/Applications/Ledger Live.app",
        "~/Applications/Ledger Live.app",
        "/usr/local/bin/ledger-live"
    ]
    
    for path in ledger_paths:
        if os.path.exists(os.path.expanduser(path)):
            print(f"✅ Found Ledger Live at: {path}")
            
    # Check for Ledger hardware connection
    try:
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True)
        if 'Ledger' in result.stdout:
            print("✅ Ledger hardware wallet detected")
        else:
            print("❌ No Ledger hardware wallet found")
    except:
        print("❌ Could not check for Ledger hardware")
    
    # Check for existing Ledger integration files
    ledger_files = [
        "ledger_integration.py",
        "ledger_wallet.py", 
        "hardware_wallet.py",
        "src/ledger_connector.py"
    ]
    
    print("\n📁 Checking for Ledger integration files:")
    for file in ledger_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")

if __name__ == "__main__":
    check_ledger_integration()

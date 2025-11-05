#!/usr/bin/env python3
"""
🪙 Coinbase CDP API Verification
Tests the Cloud Developer Platform (CDP) API format
"""

import os
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment
load_dotenv(project_root / '.env')

def verify_coinbase_cdp():
    """Verify Coinbase CDP API"""
    try:
        from coinbase.rest import RESTClient

        api_key = os.getenv("COINBASE_API_KEY")
        api_secret = os.getenv("COINBASE_API_SECRET")

        if not api_key or not api_secret:
            print("❌ Coinbase CDP keys not found in .env")
            return False

        print(f"🔍 Testing Coinbase CDP API...")
        print(f"   API Key: {api_key[:50]}...")
        print(f"   Secret: {'[EC PRIVATE KEY]' if 'BEGIN EC PRIVATE KEY' in api_secret else '[STANDARD KEY]'}")

        # Try to create client
        client = RESTClient(
            api_key=api_key,
            api_secret=api_secret
        )

        # Test with a simple call
        print("\n📞 Attempting API call...")

        try:
            accounts = client.get_accounts()

            print("\n✅ Coinbase CDP connected successfully!")
            print(f"   Found {len(accounts.get('accounts', []))} accounts")

            # Show accounts with balance
            for account in accounts.get('accounts', []):
                currency = account.get('currency')
                balance = account.get('available_balance', {}).get('value', '0')
                if float(balance) > 0:
                    print(f"   {currency}: {balance}")

            return True

        except Exception as api_error:
            error_msg = str(api_error)

            # Check for specific error types
            if "401" in error_msg or "Unauthorized" in error_msg:
                print("\n❌ 401 Unauthorized")
                print("\n📋 Possible causes:")
                print("   1. API key not yet active (wait 5 minutes after creation)")
                print("   2. Key has wrong permissions (needs View + Trade)")
                print("   3. IP whitelist enabled but your IP not added")
                print("   4. Key format may be for different Coinbase API")

                print("\n🔧 Your key format:")
                if api_key.startswith("organizations/"):
                    print("   ✅ CDP format (Cloud Developer Platform)")
                    print("   Note: This is the NEW Coinbase format")
                else:
                    print("   ⚠️ Legacy format (older API)")

                print("\n💡 Troubleshooting steps:")
                print("   1. Visit https://portal.cdp.coinbase.com/")
                print("   2. Check key status and permissions")
                print("   3. Ensure 'Read' and 'Trade' are enabled")
                print("   4. If using IP whitelist, add current IP:")
                print(f"      curl ifconfig.me")

            elif "404" in error_msg:
                print("\n❌ 404 Not Found")
                print("   This API endpoint may not be available with CDP keys")
                print("   CDP keys are for Developer Platform, not Advanced Trade")

            else:
                print(f"\n❌ API Error: {error_msg}")

            return False

    except ImportError:
        print("❌ Coinbase SDK not installed")
        print("   Install with: pip install coinbase-advanced-py")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_key_type():
    """Determine which type of Coinbase key is configured"""
    api_key = os.getenv("COINBASE_API_KEY", "")
    api_secret = os.getenv("COINBASE_API_SECRET", "")

    print("\n🔍 Coinbase API Key Analysis:")
    print("="*60)

    if not api_key:
        print("❌ No API key found in .env")
        return

    # Check key format
    if api_key.startswith("organizations/"):
        print("✅ Key Type: CDP (Cloud Developer Platform)")
        print("   Format: organizations/{org_id}/apiKeys/{key_id}")
        print("   Portal: https://portal.cdp.coinbase.com/")
        print("   Documentation: https://docs.cdp.coinbase.com/")

        if "BEGIN EC PRIVATE KEY" in api_secret:
            print("✅ Secret Type: EC Private Key (correct for CDP)")
        else:
            print("⚠️ Secret Type: Unexpected format for CDP")

    else:
        print("⚠️ Key Type: Legacy/Advanced Trade format")
        print("   This may be the older API format")
        print("   Consider creating a new CDP key")

    print("\n📝 What each API format supports:")
    print("\n   CDP (Cloud Developer Platform):")
    print("   • Wallet operations")
    print("   • Advanced features")
    print("   • New unified API")
    print("   • May NOT support Advanced Trade endpoints")

    print("\n   Advanced Trade API:")
    print("   • Trading operations")
    print("   • Order management")
    print("   • Portfolio tracking")
    print("   • This is what you likely need for trading")

    print("\n💡 Recommendation:")
    print("   For SovereignShadow trading system, you need:")
    print("   → Coinbase Advanced Trade API keys")
    print("   → NOT CDP (Cloud Developer Platform) keys")
    print("\n   Create keys at: https://www.coinbase.com/settings/api")
    print("   (NOT at portal.cdp.coinbase.com)")


if __name__ == "__main__":
    print("🪙 COINBASE CDP API VERIFICATION")
    print("="*60)

    # First, analyze key type
    check_key_type()

    # Then attempt connection
    print("\n" + "="*60)
    verify_coinbase_cdp()

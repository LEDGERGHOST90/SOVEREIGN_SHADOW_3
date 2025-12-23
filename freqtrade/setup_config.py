#!/usr/bin/env python3
"""
FreqTrade Config Setup - CDP Key Support
Configures FreqTrade with Coinbase CDP (Cloud Developer Platform) credentials
"""
import os
import json
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path('/Volumes/LegacySafe/SS_III/.env')
load_dotenv(env_path)

# Paths
CONFIG_PATH = Path('/Volumes/LegacySafe/SS_III/freqtrade/config.json')

def setup_config():
    """Load config and inject CDP API keys."""

    # Load existing config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Get Coinbase CDP credentials
    api_key = os.getenv('COINBASE_API_KEY', '')
    secret_file = os.getenv('COINBASE_API_SECRET_FILE', '')

    if not api_key:
        print("ERROR: COINBASE_API_KEY not found in .env")
        return False

    if not secret_file or not os.path.exists(secret_file):
        print(f"ERROR: Secret file not found at: {secret_file}")
        return False

    # Read the private key from file
    with open(secret_file, 'r') as f:
        private_key = f.read()

    # CDP keys use special format in CCXT
    # Key format: organizations/{org_id}/apiKeys/{key_id}
    # Secret: The PEM private key content

    config['exchange']['key'] = api_key
    config['exchange']['secret'] = private_key

    # Generate secure tokens for API server
    config['api_server']['jwt_secret_key'] = secrets.token_hex(32)
    config['api_server']['ws_token'] = secrets.token_hex(16)

    # Save updated config
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    print("=" * 50)
    print("FreqTrade Config Updated!")
    print("=" * 50)
    print(f"Exchange: {config['exchange']['name']}")
    print(f"Key Type: CDP (Cloud Developer Platform)")
    print(f"Key ID: {api_key[:50]}...")
    print(f"Pairs: {config['exchange']['pair_whitelist']}")
    print(f"Dry Run: {config['dry_run']}")
    print(f"Strategy: {config['strategy']}")
    print("=" * 50)

    return True

def test_connection():
    """Test exchange connection with FreqTrade."""
    print("\nTesting exchange connection...")
    import subprocess
    result = subprocess.run(
        ['freqtrade', 'test-pairlist', '-c', 'config.json'],
        cwd='/Volumes/LegacySafe/SS_III/freqtrade',
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def test_ccxt_direct():
    """Test CCXT connection directly."""
    print("\nTesting CCXT direct connection...")
    import ccxt

    api_key = os.getenv('COINBASE_API_KEY', '')
    secret_file = os.getenv('COINBASE_API_SECRET_FILE', '')

    with open(secret_file, 'r') as f:
        private_key = f.read()

    try:
        exchange = ccxt.coinbase({
            'apiKey': api_key,
            'secret': private_key,
            'enableRateLimit': True,
        })

        # Test by fetching balance
        balance = exchange.fetch_balance()
        usdc = balance.get('USDC', {}).get('free', 0)
        print(f"Connection successful!")
        print(f"USDC Balance: ${usdc:.2f}")

        # Get INJ and LINK prices
        inj_ticker = exchange.fetch_ticker('INJ/USDC')
        link_ticker = exchange.fetch_ticker('LINK/USDC')
        print(f"INJ Price: ${inj_ticker['last']:.4f}")
        print(f"LINK Price: ${link_ticker['last']:.4f}")

        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == '__main__':
    print("Setting up FreqTrade for Coinbase CDP...")
    if setup_config():
        print("\nConfig saved. Testing connections...")
        if test_ccxt_direct():
            print("\n✓ CCXT direct connection works")
            test_connection()
        else:
            print("\n✗ CCXT connection failed - check API keys")

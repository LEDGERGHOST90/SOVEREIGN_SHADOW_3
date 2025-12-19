#!/usr/bin/env python3
"""
SS_III → Replit Portfolio Push
Gathers live data from all exchanges locally and pushes to Shadow.AI Replit
"""

import json
import os
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path

import jwt
import requests
from cryptography.hazmat.primitives import serialization

# Paths
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
BRAIN_PATH = SS3_ROOT / "BRAIN.json"
ENV_PATH = SS3_ROOT / ".env"
REPLIT_URL = "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"


def load_env():
    """Load environment variables from .env"""
    env = {}
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    return env


def fetch_coinbase_balance(env):
    """Fetch Coinbase balance using official coinbase-advanced-py library"""
    try:
        api_key = env.get('COINBASE_API_KEY')
        pem_path = env.get('COINBASE_API_SECRET_FILE')

        if not api_key or not pem_path:
            return {"error": "Missing Coinbase credentials", "holdings": []}

        with open(pem_path, 'r') as f:
            api_secret = f.read()

        # Use official library - handles JWT auth correctly
        from coinbase.rest import RESTClient
        client = RESTClient(api_key=api_key, api_secret=api_secret)
        accounts = client.get_accounts()

        holdings = []
        for acc in accounts.accounts:
            # Handle dict or object response
            if isinstance(acc.available_balance, dict):
                bal = float(acc.available_balance.get('value', 0))
            else:
                bal = float(acc.available_balance.value) if acc.available_balance else 0

            if bal > 0.0001:
                holdings.append({
                    "symbol": acc.currency,
                    "amount": bal,
                    "source": "coinbase"
                })
        return {"status": "connected", "holdings": holdings}
    except Exception as e:
        return {"error": str(e), "holdings": []}


def fetch_kraken_balance(env):
    """Fetch Kraken balance"""
    try:
        api_key = env.get('KRAKEN_API_KEY')
        api_secret = env.get('KRAKEN_PRIVATE_KEY')

        if not api_key or not api_secret:
            return {"error": "Missing Kraken credentials", "holdings": []}

        import urllib.parse

        url = 'https://api.kraken.com/0/private/Balance'
        nonce = str(int(time.time() * 1000))
        data = {'nonce': nonce}
        post_data = urllib.parse.urlencode(data)

        message = b'/0/private/Balance' + hashlib.sha256((nonce + post_data).encode()).digest()
        signature = base64.b64encode(hmac.new(base64.b64decode(api_secret), message, hashlib.sha512).digest())

        headers = {
            'API-Key': api_key,
            'API-Sign': signature.decode()
        }

        response = requests.post(url, headers=headers, data=data, timeout=15)

        if response.ok:
            result = response.json()
            if result.get('error'):
                return {"error": str(result['error']), "holdings": []}

            holdings = []
            symbol_map = {
                'XXBT': 'BTC', 'XETH': 'ETH', 'XXDG': 'DOGE',
                'ZUSD': 'USD', 'XXRP': 'XRP', 'XSOL': 'SOL'
            }

            for asset, amount in result.get('result', {}).items():
                if float(amount) > 0.0001:
                    symbol = symbol_map.get(asset, asset)
                    holdings.append({
                        "symbol": symbol,
                        "amount": float(amount),
                        "source": "kraken"
                    })
            return {"status": "connected", "holdings": holdings}
        else:
            return {"error": f"HTTP {response.status_code}", "holdings": []}
    except Exception as e:
        return {"error": str(e), "holdings": []}


def fetch_binance_us_balance(env):
    """Fetch Binance US balance"""
    try:
        api_key = env.get('BINANCE_US_API_KEY')
        api_secret = env.get('BINANCE_US_API_SECRET')

        if not api_key or not api_secret:
            return {"error": "Missing Binance US credentials", "holdings": []}

        timestamp = str(int(time.time() * 1000))
        query = f'timestamp={timestamp}'
        signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()

        url = f'https://api.binance.us/api/v3/account?{query}&signature={signature}'
        headers = {'X-MBX-APIKEY': api_key}

        response = requests.get(url, headers=headers, timeout=15)

        if response.ok:
            data = response.json()
            holdings = []
            for b in data.get('balances', []):
                total = float(b['free']) + float(b['locked'])
                if total > 0.0001:
                    holdings.append({
                        "symbol": b['asset'],
                        "amount": total,
                        "source": "binance_us"
                    })
            return {"status": "connected", "holdings": holdings}
        else:
            return {"error": f"HTTP {response.status_code}", "holdings": []}
    except Exception as e:
        return {"error": str(e), "holdings": []}


def fetch_okx_balance(env):
    """Fetch OKX balance"""
    try:
        api_key = env.get('OKX_API_KEY')
        secret_key = env.get('OKX_SECRET_KEY')
        passphrase = env.get('OKX_PASSPHRASE')

        if not api_key or not secret_key or not passphrase:
            return {"error": "Missing OKX credentials", "holdings": []}

        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + \
                    datetime.now(timezone.utc).strftime('%f')[:3] + 'Z'
        method = 'GET'
        request_path = '/api/v5/account/balance'

        prehash = timestamp + method + request_path
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), prehash.encode(), hashlib.sha256).digest()
        ).decode()

        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }

        response = requests.get('https://us.okx.com/api/v5/account/balance', headers=headers, timeout=15)

        if response.ok:
            data = response.json()
            if data.get('code') == '0':
                details = data.get('data', [{}])[0].get('details', [])
                holdings = []
                for d in details:
                    bal = float(d.get('availBal', 0) or 0)
                    if bal > 0.0001:
                        holdings.append({
                            "symbol": d.get('ccy'),
                            "amount": bal,
                            "source": "okx"
                        })
                return {"status": "connected", "holdings": holdings}
            else:
                return {"error": data.get('msg', 'Unknown error'), "holdings": []}
        else:
            return {"error": f"HTTP {response.status_code}", "holdings": []}
    except Exception as e:
        return {"error": str(e), "holdings": []}


def push_to_replit(portfolio_data):
    """Push portfolio data to Replit"""
    try:
        # Try POST to update endpoint
        response = requests.post(
            f"{REPLIT_URL}/api/portfolio/update",
            json=portfolio_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)


def update_brain(portfolio_data):
    """Update local BRAIN.json with portfolio data"""
    try:
        with open(BRAIN_PATH) as f:
            brain = json.load(f)
    except:
        brain = {}

    # Calculate totals
    total_holdings = []
    exchange_totals = {}

    for exchange, data in portfolio_data['exchanges'].items():
        holdings = data.get('holdings', [])
        total_holdings.extend(holdings)
        # Would need price data to calculate USD values

    brain['portfolio']['exchanges'] = {
        'kraken': sum(h['amount'] for h in portfolio_data['exchanges'].get('kraken', {}).get('holdings', []) if h['symbol'] == 'USD'),
        'binance_us': sum(h['amount'] for h in portfolio_data['exchanges'].get('binance_us', {}).get('holdings', []) if h['symbol'] in ['USD', 'USDC', 'USDT']),
        'coinbase': sum(h['amount'] for h in portfolio_data['exchanges'].get('coinbase', {}).get('holdings', []) if h['symbol'] in ['USD', 'USDC']),
        'okx': sum(h['amount'] for h in portfolio_data['exchanges'].get('okx', {}).get('holdings', []) if h['symbol'] in ['USD', 'USDT'])
    }

    brain['last_updated'] = datetime.now().isoformat()
    brain['last_sync'] = {
        'timestamp': datetime.now().isoformat(),
        'exchanges_checked': list(portfolio_data['exchanges'].keys()),
        'total_holdings': len(total_holdings)
    }

    with open(BRAIN_PATH, 'w') as f:
        json.dump(brain, f, indent=2)

    return brain


def main():
    print("=" * 60)
    print("🔄 SS_III → REPLIT PORTFOLIO PUSH")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    # Load credentials
    env = load_env()
    print(f"✅ Loaded {len(env)} environment variables")

    # Fetch from all exchanges
    portfolio = {
        "timestamp": datetime.now().isoformat(),
        "source": "ss3_local",
        "exchanges": {}
    }

    print("\n📡 Fetching exchange data...")

    # Coinbase
    print("  → Coinbase...", end=" ")
    coinbase = fetch_coinbase_balance(env)
    portfolio['exchanges']['coinbase'] = coinbase
    if coinbase.get('error'):
        print(f"❌ {coinbase['error']}")
    else:
        print(f"✅ {len(coinbase['holdings'])} holdings")
        for h in coinbase['holdings']:
            print(f"      {h['symbol']}: {h['amount']}")

    # Kraken
    print("  → Kraken...", end=" ")
    kraken = fetch_kraken_balance(env)
    portfolio['exchanges']['kraken'] = kraken
    if kraken.get('error'):
        print(f"❌ {kraken['error']}")
    else:
        print(f"✅ {len(kraken['holdings'])} holdings")
        for h in kraken['holdings']:
            print(f"      {h['symbol']}: {h['amount']}")

    # Binance US
    print("  → Binance US...", end=" ")
    binance = fetch_binance_us_balance(env)
    portfolio['exchanges']['binance_us'] = binance
    if binance.get('error'):
        print(f"❌ {binance['error']}")
    else:
        print(f"✅ {len(binance['holdings'])} holdings")
        for h in binance['holdings']:
            print(f"      {h['symbol']}: {h['amount']}")

    # OKX
    print("  → OKX...", end=" ")
    okx = fetch_okx_balance(env)
    portfolio['exchanges']['okx'] = okx
    if okx.get('error'):
        print(f"❌ {okx['error']}")
    else:
        print(f"✅ {len(okx['holdings'])} holdings")
        for h in okx['holdings']:
            print(f"      {h['symbol']}: {h['amount']}")

    # Push to Replit
    print("\n📤 Pushing to Replit...")
    status, response = push_to_replit(portfolio)
    if status == 200:
        print(f"✅ Push successful")
    else:
        print(f"⚠️  Push status: {status}")
        print(f"   Response: {response[:200]}")

    # Update local BRAIN.json
    print("\n📝 Updating BRAIN.json...")
    brain = update_brain(portfolio)
    print(f"✅ BRAIN.json updated: {brain.get('last_updated')}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 PORTFOLIO SUMMARY")
    print("=" * 60)

    all_holdings = []
    for ex, data in portfolio['exchanges'].items():
        all_holdings.extend(data.get('holdings', []))

    # Group by symbol
    by_symbol = {}
    for h in all_holdings:
        sym = h['symbol']
        if sym not in by_symbol:
            by_symbol[sym] = {'total': 0, 'sources': []}
        by_symbol[sym]['total'] += h['amount']
        by_symbol[sym]['sources'].append(f"{h['source']}:{h['amount']:.6f}")

    for sym, data in sorted(by_symbol.items()):
        print(f"  {sym}: {data['total']:.6f} ({', '.join(data['sources'])})")

    print("\n✅ Sync complete!")
    return portfolio


if __name__ == "__main__":
    main()

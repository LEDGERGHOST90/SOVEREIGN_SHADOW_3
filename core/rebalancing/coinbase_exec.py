#!/usr/bin/env python3
# Sovereign Shadow - Coinbase Advanced Trade Execution
# Location: core/rebalancing/coinbase_exec.py

"""
Handles trade execution via Coinbase Advanced Trade API
Supports both paper and live trading modes
"""

import os
import json
import time
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
import requests

# Dynamic path resolution
BASE_DIR = Path(__file__).parent.parent.parent  # Go up from core/rebalancing/
LOGS_DIR = BASE_DIR / "logs"

# Safety guardrails
ENV = os.getenv("ENV", "paper")
DISABLE_REAL = os.getenv("DISABLE_REAL_EXCHANGES", "1") == "1"

# API credentials
API_KEY = os.getenv("COINBASE_API_KEY", "")
API_SECRET = os.getenv("COINBASE_API_SECRET", "")
BASE_URL = "https://api.coinbase.com"

def generate_signature(timestamp, method, path, body=""):
    """Generate HMAC signature for Coinbase API"""
    message = f"{timestamp}{method}{path}{body}"
    signature = hmac.new(
        API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def get_auth_headers(method, path, body=""):
    """Generate authentication headers"""
    timestamp = str(int(time.time()))
    signature = generate_signature(timestamp, method, path, body)
    
    return {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

def get_coinbase_balances():
    """Get all account balances from Coinbase"""
    if DISABLE_REAL:
        print("📄 PAPER MODE: Returning mock Coinbase balances")
        return {
            "XRP": {"balance": 424.23, "value": 1060.85},
            "USDC": {"balance": 0.36, "value": 0.36}
        }
    
    endpoint = "/api/v3/brokerage/accounts"
    headers = get_auth_headers("GET", endpoint)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        
        accounts = response.json().get("accounts", [])
        balances = {}
        
        for account in accounts:
            currency = account["currency"]
            balance = float(account["available_balance"]["value"])
            
            if balance > 0:
                price = get_live_price(currency)
                value = balance * price
                
                balances[currency] = {
                    "balance": balance,
                    "value": value
                }
        
        return balances
    except Exception as e:
        print(f"❌ Error fetching Coinbase balances: {e}")
        return {}

def get_live_price(asset):
    """Get current spot price for asset"""
    if asset == "USDC" or asset == "USD":
        return 1.0
    
    try:
        endpoint = f"/api/v3/brokerage/products/{asset}-USD"
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"⚠️ Could not fetch price for {asset}: {e}")
        fallbacks = {"XRP": 2.50, "SOL": 185.0, "ETH": 4000.0, "BTC": 69000.0}
        return fallbacks.get(asset, 0)

def buy(asset, amount_usd, slippage_limit=0.005, offset=0):
    """Execute market buy order"""
    product_id = f"{asset}-USD"
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "BUY",
        "asset": asset,
        "amount_usd": amount_usd,
        "offset": offset,
        "mode": "PAPER" if DISABLE_REAL else "LIVE"
    }
    
    if DISABLE_REAL:
        print(f"📄 PAPER: Would buy ${amount_usd:.2f} of {asset} with {offset:+.1f}% offset")
        log_entry["status"] = "simulated"
        log_trade(log_entry)
        return {"success": True, "simulated": True}
    
    # Real execution
    endpoint = "/api/v3/brokerage/orders"
    
    order_data = {
        "client_order_id": f"ss_buy_{asset}_{int(time.time())}",
        "product_id": product_id,
        "side": "BUY",
        "order_configuration": {
            "market_market_ioc": {
                "quote_size": str(amount_usd)
            }
        }
    }
    
    body = json.dumps(order_data)
    headers = get_auth_headers("POST", endpoint, body)
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, data=body)
        response.raise_for_status()
        
        result = response.json()
        log_entry["status"] = "success"
        log_entry["order_id"] = result.get("order_id")
        log_entry["response"] = result
        
        print(f"✅ BUY executed: ${amount_usd:.2f} {asset}")
        log_trade(log_entry)
        return result
    except Exception as e:
        print(f"❌ BUY failed: {e}")
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)
        log_trade(log_entry)
        return {"success": False, "error": str(e)}

def sell(asset, amount_usd):
    """Execute market sell order"""
    product_id = f"{asset}-USD"
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": "SELL",
        "asset": asset,
        "amount_usd": amount_usd,
        "mode": "PAPER" if DISABLE_REAL else "LIVE"
    }
    
    if DISABLE_REAL:
        print(f"📄 PAPER: Would sell ${amount_usd:.2f} of {asset}")
        log_entry["status"] = "simulated"
        log_trade(log_entry)
        return {"success": True, "simulated": True}
    
    # Get current price to calculate base size
    price = get_live_price(asset)
    base_size = amount_usd / price
    
    endpoint = "/api/v3/brokerage/orders"
    
    order_data = {
        "client_order_id": f"ss_sell_{asset}_{int(time.time())}",
        "product_id": product_id,
        "side": "SELL",
        "order_configuration": {
            "market_market_ioc": {
                "base_size": str(base_size)
            }
        }
    }
    
    body = json.dumps(order_data)
    headers = get_auth_headers("POST", endpoint, body)
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, data=body)
        response.raise_for_status()
        
        result = response.json()
        log_entry["status"] = "success"
        log_entry["order_id"] = result.get("order_id")
        log_entry["response"] = result
        
        print(f"✅ SELL executed: ${amount_usd:.2f} {asset}")
        log_trade(log_entry)
        return result
    except Exception as e:
        print(f"❌ SELL failed: {e}")
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)
        log_trade(log_entry)
        return {"success": False, "error": str(e)}

def log_trade(trade_data):
    """Append trade to persistent log"""
    log_file = LOGS_DIR / "trade_execution.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, "a") as f:
        json.dump(trade_data, f)
        f.write("\n")

if __name__ == "__main__":
    # Test balances
    balances = get_coinbase_balances()
    print("\n💰 Coinbase Balances:")
    for asset, data in balances.items():
        print(f"  {asset}: {data['balance']:.6f} (${data['value']:.2f})")

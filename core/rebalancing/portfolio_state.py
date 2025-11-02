#!/usr/bin/env python3
# Sovereign Shadow - Portfolio State Aggregator
# Location: /home/sovereign_shadow/core_portfolio/portfolio_state.py

"""
Aggregates portfolio positions across multiple sources:
- Coinbase Exchange
- Ledger cold storage
- AAVE DeFi positions

Returns unified portfolio with weights and allocations
"""

import os
import json
from decimal import Decimal
from datetime import datetime

# Import your existing clients
try:
    from coinbase_exec import get_coinbase_balances
    from aave_client import get_aave_positions
except ImportError:
    print("⚠️ Some clients not available, using mock data")
    
    def get_coinbase_balances():
        return {"XRP": {"balance": 424.23, "value": 1060.85}}
    
    def get_aave_positions():
        return {
            "stETH": {"balance": 1.0, "value": 3870.00},
            "BTC": {"balance": 0.032, "value": 2224.31}
        }

# Mock Ledger client (replace with your actual implementation)
def get_ledger_balances():
    """Get balances from Ledger hardware wallet"""
    return {
        "SOL": {"balance": 2.5046, "value": 464.55},
        "ETH": {"balance": 0.0413, "value": 159.86},
        "AAVE": {"balance": 0.309, "value": 68.63},
        "USDC": {"balance": 84.42, "value": 84.42}
    }

PRICES_CACHE = {}

def get_live_price(asset):
    """Get current market price for asset"""
    global PRICES_CACHE
    
    # Mock prices - replace with actual API calls
    prices = {
        "ETH": 4000.0,
        "BTC": 69000.0,
        "SOL": 185.0,
        "XRP": 2.50,
        "AAVE": 222.0,
        "USDC": 1.0,
        "stETH": 4000.0
    }
    
    PRICES_CACHE[asset] = prices.get(asset, 0.0)
    return PRICES_CACHE[asset]

def normalize_asset_name(asset):
    """Normalize asset names (stETH -> ETH, wBTC -> BTC, etc.)"""
    MAPPINGS = {
        "stETH": "ETH",
        "wstETH": "ETH",
        "WETH": "ETH",
        "wBTC": "BTC",
        "USDtb": "USDC"
    }
    return MAPPINGS.get(asset, asset)

def get_portfolio_allocation():
    """
    Main function: aggregate all positions and calculate weights
    """
    print("📊 Aggregating portfolio positions...")
    
    # Gather from all sources
    coinbase = get_coinbase_balances()
    ledger = get_ledger_balances()
    aave = get_aave_positions()
    
    # Aggregate by asset
    portfolio = {}
    
    for source_name, source_data in [
        ("Coinbase", coinbase),
        ("Ledger", ledger),
        ("AAVE", aave)
    ]:
        for asset, data in source_data.items():
            normalized = normalize_asset_name(asset)
            
            if normalized not in portfolio:
                portfolio[normalized] = {
                    "balance": 0,
                    "value": 0,
                    "sources": []
                }
            
            portfolio[normalized]["balance"] += data["balance"]
            portfolio[normalized]["value"] += data["value"]
            portfolio[normalized]["sources"].append({
                "source": source_name,
                "balance": data["balance"],
                "value": data["value"]
            })
    
    # Calculate total and weights
    total_value = sum(p["value"] for p in portfolio.values())
    
    for asset in portfolio:
        portfolio[asset]["weight"] = portfolio[asset]["value"] / total_value if total_value > 0 else 0
        portfolio[asset]["target_weight"] = None
    
    # Add metadata
    portfolio["_metadata"] = {
        "total_value": total_value,
        "timestamp": datetime.utcnow().isoformat(),
        "sources": ["Coinbase", "Ledger", "AAVE"]
    }
    
    return portfolio

def save_portfolio_snapshot(portfolio, filename=None):
    """Save portfolio state to JSON for audit trail"""
    if filename is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/sovereign_shadow/logs/portfolio_snapshot_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Convert Decimal to float for JSON serialization
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    with open(filename, "w") as f:
        json.dump(portfolio, f, indent=2, default=decimal_default)
    
    print(f"💾 Portfolio snapshot saved: {filename}")
    return filename

if __name__ == "__main__":
    # Test the aggregator
    portfolio = get_portfolio_allocation()
    
    print("\n📊 CURRENT PORTFOLIO ALLOCATION")
    print("=" * 70)
    
    total = portfolio["_metadata"]["total_value"]
    print(f"Total Value: ${total:,.2f}\n")
    
    # Sort by value descending
    assets = [(k, v) for k, v in portfolio.items() if k != "_metadata"]
    assets.sort(key=lambda x: x[1]["value"], reverse=True)
    
    print(f"{'Asset':<8} | {'Value':>12} | {'Weight':>7} | {'Balance':>12}")
    print("-" * 70)
    
    for asset, data in assets:
        weight_pct = data["weight"] * 100
        value = data["value"]
        balance = data["balance"]
        
        print(f"{asset:<8} | ${value:>11,.2f} | {weight_pct:>6.1f}% | {balance:>12.6f}")
        
        # Show sources if multiple
        if len(data["sources"]) > 1:
            for src in data["sources"]:
                print(f"         └─ {src['source']:10s}: ${src['value']:>8,.2f}")
    
    print("=" * 70)
    
    # Save snapshot
    save_portfolio_snapshot(portfolio)

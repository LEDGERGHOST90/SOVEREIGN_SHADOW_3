#!/usr/bin/env python3
"""
COLD STORAGE AUTO-REFRESH
Queries blockchain APIs directly for real-time Ledger balances.
Updates BRAIN.json automatically.

Usage:
    python3 bin/refresh_cold_storage.py          # One-time refresh
    python3 bin/refresh_cold_storage.py --watch  # Continuous (every 5 min)
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

BRAIN_PATH = Path(__file__).parent.parent / "BRAIN.json"

# Wallet addresses from .env
WALLETS = {
    "BTC": os.getenv("LEDGER_BTC_ADDRESS", "bc1qlpkhy9lzh6qwjhc0muhlrzqf3vfrhgezmjp0kx"),
    "ETH": os.getenv("LEDGER_ETH_ADDRESS", "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"),
    "XRP": os.getenv("LEDGER_XRP_ADDRESS", "rGvSX7BMyuzkghXbaJqLHk529pYE2j5WR3"),
    "SOL": os.getenv("LEDGER_SOL_ADDRESS", "RovUJaZwiZ1X36sEW7TBmhie5unzPmxtMg1ATwFtGVk"),
}

# ERC-20 token contracts on Ethereum
ERC20_TOKENS = {
    "wstETH": "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
}

# Etherscan API (free tier - 5 calls/sec)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")  # Optional, works without

# =============================================================================
# BLOCKCHAIN QUERIES
# =============================================================================

def get_btc_balance_from_ledger_addresses() -> dict:
    """Query Bitcoin balance from ALL addresses in Ledger Live HD wallet"""
    try:
        from pathlib import Path
        import json

        ledger_file = Path.home() / "Library/Application Support/Ledger Live/app.json"
        if not ledger_file.exists():
            print("  Ledger Live not found, using single address")
            return get_btc_balance_single(WALLETS.get("BTC", ""))

        data = json.loads(ledger_file.read_text())
        accounts = data.get("data", {}).get("accounts", [])

        addresses = set()
        for acc_wrapper in accounts:
            acc = acc_wrapper.get("data", {})
            if "bitcoin" in acc.get("currencyId", ""):
                btc_resources = acc.get("bitcoinResources", {})
                for utxo in btc_resources.get("utxos", []):
                    if len(utxo) >= 4:
                        addresses.add(utxo[3])

        if not addresses:
            print("  No BTC addresses found in Ledger Live")
            return {"balance": 0, "success": False}

        total_sats = 0
        address_balances = {}

        for addr in addresses:
            try:
                resp = requests.get(f"https://blockstream.info/api/address/{addr}", timeout=10)
                d = resp.json()
                funded = d.get("chain_stats", {}).get("funded_txo_sum", 0)
                spent = d.get("chain_stats", {}).get("spent_txo_sum", 0)
                bal = funded - spent
                if bal > 0:
                    total_sats += bal
                    address_balances[addr] = bal
                time.sleep(0.2)  # Rate limit
            except:
                pass

        btc = Decimal(total_sats) / Decimal("100000000")
        return {
            "balance": float(btc),
            "raw": total_sats,
            "addresses": len(address_balances),
            "success": True
        }
    except Exception as e:
        print(f"  BTC query error: {e}")
        return {"balance": 0, "success": False}


def get_btc_balance_single(address: str) -> dict:
    """Query Bitcoin balance from single address via Blockstream"""
    try:
        resp = requests.get(f"https://blockstream.info/api/address/{address}", timeout=10)
        d = resp.json()
        funded = d.get("chain_stats", {}).get("funded_txo_sum", 0)
        spent = d.get("chain_stats", {}).get("spent_txo_sum", 0)
        satoshis = funded - spent
        btc = Decimal(satoshis) / Decimal("100000000")
        return {"balance": float(btc), "raw": satoshis, "success": True}
    except Exception as e:
        print(f"  BTC query error: {e}")
    return {"balance": 0, "success": False}


def get_eth_balance(address: str) -> dict:
    """Query ETH balance from public RPC"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }
        resp = requests.post("https://eth.llamarpc.com", json=payload, timeout=10)
        data = resp.json()

        if "result" in data:
            wei = int(data["result"], 16)
            eth = Decimal(wei) / Decimal("1000000000000000000")
            return {"balance": float(eth), "raw": wei, "success": True}
    except Exception as e:
        print(f"  ETH query error: {e}")
    return {"balance": 0, "success": False}


def get_erc20_balance(wallet_address: str, token_address: str, decimals: int = 18) -> dict:
    """Query ERC-20 token balance from public RPC"""
    try:
        # balanceOf(address) = 0x70a08231
        data = "0x70a08231" + "000000000000000000000000" + wallet_address[2:]

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{"to": token_address, "data": data}, "latest"],
            "id": 1
        }
        resp = requests.post("https://eth.llamarpc.com", json=payload, timeout=10)
        result = resp.json()

        if "result" in result and result["result"] != "0x":
            raw = int(result["result"], 16)
            balance = Decimal(raw) / Decimal(10 ** decimals)
            return {"balance": float(balance), "raw": raw, "success": True}
    except Exception as e:
        print(f"  ERC-20 query error: {e}")
    return {"balance": 0, "success": False}


def get_aave_position(wallet_address: str) -> dict:
    """Query AAVE V3 position for wstETH collateral"""
    try:
        aave_pool = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
        user_padded = "000000000000000000000000" + wallet_address[2:].lower()

        # getUserAccountData(address)
        func_sig = "0xbf92857c"
        data = func_sig + user_padded

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{"to": aave_pool, "data": data}, "latest"],
            "id": 1
        }
        resp = requests.post("https://eth.llamarpc.com", json=payload, timeout=15)
        result = resp.json()

        if "result" in result and len(result["result"]) > 2:
            hex_result = result["result"][2:]

            # Parse return values (6 uint256 values)
            total_collateral = int(hex_result[0:64], 16) / 1e8
            total_debt = int(hex_result[64:128], 16) / 1e8
            health_factor = int(hex_result[320:384], 16) / 1e18

            return {
                "collateral_usd": round(total_collateral, 2),
                "debt_usd": round(total_debt, 2),
                "health_factor": round(health_factor, 2),
                "net_usd": round(total_collateral - total_debt, 2),
                "success": True
            }
    except Exception as e:
        print(f"  AAVE query error: {e}")
    return {"collateral_usd": 0, "debt_usd": 0, "success": False}


def get_xrp_balance(address: str) -> dict:
    """Query XRP balance from XRPL"""
    try:
        url = "https://s1.ripple.com:51234/"
        payload = {
            "method": "account_info",
            "params": [{"account": address, "ledger_index": "validated"}]
        }
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()

        if "result" in data and "account_data" in data["result"]:
            drops = int(data["result"]["account_data"]["Balance"])
            xrp = Decimal(drops) / Decimal("1000000")
            return {"balance": float(xrp), "raw": drops, "success": True}
    except Exception as e:
        print(f"  XRP query error: {e}")
    return {"balance": 0, "success": False}


def get_sol_balance(address: str) -> dict:
    """Query SOL balance from Solana RPC"""
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()

        if "result" in data and "value" in data["result"]:
            lamports = int(data["result"]["value"])
            sol = Decimal(lamports) / Decimal("1000000000")
            return {"balance": float(sol), "raw": lamports, "success": True}
    except Exception as e:
        print(f"  SOL query error: {e}")
    return {"balance": 0, "success": False}


def get_prices() -> dict:
    """Get current prices from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,ripple,solana,lido-staked-ether,usd-coin",
            "vs_currencies": "usd"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        return {
            "BTC": data.get("bitcoin", {}).get("usd", 0),
            "ETH": data.get("ethereum", {}).get("usd", 0),
            "XRP": data.get("ripple", {}).get("usd", 0),
            "SOL": data.get("solana", {}).get("usd", 0),
            "wstETH": data.get("lido-staked-ether", {}).get("usd", 0),
            "USDC": 1.0,  # Stablecoin
        }
    except Exception as e:
        print(f"  Price query error: {e}")
        return {}


# =============================================================================
# MAIN REFRESH LOGIC
# =============================================================================

def refresh_cold_storage() -> dict:
    """Refresh all cold storage balances from blockchain APIs"""

    print("\n" + "=" * 60)
    print("COLD STORAGE REFRESH - Querying Blockchains")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "source": "blockchain_apis",
        "assets": {},
        "total_usd": 0,
        "assets_over_50": {}
    }

    # Get current prices
    print("\nFetching prices...")
    prices = get_prices()
    results["prices"] = prices

    # Query BTC (all HD wallet addresses)
    print(f"\nQuerying BTC (HD wallet - all addresses)...")
    btc = get_btc_balance_from_ledger_addresses()
    if btc["success"]:
        usd = btc["balance"] * prices.get("BTC", 0)
        results["assets"]["BTC"] = {
            "address": "HD_WALLET_MULTI_ADDRESS",
            "address_count": btc.get("addresses", 1),
            "balance": btc["balance"],
            "usd": round(usd, 2),
            "price": prices.get("BTC", 0)
        }
        results["total_usd"] += usd
        print(f"  BTC: {btc['balance']:.8f} = ${usd:,.2f} ({btc.get('addresses', 1)} addresses)")

    # Query ETH (native)
    print(f"\nQuerying ETH: {WALLETS['ETH'][:20]}...")
    eth = get_eth_balance(WALLETS["ETH"])
    if eth["success"]:
        usd = eth["balance"] * prices.get("ETH", 0)
        results["assets"]["ETH"] = {
            "address": WALLETS["ETH"],
            "balance": eth["balance"],
            "usd": round(usd, 2),
            "price": prices.get("ETH", 0)
        }
        results["total_usd"] += usd
        print(f"  ETH: {eth['balance']:.8f} = ${usd:,.2f}")

    # Query wstETH (ERC-20)
    print(f"\nQuerying wstETH (ERC-20)...")
    time.sleep(0.3)  # Rate limit
    wsteth = get_erc20_balance(WALLETS["ETH"], ERC20_TOKENS["wstETH"], 18)
    if wsteth["success"]:
        usd = wsteth["balance"] * prices.get("wstETH", 0)
        results["assets"]["wstETH"] = {
            "address": WALLETS["ETH"],
            "contract": ERC20_TOKENS["wstETH"],
            "balance": wsteth["balance"],
            "usd": round(usd, 2),
            "price": prices.get("wstETH", 0),
            "note": "AAVE collateral"
        }
        results["total_usd"] += usd
        print(f"  wstETH: {wsteth['balance']:.8f} = ${usd:,.2f}")

    # Query USDC (ERC-20)
    print(f"\nQuerying USDC (ERC-20)...")
    time.sleep(0.3)  # Rate limit
    usdc = get_erc20_balance(WALLETS["ETH"], ERC20_TOKENS["USDC"], 6)
    if usdc["success"]:
        usd = usdc["balance"] * prices.get("USDC", 1)
        results["assets"]["USDC"] = {
            "address": WALLETS["ETH"],
            "contract": ERC20_TOKENS["USDC"],
            "balance": usdc["balance"],
            "usd": round(usd, 2),
            "price": 1.0
        }
        results["total_usd"] += usd
        print(f"  USDC: {usdc['balance']:.2f} = ${usd:,.2f}")

    # Query XRP
    print(f"\nQuerying XRP: {WALLETS['XRP'][:20]}...")
    xrp = get_xrp_balance(WALLETS["XRP"])
    if xrp["success"]:
        usd = xrp["balance"] * prices.get("XRP", 0)
        results["assets"]["XRP"] = {
            "address": WALLETS["XRP"],
            "balance": xrp["balance"],
            "usd": round(usd, 2),
            "price": prices.get("XRP", 0)
        }
        results["total_usd"] += usd
        print(f"  XRP: {xrp['balance']:.6f} = ${usd:,.2f}")

    # Query SOL
    print(f"\nQuerying SOL: {WALLETS['SOL'][:20]}...")
    sol = get_sol_balance(WALLETS["SOL"])
    if sol["success"]:
        usd = sol["balance"] * prices.get("SOL", 0)
        results["assets"]["SOL"] = {
            "address": WALLETS["SOL"],
            "balance": sol["balance"],
            "usd": round(usd, 2),
            "price": prices.get("SOL", 0)
        }
        results["total_usd"] += usd
        print(f"  SOL: {sol['balance']:.8f} = ${usd:,.2f}")

    # Query AAVE Position
    print(f"\nQuerying AAVE V3 Position...")
    aave = get_aave_position(WALLETS["ETH"])
    if aave["success"]:
        results["aave"] = {
            "collateral_usd": aave["collateral_usd"],
            "debt_usd": aave["debt_usd"],
            "health_factor": aave["health_factor"],
            "net_usd": aave["net_usd"]
        }
        # Add collateral to total (debt will be subtracted later)
        results["total_usd"] += aave["collateral_usd"]
        results["total_debt"] = aave["debt_usd"]
        print(f"  Collateral: ${aave['collateral_usd']:,.2f}")
        print(f"  Debt: -${aave['debt_usd']:,.2f}")
        print(f"  Health Factor: {aave['health_factor']}")

    # Filter assets over $50
    for asset, data in results["assets"].items():
        if data["usd"] >= 50:
            results["assets_over_50"][asset] = data

    results["total_usd"] = round(results["total_usd"], 2)

    # Calculate net (total - debt)
    total_debt = results.get("total_debt", 0)
    net_value = results["total_usd"] - total_debt

    print("\n" + "=" * 60)
    print(f"TOTAL ASSETS: ${results['total_usd']:,.2f}")
    if total_debt > 0:
        print(f"TOTAL DEBT:   -${total_debt:,.2f}")
        print(f"NET VALUE:    ${net_value:,.2f}")
    print(f"Assets over $50: {len(results['assets_over_50'])}")
    print("=" * 60)

    results["net_value"] = round(net_value, 2)
    return results


def update_brain(cold_storage_data: dict) -> bool:
    """Update BRAIN.json with fresh cold storage data"""
    try:
        # Read current BRAIN
        with open(BRAIN_PATH, 'r') as f:
            brain = json.load(f)

        # Update ledger section
        brain["portfolio"]["ledger"] = {
            "total": cold_storage_data["total_usd"],
            "last_refresh": cold_storage_data["timestamp"],
            "source": "blockchain_apis"
        }

        # Add individual assets
        for asset, data in cold_storage_data["assets"].items():
            brain["portfolio"]["ledger"][asset] = data["balance"]
            brain["portfolio"]["ledger"][f"{asset}_usd"] = data["usd"]

        # Update cold_storage_over_50
        brain["config"]["wallets"]["cold_storage_over_50"] = {}
        for asset, data in cold_storage_data["assets_over_50"].items():
            brain["config"]["wallets"]["cold_storage_over_50"][asset] = {
                "address": data["address"],
                "balance": data["balance"],
                "usd": data["usd"],
                "source": "blockchain_api"
            }

        # Update prices
        brain["prices"] = {
            **cold_storage_data["prices"],
            "updated": cold_storage_data["timestamp"]
        }

        # Update ledger_total
        brain["portfolio"]["ledger_total"] = cold_storage_data["total_usd"]

        # Update AAVE data if present
        if "aave" in cold_storage_data:
            brain["portfolio"]["aave"] = {
                "collateral": cold_storage_data["aave"]["collateral_usd"],
                "debt": cold_storage_data["aave"]["debt_usd"],
                "health_factor": cold_storage_data["aave"]["health_factor"],
                "net": cold_storage_data["aave"]["net_usd"],
                "source": "blockchain_api"
            }
            brain["portfolio"]["aave_debt"] = cold_storage_data["aave"]["debt_usd"]

        # Recalculate net worth
        exchange_total = brain["portfolio"].get("exchange_total", 0)
        aave_debt = cold_storage_data.get("total_debt", brain["portfolio"].get("aave_debt", 0))

        # Net worth = Ledger assets + Exchange assets - AAVE debt
        brain["portfolio"]["net_worth"] = round(
            cold_storage_data.get("net_value", cold_storage_data["total_usd"]) + exchange_total, 2
        )
        brain["portfolio"]["ledger_net"] = round(
            cold_storage_data["total_usd"] - aave_debt, 2
        )

        # Update timestamp
        brain["last_updated"] = cold_storage_data["timestamp"]
        brain["portfolio"]["snapshot_time"] = cold_storage_data["timestamp"]

        # Write back
        with open(BRAIN_PATH, 'w') as f:
            json.dump(brain, f, indent=2)

        print(f"\n✅ BRAIN.json updated")
        print(f"   Net Worth: ${brain['portfolio']['net_worth']:,.2f}")
        return True

    except Exception as e:
        print(f"\n❌ Failed to update BRAIN.json: {e}")
        return False


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Refresh cold storage balances")
    parser.add_argument("--watch", action="store_true", help="Continuous refresh every 5 minutes")
    parser.add_argument("--interval", type=int, default=300, help="Refresh interval in seconds (default: 300)")
    args = parser.parse_args()

    if args.watch:
        print(f"Starting continuous refresh (every {args.interval}s)...")
        print("Press Ctrl+C to stop\n")

        while True:
            try:
                data = refresh_cold_storage()
                update_brain(data)
                print(f"\nNext refresh in {args.interval}s...")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
    else:
        data = refresh_cold_storage()
        update_brain(data)


if __name__ == "__main__":
    main()

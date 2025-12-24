#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Multi-Platform Top Performer Scanner
Scans Coinbase, Kraken, Binance for top gainers
Aggregates across all platforms for unified view

Usage:
    python scanners/platform_scanner.py                  # Full scan
    python scanners/platform_scanner.py --platform coinbase
    python scanners/platform_scanner.py --top 10
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List
import time

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# PLATFORM CONFIGURATIONS
# =============================================================================

PLATFORMS = {
    "coinbase": {
        "name": "Coinbase",
        "api_url": "https://api.exchange.coinbase.com",
        "products_endpoint": "/products",
        "ticker_endpoint": "/products/{}/ticker",
        "stats_endpoint": "/products/{}/stats",
        "quote_currency": "USD"
    },
    "kraken": {
        "name": "Kraken",
        "api_url": "https://api.kraken.com/0/public",
        "pairs_endpoint": "/AssetPairs",
        "ticker_endpoint": "/Ticker"
    },
    "binance": {
        "name": "Binance US",
        "api_url": "https://api.binance.us/api/v3",
        "ticker_endpoint": "/ticker/24hr"
    }
}

@dataclass
class AssetPerformance:
    symbol: str
    platform: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float

# =============================================================================
# COINBASE SCANNER
# =============================================================================

def scan_coinbase(limit: int = 25) -> List[AssetPerformance]:
    """Scan Coinbase for top performers"""
    results = []

    try:
        # Get all products
        resp = requests.get(
            f"{PLATFORMS['coinbase']['api_url']}/products",
            timeout=10
        )
        products = resp.json()

        # Filter USD pairs
        usd_products = [p for p in products if p.get("quote_currency") == "USD"
                       and p.get("status") == "online"
                       and not p.get("trading_disabled", False)]

        print(f"  Scanning {len(usd_products)} Coinbase pairs...")

        # Get 24h stats for each (batch requests)
        for product in usd_products[:100]:  # Limit to avoid rate limits
            try:
                stats_resp = requests.get(
                    f"{PLATFORMS['coinbase']['api_url']}/products/{product['id']}/stats",
                    timeout=5
                )
                stats = stats_resp.json()

                if "open" in stats and "last" in stats:
                    open_price = float(stats["open"])
                    last_price = float(stats["last"])

                    if open_price > 0:
                        change_24h = ((last_price - open_price) / open_price) * 100

                        results.append(AssetPerformance(
                            symbol=product["base_currency"],
                            platform="coinbase",
                            price=last_price,
                            change_24h=change_24h,
                            volume_24h=float(stats.get("volume", 0)),
                            high_24h=float(stats.get("high", 0)),
                            low_24h=float(stats.get("low", 0))
                        ))

                time.sleep(0.05)  # Rate limit protection

            except Exception:
                continue

    except Exception as e:
        print(f"  Coinbase error: {e}")

    # Sort by 24h change
    results.sort(key=lambda x: x.change_24h, reverse=True)
    return results[:limit]

# =============================================================================
# KRAKEN SCANNER
# =============================================================================

def scan_kraken(limit: int = 25) -> List[AssetPerformance]:
    """Scan Kraken for top performers"""
    results = []

    try:
        # Get all pairs
        pairs_resp = requests.get(
            f"{PLATFORMS['kraken']['api_url']}/AssetPairs",
            timeout=10
        )
        pairs_data = pairs_resp.json()

        if pairs_data.get("error"):
            print(f"  Kraken error: {pairs_data['error']}")
            return results

        # Filter USD pairs
        usd_pairs = [k for k, v in pairs_data["result"].items()
                    if k.endswith("USD") and not k.endswith("ZUSD")]

        print(f"  Scanning {len(usd_pairs)} Kraken pairs...")

        # Get tickers (can batch)
        ticker_resp = requests.get(
            f"{PLATFORMS['kraken']['api_url']}/Ticker",
            params={"pair": ",".join(usd_pairs[:50])},  # Batch limit
            timeout=10
        )
        ticker_data = ticker_resp.json()

        if ticker_data.get("error"):
            print(f"  Kraken ticker error: {ticker_data['error']}")
            return results

        for pair, data in ticker_data.get("result", {}).items():
            try:
                # Kraken format: c=last, o=open, h=high, l=low, v=volume
                last_price = float(data["c"][0])
                open_price = float(data["o"])

                if open_price > 0:
                    change_24h = ((last_price - open_price) / open_price) * 100

                    # Extract symbol from pair
                    symbol = pair.replace("USD", "").replace("XBT", "BTC")
                    if symbol.startswith("X") and len(symbol) > 3:
                        symbol = symbol[1:]  # Remove X prefix
                    if symbol.startswith("Z"):
                        symbol = symbol[1:]  # Remove Z prefix

                    results.append(AssetPerformance(
                        symbol=symbol,
                        platform="kraken",
                        price=last_price,
                        change_24h=change_24h,
                        volume_24h=float(data["v"][1]),
                        high_24h=float(data["h"][1]),
                        low_24h=float(data["l"][1])
                    ))

            except Exception:
                continue

    except Exception as e:
        print(f"  Kraken error: {e}")

    results.sort(key=lambda x: x.change_24h, reverse=True)
    return results[:limit]

# =============================================================================
# BINANCE SCANNER
# =============================================================================

def scan_binance(limit: int = 25) -> List[AssetPerformance]:
    """Scan Binance US for top performers"""
    results = []

    try:
        resp = requests.get(
            f"{PLATFORMS['binance']['api_url']}/ticker/24hr",
            timeout=10
        )
        tickers = resp.json()

        print(f"  Scanning {len(tickers)} Binance pairs...")

        # Filter USD pairs
        for ticker in tickers:
            symbol = ticker.get("symbol", "")
            if symbol.endswith("USD") or symbol.endswith("USDT"):
                try:
                    base = symbol.replace("USDT", "").replace("USD", "")
                    change_24h = float(ticker.get("priceChangePercent", 0))

                    results.append(AssetPerformance(
                        symbol=base,
                        platform="binance",
                        price=float(ticker.get("lastPrice", 0)),
                        change_24h=change_24h,
                        volume_24h=float(ticker.get("quoteVolume", 0)),
                        high_24h=float(ticker.get("highPrice", 0)),
                        low_24h=float(ticker.get("lowPrice", 0))
                    ))
                except Exception:
                    continue

    except Exception as e:
        print(f"  Binance error: {e}")

    results.sort(key=lambda x: x.change_24h, reverse=True)
    return results[:limit]

# =============================================================================
# AGGREGATOR
# =============================================================================

def scan_all_platforms(per_platform: int = 25) -> dict:
    """Scan all platforms and aggregate results"""
    print(f"\n{'='*70}")
    print(f"SOVEREIGN SHADOW - Multi-Platform Scanner")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    all_results = {
        "coinbase": [],
        "kraken": [],
        "binance": []
    }

    # Scan each platform
    print("\n[COINBASE]")
    all_results["coinbase"] = scan_coinbase(per_platform)

    print("\n[KRAKEN]")
    all_results["kraken"] = scan_kraken(per_platform)

    print("\n[BINANCE US]")
    all_results["binance"] = scan_binance(per_platform)

    return all_results

def print_top_performers(results: dict, per_platform: int = 25, unified_top: int = 10, best_of_best: int = 3):
    """Print formatted results"""

    # Per-platform top performers
    for platform, assets in results.items():
        print(f"\n{'='*70}")
        print(f"TOP {min(per_platform, len(assets))} - {platform.upper()}")
        print(f"{'='*70}")
        print(f"{'Rank':<5} {'Symbol':<10} {'Price':>15} {'24h Change':>12} {'Volume':>18}")
        print("-" * 70)

        for i, asset in enumerate(assets[:per_platform], 1):
            change_str = f"+{asset.change_24h:.2f}%" if asset.change_24h >= 0 else f"{asset.change_24h:.2f}%"
            vol_str = f"${asset.volume_24h:,.0f}" if asset.volume_24h else "N/A"

            print(f"{i:<5} {asset.symbol:<10} ${asset.price:>14,.6f} {change_str:>12} {vol_str:>18}")

    # Unified top across all platforms
    all_assets = []
    for platform, assets in results.items():
        all_assets.extend(assets)

    # Remove duplicates (keep highest change)
    seen = {}
    for asset in all_assets:
        if asset.symbol not in seen or asset.change_24h > seen[asset.symbol].change_24h:
            seen[asset.symbol] = asset

    unified = list(seen.values())
    unified.sort(key=lambda x: x.change_24h, reverse=True)

    print(f"\n{'='*70}")
    print(f"TOP {unified_top} ACROSS ALL PLATFORMS")
    print(f"{'='*70}")
    print(f"{'Rank':<5} {'Symbol':<10} {'Platform':<12} {'Price':>15} {'24h Change':>12}")
    print("-" * 70)

    for i, asset in enumerate(unified[:unified_top], 1):
        change_str = f"+{asset.change_24h:.2f}%" if asset.change_24h >= 0 else f"{asset.change_24h:.2f}%"
        print(f"{i:<5} {asset.symbol:<10} {asset.platform:<12} ${asset.price:>14,.6f} {change_str:>12}")

    # BEST OF THE BEST
    print(f"\n{'='*70}")
    print(f"TOP {best_of_best} PLAYS - BEST OF THE BEST")
    print(f"{'='*70}")

    for i, asset in enumerate(unified[:best_of_best], 1):
        change_str = f"+{asset.change_24h:.2f}%" if asset.change_24h >= 0 else f"{asset.change_24h:.2f}%"
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"

        print(f"\n{emoji} #{i} {asset.symbol}")
        print(f"   Platform: {asset.platform.upper()}")
        print(f"   Price: ${asset.price:,.6f}")
        print(f"   24h Change: {change_str}")
        print(f"   24h Range: ${asset.low_24h:,.6f} - ${asset.high_24h:,.6f}")
        print(f"   Volume: ${asset.volume_24h:,.0f}")

    return unified[:best_of_best]

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Platform Top Performer Scanner")
    parser.add_argument("--platform", choices=["coinbase", "kraken", "binance", "all"], default="all")
    parser.add_argument("--per-platform", type=int, default=25, help="Top N per platform")
    parser.add_argument("--top", type=int, default=10, help="Unified top N")
    parser.add_argument("--best", type=int, default=3, help="Best of the best")

    args = parser.parse_args()

    if args.platform == "all":
        results = scan_all_platforms(args.per_platform)
    else:
        results = {args.platform: []}
        if args.platform == "coinbase":
            results["coinbase"] = scan_coinbase(args.per_platform)
        elif args.platform == "kraken":
            results["kraken"] = scan_kraken(args.per_platform)
        elif args.platform == "binance":
            results["binance"] = scan_binance(args.per_platform)

    top_plays = print_top_performers(results, args.per_platform, args.top, args.best)

    print(f"\n{'='*70}")
    print("Scan complete.")
    print(f"{'='*70}\n")

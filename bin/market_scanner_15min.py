#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW 24/7 MARKET SCANNER
Runs every 15 minutes - Tracks BTC, ETH, SOL, XRP prices and alerts
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure paths
LOGS_DIR = PROJECT_ROOT / "logs" / "market_scanner"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SCAN_LOG = LOGS_DIR / "scan_history.jsonl"
ALERT_LOG = LOGS_DIR / "price_alerts.jsonl"
LATEST_SCAN = LOGS_DIR / "latest_scan.json"

# Price alert levels (from PERSISTENT_STATE.json)
PRICE_ALERTS = {
    "BTC": [99000, 97000, 95000, 90000],  # Alert if BTC hits these levels
    "ETH": [3500, 3000, 2800, 2500],
    "SOL": [200, 180, 160, 140],
    "XRP": [0.50, 0.45, 0.40, 0.35]
}

def log_event(message: str, level: str = "INFO"):
    """Log event with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def fetch_crypto_prices():
    """Fetch current crypto prices from CoinGecko (free API, no key needed)"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana,ripple",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_last_updated_at": "true"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Map to friendly names
        prices = {
            "BTC": {
                "price": data["bitcoin"]["usd"],
                "change_24h": data["bitcoin"].get("usd_24h_change", 0),
                "volume_24h": data["bitcoin"].get("usd_24h_vol", 0),
                "last_updated": data["bitcoin"].get("last_updated_at", 0)
            },
            "ETH": {
                "price": data["ethereum"]["usd"],
                "change_24h": data["ethereum"].get("usd_24h_change", 0),
                "volume_24h": data["ethereum"].get("usd_24h_vol", 0),
                "last_updated": data["ethereum"].get("last_updated_at", 0)
            },
            "SOL": {
                "price": data["solana"]["usd"],
                "change_24h": data["solana"].get("usd_24h_change", 0),
                "volume_24h": data["solana"].get("usd_24h_vol", 0),
                "last_updated": data["solana"].get("last_updated_at", 0)
            },
            "XRP": {
                "price": data["ripple"]["usd"],
                "change_24h": data["ripple"].get("usd_24h_change", 0),
                "volume_24h": data["ripple"].get("usd_24h_vol", 0),
                "last_updated": data["ripple"].get("last_updated_at", 0)
            }
        }

        return prices

    except Exception as e:
        log_event(f"Error fetching prices: {e}", "ERROR")
        return None

def check_price_alerts(prices: dict, previous_prices: dict = None):
    """Check if any price alerts have been triggered"""
    alerts = []

    for symbol, price_data in prices.items():
        current_price = price_data["price"]

        # Check against alert levels
        for alert_level in PRICE_ALERTS.get(symbol, []):
            # Alert if price crosses below the level
            if previous_prices:
                prev_price = previous_prices.get(symbol, {}).get("price", 0)
                if prev_price > alert_level >= current_price:
                    alerts.append({
                        "symbol": symbol,
                        "alert_type": "price_drop",
                        "alert_level": alert_level,
                        "current_price": current_price,
                        "previous_price": prev_price,
                        "timestamp": datetime.now().isoformat()
                    })

    return alerts

def save_scan_result(prices: dict, alerts: list):
    """Save scan result to log files"""
    scan_result = {
        "timestamp": datetime.now().isoformat(),
        "prices": prices,
        "alerts_triggered": len(alerts),
        "alerts": alerts
    }

    # Save to JSONL (append)
    with open(SCAN_LOG, "a") as f:
        f.write(json.dumps(scan_result) + "\n")

    # Save latest scan (overwrite)
    with open(LATEST_SCAN, "w") as f:
        json.dump(scan_result, f, indent=2)

    # Save alerts if any
    if alerts:
        for alert in alerts:
            with open(ALERT_LOG, "a") as f:
                f.write(json.dumps(alert) + "\n")

    log_event(f"Scan saved: {len(alerts)} alerts triggered")

def load_previous_scan():
    """Load previous scan for comparison"""
    try:
        if LATEST_SCAN.exists():
            with open(LATEST_SCAN, "r") as f:
                data = json.load(f)
                return data.get("prices", {})
    except Exception as e:
        log_event(f"Could not load previous scan: {e}", "WARNING")

    return None

def display_results(prices: dict, alerts: list):
    """Display scan results"""
    print("\n" + "="*70)
    print("🏴 SOVEREIGN SHADOW 24/7 MARKET SCANNER")
    print(f"   Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PST')}")
    print("="*70)

    for symbol, data in prices.items():
        change_emoji = "📈" if data["change_24h"] > 0 else "📉"
        print(f"\n{symbol}:")
        print(f"  Price: ${data['price']:,.2f}")
        print(f"  24h Change: {change_emoji} {data['change_24h']:+.2f}%")
        print(f"  24h Volume: ${data['volume_24h']:,.0f}")

    if alerts:
        print(f"\n{'='*70}")
        print(f"🚨 {len(alerts)} PRICE ALERT(S) TRIGGERED!")
        print(f"{'='*70}")
        for alert in alerts:
            print(f"\n  {alert['symbol']}: Dropped below ${alert['alert_level']:,.2f}")
            print(f"  Current: ${alert['current_price']:,.2f}")
            print(f"  Previous: ${alert['previous_price']:,.2f}")
    else:
        print(f"\n✅ No price alerts triggered")

    print(f"\n{'='*70}")
    print(f"📁 Logs saved to: {LOGS_DIR}")
    print(f"   • {SCAN_LOG.name}")
    print(f"   • {LATEST_SCAN.name}")
    if alerts:
        print(f"   • {ALERT_LOG.name}")
    print("="*70 + "\n")

def main():
    """Main execution"""
    log_event("🏴 Starting market scanner...")

    # Load previous scan for comparison
    previous_prices = load_previous_scan()

    # Fetch current prices
    prices = fetch_crypto_prices()

    if not prices:
        log_event("Failed to fetch prices, exiting", "ERROR")
        return 1

    log_event(f"Fetched prices for {len(prices)} assets")

    # Check for price alerts
    alerts = check_price_alerts(prices, previous_prices)

    if alerts:
        log_event(f"🚨 {len(alerts)} price alert(s) triggered!", "ALERT")

    # Save results
    save_scan_result(prices, alerts)

    # Display results
    display_results(prices, alerts)

    log_event("✅ Market scanner completed successfully")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log_event("Scanner interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        log_event(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

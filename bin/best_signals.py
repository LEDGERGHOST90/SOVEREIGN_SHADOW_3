#!/usr/bin/env python3
"""
BEST SIGNALS SCANNER
Scans ALL available assets and returns only the highest-ROI opportunities
"""

import os
import sys
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Comprehensive asset list - top 100 by market cap + trending
ALL_ASSETS = [
    # Top 20
    "BTC", "ETH", "XRP", "SOL", "BNB", "DOGE", "ADA", "TRX", "AVAX", "LINK",
    "TON", "SHIB", "DOT", "BCH", "NEAR", "LTC", "UNI", "PEPE", "ICP", "APT",
    # 21-50
    "ETC", "RENDER", "FET", "STX", "XLM", "CRO", "MNT", "OKB", "INJ", "ARB",
    "FIL", "IMX", "HBAR", "VET", "ATOM", "OP", "MKR", "WIF", "GRT", "THETA",
    # 51-80 (high volatility / meme potential)
    "BONK", "FLOKI", "JASMY", "SEI", "SUI", "TIA", "JUP", "PYTH", "WLD", "BLUR",
    "ONDO", "STRK", "MANTA", "DYM", "ALT", "PIXEL", "PORTAL", "AEVO", "ENA", "ETHFI",
    # High volatility alts
    "ORDI", "SATS", "1000SATS", "RAY", "JTO", "MEME", "NFT", "AI", "TAO", "RNDR"
]

API_BASE = "http://localhost:8000"

def generate_signal(symbol):
    """Generate signal for a single asset"""
    try:
        resp = requests.post(
            f"{API_BASE}/api/signals/generate",
            json={"symbol": symbol},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            signal = data.get("signal", {})
            return {
                "symbol": symbol,
                "action": signal.get("action", "ERROR"),
                "confidence": signal.get("confidence", 0),
                "reasoning": signal.get("reasoning", ""),
                "risk_level": signal.get("risk_level", "unknown"),
                "entry_price": signal.get("entry_price"),
                "stop_loss": signal.get("stop_loss"),
                "take_profit_1": signal.get("take_profit_1"),
            }
    except Exception as e:
        pass
    return None

def scan_all_assets(max_workers=5):
    """Scan all assets in parallel"""
    print(f"🔍 Scanning {len(ALL_ASSETS)} assets for best signals...")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_signal, symbol): symbol for symbol in ALL_ASSETS}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            if result:
                results.append(result)
                # Show progress
                if result["action"] in ["BUY", "SELL"] and result["confidence"] >= 70:
                    emoji = "🟢" if result["action"] == "BUY" else "🔴"
                    print(f"   {emoji} FOUND: {result['symbol']} {result['action']} ({result['confidence']}%)")
            
            # Progress indicator
            if completed % 10 == 0:
                print(f"   ... scanned {completed}/{len(ALL_ASSETS)}")
    
    return results

def rank_signals(results):
    """Rank signals by potential ROI"""
    
    # Separate by action
    buy_signals = [r for r in results if r["action"] == "BUY" and r["confidence"] >= 60]
    sell_signals = [r for r in results if r["action"] == "SELL" and r["confidence"] >= 70]
    
    # Sort by confidence
    buy_signals.sort(key=lambda x: x["confidence"], reverse=True)
    sell_signals.sort(key=lambda x: x["confidence"], reverse=True)
    
    return buy_signals, sell_signals

def main():
    print("=" * 70)
    print("🎯 BEST SIGNALS SCANNER - Finding Highest ROI Opportunities")
    print("=" * 70)
    print()
    
    # Scan all assets
    results = scan_all_assets(max_workers=5)
    
    # Rank them
    buy_signals, sell_signals = rank_signals(results)
    
    print()
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    
    # Best BUY opportunities
    print(f"\n🟢 TOP BUY SIGNALS ({len(buy_signals)} found):")
    if buy_signals:
        for i, sig in enumerate(buy_signals[:10], 1):
            print(f"   {i}. {sig['symbol']}: {sig['confidence']}% confidence")
            print(f"      {sig['reasoning'][:80]}...")
            print()
    else:
        print("   No strong BUY signals found (RSI not oversold)")
    
    # Best SELL opportunities
    print(f"\n🔴 TOP SELL SIGNALS ({len(sell_signals)} found):")
    if sell_signals:
        for i, sig in enumerate(sell_signals[:5], 1):
            print(f"   {i}. {sig['symbol']}: {sig['confidence']}% confidence")
            print(f"      {sig['reasoning'][:80]}...")
            print()
    else:
        print("   No strong SELL signals")
    
    # Summary
    print("=" * 70)
    print(f"📈 SUMMARY: {len(buy_signals)} buys, {len(sell_signals)} sells from {len(results)} scanned")
    print("=" * 70)
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "scanned": len(results),
        "buy_signals": buy_signals[:10],
        "sell_signals": sell_signals[:5]
    }
    
    output_file = "/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/logs/best_signals.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Saved to: {output_file}")
    
    return output

if __name__ == "__main__":
    main()

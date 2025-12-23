#!/usr/bin/env python3
"""
🔍 AI BASKET SCANNER SWARM
Low-latency position monitor for FET, RENDER, SUI
Commander: LedgerGhost90
Created: 2025-12-23
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

# Actual fill prices from Coinbase (slippage accounted)
# 3-TIER LADDER EXIT: TP1 +25% (50%), TP2 +40% (30%), TP3 +60% (20%), SL -7%
POSITIONS = {
    'FET': {
        'quantity': 916.1,
        'entry': 0.2104,  # Actual fill
        'stop_loss': 0.1957,  # -7% from actual
        'tp1': 0.2630,  # +25% → sell 50%
        'tp2': 0.2946,  # +40% → sell 30%
        'tp3': 0.3366,  # +60% → sell 20% (moonbag)
        'coingecko_id': 'fetch-ai'
    },
    'RENDER': {
        'quantity': 123.8,
        'entry': 1.2780,  # Actual fill
        'stop_loss': 1.1885,  # -7% from actual
        'tp1': 1.5975,  # +25% → sell 50%
        'tp2': 1.7892,  # +40% → sell 30%
        'tp3': 2.0448,  # +60% → sell 20% (moonbag)
        'coingecko_id': 'render-token'
    },
    'SUI': {
        'quantity': 90.7,
        'entry': 1.4370,  # Actual fill (avg of 2 fills)
        'stop_loss': 1.3364,  # -7% from actual
        'tp1': 1.7963,  # +25% → sell 50%
        'tp2': 2.0118,  # +40% → sell 30%
        'tp3': 2.2992,  # +60% → sell 20% (moonbag)
        'coingecko_id': 'sui'
    }
}

SCAN_INTERVAL = 30  # seconds
NTFY_TOPIC = "sovereignshadow_dc4d2fa1"
LOG_PATH = Path("/Volumes/LegacySafe/SS_III/logs/ai_basket")
LOG_PATH.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ALERT SYSTEM
# ============================================================================

def send_alert(title: str, message: str, priority: str = "default"):
    """Send push notification via ntfy"""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": "chart_with_upwards_trend" if "TP" in title else "warning"
            },
            timeout=5
        )
        print(f"📱 ALERT SENT: {title}")
    except Exception as e:
        print(f"❌ Alert failed: {e}")

# ============================================================================
# PRICE FETCHER
# ============================================================================

async def fetch_prices() -> Dict[str, float]:
    """Fetch current prices from CoinGecko"""
    ids = ",".join(p['coingecko_id'] for p in POSITIONS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()

        prices = {}
        for symbol, config in POSITIONS.items():
            cg_id = config['coingecko_id']
            if cg_id in data:
                prices[symbol] = data[cg_id]['usd']

        return prices

    except Exception as e:
        print(f"❌ Price fetch error: {e}")
        return {}

# ============================================================================
# POSITION MONITOR
# ============================================================================

class PositionMonitor:
    def __init__(self):
        self.alerts_sent = {sym: {'tp1': False, 'tp2': False, 'tp3': False, 'sl': False} for sym in POSITIONS}
        self.last_prices = {}
        self.start_time = datetime.now()

    def check_levels(self, symbol: str, price: float) -> Optional[str]:
        """Check if price hit any levels"""
        pos = POSITIONS[symbol]
        alerts = self.alerts_sent[symbol]

        # Check TP3 first (highest priority - moonbag)
        if price >= pos['tp3'] and not alerts['tp3']:
            alerts['tp3'] = True
            return f"🚀 TP3 MOONBAG: {symbol} @ ${price:.4f} (+60%) - SELL 20%"

        # Check TP2
        if price >= pos['tp2'] and not alerts['tp2']:
            alerts['tp2'] = True
            return f"🎯 TP2 HIT: {symbol} @ ${price:.4f} (+40%) - SELL 30%"

        # Check TP1
        if price >= pos['tp1'] and not alerts['tp1']:
            alerts['tp1'] = True
            return f"🎯 TP1 HIT: {symbol} @ ${price:.4f} (+25%) - SELL 50%"

        # Check Stop Loss
        if price <= pos['stop_loss'] and not alerts['sl']:
            alerts['sl'] = True
            return f"🛑 STOP LOSS: {symbol} @ ${price:.4f} (-7%) - SELL 100%"

        return None

    def calculate_pnl(self, symbol: str, price: float) -> Dict:
        """Calculate P&L for position"""
        pos = POSITIONS[symbol]
        entry = pos['entry']
        qty = pos['quantity']

        value = qty * price
        cost = qty * entry
        pnl = value - cost
        pnl_pct = (price - entry) / entry * 100

        return {
            'symbol': symbol,
            'price': price,
            'entry': entry,
            'quantity': qty,
            'value': value,
            'cost': cost,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        }

    async def scan_loop(self):
        """Main scanning loop"""
        print("=" * 60)
        print("🔍 AI BASKET SCANNER SWARM - ACTIVE")
        print("=" * 60)
        print(f"Monitoring: {', '.join(POSITIONS.keys())}")
        print(f"Interval: {SCAN_INTERVAL}s")
        print(f"Alerts: ntfy.sh/{NTFY_TOPIC}")
        print("=" * 60)

        iteration = 0

        while True:
            iteration += 1

            try:
                prices = await fetch_prices()

                if not prices:
                    await asyncio.sleep(SCAN_INTERVAL)
                    continue

                timestamp = datetime.now().strftime("%H:%M:%S")

                print(f"\n[{timestamp}] Scan #{iteration}")
                print("-" * 50)

                total_value = 0
                total_pnl = 0

                for symbol in POSITIONS:
                    if symbol not in prices:
                        continue

                    price = prices[symbol]
                    pnl_data = self.calculate_pnl(symbol, price)

                    total_value += pnl_data['value']
                    total_pnl += pnl_data['pnl']

                    # Check for alerts
                    alert = self.check_levels(symbol, price)
                    if alert:
                        send_alert(f"{symbol} ALERT", alert, "high")
                        print(f"  🚨 {alert}")

                    # Display
                    arrow = "🟢" if pnl_data['pnl'] >= 0 else "🔴"
                    print(f"  {arrow} {symbol}: ${price:.4f} | P&L: ${pnl_data['pnl']:+.2f} ({pnl_data['pnl_pct']:+.1f}%)")

                print(f"\n  💰 TOTAL: ${total_value:.2f} | P&L: ${total_pnl:+.2f}")

                # Log to file
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices,
                    'total_value': total_value,
                    'total_pnl': total_pnl
                }

                log_file = LOG_PATH / f"scan_{datetime.now().strftime('%Y%m%d')}.jsonl"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')

            except Exception as e:
                print(f"❌ Scan error: {e}")

            await asyncio.sleep(SCAN_INTERVAL)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔍 AI BASKET SCANNER SWARM                            ║
    ║     Low-Latency Position Monitor                          ║
    ║     FET | RENDER | SUI                                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    monitor = PositionMonitor()

    try:
        asyncio.run(monitor.scan_loop())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scanner stopped by user")
        print("=" * 60)

if __name__ == "__main__":
    main()

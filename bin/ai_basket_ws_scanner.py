#!/usr/bin/env python3
"""
🔍 AI BASKET SCANNER - WEBSOCKET EDITION
Real-time price monitoring via Coinbase WebSocket
Zero polling, instant alerts, no rate limits

Commander: LedgerGhost90
Created: 2025-12-23
"""

import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import requests

# Crash protection
MAX_RECONNECT_ATTEMPTS = 100
RECONNECT_DELAY = 5

# ============================================================================
# CONFIGURATION
# ============================================================================

# AI BASKET - Active trades with TP/SL alerts
POSITIONS = {
    'FET': {
        'quantity': 916.1,
        'entry': 0.2104,
        'stop_loss': 0.1957,
        'tp1': 0.2630,
        'tp2': 0.2946,
        'tp3': 0.3366,
        'pair': 'FET-USD'
    },
    'RENDER': {
        'quantity': 123.8,
        'entry': 1.2780,
        'stop_loss': 1.1885,
        'tp1': 1.5975,
        'tp2': 1.7892,
        'tp3': 2.0448,
        'pair': 'RENDER-USD'
    },
    'SUI': {
        'quantity': 90.7,
        'entry': 1.4370,
        'stop_loss': 1.3364,
        'tp1': 1.7963,
        'tp2': 2.0118,
        'tp3': 2.2992,
        'pair': 'SUI-USD'
    }
}

# LEDGER HOLDS - Long-term holdings (tracking only, no TP/SL)
HOLDS = {
    'BTC': {
        'quantity': 0.01485,
        'entry': 94500,
        'pair': 'BTC-USD',
        'location': 'ledger'
    },
    'ETH': {
        'quantity': 0.8427,
        'entry': 3340,
        'pair': 'ETH-USD',
        'location': 'ledger+aave'
    },
    'XRP': {
        'quantity': 276.5,
        'entry': 2.23,
        'pair': 'XRP-USD',
        'location': 'ledger'
    }
}

NTFY_TOPIC = "sovereignshadow_dc4d2fa1"
LOG_PATH = Path("/Volumes/LegacySafe/SS_III/logs/ai_basket")
LOG_PATH.mkdir(parents=True, exist_ok=True)

# Coinbase WebSocket endpoint (public, no auth needed for ticker)
WS_URL = "wss://ws-feed.exchange.coinbase.com"

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
        print(f"⚠️  Alert failed: {e}")

# ============================================================================
# POSITION MONITOR
# ============================================================================

class WebSocketMonitor:
    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.alerts_sent = {sym: {'tp1': False, 'tp2': False, 'tp3': False, 'sl': False} for sym in POSITIONS}
        self.last_log_time = 0
        self.last_display_time = 0
        self.message_count = 0
        self.start_time = datetime.now()

    def check_levels(self, symbol: str, price: float) -> Optional[str]:
        """Check if price hit any levels"""
        pos = POSITIONS[symbol]
        alerts = self.alerts_sent[symbol]

        if price >= pos['tp3'] and not alerts['tp3']:
            alerts['tp3'] = True
            return f"🚀 TP3 MOONBAG: {symbol} @ ${price:.4f} (+60%) - SELL 20%"

        if price >= pos['tp2'] and not alerts['tp2']:
            alerts['tp2'] = True
            return f"🎯 TP2 HIT: {symbol} @ ${price:.4f} (+40%) - SELL 30%"

        if price >= pos['tp1'] and not alerts['tp1']:
            alerts['tp1'] = True
            return f"🎯 TP1 HIT: {symbol} @ ${price:.4f} (+25%) - SELL 50%"

        if price <= pos['stop_loss'] and not alerts['sl']:
            alerts['sl'] = True
            return f"🛑 STOP LOSS: {symbol} @ ${price:.4f} (-7%) - SELL 100%"

        return None

    def calculate_totals(self) -> Dict:
        """Calculate total portfolio value and P&L"""
        total_value = 0
        total_cost = 0

        for symbol, pos in POSITIONS.items():
            if symbol in self.prices:
                price = self.prices[symbol]
                total_value += pos['quantity'] * price
                total_cost += pos['quantity'] * pos['entry']

        return {
            'value': total_value,
            'cost': total_cost,
            'pnl': total_value - total_cost,
            'pnl_pct': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        }

    def display_status(self, force: bool = False):
        """Display current status (throttled to every 10 seconds unless forced)"""
        now = time.time()
        if not force and (now - self.last_display_time) < 10:
            return
        self.last_display_time = now

        timestamp = datetime.now().strftime("%H:%M:%S")
        totals = self.calculate_totals()

        print(f"\n[{timestamp}] WebSocket Update (msgs: {self.message_count})")
        print("-" * 50)

        for symbol, pos in POSITIONS.items():
            if symbol in self.prices:
                price = self.prices[symbol]
                pnl = (price - pos['entry']) / pos['entry'] * 100
                value = pos['quantity'] * price
                arrow = "🟢" if pnl >= 0 else "🔴"
                print(f"  {arrow} {symbol}: ${price:.4f} | {pnl:+.2f}% | ${value:.2f}")

        pnl_arrow = "📈" if totals['pnl'] >= 0 else "📉"
        print(f"\n  {pnl_arrow} TOTAL: ${totals['value']:.2f} | P&L: ${totals['pnl']:+.2f} ({totals['pnl_pct']:+.2f}%)")

    def log_to_file(self):
        """Log to JSONL file (every 30 seconds)"""
        now = time.time()
        if (now - self.last_log_time) < 30:
            return
        self.last_log_time = now

        if len(self.prices) < len(POSITIONS):
            return

        totals = self.calculate_totals()
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prices': self.prices.copy(),
            'total_value': totals['value'],
            'total_pnl': totals['pnl'],
            'source': 'websocket'
        }

        log_file = LOG_PATH / f"scan_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    async def handle_message(self, message: dict):
        """Process incoming WebSocket message"""
        if message.get('type') == 'ticker':
            product_id = message.get('product_id', '')
            price_str = message.get('price')

            if price_str:
                price = float(price_str)

                # Map pair back to symbol
                for symbol, pos in POSITIONS.items():
                    if pos['pair'] == product_id:
                        old_price = self.prices.get(symbol)
                        self.prices[symbol] = price
                        self.message_count += 1

                        # Check for alerts on every price update
                        alert = self.check_levels(symbol, price)
                        if alert:
                            send_alert(f"{symbol} ALERT", alert, "high")
                            print(f"\n🚨 {alert}")
                            self.display_status(force=True)

                        # Log periodically
                        self.log_to_file()

                        # Display status periodically
                        self.display_status()
                        break

    async def connect(self):
        """Connect to Coinbase WebSocket"""
        try:
            import websockets
        except ImportError:
            print("❌ websockets not installed. Installing...")
            os.system(f"{sys.executable} -m pip install websockets")
            import websockets

        product_ids = [pos['pair'] for pos in POSITIONS.values()]

        subscribe_message = {
            "type": "subscribe",
            "product_ids": product_ids,
            "channels": ["ticker"]
        }

        reconnect_count = 0

        while reconnect_count < MAX_RECONNECT_ATTEMPTS:
            try:
                print(f"\n🔌 Connecting to Coinbase WebSocket...")

                async with websockets.connect(WS_URL, ping_interval=30) as ws:
                    print(f"✅ Connected! Subscribing to {product_ids}")
                    await ws.send(json.dumps(subscribe_message))

                    # Reset reconnect counter on successful connection
                    reconnect_count = 0

                    async for message in ws:
                        try:
                            data = json.loads(message)
                            await self.handle_message(data)
                        except json.JSONDecodeError:
                            pass
                        except Exception as e:
                            print(f"⚠️  Message error: {e}")

            except Exception as e:
                reconnect_count += 1
                print(f"\n❌ WebSocket error: {e}")
                print(f"🔄 Reconnecting in {RECONNECT_DELAY}s... (attempt {reconnect_count}/{MAX_RECONNECT_ATTEMPTS})")

                # Alert on repeated failures
                if reconnect_count == 5:
                    send_alert("⚠️ Scanner Connection Issues",
                              f"WebSocket reconnecting (attempt {reconnect_count})", "high")

                await asyncio.sleep(RECONNECT_DELAY)

        # If we get here, we've exhausted reconnection attempts
        send_alert("🚨 SCANNER DOWN",
                  f"Failed to reconnect after {MAX_RECONNECT_ATTEMPTS} attempts", "urgent")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🔍 AI BASKET SCANNER - WEBSOCKET EDITION              ║
    ║     Real-Time Price Monitoring                            ║
    ║     FET | RENDER | SUI                                    ║
    ║     ~100ms latency | Zero rate limits                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    monitor = WebSocketMonitor()

    while True:  # Immortal loop
        try:
            asyncio.run(monitor.connect())
        except KeyboardInterrupt:
            print("\n\n⚠️  Scanner stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            print(traceback.format_exc())

            try:
                requests.post(
                    f"https://ntfy.sh/{NTFY_TOPIC}",
                    data=f"Scanner crashed: {e}\nRestarting...",
                    headers={"Title": "⚠️ SCANNER CRASH", "Priority": "high"},
                    timeout=5
                )
            except:
                pass

            print("🔄 Restarting in 10s...")
            time.sleep(10)

if __name__ == "__main__":
    main()

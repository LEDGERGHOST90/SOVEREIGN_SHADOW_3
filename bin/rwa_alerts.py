#!/usr/bin/env python3
"""
RWA Price Alerts - Monitors LINK, ONDO, SYRUP for entry zones
Sends NTFY notifications when targets hit
"""

import json
import time
import requests
from datetime import datetime

NTFY_TOPIC = "sovereignshadow_dc4d2fa1"

# Alert Configuration
ALERTS = {
    'LINK': {
        'coingecko_id': 'chainlink',
        'buy_zone_low': 18.00,
        'buy_zone_high': 22.00,
        'stop_loss': 16.50,
        'triggered': False
    },
    'ONDO': {
        'coingecko_id': 'ondo-finance',
        'buy_zone_low': 0.31,  # -20% from ~0.39
        'buy_zone_high': 0.35,
        'stop_loss': 0.28,
        'triggered': False
    },
    'SYRUP': {
        'coingecko_id': 'maple',
        'buy_zone_low': 0.015,  # Research needed - placeholder
        'buy_zone_high': 0.025,
        'stop_loss': 0.012,
        'triggered': False
    },
    'INJ': {
        'coingecko_id': 'injective-protocol',
        'buy_zone_low': 3.50,   # Extreme value - back up the truck
        'buy_zone_high': 5.00,  # Current deep value zone
        'breakout_level': 7.00, # Rising - momentum starting
        'moon_level': 10.00,    # Breaking out - don't miss
        'stop_loss': 2.50,
        'triggered': False,
        'breakout_triggered': False
    },
    'QNT': {
        'coingecko_id': 'quant-network',
        'buy_zone_low': 65.00,  # Overledger bank-to-DeFi bridge
        'buy_zone_high': 75.00,
        'stop_loss': 58.00,
        'triggered': False
    }
}

def get_prices():
    """Fetch current prices from CoinGecko"""
    ids = ','.join([a['coingecko_id'] for a in ALERTS.values()])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Price fetch error: {e}")
        return {}

def send_alert(title, message, priority="high"):
    """Send NTFY notification"""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": "chart_with_upwards_trend,moneybag"
            },
            timeout=10
        )
        print(f"[ALERT SENT] {title}: {message}")
    except Exception as e:
        print(f"NTFY error: {e}")

def check_alerts(prices):
    """Check if any alert conditions are met"""
    timestamp = datetime.now().strftime("%H:%M")

    for symbol, config in ALERTS.items():
        cg_id = config['coingecko_id']
        if cg_id not in prices:
            continue

        price = prices[cg_id].get('usd', 0)
        if not price:
            continue

        # Check if in buy zone
        if config['buy_zone_low'] <= price <= config['buy_zone_high']:
            if not config['triggered']:
                send_alert(
                    f"RWA BUY ZONE: {symbol}",
                    f"{symbol} at ${price:.2f} - IN BUY ZONE (${config['buy_zone_low']}-${config['buy_zone_high']})",
                    priority="high"
                )
                config['triggered'] = True

        # Check if below buy zone (even better entry)
        elif price < config['buy_zone_low']:
            if not config['triggered']:
                send_alert(
                    f"RWA EXTREME VALUE: {symbol}",
                    f"{symbol} at ${price:.2f} - BELOW ${config['buy_zone_low']}! Back up the truck?",
                    priority="urgent"
                )
                config['triggered'] = True

        # Reset trigger if price moves back above zone
        elif price > config['buy_zone_high'] * 1.05:
            config['triggered'] = False

        # BREAKOUT ALERTS (for assets with breakout_level defined)
        if 'breakout_level' in config:
            breakout = config.get('breakout_level', 0)
            moon = config.get('moon_level', 0)
            breakout_triggered = config.get('breakout_triggered', False)

            # Breakout alert
            if price >= breakout and price < moon and not breakout_triggered:
                send_alert(
                    f"BREAKOUT: {symbol} MOVING",
                    f"{symbol} at ${price:.2f} - Above ${breakout}! Momentum starting.",
                    priority="high"
                )
                config['breakout_triggered'] = True

            # Moon alert
            elif price >= moon:
                send_alert(
                    f"MOON ALERT: {symbol}",
                    f"{symbol} at ${price:.2f} - Above ${moon}! Don't miss the move.",
                    priority="urgent"
                )

            # Reset breakout trigger if drops back
            elif price < breakout * 0.95:
                config['breakout_triggered'] = False

def main():
    print("=" * 50)
    print("RWA PRICE ALERTS - Started")
    print("=" * 50)
    print(f"Monitoring: {', '.join(ALERTS.keys())}")
    print("Alert zones:")
    for sym, cfg in ALERTS.items():
        print(f"  {sym}: ${cfg['buy_zone_low']}-${cfg['buy_zone_high']}")
    print("=" * 50)

    # Send startup notification
    send_alert(
        "RWA Alerts Active",
        f"Monitoring: LINK (<$22), ONDO (<$0.35), INJ (<$24), QNT (<$75)",
        priority="low"
    )

    while True:
        try:
            prices = get_prices()
            if prices:
                check_alerts(prices)

                # Log current prices every hour
                timestamp = datetime.now()
                if timestamp.minute == 0:
                    for sym, cfg in ALERTS.items():
                        cg_id = cfg['coingecko_id']
                        if cg_id in prices:
                            p = prices[cg_id].get('usd', 0)
                            zone_status = "IN ZONE" if cfg['buy_zone_low'] <= p <= cfg['buy_zone_high'] else "WATCHING"
                            print(f"[{timestamp.strftime('%H:%M')}] {sym}: ${p:.4f} ({zone_status})")

            time.sleep(300)  # Check every 5 minutes

        except KeyboardInterrupt:
            print("\nRWA Alerts stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()

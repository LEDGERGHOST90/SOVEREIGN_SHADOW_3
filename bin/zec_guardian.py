#!/usr/bin/env python3
"""
ZEC GUARDIAN - Auto Stop-Loss & Ladder Take-Profit
Watches price and auto-executes when targets hit.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Volumes/LegacySafe/SOVEREIGN_SHADOW_3')

from dotenv import load_dotenv
load_dotenv('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/.env')

import ccxt

# ============================================
# CONFIGURATION
# ============================================
SYMBOL = 'ZEC/USDC'
STOP_LOSS = 430.0
ENTRY_PRICE = 452.85
TOTAL_ZEC = 1.08202526

# LADDER OUT TARGETS
LADDER = [
    {"price": 480, "sell_pct": 0.33, "sold": False},
    {"price": 500, "sell_pct": 0.33, "sold": False},
    {"price": 520, "sell_pct": 0.34, "sold": False},
]

CHECK_INTERVAL = 15  # seconds

# ============================================
# SETUP
# ============================================
api_key = os.getenv("COINBASE_API_KEY")
api_secret = os.getenv("COINBASE_API_SECRET")

exchange = ccxt.coinbaseadvanced({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {'createMarketBuyOrderRequiresPrice': False}
})

def speak(text):
    """Aurora voice alert"""
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY", "sk_ff99af0872a9d9420c0fd47d0fd4bc31d395f38260ea5d8e")
        from elevenlabs import ElevenLabs
        import tempfile

        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="cgSgspJ2msm6clMCkdW9",
            model_id="eleven_multilingual_v2"
        )

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            for chunk in audio:
                f.write(chunk)
            temp_path = f.name

        subprocess.run(["afplay", temp_path], capture_output=True)
        os.unlink(temp_path)
    except:
        subprocess.run(["say", "-v", "Samantha", text], capture_output=True)

def send_notification(title, message):
    """Push notification via ntfy"""
    try:
        import requests
        requests.post(
            "https://ntfy.sh/sovereignshadow_dc4d2fa1",
            headers={"Title": title, "Priority": "urgent", "Tags": "warning"},
            data=message.encode('utf-8'),
            timeout=5
        )
    except:
        pass

def get_price():
    """Get current ZEC price"""
    ticker = exchange.fetch_ticker(SYMBOL)
    return ticker['last']

def get_balance():
    """Get ZEC balance"""
    balance = exchange.fetch_balance()
    return balance['total'].get('ZEC', 0)

def execute_sell(amount, reason):
    """Execute market sell"""
    if amount < 0.001:
        print(f"Amount too small: {amount}")
        return False

    try:
        order = exchange.create_order(
            symbol=SYMBOL,
            type='market',
            side='sell',
            amount=amount
        )

        print(f"\n{'='*60}")
        print(f"🚨 {reason} - SOLD!")
        print(f"{'='*60}")
        print(f"  Sold: {amount:.6f} ZEC")
        print(f"  Order ID: {order['id']}")

        # Log trade
        log = {
            "event": reason,
            "time": datetime.now().isoformat(),
            "quantity": amount,
            "order_id": order['id']
        }

        log_path = Path('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/memory/trade_log.json')
        logs = []
        if log_path.exists():
            logs = json.loads(log_path.read_text())
        logs.append(log)
        log_path.write_text(json.dumps(logs, indent=2))

        return True

    except Exception as e:
        print(f"SELL FAILED: {e}")
        return False

def main():
    global LADDER

    print("=" * 60)
    print("🛡️  ZEC GUARDIAN - ACTIVE")
    print("=" * 60)
    print(f"  Entry: ${ENTRY_PRICE}")
    print(f"  Stop Loss: ${STOP_LOSS}")
    print(f"  Ladder Targets:")
    for i, level in enumerate(LADDER, 1):
        print(f"    TP{i}: ${level['price']} ({level['sell_pct']*100:.0f}%)")
    print("=" * 60)

    speak("ZEC Guardian activated. Monitoring your position with ladder targets.")
    send_notification("ZEC Guardian", f"Active | SL: ${STOP_LOSS} | Ladder: $480/$500/$520")

    while True:
        try:
            price = get_price()
            zec_balance = get_balance()
            position_value = price * zec_balance
            pnl = (price - ENTRY_PRICE) * zec_balance
            pnl_pct = ((price / ENTRY_PRICE) - 1) * 100

            timestamp = datetime.now().strftime("%H:%M:%S")

            # Status indicator
            if price <= STOP_LOSS * 1.02:
                status = "⚠️  DANGER"
            elif price >= 480:
                status = "🎯 TARGET ZONE"
            else:
                status = "👁️  WATCHING"

            # Color PnL
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"

            print(f"[{timestamp}] ZEC: ${price:.2f} | PnL: {pnl_str} ({pnl_pct:+.1f}%) | {status}")

            # ========== STOP LOSS ==========
            if price <= STOP_LOSS:
                speak(f"STOP LOSS TRIGGERED! ZEC at {price:.0f} dollars. Selling everything!")
                send_notification("🚨 STOP LOSS", f"ZEC hit ${price:.2f} - SELLING ALL")

                if execute_sell(zec_balance, "STOP_LOSS"):
                    speak("Position closed. Stop loss executed. Trade complete.")
                    break

            # ========== LADDER TAKE PROFITS ==========
            for i, level in enumerate(LADDER):
                if not level['sold'] and price >= level['price']:
                    sell_amount = TOTAL_ZEC * level['sell_pct']
                    actual_sell = min(sell_amount, zec_balance)

                    speak(f"Take profit {i+1} hit! ZEC at {price:.0f} dollars. Selling {level['sell_pct']*100:.0f} percent.")
                    send_notification(f"🎯 TP{i+1} HIT", f"ZEC ${price:.2f} - Selling {actual_sell:.2f} ZEC")

                    if execute_sell(actual_sell, f"TAKE_PROFIT_{i+1}"):
                        LADDER[i]['sold'] = True
                        speak(f"Sold! Profit locked at {price:.0f}.")

                    time.sleep(2)

            # Check if all sold
            remaining = get_balance()
            if remaining < 0.001:
                speak("All ZEC sold. Guardian complete. Great trade!")
                print("\n✅ ALL TARGETS HIT - GUARDIAN COMPLETE")
                break

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nGuardian stopped by user.")
            speak("ZEC Guardian deactivated.")
            break

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()

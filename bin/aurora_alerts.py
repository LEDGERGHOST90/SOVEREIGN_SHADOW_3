#!/usr/bin/env python3
"""
AURORA ALERT SYSTEM - Voice + Push Notifications
ElevenLabs voice synthesis + ntfy.sh push notifications

Features:
- Voice alerts through speakers (ElevenLabs)
- Push notifications to phone (ntfy.sh)
- Signal alerts when high-confidence opportunities appear
- Market state alerts (Fear & Greed extremes)
- Portfolio alerts (price movements)

USAGE:
    python bin/aurora_alerts.py --test              # Test notifications
    python bin/aurora_alerts.py --watch             # Watch for signals
    python bin/aurora_alerts.py --alert "message"   # Send custom alert
"""

import os
import sys
import json
import time
import argparse
import requests
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
API_BASE = "http://localhost:8000"
NTFY_TOPIC = "ntfy.sh/sovereignshadow_dc4d2fa1"

# Load .env file from project root
def load_env():
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# ElevenLabs config (loaded from .env)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
AURORA_VOICE_ID = "cgSgspJ2msm6clMCkdW9"  # Jessica voice - Aurora's voice

# Notification sounds - in sounds/ directory
SOUNDS_DIR = PROJECT_ROOT / "sounds"
SOUNDS = {
    "alert": SOUNDS_DIR / "vegas_trap.mp3",
    "signal": SOUNDS_DIR / "shadow_alert.mp3",
    "high_priority": SOUNDS_DIR / "808_synth.mp3",
    "urgent": SOUNDS_DIR / "casino_alert.mp3",
    "buy": SOUNDS_DIR / "jackpot.mp3",
    "sell": SOUNDS_DIR / "radar_lock.mp3",
}


class AuroraAlerts:
    """Aurora voice + push notification system with Jessica voice"""

    def __init__(self):
        self.ntfy_url = f"https://{NTFY_TOPIC}"
        self.has_elevenlabs = bool(ELEVENLABS_API_KEY)
        self.last_alert_time = {}  # Prevent spam
        self.sounds_enabled = True

    def play_sound(self, sound_type: str = "alert"):
        """Play notification sound before voice alert"""
        if not self.sounds_enabled:
            return

        sound_file = SOUNDS.get(sound_type, SOUNDS["alert"])
        if sound_file.exists():
            try:
                subprocess.run(["afplay", str(sound_file)], check=True, timeout=5)
            except Exception as e:
                print(f"[SOUND ERROR] {e}")

    def send_push(self, title: str, message: str, priority: str = "default", tags: list = None):
        """
        Send push notification via ntfy.sh

        Priority: min, low, default, high, urgent
        Tags: emoji tags like ["money_mouth_face", "chart_with_upwards_trend"]
        """
        try:
            headers = {
                "Title": title,
                "Priority": priority
            }

            if tags:
                headers["Tags"] = ",".join(tags)

            resp = requests.post(
                self.ntfy_url,
                data=message,
                headers=headers,
                timeout=10
            )

            if resp.status_code == 200:
                print(f"[PUSH] {title}: {message}")
                return True
            else:
                print(f"[PUSH ERROR] {resp.status_code}: {resp.text}")
                return False

        except Exception as e:
            print(f"[PUSH ERROR] {e}")
            return False

    def speak(self, text: str, save_file: str = None):
        """
        Speak text using ElevenLabs SDK (Jessica voice)

        Falls back to macOS say command if no API key
        """
        # Rate limit
        now = time.time()
        if "speak" in self.last_alert_time:
            if now - self.last_alert_time["speak"] < 5:
                return  # Skip if spoken recently
        self.last_alert_time["speak"] = now

        if self.has_elevenlabs:
            try:
                from elevenlabs import ElevenLabs
                from elevenlabs.types import VoiceSettings

                client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

                # Generate with Jessica voice - Aurora's voice
                audio = client.text_to_speech.convert(
                    text=text,
                    voice_id=AURORA_VOICE_ID,
                    model_id="eleven_multilingual_v2",
                    voice_settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.8,
                        style=0.6,
                        use_speaker_boost=True
                    )
                )

                # Save and play audio
                audio_file = save_file or "/tmp/aurora_alert.mp3"
                with open(audio_file, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)

                # Play audio (macOS)
                subprocess.run(["afplay", audio_file], check=True)
                print(f"[AURORA/Jessica] {text}")
                return True

            except Exception as e:
                print(f"[ELEVENLABS ERROR] {e}")

        # Fallback to macOS say command
        try:
            subprocess.run(["say", "-v", "Samantha", text], check=True)
            print(f"[AURORA/Fallback] {text}")
            return True
        except:
            print(f"[VOICE] {text}")
            return False

    def alert_signal(self, symbol: str, action: str, confidence: int, reason: str = ""):
        """Alert for trading signal"""
        title = f"{action} Signal: {symbol}"
        message = f"{symbol} {action} ({confidence}%)"
        if reason:
            message += f"\n{reason}"

        # Play sound + voice alert for high confidence
        if confidence >= 80:
            # Play appropriate sound first
            if "BUY" in action:
                self.play_sound("buy")
            else:
                self.play_sound("sell")
            self.speak(f"Alert! High confidence {action.lower()} signal on {symbol}. {confidence} percent confidence.")

        # Push notification
        if "BUY" in action:
            tags = ["chart_with_upwards_trend", "money_mouth_face"]
            priority = "high" if confidence >= 80 else "default"
        else:
            tags = ["chart_with_downwards_trend", "warning"]
            priority = "high" if confidence >= 80 else "default"

        self.send_push(title, message, priority, tags)

    def alert_market_state(self, fear_greed: int, classification: str):
        """Alert for extreme market conditions"""
        # Only alert at extremes
        if fear_greed <= 20:
            title = "EXTREME FEAR"
            message = f"Fear & Greed at {fear_greed} - Historically best buy zone!"
            tags = ["green_circle", "money_bag"]
            priority = "urgent"
            self.play_sound("urgent")  # Casino alert for extreme
            self.speak(f"Market alert! Extreme fear detected. Fear and greed index at {fear_greed}. This is historically the best buying opportunity.")
        elif fear_greed <= 30:
            title = "FEAR ZONE"
            message = f"Fear & Greed at {fear_greed} - Good accumulation zone"
            tags = ["green_circle"]
            priority = "high"
            self.play_sound("high_priority")  # Vegas synth
            self.speak(f"Market update. Fear and greed index at {fear_greed}. Consider accumulating.")
        elif fear_greed >= 80:
            title = "EXTREME GREED"
            message = f"Fear & Greed at {fear_greed} - Take profits zone!"
            tags = ["red_circle", "warning"]
            priority = "urgent"
            self.play_sound("urgent")  # Casino alert for extreme
            self.speak(f"Warning! Extreme greed detected. Fear and greed at {fear_greed}. Consider taking profits.")
        elif fear_greed >= 70:
            title = "GREED ZONE"
            message = f"Fear & Greed at {fear_greed} - Be cautious"
            tags = ["yellow_circle"]
            priority = "high"
            self.play_sound("signal")  # Shadow alert
        else:
            return  # No alert for neutral

        self.send_push(title, message, priority, tags)

    def alert_portfolio(self, symbol: str, change: float, value: float):
        """Alert for significant portfolio movements"""
        if abs(change) >= 5:
            if change > 0:
                title = f"{symbol} +{change:.1f}%"
                message = f"Your {symbol} is up {change:.1f}% (${value:,.2f})"
                tags = ["rocket"]
                priority = "default"
            else:
                title = f"{symbol} {change:.1f}%"
                message = f"Your {symbol} is down {abs(change):.1f}% (${value:,.2f})"
                tags = ["warning"]
                priority = "high"

            self.send_push(title, message, priority, tags)

    def alert_custom(self, message: str, priority: str = "default"):
        """Send custom alert"""
        self.play_sound("alert")  # Vegas trap
        self.speak(message)
        self.send_push("Aurora Alert", message, priority, ["robot_face"])

    def test_alerts(self):
        """Test all alert types with Jessica voice + Vegas sounds"""
        print("Testing Aurora Alert System (Jessica Voice + Vegas Sounds)...")
        print()

        # Test sounds
        print("[1/6] Testing Vegas trap sound...")
        self.play_sound("alert")
        time.sleep(1)

        print("[2/6] Testing jackpot sound...")
        self.play_sound("buy")
        time.sleep(1)

        # Test push
        print("[3/6] Testing push notification...")
        self.send_push("Test Alert", "This is a test from Sovereign Shadow", "default", ["test_tube"])

        time.sleep(2)

        # Test voice
        print("[4/6] Testing Jessica voice...")
        self.speak("Testing Aurora voice system with Jessica. All systems nominal.")

        time.sleep(2)

        # Test signal alert
        print("[5/6] Testing signal alert...")
        self.alert_signal("BTC", "BUY", 85, "Fear & Greed at extreme low")

        time.sleep(2)

        # Test market alert
        print("[6/6] Testing market alert...")
        self.alert_market_state(23, "Extreme Fear")

        print()
        print("All tests complete! Aurora is ready with Jessica voice.")


def watch_for_signals():
    """Continuous monitoring for signals"""
    aurora = AuroraAlerts()
    last_fng = None

    print("Aurora Alert System watching for signals...")
    print("Press Ctrl+C to stop")
    print()

    while True:
        try:
            # Get smart signals
            resp = requests.get(f"{API_BASE}/api/swarm/smart-signals", timeout=15)
            data = resp.json()

            if "market_state" in data:
                fng = data["market_state"]["fear_greed"]
                fng_val = fng["value"]

                # Alert if Fear & Greed changed significantly
                if last_fng is None or abs(fng_val - last_fng) >= 5:
                    if fng_val <= 30 or fng_val >= 70:
                        aurora.alert_market_state(fng_val, fng["classification"])
                    last_fng = fng_val

                # Check for high-confidence signals
                for sig in data.get("signals", []):
                    if sig["confidence"] >= 80:
                        aurora.alert_signal(
                            sig["symbol"],
                            sig["action"],
                            sig["confidence"],
                            sig["reasons"][0] if sig["reasons"] else ""
                        )

            # Also check best signals
            resp = requests.get(f"{API_BASE}/api/swarm/best-signals", timeout=15)
            best = resp.json()

            for sig in best.get("buy_signals", [])[:3]:
                if sig["confidence"] >= 85:
                    aurora.alert_signal(sig["symbol"], "BUY", sig["confidence"])

            for sig in best.get("sell_signals", [])[:3]:
                if sig["confidence"] >= 90:
                    aurora.alert_signal(sig["symbol"], "SELL", sig["confidence"])

            # Check every 5 minutes
            time.sleep(300)

        except KeyboardInterrupt:
            print("\nAurora signing off...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description="Aurora Alert System")
    parser.add_argument("--test", action="store_true", help="Test notifications")
    parser.add_argument("--watch", action="store_true", help="Watch for signals")
    parser.add_argument("--alert", type=str, help="Send custom alert")
    parser.add_argument("--push", type=str, help="Send push notification only")
    parser.add_argument("--speak", type=str, help="Speak message only")

    args = parser.parse_args()
    aurora = AuroraAlerts()

    if args.test:
        aurora.test_alerts()
    elif args.watch:
        watch_for_signals()
    elif args.alert:
        aurora.alert_custom(args.alert)
    elif args.push:
        aurora.send_push("Sovereign Shadow", args.push, "default", ["robot_face"])
    elif args.speak:
        aurora.speak(args.speak)
    else:
        # Default: test
        aurora.test_alerts()


if __name__ == "__main__":
    main()

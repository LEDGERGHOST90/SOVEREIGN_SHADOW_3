#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Real-Time Asset Alert System
Monitors classified assets with tier-based alert thresholds
Integrates with Aurora voice + ntfy.sh push notifications

Usage:
    python scanners/realtime_alerts.py              # Run once
    python scanners/realtime_alerts.py --daemon     # Continuous monitoring
    python scanners/realtime_alerts.py --test       # Test alerts
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# ASSET CLASSIFICATION SYSTEM
# =============================================================================

ASSET_TIERS = {
    # TIER 1: Core Portfolio (highest trust, conservative alerts)
    "core": {
        "assets": ["BTC", "ETH", "SOL", "XRP"],
        "price_change_alert": 5.0,      # Alert on 5%+ move
        "volume_spike_alert": 200,       # Alert on 2x volume
        "check_interval": 60,            # Check every 60 seconds
        "voice": "elder",                # BTC Elder voice for core
        "priority": "high"
    },

    # TIER 2: Alt Majors (solid projects, moderate alerts)
    "alt_major": {
        "assets": ["RENDER", "SUI", "ADA", "APT", "DOGE", "AVAX", "LINK", "DOT"],
        "price_change_alert": 7.0,       # Alert on 7%+ move
        "volume_spike_alert": 250,       # Alert on 2.5x volume
        "check_interval": 120,           # Check every 2 minutes
        "voice": "architect",            # Architect voice for alts
        "priority": "default"
    },

    # TIER 3: Meme/Momentum (high volatility, aggressive alerts)
    "meme": {
        "assets": ["BONK", "TURBO", "PEPE", "WIF", "FLOKI", "SHIB", "MEME"],
        "price_change_alert": 10.0,      # Alert on 10%+ move (they're volatile)
        "volume_spike_alert": 300,       # Alert on 3x volume
        "check_interval": 60,            # Check every 60 seconds (fast movers)
        "voice": "siren",                # XRP Siren voice for memes (temptation)
        "priority": "high"
    },

    # TIER 4: Watchlist (tracking, info only)
    "watchlist": {
        "assets": ["INJ", "SEI", "TIA", "ONDO", "JUP", "PYTH", "WLD"],
        "price_change_alert": 8.0,
        "volume_spike_alert": 250,
        "check_interval": 300,           # Check every 5 minutes
        "voice": "ghost",                # SOL Ghost voice
        "priority": "low"
    }
}

# Flatten for quick lookup
ASSET_TO_TIER = {}
for tier_name, tier_data in ASSET_TIERS.items():
    for asset in tier_data["assets"]:
        ASSET_TO_TIER[asset] = tier_name

ALL_ASSETS = list(ASSET_TO_TIER.keys())

# =============================================================================
# COUNCIL VOICE MAPPING
# =============================================================================

COUNCIL_VOICES = {
    "elder": "nPczCjzI2devNBz1zQrb",      # Brian - wise BTC Elder
    "architect": "JBFqnCBsd6RMkjVDRZzb",  # George - system Architect
    "siren": "FGY2WhTYpPnrIDTdsKH5",      # Laura - tempting XRP Siren
    "ghost": "SAz9YHcvj6GT2YYXdXww",      # River - ethereal SOL Ghost
    "banker": "pqHfZKP75CvOlQylNhV4",     # Bill - AAVE Banker
    "hostage": "cgSgspJ2msm6clMCkdW9",    # Jessica/Aurora - wstETH Hostage
    "mirror": "EXAVITQu4vr4xnSDxMaL",     # Sarah - emotion Mirror
    "shade": "SOYHLrjzK2X1ezoPC6cr"       # Harry - SHADE guardian
}

# =============================================================================
# API CONFIGURATION
# =============================================================================

@dataclass
class PriceData:
    symbol: str
    price: float
    change_24h: float
    change_1h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime
    tier: str

def load_api_key() -> Optional[str]:
    """Load CryptoCompare API key from .env"""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("CRYPTOCOMPARE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("CRYPTOCOMPARE_API_KEY")

def load_elevenlabs_key() -> Optional[str]:
    """Load ElevenLabs API key from .env"""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("ELEVENLABS_API_KEY")

# =============================================================================
# PRICE FETCHING
# =============================================================================

def fetch_prices(symbols: list, api_key: str) -> dict:
    """Fetch current prices from CryptoCompare"""
    try:
        # Multi-symbol price fetch
        symbols_str = ",".join(symbols)
        url = f"https://min-api.cryptocompare.com/data/pricemultifull"
        params = {
            "fsyms": symbols_str,
            "tsyms": "USD",
            "api_key": api_key
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "RAW" not in data:
            print(f"API Error: {data.get('Message', 'Unknown error')}")
            return {}

        results = {}
        for symbol in symbols:
            if symbol in data["RAW"] and "USD" in data["RAW"][symbol]:
                raw = data["RAW"][symbol]["USD"]
                results[symbol] = PriceData(
                    symbol=symbol,
                    price=raw.get("PRICE", 0),
                    change_24h=raw.get("CHANGEPCT24HOUR", 0),
                    change_1h=raw.get("CHANGEPCTHOUR", 0),
                    volume_24h=raw.get("VOLUME24HOURTO", 0),
                    market_cap=raw.get("MKTCAP", 0),
                    timestamp=datetime.now(),
                    tier=ASSET_TO_TIER.get(symbol, "unknown")
                )

        return results

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}

# =============================================================================
# ALERT SYSTEM
# =============================================================================

class AlertManager:
    def __init__(self):
        self.last_prices = {}
        self.alert_cooldowns = {}  # Prevent spam
        self.cooldown_minutes = 15
        self.alerts_today = []
        self.state_file = PROJECT_ROOT / "memory" / "alert_state.json"
        self.load_state()

    def load_state(self):
        """Load previous state"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                self.last_prices = data.get("last_prices", {})
                self.alerts_today = data.get("alerts_today", [])
            except:
                pass

    def save_state(self):
        """Save current state"""
        self.state_file.parent.mkdir(exist_ok=True)
        data = {
            "last_prices": self.last_prices,
            "alerts_today": self.alerts_today[-50:],  # Keep last 50
            "updated": datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(data, indent=2))

    def check_alert_conditions(self, price_data: PriceData) -> list:
        """Check if price data triggers any alerts"""
        alerts = []
        tier_config = ASSET_TIERS.get(price_data.tier, ASSET_TIERS["watchlist"])

        # Check cooldown
        cooldown_key = f"{price_data.symbol}_alert"
        if cooldown_key in self.alert_cooldowns:
            if datetime.now() < self.alert_cooldowns[cooldown_key]:
                return []  # Still in cooldown

        # Price change alert (1h and 24h)
        threshold = tier_config["price_change_alert"]

        if abs(price_data.change_1h) >= threshold:
            direction = "PUMPING" if price_data.change_1h > 0 else "DUMPING"
            alerts.append({
                "type": "price_1h",
                "symbol": price_data.symbol,
                "tier": price_data.tier,
                "message": f"{price_data.symbol} {direction} {abs(price_data.change_1h):.1f}% in 1 hour!",
                "change": price_data.change_1h,
                "price": price_data.price,
                "priority": "urgent" if abs(price_data.change_1h) >= threshold * 1.5 else tier_config["priority"]
            })

        if abs(price_data.change_24h) >= threshold * 1.5:  # Higher bar for 24h
            direction = "UP" if price_data.change_24h > 0 else "DOWN"
            alerts.append({
                "type": "price_24h",
                "symbol": price_data.symbol,
                "tier": price_data.tier,
                "message": f"{price_data.symbol} {direction} {abs(price_data.change_24h):.1f}% in 24 hours",
                "change": price_data.change_24h,
                "price": price_data.price,
                "priority": tier_config["priority"]
            })

        # Set cooldown if alerts triggered
        if alerts:
            self.alert_cooldowns[cooldown_key] = datetime.now() + timedelta(minutes=self.cooldown_minutes)

        return alerts

    def process_alerts(self, alerts: list, voice_enabled: bool = True):
        """Process and send alerts"""
        for alert in alerts:
            # Log alert
            self.alerts_today.append({
                **alert,
                "timestamp": datetime.now().isoformat()
            })

            # Console output
            emoji = "🚀" if alert["change"] > 0 else "📉"
            tier_emoji = {"core": "💎", "alt_major": "🔷", "meme": "🎰", "watchlist": "👀"}.get(alert["tier"], "📊")
            print(f"\n{emoji} {tier_emoji} ALERT: {alert['message']}")
            print(f"   Price: ${alert['price']:,.4f} | Tier: {alert['tier'].upper()}")

            # Voice alert (Aurora)
            if voice_enabled:
                self.speak_alert(alert)

            # Push notification
            self.push_alert(alert)

        self.save_state()

    def speak_alert(self, alert: dict):
        """Speak alert using appropriate council voice"""
        try:
            tier_config = ASSET_TIERS.get(alert["tier"], ASSET_TIERS["watchlist"])
            voice_name = tier_config["voice"]
            voice_id = COUNCIL_VOICES.get(voice_name, COUNCIL_VOICES["hostage"])

            # Build speech text
            direction = "pumping" if alert["change"] > 0 else "dumping"
            text = f"{alert['symbol']} alert. {direction} {abs(alert['change']):.0f} percent. "

            if alert["tier"] == "core":
                text += "Core asset movement. Monitor closely."
            elif alert["tier"] == "meme":
                text += "Meme momentum detected. High risk."
            else:
                text += f"Current price {alert['price']:.2f} dollars."

            # Use ElevenLabs
            api_key = load_elevenlabs_key()
            if api_key:
                from elevenlabs import ElevenLabs
                from elevenlabs.types import VoiceSettings
                import tempfile

                client = ElevenLabs(api_key=api_key)
                audio = client.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    voice_settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.8,
                        style=0.6,
                        use_speaker_boost=True
                    )
                )

                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    for chunk in audio:
                        f.write(chunk)
                    temp_path = f.name

                # Play Vegas sound first, then voice
                vegas_sound = PROJECT_ROOT / "sounds" / "vegas_trap.mp3"
                if vegas_sound.exists():
                    subprocess.run(["afplay", str(vegas_sound)], capture_output=True)

                subprocess.run(["afplay", temp_path], capture_output=True)
                os.unlink(temp_path)
            else:
                # Fallback to macOS say
                subprocess.run(["say", "-v", "Alex", text], capture_output=True)

        except Exception as e:
            print(f"Voice alert error: {e}")

    def push_alert(self, alert: dict):
        """Send push notification via ntfy.sh"""
        try:
            topic = "sovereignshadow_dc4d2fa1"
            direction = "UP" if alert["change"] > 0 else "DOWN"
            tier_tag = {"core": "gem", "alt_major": "chart", "meme": "slot_machine", "watchlist": "eyes"}.get(alert["tier"], "bell")

            priority = "urgent" if alert.get("priority") == "urgent" else "high" if alert.get("priority") == "high" else "default"

            requests.post(
                f"https://ntfy.sh/{topic}",
                headers={
                    "Title": f"{alert['symbol']} {direction} - {alert['tier'].upper()}",
                    "Priority": priority,
                    "Tags": f"{tier_tag},moneybag"
                },
                data=alert["message"].encode('utf-8'),
                timeout=5
            )
        except Exception as e:
            print(f"Push notification error: {e}")

# =============================================================================
# MAIN SCANNER
# =============================================================================

def run_scan(voice_enabled: bool = True):
    """Run a single price scan"""
    api_key = load_api_key()
    if not api_key:
        print("ERROR: CRYPTOCOMPARE_API_KEY not found in .env")
        return

    print(f"\n{'='*60}")
    print(f"SOVEREIGN SHADOW - Real-Time Asset Scanner")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Fetch all prices
    prices = fetch_prices(ALL_ASSETS, api_key)

    if not prices:
        print("Failed to fetch prices")
        return

    # Initialize alert manager
    alert_mgr = AlertManager()

    # Check each asset
    all_alerts = []

    print(f"\n📊 PRICE OVERVIEW BY TIER:")
    for tier_name, tier_config in ASSET_TIERS.items():
        print(f"\n  [{tier_name.upper()}]")
        for symbol in tier_config["assets"]:
            if symbol in prices:
                p = prices[symbol]
                change_color = "+" if p.change_1h >= 0 else ""
                print(f"    {symbol:8} ${p.price:>12,.4f}  {change_color}{p.change_1h:>6.2f}% (1h)  {change_color}{p.change_24h:>6.2f}% (24h)")

                # Check alerts
                alerts = alert_mgr.check_alert_conditions(p)
                all_alerts.extend(alerts)

    # Process any alerts
    if all_alerts:
        print(f"\n🚨 {len(all_alerts)} ALERT(S) TRIGGERED:")
        alert_mgr.process_alerts(all_alerts, voice_enabled)
    else:
        print(f"\n✅ No alerts triggered. Markets stable.")

    print(f"\n{'='*60}")

def run_daemon(interval: int = 60):
    """Run continuous monitoring"""
    print("Starting daemon mode... Press Ctrl+C to stop")

    while True:
        try:
            run_scan(voice_enabled=True)
            print(f"\nNext scan in {interval} seconds...")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nDaemon stopped.")
            break
        except Exception as e:
            print(f"Scan error: {e}")
            time.sleep(30)

def test_alerts():
    """Test the alert system"""
    print("Testing alert system...")

    alert_mgr = AlertManager()

    # Create fake alert
    test_alert = {
        "type": "price_1h",
        "symbol": "BTC",
        "tier": "core",
        "message": "BTC PUMPING 6.5% in 1 hour! Test alert.",
        "change": 6.5,
        "price": 95000.00,
        "priority": "high"
    }

    alert_mgr.process_alerts([test_alert], voice_enabled=True)
    print("\nTest complete!")

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sovereign Shadow Real-Time Alerts")
    parser.add_argument("--daemon", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Scan interval in seconds")
    parser.add_argument("--test", action="store_true", help="Test alert system")
    parser.add_argument("--silent", action="store_true", help="Disable voice alerts")

    args = parser.parse_args()

    if args.test:
        test_alerts()
    elif args.daemon:
        run_daemon(args.interval)
    else:
        run_scan(voice_enabled=not args.silent)

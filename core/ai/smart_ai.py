#!/usr/bin/env python3
"""
SMART AI - Self-Healing Multi-Provider AI Router
Never worry about API keys again. Automatically falls back to working providers.

Usage:
    from core.ai.smart_ai import ai
    response = ai.ask("Analyze BTC")

Features:
- Tests all providers on startup
- Caches working provider
- Auto-fallback if current provider fails
- Health check endpoint
- Alerts via NTFY when provider goes down
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("shadow.smart_ai")

# Config
REPLIT_URL = os.getenv(
    "REPLIT_API_URL",
    "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
)
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "sovereignshadow_dc4d2fa1")
CACHE_FILE = Path("/Volumes/LegacySafe/SS_III/data/ai_provider_cache.json")

# Provider priority (in order of preference)
PROVIDERS = [
    {"name": "anthropic", "model": "claude-haiku-4-5", "label": "Claude"},
    {"name": "openai", "model": "gpt-4o-mini", "label": "GPT-4o"},
    {"name": "gemini", "model": "gemini-2.5-flash", "label": "Gemini"},
]


class SmartAI:
    """
    Self-healing AI router that never fails (as long as one provider works).
    """

    def __init__(self, auto_test: bool = True):
        self.base_url = REPLIT_URL
        self.working_provider = None
        self.provider_status = {}
        self.last_health_check = None

        # Load cached provider
        self._load_cache()

        # Test providers on startup
        if auto_test and not self.working_provider:
            self.health_check()

    def _load_cache(self):
        """Load cached working provider."""
        try:
            if CACHE_FILE.exists():
                data = json.loads(CACHE_FILE.read_text())
                cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))

                # Cache valid for 1 hour
                if datetime.now() - cached_at < timedelta(hours=1):
                    self.working_provider = data.get("working_provider")
                    self.provider_status = data.get("status", {})
                    logger.info(f"Loaded cached provider: {self.working_provider}")
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")

    def _save_cache(self):
        """Save working provider to cache."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "working_provider": self.working_provider,
                "status": self.provider_status,
                "cached_at": datetime.now().isoformat()
            }
            CACHE_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    def _test_provider(self, provider: Dict) -> bool:
        """Test if a provider works."""
        try:
            # Set provider
            requests.post(
                f"{self.base_url}/api/terminal/set-provider",
                json={"provider": provider["name"], "model": provider["model"]},
                timeout=10
            )

            # Test with simple query
            resp = requests.post(
                f"{self.base_url}/api/terminal/chat",
                json={"message": "Say OK"},
                timeout=30
            )
            result = resp.json()
            return result.get("success", False)

        except Exception as e:
            logger.warning(f"Provider test failed ({provider['name']}): {e}")
            return False

    def health_check(self, force: bool = False) -> Dict[str, Any]:
        """
        Test all providers and find working ones.
        Results are cached for 1 hour unless force=True.
        """
        if not force and self.last_health_check:
            if datetime.now() - self.last_health_check < timedelta(hours=1):
                return {"status": "cached", "provider": self.working_provider}

        logger.info("Running AI provider health check...")
        results = {}
        working = None

        for provider in PROVIDERS:
            name = provider["name"]
            is_working = self._test_provider(provider)
            results[name] = {
                "working": is_working,
                "model": provider["model"],
                "tested_at": datetime.now().isoformat()
            }

            if is_working and not working:
                working = provider
                logger.info(f"Found working provider: {name}")

        self.provider_status = results
        self.last_health_check = datetime.now()

        if working:
            self.working_provider = working
            self._save_cache()

            # Set as active provider
            requests.post(
                f"{self.base_url}/api/terminal/set-provider",
                json={"provider": working["name"], "model": working["model"]},
                timeout=10
            )
        else:
            # ALL PROVIDERS DOWN - Alert!
            self._send_alert(
                "ALL AI PROVIDERS DOWN",
                "OpenAI, Anthropic, and Gemini all failing. Check Replit.",
                priority="urgent"
            )

        return {
            "status": "checked",
            "provider": self.working_provider,
            "results": results
        }

    def _send_alert(self, title: str, message: str, priority: str = "high"):
        """Send NTFY alert."""
        try:
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=message.encode('utf-8'),
                headers={"Title": title, "Priority": priority},
                timeout=10
            )
        except Exception as e:
            logger.error(f"Alert failed: {e}")

    def ask(self, message: str, system_prompt: str = None, retries: int = 2) -> str:
        """
        Ask the AI. Automatically uses working provider with fallback.
        """
        # Ensure we have a working provider
        if not self.working_provider:
            self.health_check()

        if not self.working_provider:
            return "Error: All AI providers are down. Check API keys."

        # Try current provider
        for attempt in range(retries + 1):
            try:
                payload = {"message": message}
                if system_prompt:
                    payload["system_prompt"] = system_prompt

                resp = requests.post(
                    f"{self.base_url}/api/terminal/chat",
                    json=payload,
                    timeout=60
                )
                result = resp.json()

                if result.get("success"):
                    return result.get("response", "")

                # Provider failed - try fallback
                error = result.get("error", "")
                if "API key" in str(error) or "expired" in str(error).lower():
                    logger.warning(f"Provider {self.working_provider['name']} failed, finding fallback...")
                    self.working_provider = None
                    self.health_check(force=True)

                    if self.working_provider:
                        continue  # Retry with new provider
                    else:
                        return f"Error: All providers down - {error}"

            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    continue

        return "Error: Request failed after retries"

    def analyze_market(self, asset: str) -> str:
        """Quick market analysis."""
        return self.ask(
            f"Analyze {asset} - give sentiment, key levels, recommendation. Be concise.",
            system_prompt="You are an elite crypto analyst. Be direct and actionable."
        )

    def rwa_insight(self, topic: str) -> str:
        """RWA-specific analysis."""
        return self.ask(
            f"RWA Analysis: {topic}",
            system_prompt="You are an RWA tokenization expert. Focus on LINK, INJ, QNT, ONDO, PLUME."
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current AI status."""
        return {
            "working_provider": self.working_provider["name"] if self.working_provider else None,
            "model": self.working_provider["model"] if self.working_provider else None,
            "all_providers": self.provider_status,
            "last_check": self.last_health_check.isoformat() if self.last_health_check else None
        }


# Global instance
ai = SmartAI(auto_test=False)


# CLI test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("SMART AI - Self-Healing Provider Test")
    print("=" * 60)

    # Force health check
    status = ai.health_check(force=True)
    print(f"\nHealth Check Results:")
    for name, info in status.get("results", {}).items():
        emoji = "✅" if info["working"] else "❌"
        print(f"  {emoji} {name}: {info['model']}")

    if ai.working_provider:
        print(f"\nUsing: {ai.working_provider['label']} ({ai.working_provider['model']})")

        # Test query
        response = ai.ask("What is 2+2? Answer with just the number.")
        print(f"Test response: {response}")
    else:
        print("\n❌ ALL PROVIDERS DOWN!")

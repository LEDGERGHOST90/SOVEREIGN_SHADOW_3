#!/usr/bin/env python3
"""
Replit AI Proxy - Routes AI calls through Replit's managed API keys
Works with OpenAI and Anthropic (Gemini key is expired on Replit too)

Usage:
    from core.ai.replit_proxy import ReplitAI
    ai = ReplitAI()
    response = ai.ask("Analyze BTC market conditions")
"""

import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("shadow.replit_proxy")

REPLIT_API_URL = os.getenv(
    "REPLIT_API_URL",
    "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
)


class ReplitAI:
    """
    Proxy AI calls through Replit's managed API keys.
    Supports: OpenAI (gpt-4o-mini), Anthropic (claude-haiku-4-5)
    """

    def __init__(self, provider: str = "anthropic", model: str = None):
        """
        Initialize Replit AI proxy.

        Args:
            provider: "openai" or "anthropic" (default: anthropic)
            model: Specific model to use, or None for provider default
        """
        self.base_url = REPLIT_API_URL
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self._set_provider()

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-haiku-4-5",
            "gemini": "gemini-2.5-flash"  # Currently broken
        }
        return defaults.get(provider, "gpt-4o-mini")

    def _set_provider(self) -> bool:
        """Set the AI provider on Replit."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/terminal/set-provider",
                json={"provider": self.provider, "model": self.model},
                timeout=10
            )
            result = resp.json()
            if result.get("success"):
                logger.info(f"Replit AI set to {self.provider}/{self.model}")
                return True
            else:
                logger.error(f"Failed to set provider: {result}")
                return False
        except Exception as e:
            logger.error(f"Provider set failed: {e}")
            return False

    def ask(self, message: str, system_prompt: str = None) -> str:
        """
        Ask the AI a question.

        Args:
            message: The question or prompt
            system_prompt: Optional system context

        Returns:
            AI response text, or error string
        """
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
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"AI request failed: {error}")
                return f"Error: {error}"

        except Exception as e:
            logger.error(f"AI request exception: {e}")
            return f"Error: {str(e)}"

    def analyze_market(self, asset: str, context: Dict[str, Any] = None) -> str:
        """
        Analyze market conditions for an asset.

        Args:
            asset: Asset symbol (e.g., "BTC", "LINK")
            context: Optional market data context

        Returns:
            Market analysis text
        """
        system_prompt = """You are an elite crypto market analyst.
Analyze the asset and provide:
1. Current sentiment (bullish/bearish/neutral)
2. Key technical levels
3. Risk factors
4. Actionable recommendation

Be concise and specific."""

        message = f"Analyze {asset} market conditions."
        if context:
            message += f"\n\nContext: {context}"

        return self.ask(message, system_prompt)

    def get_rwa_insight(self, topic: str) -> str:
        """
        Get RWA (Real World Asset) specific insights.

        Args:
            topic: RWA topic to analyze

        Returns:
            RWA analysis text
        """
        system_prompt = """You are a Real World Asset (RWA) tokenization expert.
Focus on:
- Infrastructure protocols (LINK, QNT)
- RWA-native protocols (ONDO, MAPLE, PLUME)
- Institutional adoption signals
- Regulatory developments

Provide institutional-grade analysis."""

        return self.ask(f"Analyze RWA topic: {topic}", system_prompt)


# Convenience function for quick access
def ask_ai(message: str, provider: str = "anthropic") -> str:
    """Quick AI query using Replit proxy."""
    ai = ReplitAI(provider=provider)
    return ai.ask(message)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing Replit AI Proxy...")
    ai = ReplitAI(provider="anthropic")

    response = ai.ask("What is the capital of France? Answer in one word.")
    print(f"Response: {response}")

    print("\nTesting RWA insight...")
    insight = ai.get_rwa_insight("Chainlink Swift integration progress")
    print(f"RWA Insight: {insight[:300]}...")

"""Sovereign Shadow II - Exchange connector framework.

Design goals:
- Default to SAFE/FAKE mode.
- Hard safety gates before any live order placement.
- Reliable API calls with exponential backoff.

This module is intentionally independent from the legacy `exchanges/` package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, TypeVar
import os
import time


T = TypeVar("T")


@dataclass(frozen=True)
class SafetyConfig:
    env: str
    allow_live_exchange: bool

    @staticmethod
    def from_env() -> "SafetyConfig":
        env = os.getenv("ENV", "development")
        allow_live_exchange = os.getenv("ALLOW_LIVE_EXCHANGE", "0") == "1"
        return SafetyConfig(env=env, allow_live_exchange=allow_live_exchange)

    def assert_live_trading_allowed(self) -> None:
        # Mirrors the guardrails in the prompt.
        assert self.env == "production", "Not in production mode"
        assert self.allow_live_exchange is True, "Live trading not authorized"


class ConnectorError(RuntimeError):
    pass


class BaseConnector:
    """Minimal connector interface used by the orchestrator."""

    name: str = "base"

    def __init__(self, *, safety: Optional[SafetyConfig] = None):
        self.safety = safety or SafetyConfig.from_env()

    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError

    def fetch_ohlcv(self, symbol: str, timeframe: str = "15m", limit: int = 200) -> Any:
        raise NotImplementedError

    def fetch_balance(self) -> Dict[str, Any]:
        raise NotImplementedError

    def create_order(self, **kwargs: Any) -> Dict[str, Any]:
        """Place an order.

        MUST call `self.safety.assert_live_trading_allowed()` unless this is a sandbox.
        """
        raise NotImplementedError

    @staticmethod
    def _retry(
        fn: Callable[[], T],
        *,
        max_attempts: int = 5,
        base_delay_s: float = 0.5,
        max_delay_s: float = 8.0,
        retry_on: tuple[type[BaseException], ...] = (Exception,),
    ) -> T:
        """Exponential backoff wrapper for flaky API calls."""
        attempt = 0
        delay = base_delay_s
        while True:
            attempt += 1
            try:
                return fn()
            except retry_on as e:
                if attempt >= max_attempts:
                    raise ConnectorError(f"API call failed after {attempt} attempts: {e}") from e
                time.sleep(delay)
                delay = min(delay * 2, max_delay_s)

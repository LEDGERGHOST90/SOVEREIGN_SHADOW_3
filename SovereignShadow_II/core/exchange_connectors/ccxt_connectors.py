"""CCXT-based connectors (Coinbase/OKX/Kraken/BinanceUS).

Note: Coinbase sandbox mode is not publicly supported by CCXT for spot Coinbase.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import os

import ccxt

from .base_connector import BaseConnector, SafetyConfig


class CCXTConnector(BaseConnector):
    exchange_id: str

    def __init__(
        self,
        *,
        exchange_id: str,
        use_sandbox: bool = False,
        safety: Optional[SafetyConfig] = None,
        ccxt_options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(safety=safety)
        self.exchange_id = exchange_id
        self.use_sandbox = use_sandbox
        self.ccxt_options = ccxt_options or {}
        self.exchange = self._init_exchange()

    def _init_exchange(self):
        # Convention: <EXCHANGE>_API_KEY / _API_SECRET / optional _PASSPHRASE
        prefix = self.exchange_id.upper().replace("-", "_")
        api_key = os.getenv(f"{prefix}_API_KEY")
        api_secret = os.getenv(f"{prefix}_API_SECRET")
        passphrase = os.getenv(f"{prefix}_PASSPHRASE") or os.getenv(f"{prefix}_PASSWORD")

        if not api_key or not api_secret:
            raise ValueError(f"Missing {prefix} credentials")

        klass = getattr(ccxt, self.exchange_id)

        params: Dict[str, Any] = {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        }
        if passphrase:
            # CCXT uses `password` for passphrase on several exchanges.
            params["password"] = passphrase

        params.update(self.ccxt_options)
        exchange = klass(params)

        if self.use_sandbox:
            # Not all exchanges support sandbox.
            try:
                exchange.set_sandbox_mode(True)
            except Exception:
                pass

        return exchange

    @property
    def name(self) -> str:  # type: ignore[override]
        return self.exchange_id

    def test_connection(self) -> Dict[str, Any]:
        try:
            balance = self._retry(lambda: self.exchange.fetch_balance())
            total = balance.get("total") or {}
            return {"status": "SUCCESS", "balance": total}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def fetch_balance(self) -> Dict[str, Any]:
        return self._retry(lambda: self.exchange.fetch_balance())

    def fetch_ohlcv(self, symbol: str, timeframe: str = "15m", limit: int = 200) -> Any:
        return self._retry(lambda: self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit))

    def create_order(self, **kwargs: Any) -> Dict[str, Any]:
        # Hard safety gate: unless we're explicitly in sandbox, do not allow live trading.
        if not self.use_sandbox:
            self.safety.assert_live_trading_allowed()

        # Expected kwargs: symbol, type, side, amount, price (optional)
        return self._retry(lambda: self.exchange.create_order(**kwargs))


class CoinbaseAdvancedConnector(CCXTConnector):
    def __init__(self, use_sandbox: bool = True, safety: Optional[SafetyConfig] = None):
        super().__init__(
            exchange_id="coinbase",
            use_sandbox=use_sandbox,
            safety=safety,
            ccxt_options={
                "options": {
                    "fetchBalance": {"type": "spot"},
                    "defaultType": "spot",
                }
            },
        )


class OKXConnector(CCXTConnector):
    def __init__(self, use_sandbox: bool = True, safety: Optional[SafetyConfig] = None):
        super().__init__(exchange_id="okx", use_sandbox=use_sandbox, safety=safety)


class KrakenConnector(CCXTConnector):
    def __init__(self, use_sandbox: bool = False, safety: Optional[SafetyConfig] = None):
        super().__init__(exchange_id="kraken", use_sandbox=use_sandbox, safety=safety)


class BinanceUSConnector(CCXTConnector):
    def __init__(self, use_sandbox: bool = True, safety: Optional[SafetyConfig] = None):
        super().__init__(exchange_id="binanceus", use_sandbox=use_sandbox, safety=safety)

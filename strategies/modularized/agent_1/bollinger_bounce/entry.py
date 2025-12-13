from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """BollingerBounce entry skill.

    Logic:
    - Close touches or breaks below lower Bollinger band (20, 2)
    - RSI(14) < 40
    """

    name = "bollinger_bounce_entry"
    indicators = ["bbands_20_2", "rsi_14"]
    warmup = 120

    def __init__(self, *, period: int = 20, std_mult: float = 2.0):
        self.period = int(period)
        self.std_mult = float(std_mult)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < self.period + 10:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        mid = close.rolling(self.period).mean()
        sd = close.rolling(self.period).std(ddof=0)
        lower = mid - (self.std_mult * sd)

        rsi = float(self._rsi(close, 14).iloc[-1])
        price = float(close.iloc[-1])

        if price <= float(lower.iloc[-1]) and rsi < 40:
            band_dist = (float(lower.iloc[-1]) - price) / max(price, 1e-9)
            confidence = min(100.0, band_dist * 10000.0 + (40 - rsi) * 2.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": price,
                "reasoning": "Close below lower Bollinger band with weak RSI (bounce setup)",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

    @staticmethod
    def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = (-delta).clip(lower=0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-9)
        return 100.0 - (100.0 / (1.0 + rs))

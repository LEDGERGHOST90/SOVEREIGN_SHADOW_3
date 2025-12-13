from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """RSIReversion entry skill.

    Logic:
    - RSI(14) < 30
    - Price not in steep downtrend: EMA(20) >= EMA(50) OR regime will filter externally
    """

    name = "rsi_reversion_entry"
    indicators = ["rsi_14", "ema_20", "ema_50"]
    warmup = 120

    def __init__(self, *, rsi_threshold: float = 30.0):
        self.rsi_threshold = float(rsi_threshold)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 60:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        rsi = float(self._rsi(close, 14).iloc[-1])

        price = float(close.iloc[-1])
        trend_ok = float(ema20.iloc[-1]) >= float(ema50.iloc[-1])

        if rsi < self.rsi_threshold and trend_ok:
            confidence = min(100.0, (self.rsi_threshold - rsi) * 3.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": price,
                "reasoning": f"RSI oversold ({rsi:.1f}) with non-bearish EMA structure",
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

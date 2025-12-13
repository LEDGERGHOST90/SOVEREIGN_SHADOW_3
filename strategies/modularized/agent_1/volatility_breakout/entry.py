from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """VolatilityBreakout entry skill.

    Logic:
    - Break above previous close + k*ATR
    """

    name = "volatility_breakout_entry"
    indicators = ["atr_14"]
    warmup = 120

    def __init__(self, *, atr_k: float = 1.0):
        self.atr_k = float(atr_k)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        atr = self._atr(df)

        trigger = float(close.iloc[-2]) + (self.atr_k * atr)
        current = float(close.iloc[-1])

        if current > trigger:
            confidence = min(100.0, ((current - trigger) / max(atr, 1e-9)) * 25.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": current,
                "reasoning": "Close broke above ATR-based breakout trigger",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

    @staticmethod
    def _atr(df: pd.DataFrame, period: int = 14) -> float:
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)
        tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        return float(atr) if pd.notna(atr) else float(tr.iloc[-1])

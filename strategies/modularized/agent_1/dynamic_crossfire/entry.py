from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """DynamicCrossfire entry skill.

    Logic:
    - EMA(9) crosses above EMA(21)
    - Volatility filter: ATR(14) / close >= 0.001
    """

    name = "dynamic_crossfire_entry"
    indicators = ["ema_9", "ema_21", "atr_14"]
    warmup = 100

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()

        atr = self._atr(df)
        vol_ratio = float(atr / max(close.iloc[-1], 1e-9))

        crossed_up = float(ema9.iloc[-2]) <= float(ema21.iloc[-2]) and float(ema9.iloc[-1]) > float(ema21.iloc[-1])

        if crossed_up and vol_ratio >= 0.001:
            confidence = min(100.0, (vol_ratio * 10000.0))
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": float(close.iloc[-1]),
                "reasoning": "EMA9 crossed above EMA21 with sufficient ATR volatility",
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

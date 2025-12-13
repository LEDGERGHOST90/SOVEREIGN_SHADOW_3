from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """TrendFollowEMA entry skill.

    Logic:
    - EMA(20) > EMA(50) (uptrend)
    - Price pulls back near EMA(20) and closes back above it
    """

    name = "trend_follow_ema_entry"
    indicators = ["ema_20", "ema_50"]
    warmup = 150

    def __init__(self, *, pullback_pct: float = 0.002):
        self.pullback_pct = float(pullback_pct)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 60:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        uptrend = float(ema20.iloc[-1]) > float(ema50.iloc[-1])
        price = float(close.iloc[-1])
        ema20_now = float(ema20.iloc[-1])

        near_ema = abs(price - ema20_now) / max(price, 1e-9) <= self.pullback_pct
        closed_above = price > ema20_now

        if uptrend and near_ema and closed_above:
            confidence = min(100.0, (float(ema20.iloc[-1]) - float(ema50.iloc[-1])) / max(price, 1e-9) * 20_000.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": price,
                "reasoning": "Uptrend (EMA20>EMA50) with pullback to EMA20 and reclaim",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

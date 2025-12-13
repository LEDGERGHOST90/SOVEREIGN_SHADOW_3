from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """ElderReversion entry skill.

    Logic (simple Elder Ray approximation):
    - Bull power < 0 (high - EMA13 < 0)
    - Price above EMA13
    """

    name = "elder_reversion_entry"
    indicators = ["elder_ray", "ema_13"]
    warmup = 100

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        high = df["high"].astype(float)

        ema_13 = close.ewm(span=13, adjust=False).mean()
        bull_power = high - ema_13

        current_bull = float(bull_power.iloc[-1])
        current_price = float(close.iloc[-1])
        current_ema = float(ema_13.iloc[-1])

        if current_bull < 0 and current_price > current_ema:
            confidence = min(abs(current_bull / max(current_price, 1e-9)) * 1000, 100)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": current_price,
                "reasoning": f"Elder Bull Power negative ({current_bull:.4f}), price above EMA-13",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

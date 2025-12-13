from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """BandedStochastic entry skill.

    Logic:
    - %K crosses above %D while both are below 20 (oversold)
    """

    name = "banded_stochastic_entry"
    indicators = ["stoch_k", "stoch_d"]
    warmup = 100

    def __init__(self, *, k_period: int = 14, d_period: int = 3, band: float = 20.0):
        self.k_period = int(k_period)
        self.d_period = int(d_period)
        self.band = float(band)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < self.k_period + self.d_period + 5:
            return {"signal": "NEUTRAL", "confidence": 0}

        k, d = self._stoch(df, self.k_period, self.d_period)

        crossed_up = float(k.iloc[-2]) <= float(d.iloc[-2]) and float(k.iloc[-1]) > float(d.iloc[-1])
        oversold = float(k.iloc[-1]) < self.band and float(d.iloc[-1]) < self.band

        price = float(df["close"].astype(float).iloc[-1])

        if crossed_up and oversold:
            confidence = min(100.0, (self.band - float(k.iloc[-1])) * 2.5)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": price,
                "reasoning": "Stochastic %K/%D bullish cross in oversold band",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

    @staticmethod
    def _stoch(df: pd.DataFrame, k_period: int, d_period: int):
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)

        lowest_low = low.rolling(k_period).min()
        highest_high = high.rolling(k_period).max()
        denom = (highest_high - lowest_low).replace(0, 1e-9)
        k = 100.0 * (close - lowest_low) / denom
        d = k.rolling(d_period).mean()
        return k, d

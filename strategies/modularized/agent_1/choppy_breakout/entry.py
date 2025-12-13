from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """ChoppyBreakout entry skill.

    Logic (range breakout in choppy regimes):
    - Compute rolling high over last N
    - Buy if close breaks above prior rolling high AND volume is above its rolling mean
    """

    name = "choppy_breakout_entry"
    indicators = ["rolling_high", "volume_mean"]
    warmup = 120

    def __init__(self, *, lookback: int = 20, vol_lookback: int = 20):
        self.lookback = int(lookback)
        self.vol_lookback = int(vol_lookback)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < self.lookback + 5:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        volume = df.get("volume", pd.Series([0] * len(df))).astype(float)

        prior_high = float(high.rolling(self.lookback).max().shift(1).iloc[-1])
        current_close = float(close.iloc[-1])

        vol_mean = float(volume.rolling(self.vol_lookback).mean().iloc[-1])
        vol_ok = float(volume.iloc[-1]) > (vol_mean * 1.2 if vol_mean > 0 else 0)

        if current_close > prior_high and vol_ok:
            breakout_pct = (current_close - prior_high) / max(prior_high, 1e-9)
            confidence = min(100.0, breakout_pct * 5000.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": current_close,
                "reasoning": "Breakout above range high with volume expansion",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

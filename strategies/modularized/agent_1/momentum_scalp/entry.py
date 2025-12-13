from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """MomentumScalp entry skill.

    Logic:
    - 3-bar momentum positive
    - RSI(14) > 55
    - Volume above rolling mean
    """

    name = "momentum_scalp_entry"
    indicators = ["momentum_3", "rsi_14", "volume_mean"]
    warmup = 120

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "NEUTRAL", "confidence": 0}

        close = df["close"].astype(float)
        volume = df.get("volume", pd.Series([0] * len(df))).astype(float)

        mom3 = float(close.iloc[-1] - close.iloc[-4])
        rsi = float(self._rsi(close, 14).iloc[-1])

        vol_mean = float(volume.rolling(20).mean().iloc[-1])
        vol_ok = float(volume.iloc[-1]) > (vol_mean * 1.1 if vol_mean > 0 else 0)

        if mom3 > 0 and rsi > 55 and vol_ok:
            # Normalize confidence by momentum magnitude.
            confidence = min(100.0, abs(mom3) / max(close.iloc[-1], 1e-9) * 50_000.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": float(close.iloc[-1]),
                "reasoning": "Short-term momentum + RSI confirmation + volume expansion",
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

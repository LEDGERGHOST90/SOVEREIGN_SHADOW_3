"""Market regime detector.

This is a pragmatic, explainable classifier intended for:
- separating trending vs choppy conditions
- separating calm vs volatile conditions

Regimes (strings):
- trending_bull
- trending_bear
- choppy_calm
- choppy_volatile

Input: a pandas DataFrame with columns: close, high, low.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RegimeResult:
    regime: str
    features: Dict[str, Any]


class MarketRegimeDetector:
    def __init__(
        self,
        *,
        vol_window: int = 50,
        ema_fast: int = 20,
        ema_slow: int = 50,
        vol_calm_threshold: float = 0.012,
        trend_strength_threshold: float = 0.002,
    ):
        self.vol_window = vol_window
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.vol_calm_threshold = vol_calm_threshold
        self.trend_strength_threshold = trend_strength_threshold

    def detect(self, df: pd.DataFrame) -> RegimeResult:
        if df is None or len(df) < max(self.vol_window, self.ema_slow) + 5:
            return RegimeResult(regime="choppy_calm", features={"reason": "insufficient_data"})

        close = df["close"].astype(float)

        rets = close.pct_change().dropna()
        vol = float(rets.tail(self.vol_window).std(ddof=0)) if len(rets) else 0.0

        ema_f = close.ewm(span=self.ema_fast, adjust=False).mean()
        ema_s = close.ewm(span=self.ema_slow, adjust=False).mean()

        # Trend strength proxy: normalized EMA spread
        spread = float((ema_f.iloc[-1] - ema_s.iloc[-1]) / close.iloc[-1])
        trend_strength = abs(spread)

        # Direction proxy
        direction = "bull" if spread >= 0 else "bear"

        volatile = vol >= self.vol_calm_threshold
        trending = trend_strength >= self.trend_strength_threshold

        if trending and direction == "bull":
            regime = "trending_bull" if not volatile else "trending_bull"
        elif trending and direction == "bear":
            regime = "trending_bear" if not volatile else "trending_bear"
        else:
            regime = "choppy_volatile" if volatile else "choppy_calm"

        features = {
            "volatility": vol,
            "ema_fast": float(ema_f.iloc[-1]),
            "ema_slow": float(ema_s.iloc[-1]),
            "ema_spread_norm": spread,
            "trend_strength": trend_strength,
        }

        return RegimeResult(regime=regime, features=features)

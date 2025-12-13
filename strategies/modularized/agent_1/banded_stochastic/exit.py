from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """BandedStochastic exit skill.

    Exit:
    - %K crosses below %D while above 80 (overbought)
    """

    name = "banded_stochastic_exit"

    def __init__(self, *, band: float = 80.0, k_period: int = 14, d_period: int = 3):
        self.band = float(band)
        self.k_period = int(k_period)
        self.d_period = int(d_period)

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < self.k_period + self.d_period + 5:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        k, d = Entry._stoch(df, self.k_period, self.d_period)  # type: ignore[name-defined]

        crossed_down = float(k.iloc[-2]) >= float(d.iloc[-2]) and float(k.iloc[-1]) < float(d.iloc[-1])
        overbought = float(k.iloc[-1]) > self.band and float(d.iloc[-1]) > self.band

        current_price = float(close.iloc[-1])
        pnl_percent = ((current_price - float(entry_price)) / float(entry_price)) * 100.0

        if crossed_down and overbought:
            return {"signal": "SELL", "reason": "STOCH_OVERBOUGHT_CROSS", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}


# Local import to reuse the stochastic helper without duplicating code.
from .entry import Entry

from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """BollingerBounce exit skill.

    Exit:
    - Close reaches middle band (20 SMA)
    """

    name = "bollinger_bounce_exit"

    def __init__(self, *, period: int = 20):
        self.period = int(period)

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < self.period + 5:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        mid = close.rolling(self.period).mean()

        price = float(close.iloc[-1])
        pnl_percent = ((price - float(entry_price)) / float(entry_price)) * 100.0

        if price >= float(mid.iloc[-1]):
            return {"signal": "SELL", "reason": "MID_BAND_REACHED", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

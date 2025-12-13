from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """DynamicCrossfire exit skill.

    Exit:
    - EMA(9) crosses below EMA(21)
    - or TP/SL thresholds (handled by risk module/engine)
    """

    name = "dynamic_crossfire_exit"

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()

        crossed_down = float(ema9.iloc[-2]) >= float(ema21.iloc[-2]) and float(ema9.iloc[-1]) < float(ema21.iloc[-1])
        current_price = float(close.iloc[-1])
        pnl_percent = ((current_price - float(entry_price)) / float(entry_price)) * 100.0

        if crossed_down:
            return {"signal": "SELL", "reason": "EMA_CROSS_DOWN", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

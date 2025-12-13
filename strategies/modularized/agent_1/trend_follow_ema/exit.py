from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """TrendFollowEMA exit skill.

    Exit:
    - Close below EMA(20)
    """

    name = "trend_follow_ema_exit"

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        ema20 = close.ewm(span=20, adjust=False).mean()

        price = float(close.iloc[-1])
        pnl_percent = ((price - float(entry_price)) / float(entry_price)) * 100.0

        if price < float(ema20.iloc[-1]):
            return {"signal": "SELL", "reason": "CLOSE_BELOW_EMA20", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

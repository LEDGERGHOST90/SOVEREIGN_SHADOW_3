from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """ChoppyBreakout exit skill.

    Exit:
    - If close falls back below EMA(20) (failed breakout)
    """

    name = "choppy_breakout_exit"

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        ema20 = close.ewm(span=20, adjust=False).mean()

        current_close = float(close.iloc[-1])
        pnl_percent = ((current_close - float(entry_price)) / float(entry_price)) * 100.0

        if current_close < float(ema20.iloc[-1]):
            return {"signal": "SELL", "reason": "FAILED_BREAKOUT", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

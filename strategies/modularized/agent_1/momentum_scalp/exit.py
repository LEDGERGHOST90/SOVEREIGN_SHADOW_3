from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """MomentumScalp exit skill.

    Exit:
    - RSI falls below 50 (momentum lost)
    """

    name = "momentum_scalp_exit"

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        rsi = float(Entry._rsi(close, 14).iloc[-1])  # type: ignore[name-defined]

        current = float(close.iloc[-1])
        pnl_percent = ((current - float(entry_price)) / float(entry_price)) * 100.0

        if rsi < 50:
            return {"signal": "SELL", "reason": "RSI_MOMENTUM_LOST", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}


from .entry import Entry

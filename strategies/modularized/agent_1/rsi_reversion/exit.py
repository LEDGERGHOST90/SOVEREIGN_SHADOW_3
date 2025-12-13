from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """RSIReversion exit skill.

    Exit:
    - RSI(14) > 50 (mean reversion achieved)
    """

    name = "rsi_reversion_exit"

    def __init__(self, *, exit_rsi: float = 50.0):
        self.exit_rsi = float(exit_rsi)

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        rsi = float(Entry._rsi(close, 14).iloc[-1])  # type: ignore[name-defined]

        price = float(close.iloc[-1])
        pnl_percent = ((price - float(entry_price)) / float(entry_price)) * 100.0

        if rsi >= self.exit_rsi:
            return {"signal": "SELL", "reason": "RSI_MEAN_REVERTED", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}


from .entry import Entry

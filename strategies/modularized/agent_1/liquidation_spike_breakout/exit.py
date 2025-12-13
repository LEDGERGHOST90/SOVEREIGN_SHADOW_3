from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """LiquidationSpikeBreakout exit skill.

    Exit:
    - If price closes back inside the breakout range (below previous 10-bar high)
    """

    name = "liquidation_spike_breakout_exit"

    def __init__(self, *, break_lookback: int = 10):
        self.break_lookback = int(break_lookback)

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "HOLD", "pnl": 0.0}

        high = df["high"].astype(float)
        close = df["close"].astype(float)

        prev_high = float(high.rolling(self.break_lookback).max().shift(1).iloc[-1])
        current_price = float(close.iloc[-1])
        pnl_percent = ((current_price - float(entry_price)) / float(entry_price)) * 100.0

        if current_price < prev_high:
            return {"signal": "SELL", "reason": "BREAKOUT_FAIL", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

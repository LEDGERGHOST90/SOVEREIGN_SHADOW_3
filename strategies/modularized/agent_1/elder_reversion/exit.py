from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Exit:
    """ElderReversion exit skill.

    Exit conditions:
    - Take profit 2%
    - Stop loss 1%
    - Bull power turns positive
    """

    name = "elder_reversion_exit"

    def __init__(self, *, take_profit_percent: float = 2.0, stop_loss_percent: float = 1.0):
        self.take_profit_percent = float(take_profit_percent)
        self.stop_loss_percent = float(stop_loss_percent)

    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {"signal": "HOLD", "pnl": 0.0}

        close = df["close"].astype(float)
        high = df["high"].astype(float)

        ema_13 = close.ewm(span=13, adjust=False).mean()
        bull_power = high - ema_13

        current_price = float(close.iloc[-1])
        pnl_percent = ((current_price - float(entry_price)) / float(entry_price)) * 100.0

        if pnl_percent >= self.take_profit_percent:
            return {"signal": "SELL", "reason": "TAKE_PROFIT", "pnl": pnl_percent}

        if pnl_percent <= -self.stop_loss_percent:
            return {"signal": "SELL", "reason": "STOP_LOSS", "pnl": pnl_percent}

        if float(bull_power.iloc[-1]) > 0:
            return {"signal": "SELL", "reason": "SIGNAL_EXIT", "pnl": pnl_percent}

        return {"signal": "HOLD", "pnl": pnl_percent}

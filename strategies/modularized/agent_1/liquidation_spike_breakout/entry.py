from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class Entry:
    """LiquidationSpikeBreakout entry skill.

    Proxy logic (since true liquidations require derivatives data):
    - Volume spike: volume > 2.5x rolling mean
    - Candle range spike: (high-low) > 2x ATR(14)
    - Breaks above previous 10-bar high

    Intended for: choppy_volatile
    """

    name = "liquidation_spike_breakout_entry"
    indicators = ["volume", "atr_14", "rolling_high"]
    warmup = 120

    def __init__(self, *, vol_mult: float = 2.5, break_lookback: int = 10):
        self.vol_mult = float(vol_mult)
        self.break_lookback = int(break_lookback)

    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 30:
            return {"signal": "NEUTRAL", "confidence": 0}

        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)
        volume = df.get("volume", pd.Series([0] * len(df))).astype(float)

        atr = self._atr(df)
        candle_range = float(high.iloc[-1] - low.iloc[-1])

        vol_mean = float(volume.rolling(20).mean().iloc[-1])
        vol_spike = float(volume.iloc[-1]) > (vol_mean * self.vol_mult if vol_mean > 0 else 0)
        range_spike = candle_range > (2.0 * atr)

        prev_high = float(high.rolling(self.break_lookback).max().shift(1).iloc[-1])
        broke = float(close.iloc[-1]) > prev_high

        if vol_spike and range_spike and broke:
            confidence = min(100.0, (candle_range / max(atr, 1e-9)) * 20.0)
            return {
                "signal": "BUY",
                "confidence": float(confidence),
                "price": float(close.iloc[-1]),
                "reasoning": "Volume+ranges spike with breakout above recent high (liquidation proxy)",
            }

        return {"signal": "NEUTRAL", "confidence": 0}

    @staticmethod
    def _atr(df: pd.DataFrame, period: int = 14) -> float:
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)
        tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        return float(atr) if pd.notna(atr) else float(tr.iloc[-1])

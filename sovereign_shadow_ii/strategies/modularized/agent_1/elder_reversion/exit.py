#!/usr/bin/env python3
"""
Elder Reversion Strategy - Exit Module
Agent 1 Strategy #1
"""

from typing import Dict, List


class ElderReversionExit:
    def __init__(self):
        self.name = "elder_reversion_exit"

    def generate_signal(self, df_or_list, entry_price: float) -> Dict:
        """
        Exit Logic:
        1. Bull Power > 0 (trend reversal complete)
        2. Take Profit 2%
        3. Stop Loss 1%
        """
        if hasattr(df_or_list, 'iloc'):
            closes = df_or_list['close'].tolist()
            highs = df_or_list['high'].tolist()
        else:
            closes = [d['close'] for d in df_or_list]
            highs = [d['high'] for d in df_or_list]

        if len(closes) < 20:
            return {'signal': 'HOLD', 'pnl': 0}

        current_price = closes[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100

        # Take profit
        if pnl_percent >= 2.0:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}

        # Stop loss
        if pnl_percent <= -1.0:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}

        # Bull power positive (reversal complete)
        ema_13 = self._calculate_ema(closes, 13)
        bull_power = highs[-1] - ema_13

        if bull_power > 0:
            return {'signal': 'SELL', 'reason': 'SIGNAL_EXIT', 'pnl': pnl_percent}

        return {'signal': 'HOLD', 'pnl': pnl_percent}

    def _calculate_ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data)
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

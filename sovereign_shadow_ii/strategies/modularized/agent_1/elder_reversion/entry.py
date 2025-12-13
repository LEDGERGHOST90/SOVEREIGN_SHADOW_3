#!/usr/bin/env python3
"""
Elder Reversion Strategy - Entry Module
Agent 1 Strategy #1

Entry Logic: Bull Power < 0 AND Price above EMA-13
This signals oversold conditions in an uptrend - prime reversion opportunity
"""

from typing import Dict, List


class ElderReversionEntry:
    def __init__(self):
        self.name = "elder_reversion_entry"
        self.indicators = ['elder_ray', 'ema_13']

    def generate_signal(self, df_or_list) -> Dict:
        """
        Generate entry signal based on Elder Ray indicator.

        Args:
            df_or_list: Either pandas DataFrame or list of OHLCV dicts

        Returns:
            {'signal': 'BUY'|'NEUTRAL', 'confidence': 0-100, 'price': float}
        """
        # Handle both DataFrame and list input
        if hasattr(df_or_list, 'iloc'):
            # It's a DataFrame
            closes = df_or_list['close'].tolist()
            highs = df_or_list['high'].tolist()
            lows = df_or_list['low'].tolist()
        else:
            # It's a list
            closes = [d['close'] for d in df_or_list]
            highs = [d['high'] for d in df_or_list]
            lows = [d['low'] for d in df_or_list]

        if len(closes) < 20:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        # Calculate EMA-13
        ema_13 = self._calculate_ema(closes, 13)

        # Calculate Elder Ray
        bull_power = highs[-1] - ema_13
        bear_power = lows[-1] - ema_13

        current_price = closes[-1]

        # Entry: Bull Power negative, price above EMA
        if bull_power < 0 and current_price > ema_13:
            confidence = min(abs(bull_power / current_price) * 1000, 100)
            confidence = max(confidence, 30)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'price': current_price,
                'reasoning': f'Elder Bull Power negative ({bull_power:.4f}), price above EMA-13'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0}

    def _calculate_ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data)
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

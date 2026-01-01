#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - Built-in Strategy Implementations

These are core strategies that are always available without external modules.
Each strategy is modularized into Entry, Exit, and Risk components.

Strategies included:
1. ElderReversion - Mean reversion using Elder Ray
2. RSIReversion - RSI-based mean reversion
3. TrendFollowEMA - EMA crossover trend following
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


# ==============================================================================
# ELDER REVERSION STRATEGY
# Type: Mean Reversion
# Best for: choppy_volatile, choppy_calm
# ==============================================================================

class ElderReversionEntry:
    """Elder Reversion entry logic using Elder Ray indicator"""

    def __init__(self):
        self.name = "elder_reversion_entry"
        self.indicators = ['elder_ray', 'ema_13']

    def generate_signal(self, market_data: List[Dict]) -> Dict:
        """
        Entry Logic: Bull Power < 0 AND Price above EMA-13
        This indicates oversold in an uptrend - reversion opportunity

        Returns:
            {'signal': 'BUY'|'NEUTRAL', 'confidence': 0-100, 'price': float}
        """
        if len(market_data) < 20:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        closes = [d['close'] for d in market_data]
        highs = [d['high'] for d in market_data]
        lows = [d['low'] for d in market_data]

        # Calculate EMA-13
        ema_13 = self._calculate_ema(closes, 13)

        # Calculate Elder Ray
        bull_power = highs[-1] - ema_13
        bear_power = lows[-1] - ema_13

        current_price = closes[-1]

        # Entry condition: Bull Power negative but price above EMA
        if bull_power < 0 and current_price > ema_13:
            # Confidence based on how oversold
            confidence = min(abs(bull_power / current_price) * 1000, 100)
            confidence = max(confidence, 30)  # Minimum 30%

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'price': current_price,
                'reasoning': f'Elder Bull Power negative ({bull_power:.2f}), price above EMA-13'
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


class ElderReversionExit:
    """Elder Reversion exit logic"""

    def __init__(self):
        self.name = "elder_reversion_exit"
        self.take_profit_percent = 2.0
        self.stop_loss_percent = 1.0

    def generate_signal(self, market_data: List[Dict], entry_price: float) -> Dict:
        """
        Exit Logic:
        1. Bull Power > 0 (trend reversal complete)
        2. Take Profit at 2%
        3. Stop Loss at 1%
        """
        if len(market_data) < 20:
            return {'signal': 'HOLD', 'pnl': 0}

        closes = [d['close'] for d in market_data]
        highs = [d['high'] for d in market_data]
        current_price = closes[-1]

        # Calculate current PnL
        pnl_percent = ((current_price - entry_price) / entry_price) * 100

        # Take profit
        if pnl_percent >= self.take_profit_percent:
            return {
                'signal': 'SELL',
                'reason': 'TAKE_PROFIT',
                'pnl': pnl_percent
            }

        # Stop loss
        if pnl_percent <= -self.stop_loss_percent:
            return {
                'signal': 'SELL',
                'reason': 'STOP_LOSS',
                'pnl': pnl_percent
            }

        # Signal exit: Bull power turns positive
        ema_13 = self._calculate_ema(closes, 13)
        bull_power = highs[-1] - ema_13

        if bull_power > 0:
            return {
                'signal': 'SELL',
                'reason': 'SIGNAL_EXIT',
                'pnl': pnl_percent
            }

        return {'signal': 'HOLD', 'pnl': pnl_percent}

    def _calculate_ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data)
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema


class ElderReversionRisk:
    """Elder Reversion risk management"""

    def __init__(self):
        self.max_position_size = 0.10  # 10% of portfolio
        self.stop_loss_percent = 1.0
        self.take_profit_percent = 2.0
        self.risk_per_trade = 0.01  # 1% risk

    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: float
    ) -> Dict:
        """Position sizing based on volatility (ATR)"""
        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = max(atr * 1.5, current_price * (self.stop_loss_percent / 100))
        position_value = (risk_amount / stop_distance) * current_price
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)

        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent / 100),
            'take_profit_price': current_price * (1 + self.take_profit_percent / 100)
        }


# ==============================================================================
# RSI REVERSION STRATEGY
# Type: Mean Reversion
# Best for: choppy_volatile, choppy_calm, capitulation
# ==============================================================================

class RSIReversionEntry:
    """RSI-based mean reversion entry"""

    def __init__(self):
        self.name = "rsi_reversion_entry"
        self.rsi_oversold = 30
        self.rsi_overbought = 70

    def generate_signal(self, market_data: List[Dict]) -> Dict:
        """
        Entry Logic: RSI < 30 (oversold)
        """
        if len(market_data) < 20:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        closes = [d['close'] for d in market_data]
        rsi = self._calculate_rsi(closes, 14)
        current_price = closes[-1]

        if rsi < self.rsi_oversold:
            # More oversold = higher confidence
            confidence = min((self.rsi_oversold - rsi) * 3 + 50, 90)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'price': current_price,
                'reasoning': f'RSI oversold at {rsi:.1f}'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'rsi': rsi}

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50

        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


class RSIReversionExit:
    """RSI reversion exit logic"""

    def __init__(self):
        self.name = "rsi_reversion_exit"
        self.rsi_exit = 50  # Exit when RSI normalizes
        self.take_profit_percent = 3.0
        self.stop_loss_percent = 1.5

    def generate_signal(self, market_data: List[Dict], entry_price: float) -> Dict:
        """
        Exit Logic:
        1. RSI > 50 (normalized)
        2. Take Profit at 3%
        3. Stop Loss at 1.5%
        """
        if len(market_data) < 20:
            return {'signal': 'HOLD', 'pnl': 0}

        closes = [d['close'] for d in market_data]
        current_price = closes[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100

        # Take profit
        if pnl_percent >= self.take_profit_percent:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}

        # Stop loss
        if pnl_percent <= -self.stop_loss_percent:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}

        # RSI exit
        rsi = self._calculate_rsi(closes, 14)
        if rsi > self.rsi_exit and pnl_percent > 0:
            return {'signal': 'SELL', 'reason': 'RSI_NORMALIZED', 'pnl': pnl_percent}

        return {'signal': 'HOLD', 'pnl': pnl_percent}

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


class RSIReversionRisk:
    """RSI reversion risk management"""

    def __init__(self):
        self.max_position_size = 0.08
        self.stop_loss_percent = 1.5
        self.take_profit_percent = 3.0
        self.risk_per_trade = 0.01

    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: float
    ) -> Dict:
        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = max(atr * 1.5, current_price * (self.stop_loss_percent / 100))
        position_value = (risk_amount / stop_distance) * current_price
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)

        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent / 100),
            'take_profit_price': current_price * (1 + self.take_profit_percent / 100)
        }


# ==============================================================================
# TREND FOLLOW EMA STRATEGY
# Type: Trend Following
# Best for: trending_bullish, trending_bearish
# ==============================================================================

class TrendFollowEMAEntry:
    """EMA crossover trend following entry"""

    def __init__(self):
        self.name = "trend_follow_ema_entry"
        self.fast_period = 9
        self.slow_period = 21

    def generate_signal(self, market_data: List[Dict]) -> Dict:
        """
        Entry Logic: Fast EMA crosses above Slow EMA
        """
        if len(market_data) < self.slow_period + 5:
            return {'signal': 'NEUTRAL', 'confidence': 0}

        closes = [d['close'] for d in market_data]

        fast_ema = self._calculate_ema(closes, self.fast_period)
        slow_ema = self._calculate_ema(closes, self.slow_period)

        # Previous values
        prev_closes = closes[:-1]
        prev_fast_ema = self._calculate_ema(prev_closes, self.fast_period)
        prev_slow_ema = self._calculate_ema(prev_closes, self.slow_period)

        current_price = closes[-1]

        # Bullish crossover
        if prev_fast_ema <= prev_slow_ema and fast_ema > slow_ema:
            # Confidence based on spread
            spread = (fast_ema - slow_ema) / slow_ema * 100
            confidence = min(spread * 50 + 50, 85)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'price': current_price,
                'reasoning': f'EMA bullish crossover (9 > 21)'
            }

        # Confirmation: already in uptrend
        if fast_ema > slow_ema and current_price > fast_ema:
            spread = (fast_ema - slow_ema) / slow_ema * 100
            if spread > 0.5:  # Significant spread
                return {
                    'signal': 'BUY',
                    'confidence': 60,
                    'price': current_price,
                    'reasoning': f'Confirmed uptrend (EMA spread: {spread:.2f}%)'
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


class TrendFollowEMAExit:
    """EMA trend following exit logic"""

    def __init__(self):
        self.name = "trend_follow_ema_exit"
        self.fast_period = 9
        self.slow_period = 21
        self.trailing_stop_percent = 2.0
        self.take_profit_percent = 5.0
        self.stop_loss_percent = 2.0

    def generate_signal(self, market_data: List[Dict], entry_price: float) -> Dict:
        """
        Exit Logic:
        1. Fast EMA crosses below Slow EMA (bearish crossover)
        2. Price closes below Slow EMA
        3. Take Profit at 5%
        4. Stop Loss at 2%
        """
        if len(market_data) < self.slow_period + 5:
            return {'signal': 'HOLD', 'pnl': 0}

        closes = [d['close'] for d in market_data]
        current_price = closes[-1]
        pnl_percent = ((current_price - entry_price) / entry_price) * 100

        # Take profit
        if pnl_percent >= self.take_profit_percent:
            return {'signal': 'SELL', 'reason': 'TAKE_PROFIT', 'pnl': pnl_percent}

        # Stop loss
        if pnl_percent <= -self.stop_loss_percent:
            return {'signal': 'SELL', 'reason': 'STOP_LOSS', 'pnl': pnl_percent}

        fast_ema = self._calculate_ema(closes, self.fast_period)
        slow_ema = self._calculate_ema(closes, self.slow_period)

        # Bearish crossover
        prev_closes = closes[:-1]
        prev_fast_ema = self._calculate_ema(prev_closes, self.fast_period)
        prev_slow_ema = self._calculate_ema(prev_closes, self.slow_period)

        if prev_fast_ema >= prev_slow_ema and fast_ema < slow_ema:
            return {'signal': 'SELL', 'reason': 'BEARISH_CROSSOVER', 'pnl': pnl_percent}

        # Price below slow EMA (trend broken)
        if current_price < slow_ema and pnl_percent > 0:
            return {'signal': 'SELL', 'reason': 'TREND_BREAK', 'pnl': pnl_percent}

        return {'signal': 'HOLD', 'pnl': pnl_percent}

    def _calculate_ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data)
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema


class TrendFollowEMARisk:
    """EMA trend following risk management"""

    def __init__(self):
        self.max_position_size = 0.12
        self.stop_loss_percent = 2.0
        self.take_profit_percent = 5.0
        self.risk_per_trade = 0.015

    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: float
    ) -> Dict:
        risk_amount = portfolio_value * self.risk_per_trade
        stop_distance = max(atr * 2, current_price * (self.stop_loss_percent / 100))
        position_value = (risk_amount / stop_distance) * current_price
        max_value = portfolio_value * self.max_position_size
        position_value = min(position_value, max_value)

        return {
            'position_value_usd': position_value,
            'quantity': position_value / current_price,
            'stop_loss_price': current_price * (1 - self.stop_loss_percent / 100),
            'take_profit_price': current_price * (1 + self.take_profit_percent / 100)
        }


# ==============================================================================
# STRATEGY REGISTRY
# ==============================================================================

STRATEGY_REGISTRY = {
    "ElderReversion": {
        "entry": ElderReversionEntry,
        "exit": ElderReversionExit,
        "risk": ElderReversionRisk,
        "type": "mean_reversion",
        "suitable_regimes": ["choppy_volatile", "choppy_calm"],
        "timeframes": ["15m", "1h"]
    },
    "RSIReversion": {
        "entry": RSIReversionEntry,
        "exit": RSIReversionExit,
        "risk": RSIReversionRisk,
        "type": "mean_reversion",
        "suitable_regimes": ["choppy_volatile", "choppy_calm", "capitulation"],
        "timeframes": ["15m", "1h", "4h"]
    },
    "TrendFollowEMA": {
        "entry": TrendFollowEMAEntry,
        "exit": TrendFollowEMAExit,
        "risk": TrendFollowEMARisk,
        "type": "trend_following",
        "suitable_regimes": ["trending_bullish", "trending_bearish"],
        "timeframes": ["15m", "1h"]
    }
}


def get_strategy(name: str) -> Optional[Dict]:
    """Get a strategy by name"""
    if name in STRATEGY_REGISTRY:
        reg = STRATEGY_REGISTRY[name]
        return {
            "entry": reg["entry"](),
            "exit": reg["exit"](),
            "risk": reg["risk"](),
            "metadata": {
                "type": reg["type"],
                "suitable_regimes": reg["suitable_regimes"],
                "timeframes": reg["timeframes"]
            }
        }
    return None


def list_strategies() -> List[str]:
    """List all available strategies"""
    return list(STRATEGY_REGISTRY.keys())


if __name__ == "__main__":
    # Test strategies
    import random

    # Generate test data
    test_data = []
    base_price = 95000
    for i in range(50):
        close = base_price + i * 10 + random.uniform(-100, 100)
        test_data.append({
            'open': close + random.uniform(-50, 50),
            'high': close + random.uniform(0, 200),
            'low': close - random.uniform(0, 200),
            'close': close,
            'volume': random.uniform(100, 1000)
        })

    print("=== BUILT-IN STRATEGY TEST ===\n")

    for name in list_strategies():
        strategy = get_strategy(name)
        print(f"\n{name}:")

        # Test entry
        entry_signal = strategy['entry'].generate_signal(test_data)
        print(f"  Entry Signal: {entry_signal.get('signal')}")
        if entry_signal.get('confidence'):
            print(f"  Confidence: {entry_signal.get('confidence'):.1f}%")

        # Test exit
        if entry_signal.get('signal') == 'BUY':
            exit_signal = strategy['exit'].generate_signal(
                test_data, entry_signal.get('price', test_data[-1]['close'])
            )
            print(f"  Exit Signal: {exit_signal.get('signal')}")

        # Test risk
        risk = strategy['risk'].calculate_position_size(
            portfolio_value=10000,
            current_price=test_data[-1]['close'],
            atr=200
        )
        print(f"  Position Size: ${risk['position_value_usd']:.2f}")

    print("\n\nBuilt-in strategies test complete!")

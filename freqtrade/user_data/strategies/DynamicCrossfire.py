# -*- coding: utf-8 -*-
"""
DynamicCrossfire Strategy - Converted for FreqTrade
Original: Moon Dev | Converted: Aurora (Claude)

Strategy: EMA Golden Cross + ADX Trend Strength
- Entry: EMA50 crosses above EMA200 + ADX > 25 and rising
- Exit: RSI > 70 or EMA death cross
- Risk: 1% per trade with swing low stop-loss

Hyperopt-enabled: Run with freqtrade hyperopt to auto-tune parameters
"""
import numpy as np
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from freqtrade.persistence import Trade
from pandas import DataFrame
import talib.abstract as ta
from datetime import datetime
from typing import Optional


class DynamicCrossfire(IStrategy):
    """
    Moon Dev's DynamicCrossfire - EMA crossover with ADX confirmation
    Optimized for trending markets (INJ, LINK, SOL)

    Hyperopt Spaces:
    - buy: EMA periods, ADX threshold, volume multiplier
    - sell: RSI overbought level
    - roi: Minimal ROI targets
    - stoploss: Stop loss percentage
    """

    # Strategy interface version
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy
    timeframe = '15m'

    # Can this strategy go short?
    can_short = False

    # Minimal ROI designed for the strategy (hyperopt will override)
    minimal_roi = {
        "0": 0.15,
        "60": 0.10,
        "120": 0.05,
        "240": 0.02
    }

    # Optimal stoploss (hyperopt will override)
    stoploss = -0.05

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # ========== HYPEROPT PARAMETER SPACES ==========

    # EMA Fast Period: 20-100 (default 50)
    ema_fast_period = IntParameter(20, 100, default=50, space='buy', optimize=True)

    # EMA Slow Period: 100-300 (default 200)
    ema_slow_period = IntParameter(100, 300, default=200, space='buy', optimize=True)

    # ADX Period: 7-21 (default 14)
    adx_period = IntParameter(7, 21, default=14, space='buy', optimize=True)

    # ADX Threshold: 15-40 (default 25) - trend strength requirement
    adx_threshold = IntParameter(15, 40, default=25, space='buy', optimize=True)

    # RSI Period: 7-21 (default 14)
    rsi_period = IntParameter(7, 21, default=14, space='sell', optimize=True)

    # RSI Overbought: 60-85 (default 70) - exit trigger
    rsi_overbought = IntParameter(60, 85, default=70, space='sell', optimize=True)

    # Volume Multiplier: 0.5-2.0 (default 1.0) - volume confirmation
    volume_mult = DecimalParameter(0.5, 2.0, default=1.0, decimals=1, space='buy', optimize=True)

    # Swing Period: 10-30 (default 20) - for dynamic stop-loss
    swing_period = IntParameter(10, 30, default=20, space='buy', optimize=True)

    # Number of candles the strategy requires before producing valid signals
    # Must be >= largest EMA period (300)
    startup_candle_count = 300

    # Position sizing (1% risk)
    position_adjustment_enable = False

    def informative_pairs(self):
        """Define informative pairs for multi-timeframe analysis."""
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several indicators to the given DataFrame.
        Uses hyperopt parameter values (.value) for optimization.
        """
        # Calculate EMAs for all possible periods in hyperopt range
        # This allows hyperopt to test different combinations without recalculating
        for period in range(20, 301, 10):
            dataframe[f'ema_{period}'] = ta.EMA(dataframe, timeperiod=period)

        # ADX for all possible periods
        for period in range(7, 22):
            dataframe[f'adx_{period}'] = ta.ADX(dataframe, timeperiod=period)

        # RSI for all possible periods
        for period in range(7, 22):
            dataframe[f'rsi_{period}'] = ta.RSI(dataframe, timeperiod=period)

        # Swing Low for all possible periods
        for period in range(10, 31):
            dataframe[f'swing_low_{period}'] = dataframe['low'].rolling(window=period).min()

        # Volume moving average for confirmation
        dataframe['volume_mean'] = dataframe['volume'].rolling(20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry conditions:
        - EMA Fast crosses above EMA Slow (Golden Cross)
        - ADX > threshold and rising (strong trend)
        - Volume above average * multiplier

        Uses hyperopt parameter values for optimization.
        """
        # Get hyperopt parameter values (round EMA to nearest 10 for pre-calculated)
        ema_fast = min(300, max(20, (self.ema_fast_period.value // 10) * 10))
        ema_slow = min(300, max(100, (self.ema_slow_period.value // 10) * 10))
        adx_p = self.adx_period.value
        adx_thresh = self.adx_threshold.value
        vol_mult = self.volume_mult.value

        # Get the pre-calculated indicators
        ema_fast_col = f'ema_{ema_fast}'
        ema_slow_col = f'ema_{ema_slow}'
        adx_col = f'adx_{adx_p}'

        conditions = []

        # Golden Cross: EMA fast crosses above EMA slow
        conditions.append(
            (dataframe[ema_fast_col] > dataframe[ema_slow_col]) &
            (dataframe[ema_fast_col].shift(1) <= dataframe[ema_slow_col].shift(1))
        )

        # ADX confirmation: above threshold and rising
        conditions.append(
            (dataframe[adx_col] > adx_thresh) &
            (dataframe[adx_col] > dataframe[adx_col].shift(1))
        )

        # Volume confirmation: above average * multiplier
        conditions.append(dataframe['volume'] > dataframe['volume_mean'] * vol_mult)

        if conditions:
            dataframe.loc[
                np.all(conditions, axis=0),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit conditions:
        - RSI > overbought threshold
        - EMA Death Cross

        Uses hyperopt parameter values for optimization.
        """
        # Get hyperopt parameter values
        ema_fast = min(300, max(20, (self.ema_fast_period.value // 10) * 10))
        ema_slow = min(300, max(100, (self.ema_slow_period.value // 10) * 10))
        rsi_p = self.rsi_period.value
        rsi_ob = self.rsi_overbought.value

        # Get the pre-calculated indicators
        ema_fast_col = f'ema_{ema_fast}'
        ema_slow_col = f'ema_{ema_slow}'
        rsi_col = f'rsi_{rsi_p}'

        # RSI overbought exit
        dataframe.loc[
            dataframe[rsi_col] > rsi_ob,
            'exit_long'
        ] = 1

        # Death Cross exit
        dataframe.loc[
            (dataframe[ema_fast_col] < dataframe[ema_slow_col]) &
            (dataframe[ema_fast_col].shift(1) >= dataframe[ema_slow_col].shift(1)),
            'exit_long'
        ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float,
                        after_fill: bool, **kwargs) -> Optional[float]:
        """
        Custom stoploss logic - use swing low as dynamic stop
        Uses hyperopt swing_period parameter.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]
            swing_col = f'swing_low_{self.swing_period.value}'
            swing_low = last_candle.get(swing_col, 0)

            # Calculate stop distance from current price
            if swing_low > 0:
                stop_distance = (current_rate - swing_low) / current_rate
                # Only tighten stop, never loosen
                if stop_distance < abs(self.stoploss):
                    return -stop_distance

        return None
